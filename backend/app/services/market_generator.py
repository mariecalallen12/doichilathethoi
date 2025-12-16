"""
Market data generator (fallback)

Sinh dữ liệu OHLC giả lập trên server khi không có dữ liệu thật,
tránh phụ thuộc API bên ngoài hoặc dữ liệu chưa có trong DB.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import List, Dict


def _seed_price(symbol: str) -> float:
    seeds = {
        "BTCUSDT": 45000.0,
        "ETHUSDT": 2500.0,
        "BNBUSDT": 300.0,
        "EURUSD": 1.08,
        "XAUUSD": 2300.0,
    }
    return seeds.get(symbol.upper(), 100.0 + (hash(symbol) % 500) / 10.0)


def generate_candles(symbol: str, limit: int = 100, timeframe: str = "1h") -> List[Dict]:
    """
    Sinh dữ liệu OHLC đơn giản bằng random-walk + noise.
    Không lưu DB, chỉ làm fallback khi thiếu dữ liệu thực.
    """
    symbol = symbol.upper()
    base_price = _seed_price(symbol)
    candles: List[Dict] = []

    # Xác định bước thời gian
    tf_map = {
        "1m": timedelta(minutes=1),
        "5m": timedelta(minutes=5),
        "15m": timedelta(minutes=15),
        "1h": timedelta(hours=1),
        "4h": timedelta(hours=4),
        "1d": timedelta(days=1),
    }
    step = tf_map.get(timeframe, timedelta(hours=1))

    # Sinh từ quá khứ đến hiện tại
    ts = datetime.utcnow() - step * limit
    price = base_price
    for _ in range(limit):
        drift = random.uniform(-0.002, 0.002)  # ±0.2%
        vol = random.uniform(0.001, 0.01)      # noise
        change = price * (drift + vol * random.choice([-1, 1]))
        open_p = price
        close_p = max(0.0001, price + change)
        high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.001))
        low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.001))
        volume = abs(change) * random.uniform(10, 100)

        candles.append({
            "timestamp": ts.isoformat(),
            "open": float(open_p),
            "high": float(high_p),
            "low": float(low_p),
            "close": float(close_p),
            "volume": float(volume),
            "number_of_trades": int(volume // 10),
        })

        price = close_p
        ts += step

    return candles


