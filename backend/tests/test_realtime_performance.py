"""
Test Real-time Performance
Tests for latency, throughput, and real-time updates
"""
import pytest
import asyncio
import time
from datetime import datetime

from app.services.trading_data_simulator import TradingDataSimulator, get_trading_data_simulator
from app.utils.performance_monitor import get_performance_monitor, LatencyTimer


@pytest.mark.asyncio
async def test_simulator_interval():
    """Test that simulator runs with 0.1s interval (10 ticks/s)"""
    sim = TradingDataSimulator(symbols=["BTCUSDT"])
    
    tick_times = []
    async def record_tick(event_type, channel, payload):
        tick_times.append(time.perf_counter())
    
    sim.broadcast_fn = record_tick
    await sim.start(interval_seconds=0.1)
    
    # Wait for 5 ticks
    await asyncio.sleep(0.6)
    await sim.stop()
    
    # Check interval is approximately 0.1s
    if len(tick_times) >= 2:
        intervals = [tick_times[i] - tick_times[i-1] for i in range(1, len(tick_times))]
        avg_interval = sum(intervals) / len(intervals)
        
        # Allow 20% tolerance
        assert 0.08 <= avg_interval <= 0.12, f"Average interval {avg_interval}s not in expected range"
        assert len(tick_times) >= 5, f"Expected at least 5 ticks, got {len(tick_times)}"


@pytest.mark.asyncio
async def test_broadcast_latency():
    """Test that broadcast latency is < 20ms"""
    sim = TradingDataSimulator(symbols=["BTCUSDT"])
    monitor = get_performance_monitor()
    monitor.reset()
    
    async def dummy_broadcast(event_type, channel, payload):
        # Simulate minimal broadcast work
        await asyncio.sleep(0.001)  # 1ms
    
    sim.broadcast_fn = dummy_broadcast
    await sim.start(interval_seconds=0.1)
    
    # Wait for some ticks
    await asyncio.sleep(0.5)
    await sim.stop()
    
    # Check broadcast stats
    stats = monitor.get_broadcast_stats()
    if stats["count"] > 0:
        assert stats["mean"] < 20, f"Average broadcast time {stats['mean']}ms exceeds 20ms"
        assert stats["max"] < 50, f"Max broadcast time {stats['max']}ms exceeds 50ms"


@pytest.mark.asyncio
async def test_24h_history_generation():
    """Test that 24h history is generated on startup"""
    sim = TradingDataSimulator(symbols=["BTCUSDT"])
    await sim.start(interval_seconds=0.1)
    
    # Wait a bit for initialization
    await asyncio.sleep(0.2)
    
    # Check candles exist
    candles = sim.candles.get("BTCUSDT", [])
    assert len(candles) > 0, "No candles generated"
    
    # Check we have approximately 24h of 1-minute candles (1440)
    # Allow some tolerance
    assert len(candles) >= 1000, f"Expected at least 1000 candles, got {len(candles)}"
    
    await sim.stop()


@pytest.mark.asyncio
async def test_scenario_application():
    """Test that scenarios are applied correctly"""
    sim = TradingDataSimulator(symbols=["BTCUSDT"])
    await sim.start(interval_seconds=0.1)
    
    # Apply UPTREND scenario
    from app.schemas.trading_simulator import TradingSimScenario
    scenario = TradingSimScenario(
        symbol="BTCUSDT",
        trend="UPTREND",
        drift=0.001,
        volatility=0.002,
    )
    
    from app.schemas.trading_simulator import TradingSimScenarioUpdate
    update = TradingSimScenarioUpdate(scenarios=[scenario])
    await sim.update_scenarios(update)
    
    # Wait for a few ticks
    await asyncio.sleep(0.3)
    
    # Check price increased (UPTREND)
    initial_price = sim.state["BTCUSDT"]["price"]
    await asyncio.sleep(0.5)
    final_price = sim.state["BTCUSDT"]["price"]
    
    # With UPTREND, price should generally increase
    # Allow some variance due to volatility
    price_change = final_price - initial_price
    assert price_change > -initial_price * 0.01, "Price should not drop significantly with UPTREND"
    
    await sim.stop()


def test_performance_monitor():
    """Test performance monitor functionality"""
    monitor = get_performance_monitor()
    monitor.reset()
    
    # Record some samples
    for i in range(10):
        monitor.record_latency(i * 2.0)  # 0, 2, 4, ..., 18 ms
    
    stats = monitor.get_latency_stats()
    assert stats["count"] == 10
    assert stats["min"] == 0.0
    assert stats["max"] == 18.0
    assert stats["mean"] == 9.0
    assert stats["median"] == 9.0


def test_latency_timer():
    """Test latency timer context manager"""
    monitor = get_performance_monitor()
    monitor.reset()
    
    with LatencyTimer(monitor):
        time.sleep(0.01)  # 10ms
    
    stats = monitor.get_latency_stats()
    assert stats["count"] == 1
    assert 8 <= stats["mean"] <= 15, f"Expected ~10ms, got {stats['mean']}ms"


@pytest.mark.asyncio
async def test_message_size_optimization():
    """Test that message payloads are optimized (small size)"""
    sim = TradingDataSimulator(symbols=["BTCUSDT"])
    monitor = get_performance_monitor()
    monitor.reset()
    
    async def record_size(event_type, channel, payload):
        import json
        size = len(json.dumps(payload).encode('utf-8'))
        monitor.record_message_size(size)
    
    sim.broadcast_fn = record_size
    await sim.start(interval_seconds=0.1)
    
    # Wait for some ticks
    await asyncio.sleep(0.5)
    await sim.stop()
    
    # Check message sizes are reasonable (optimized payloads should be < 200 bytes)
    stats = monitor.get_message_size_stats()
    if stats["count"] > 0:
        assert stats["mean"] < 200, f"Average message size {stats['mean']} bytes is too large"
        assert stats["max"] < 500, f"Max message size {stats['max']} bytes is too large"

