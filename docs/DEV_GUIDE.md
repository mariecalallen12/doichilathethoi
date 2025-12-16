# Developer Guide - Market-Maker Engine

## Tổng quan

Hướng dẫn phát triển và maintain Market-Maker Engine, bao gồm architecture, APIs, và best practices.

## 1. Architecture

### 1.1. Components

```
┌─────────────────────────────────────────┐
│         Admin Dashboard (Vue 3)          │
│  - Scenario Builder                      │
│  - Session Manager                       │
│  - Monitoring Hub                        │
│  - Educational Hub                       │
└──────────────┬──────────────────────────┘
               │ REST API + WebSocket
┌──────────────▼──────────────────────────┐
│      Backend API (FastAPI)               │
│  - Trading Data Simulator                │
│  - Matching Engine                       │
│  - Session Service                       │
│  - Market Display Config                 │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Database (TimescaleDB)              │
│  - market_data_history (hypertable)       │
│  - price_tick (hypertable)               │
│  - system_settings                       │
│  - audit_logs                            │
└──────────────────────────────────────────┘
```

### 1.2. Data Flow

1. **Admin tạo scenario** → Lưu vào `system_settings`
2. **Simulator đọc scenario** → Áp dụng cho price generation
3. **Price được generate** → Lưu vào `price_tick` và `market_data_history`
4. **WebSocket broadcast** → Client nhận real-time updates
5. **Session được lưu** → Có thể replay sau

## 2. Trading Data Simulator

### 2.1. Price Generation Algorithm

**Brownian Motion + Jump-Diffusion Model:**

```python
dS = μ*S*dt + σ*S*dW + J*dN
```

Trong đó:
- `μ`: drift rate (từ scenario)
- `σ`: volatility (từ scenario)
- `dW`: Wiener process (Gaussian noise)
- `J`: jump size
- `dN`: Poisson process (jump events)

**Implementation:**
- Drift component: `price * drift * dt`
- Brownian component: `price * volatility * sqrt(dt) * N(0,1)`
- Jump component: Poisson process với lambda = 0.1
- Target component: Mean reversion nếu có target_price

### 2.2. Matching Engine

**Price-Time Priority:**
1. Ưu tiên giá tốt nhất (best price)
2. Trong cùng giá, ưu tiên lệnh đến trước (FIFO)
3. Hỗ trợ partial fills

**Current Implementation:**
- Simulated orderbook matching
- Có thể tích hợp với real orders từ database

### 2.3. Formula Sandbox

**Security:**
- AST whitelist validation
- Blacklist dangerous functions
- Timeout ≤100ms
- Memory limit 5MB

**Allowed:**
- Math operations: `+`, `-`, `*`, `/`, `%`, `**`
- Math functions: `math.sin`, `math.cos`, `math.exp`, `math.log`, `math.sqrt`, etc.
- Built-in: `abs`, `min`, `max`, `round`
- Random: `random.random()`
- Variables: `price`, `dt`, `trend`, `target`, `drift`, `volatility`

**Not Allowed:**
- `eval`, `exec`, `compile`, `__import__`
- `open`, `file`, `input`
- `require`, `fs`, `child_process`
- Any imports

## 3. TimescaleDB Integration

### 3.1. Hypertables

- `market_data_history`: OHLCV candles (partitioned by timestamp)
- `price_tick`: Tick data (partitioned by timestamp)

### 3.2. Continuous Aggregates

- `ohlcv_1m`, `ohlcv_5m`, `ohlcv_15m`, `ohlcv_1h`, `ohlcv_4h`, `ohlcv_1d`
- Tự động aggregate từ `price_tick`
- Refresh policies tự động

### 3.3. Replay Mechanism

- Query tick data từ TimescaleDB
- Replay theo time range hoặc session
- Endpoint: `POST /api/sim/replay`

## 4. APIs

### 4.1. Simulator Endpoints

- `GET /api/sim/snapshot`: Lấy snapshot tổng hợp
- `GET /api/sim/orderbook?symbol=BTCUSDT`: Lấy orderbook
- `GET /api/sim/trades?symbol=BTCUSDT`: Lấy trades
- `GET /api/sim/candles?symbol=BTCUSDT`: Lấy candles
- `GET /api/sim/positions?symbol=BTCUSDT`: Lấy positions
- `GET /api/sim/scenarios`: Lấy scenarios
- `POST /api/sim/scenarios`: Cập nhật scenarios
- `POST /api/sim/replay`: Replay tick data

### 4.2. Admin Endpoints

- `GET /api/admin/settings/market-scenarios`: Lấy scenarios
- `PUT /api/admin/settings/market-scenarios`: Lưu scenarios
- `GET /api/admin/simulator/sessions`: Lấy sessions
- `POST /api/admin/simulator/sessions/start`: Bắt đầu session
- `POST /api/admin/simulator/sessions/stop`: Dừng session
- `POST /api/admin/simulator/sessions/replay`: Replay session
- `POST /api/admin/simulator/sessions/reset`: Reset simulator
- `GET /api/admin/simulator/monitoring`: Lấy metrics

## 5. WebSocket Events

### 5.1. Channels

- `prices`: Price updates
- `orderbook`: Orderbook updates
- `trades`: Trade updates
- `candles`: Candle updates
- `positions`: Position updates
- `logs`: Log events (Educational Hub)

### 5.2. Event Types

- `price_update`: Price changed
- `orderbook_update`: Orderbook changed
- `trade_update`: New trade
- `candle_update`: New candle
- `position_update`: Position changed
- `log_event`: Log event (Rule-Change, Event-Inject, Auto-Adjust)

## 6. Development Workflow

### 6.1. Local Development

```bash
# Start services
docker-compose up -d

# Run migrations
cd backend
alembic upgrade head

# Start backend
uvicorn app.main:app --reload

# Start admin app
cd Admin-app
npm run dev
```

### 6.2. Testing

```bash
# Run tests
cd backend
pytest tests/

# Test simulator
pytest tests/test_trading_data_simulator.py
```

### 6.3. Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 7. Performance Optimization

### 7.1. Latency Targets

- Price update: <20ms (internal network)
- WebSocket broadcast: <30ms
- Database write: <10ms (async)

### 7.2. Optimization Tips

- Batch database writes nếu cần
- Use connection pooling
- Cache scenarios trong memory
- Optimize formula evaluation

## 8. Security

### 8.1. Formula Sandbox

- AST validation
- Blacklist dangerous functions
- Timeout và memory limits
- No file system access

### 8.2. Audit Logging

- Log tất cả admin actions
- Store trong `audit_log` table
- Include: user, action, timestamp, IP

## 9. Monitoring & Debugging

### 9.1. Logs

- Backend logs: `backend/logs/`
- Check simulator metrics: `/api/admin/simulator/monitoring`

### 9.2. Debugging

- Enable DEBUG mode: `DEBUG=true`
- Check WebSocket connections
- Monitor database queries
- Use TimescaleDB EXPLAIN ANALYZE

## 10. Future Enhancements

### 10.1. Matching Engine

- Tích hợp với real orders từ database
- Support advanced order types (Iceberg, OCO, Trailing Stop)
- Order matching với real-time updates

### 10.2. Educational Hub

- Thêm indicators (RSI, MACD, etc.)
- Backtesting capabilities
- Strategy testing

### 10.3. Performance

- Load testing với 10k+ connections
- Optimize database queries
- Implement caching layer

---

**Phiên bản:** 1.0  
**Ngày cập nhật:** 2025-01-09

