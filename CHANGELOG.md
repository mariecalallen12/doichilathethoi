# Changelog

Tất cả các thay đổi đáng chú ý trong dự án ForEx Trading Platform được ghi lại trong file này.

## [2.1.0] - 2025-12-20

### ✅ Production Status
- **Backend API**: 30+ endpoints running on port 8000
- **Frontend Apps**: Built and ready (Client-app 3002, Admin-app 3001)
- **Database**: TimescaleDB + PostgreSQL running
- **Cache Layer**: Redis active

### Current System State

#### Infrastructure Services
- **PostgreSQL Databases**: ✅ Running
- **Redis Instances**: ✅ Running  
- **Mailpit**: Email testing (✅)

### Outstanding Items
- [ ] Create unified docker-compose for full stack
- [ ] Setup Nginx reverse proxy
- [ ] Configure SSL/TLS
- [ ] Integration testing
- [ ] Automated backups
- [ ] Monitoring dashboards
- [ ] Documentation cleanup

## [2.0.0] - 2025-01-09

### Added

#### Market-Maker Engine
- **Brownian Motion + Jump-Diffusion Model**: Nâng cấp thuật toán sinh dữ liệu với mô hình realistic hơn
  - Drift component: `price * drift * dt`
  - Brownian component: `price * volatility * sqrt(dt) * N(0,1)` với Box-Muller transform
  - Jump-Diffusion component: Poisson process với lambda = 0.1
  - Mean reversion cho target price

- **Matching Engine với Price-Time Priority**: 
  - Ưu tiên giá tốt nhất (best price)
  - Trong cùng giá, ưu tiên lệnh đến trước (FIFO)
  - Hỗ trợ partial fills
  - Cải thiện logic matching trong `_match_orderbook()`

#### TimescaleDB Integration
- **TimescaleDB Extension**: Upgrade từ PostgreSQL thường lên TimescaleDB
  - Cập nhật `docker-compose.yml` để dùng `timescale/timescaledb:latest-pg15`
  - Migration `20250109_001_add_timescaledb_support.py`:
    - Enable TimescaleDB extension
    - Convert `market_data_history` thành hypertable
    - Tạo bảng `price_tick` cho tick data storage
    - Tạo continuous aggregates cho OHLCV (1m, 5m, 15m, 1h, 4h, 1d)

- **Tick Data Storage**: 
  - Model `PriceTick` trong `app/models/market.py`
  - Tự động lưu tick data khi persist candle
  - Indexes tối ưu cho query performance

- **Replay Mechanism**:
  - Endpoint `POST /api/sim/replay` để replay tick data
  - Hỗ trợ replay theo time range hoặc session
  - Query từ TimescaleDB với performance tốt

#### Admin Dashboard Enhancements
- **Monaco Editor Integration**:
  - Cài đặt `monaco-editor` package
  - Component `MonacoEditor.vue` với:
    - Syntax highlighting cho JavaScript
    - Autocomplete cho các biến: price, dt, trend, target, drift, volatility
    - Dark theme (vs-dark)
    - Validation và error highlighting
  - Tích hợp vào Scenario Builder thay thế textarea

- **Formula Sandbox Security**:
  - Enhanced `_safe_eval_formula()` với:
    - Timeout ≤100ms
    - Memory limit 5MB
    - Blacklist dangerous functions (eval, exec, import, etc.)
    - AST whitelist validation nâng cao
    - Better error handling

#### Documentation
- **Technical Review** (`docs/RESEARCH.md`):
  - Đánh giá cấu trúc Order Book (Tree vs HashMap)
  - Đánh giá thuật toán Matching
  - Quyết định công nghệ (Python/FastAPI)
  - Tài liệu tham khảo

- **Admin User Guide** (`docs/ADMIN_USER_GUIDE.md`):
  - Hướng dẫn sử dụng Scenario Builder
  - Hướng dẫn Session Manager
  - Hướng dẫn Monitoring Hub
  - Best practices và troubleshooting

- **Developer Guide** (`docs/DEV_GUIDE.md`):
  - Architecture overview
  - API documentation
  - Development workflow
  - Performance optimization tips

### Changed

- **Trading Data Simulator**:
  - Cải thiện `_update_symbol()` với Brownian Motion + Jump-Diffusion
  - Cải thiện `_match_orderbook()` với price-time priority
  - Cải thiện `_persist_candle()` để lưu cả tick data
  - Fix missing `ast` import

- **Docker Compose**:
  - Update postgres service để dùng TimescaleDB image

### Fixed

- Fix missing `ast` import trong `trading_data_simulator.py`
- Fix formula evaluation với better error handling

### Security

- Enhanced Formula Sandbox:
  - Timeout protection (≤100ms)
  - Memory limit (5MB)
  - Blacklist dangerous functions
  - AST validation

## [1.0.0] - 2025-01-08

### Added
- Initial Market-Maker Engine implementation
- Scenario Builder UI
- Session Manager
- Basic Trading Data Simulator
- WebSocket real-time updates

---

**Format:** [Version] - YYYY-MM-DD  
**Categories:** Added, Changed, Deprecated, Removed, Fixed, Security


