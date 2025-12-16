# Admin User Guide - Market-Maker Engine & Admin Dashboard

## Tổng quan

Hướng dẫn sử dụng Admin Dashboard để quản lý Market-Maker Engine, Scenario Builder, Session Manager, và các tính năng quản trị nâng cao.

## 1. Scenario Builder

### 1.1. Tạo và chỉnh sửa kịch bản

1. Truy cập **Scenario Builder** trong Admin Dashboard
2. Thêm hoặc chỉnh sửa kịch bản cho từng symbol (BTCUSDT, ETHUSDT, etc.)
3. Cấu hình các tham số:
   - **Symbol**: Cặp giao dịch (BTCUSDT, ETHUSDT, etc.)
   - **Tên kịch bản**: Mô tả ngắn gọn
   - **Xu hướng**: UPTREND, DOWNTREND, SIDEWAY
   - **Drift**: Tốc độ drift (ví dụ: 0.0005)
   - **Volatility**: Độ biến động (ví dụ: 0.002)
   - **Spread (bps)**: Spread tính bằng basis points (ví dụ: 8)
   - **Depth**: Độ sâu orderbook (ví dụ: 10)
   - **Target Price**: Giá mục tiêu (nếu có)
   - **House Edge**: Edge của house (ví dụ: 0)
   - **Anti-TA**: Bật để làm nhiễu mô hình technical analysis

### 1.2. Formula Editor (Monaco Editor)

- Sử dụng Monaco Editor để viết công thức tùy chỉnh
- Hỗ trợ autocomplete cho các biến:
  - `price`: Giá hiện tại
  - `dt`: Delta time (seconds)
  - `trend`: Xu hướng (UPTREND, DOWNTREND, SIDEWAY)
  - `target`: Target price (nếu có)
  - `drift`: Drift rate
  - `volatility`: Volatility
  - `math.*`: Các hàm toán học (sin, cos, exp, log, sqrt, etc.)
  - `random.random()`: Random number generator

**Ví dụ công thức:**
```javascript
price * (1 + drift * dt) + (random.random() - 0.5) * volatility * price
```

### 1.3. Lưu và áp dụng

- Click **"Lưu Scenario"** để lưu vào database
- Kịch bản sẽ được áp dụng ngay lập tức cho simulator (không cần restart server)

## 2. Session Manager

### 2.1. Bắt đầu session

1. Nhập **Tên phiên** (ví dụ: "Phiên sáng 08:00")
2. Nhập **Ghi chú** (mục tiêu, chiến lược, etc.)
3. Click **"Bắt đầu session"**
4. Simulator sẽ reset và áp dụng kịch bản hiện tại

### 2.2. Dừng session

1. Tìm session đang chạy trong danh sách
2. Nhập **Ghi chú kết quả** (nếu cần)
3. Click **"Dừng"**
4. Session sẽ được lưu với trạng thái "stopped"

### 2.3. Replay session

1. Click **"Replay"** trên session đã dừng
2. Simulator sẽ tải lại snapshot kịch bản của session đó
3. Có thể replay tick data từ TimescaleDB nếu cần

### 2.4. Reset Simulator

- Click **"Reset / Replay"** để reset toàn bộ simulator
- Xóa lịch sử session và khởi tạo lại trạng thái

## 3. Monitoring Hub

### 3.1. Metrics

- **Symbols**: Danh sách symbols đang được simulate
- **Latency (ms)**: Độ trễ trung bình
- **Scenarios**: Số lượng kịch bản đang active
- **Last Updated**: Thời gian cập nhật cuối

### 3.2. Snapshot

- **Prices**: Giá hiện tại của các symbols
- **Trades**: Số lượng trades gần đây
- **Positions**: Số lượng positions đang mở

## 4. Market Display Configuration

### 4.1. Cấu hình hiển thị

- **Spread**: Điều chỉnh spread slider/input
- **Candle Color**: Chọn màu và style cho candles
- **Volume 24h**: Nhập volume 24h
- **Market Cap**: Nhập market cap

### 4.2. Preview trực tiếp

- Thay đổi cấu hình sẽ được preview ngay qua WebSocket
- Không cần refresh trang

## 5. Educational Hub

### 5.1. Real-time Chart

- Hiển thị chart real-time với TradingView Lightweight Charts
- Cập nhật theo thời gian thực qua WebSocket

### 5.2. Log Panel

- Hiển thị log events với timestamp
- Filter theo type:
  - **Rule-Change**: Thay đổi rule/kịch bản
  - **Event-Inject**: Event được inject
  - **Auto-Adjust**: Tự động điều chỉnh
- Hiển thị "why" cho mỗi thay đổi giá

## 6. Export & Reports

### 6.1. Export Session Results

- Export session results ra CSV/Excel
- Bao gồm: session info, scenarios, results, timestamps

### 6.2. Audit Logs

- Xem audit logs cho tất cả admin actions
- Filter theo user, action, timestamp

## 7. Best Practices

### 7.1. Scenario Design

- Bắt đầu với kịch bản đơn giản (SIDEWAY, volatility thấp)
- Tăng dần complexity khi đã quen
- Test với target price để verify accuracy

### 7.2. Session Management

- Đặt tên session rõ ràng, có timestamp
- Ghi chú mục tiêu và kết quả để dễ review sau
- Replay session để verify reproducibility

### 7.3. Monitoring

- Theo dõi latency thường xuyên
- Kiểm tra số lượng trades/positions
- Nếu giá không đổi, thử Reset hoặc Replay

## 8. Troubleshooting

### 8.1. Giá không thay đổi

- Kiểm tra scenario có đúng không
- Thử Reset simulator
- Replay session để verify

### 8.2. Formula không hoạt động

- Kiểm tra syntax (dùng Monaco Editor autocomplete)
- Đảm bảo chỉ dùng các biến/functions được phép
- Xem log để biết lỗi cụ thể

### 8.3. Latency cao

- Kiểm tra database connection
- Giảm số lượng symbols nếu cần
- Tối ưu formula nếu quá phức tạp

---

**Phiên bản:** 1.0  
**Ngày cập nhật:** 2025-01-09

