# BACKEND API REFERENCE - TÀI LIỆU HƯỚNG DẪN API

> **Tài liệu đầy đủ các API endpoints của hệ thống CMEETRADING Backend**
> 
> **Phiên bản:** 2.1.0  
> **Cập nhật:** 2025-12-21  
> **Tổng số endpoints:** 263 HTTP + 2 WebSocket

---

## 📋 MỤC LỤC

1. [Tổng quan](#tổng-quan)
2. [Authentication & Authorization](#1-authentication--authorization)
3. [Client Dashboard](#2-client-dashboard)
4. [Admin Management](#3-admin-management)
5. [Financial Operations](#4-financial-operations)
6. [Market Data](#5-market-data)
7. [Portfolio Management](#6-portfolio-management)
8. [Compliance & Risk](#7-compliance--risk)
9. [User Management](#8-user-management)
10. [Monitoring & Diagnostics](#9-monitoring--diagnostics)
11. [Education & Analysis](#10-education--analysis)
12. [Support & Legal](#11-support--legal)
13. [Simulation & Testing](#12-simulation--testing)
14. [WebSocket Endpoints](#13-websocket-endpoints)
15. [Authentication Guide](#authentication-guide)
16. [Error Handling](#error-handling)

---

## TỔNG QUAN

### Base URL
```
Development: http://localhost:8000
Production:  https://api.digitalutopia.com
```

### Authentication
Hầu hết các endpoints yêu cầu JWT token trong header:
```http
Authorization: Bearer <your_access_token>
```

### Content Type
```http
Content-Type: application/json
```

### Rate Limiting
- **60 requests/minute**
- **1000 requests/hour**

---

## 1. AUTHENTICATION & AUTHORIZATION

### Module: `auth.py`
**Base URL:** `/api/auth`

| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|-------|---------------|
| POST | `/api/auth/login` | Đăng nhập hệ thống | ❌ |
| POST | `/api/auth/register` | Đăng ký tài khoản mới | ❌ |
| POST | `/api/auth/refresh` | Làm mới access token | ✅ |
| POST | `/api/auth/logout` | Đăng xuất | ✅ |
| GET | `/api/auth/me` | Lấy thông tin user hiện tại | ✅ |
| POST | `/api/auth/verify-email` | Xác thực email | ❌ |
| POST | `/api/auth/forgot-password` | Quên mật khẩu | ❌ |
| POST | `/api/auth/reset-password` | Đặt lại mật khẩu | ❌ |

#### Example: Login Request
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password"
  }'
```

#### Example: Login Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Nguyễn Văn A",
    "role": "user"
  }
}
```

---

## 2. CLIENT DASHBOARD

### Module: `client.py`
**Base URL:** `/api/client`

| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|-------|---------------|
| GET | `/api/client/dashboard` | Lấy dữ liệu dashboard | ✅ |
| GET | `/api/client/wallet` | Lấy thông tin ví | ✅ |
| GET | `/api/client/orders` | Lấy danh sách lệnh | ✅ |
| GET | `/api/client/positions` | Lấy danh sách vị thế | ✅ |
| POST | `/api/client/orders` | Tạo lệnh mới | ✅ |
| POST | `/api/client/orders/{order_id}/cancel` | Hủy lệnh | ✅ |
| GET | `/api/client/profile` | Lấy thông tin profile | ✅ |
| PUT | `/api/client/profile` | Cập nhật profile | ✅ |
| GET | `/api/client/settings` | Lấy cài đặt | ✅ |
| PUT | `/api/client/settings` | Cập nhật cài đặt | ✅ |
| GET | `/api/client/preferences` | Lấy preferences | ✅ |
| PUT | `/api/client/preferences` | Cập nhật preferences | ✅ |
| POST | `/api/client/2fa/setup` | Thiết lập 2FA | ✅ |
| POST | `/api/client/2fa/verify` | Xác thực 2FA | ✅ |
| POST | `/api/client/2fa/disable` | Tắt 2FA | ✅ |
| GET | `/api/client/onboarding/status` | Trạng thái onboarding | ✅ |
| POST | `/api/client/onboarding/complete` | Hoàn thành onboarding | ✅ |
| GET | `/api/client/settings/registration-fields` | Lấy trường đăng ký | ✅ |

#### Example: Get Dashboard
```bash
curl -X GET http://localhost:8000/api/client/dashboard \
  -H "Authorization: Bearer <token>"
```

---

## 3. ADMIN MANAGEMENT

### Module: `admin.py`
**Base URL:** `/api/admin`

#### 3.1 User Management
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/admin/users` | Danh sách users |
| GET | `/api/admin/users/{user_id}` | Chi tiết user |
| PUT | `/api/admin/users/{user_id}` | Cập nhật user |
| GET | `/api/admin/users/{user_id}/performance` | Hiệu suất user |
| POST | `/api/admin/users/bulk-update` | Cập nhật hàng loạt |

#### 3.2 Dashboard & Analytics
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/admin/dashboard` | Admin dashboard |
| GET | `/api/admin/platform-stats` | Thống kê nền tảng |
| GET | `/api/admin/platform/stats` | Thống kê nền tảng (v2) |
| GET | `/api/admin/analytics` | Phân tích |
| GET | `/api/admin/analytics/performance` | Phân tích hiệu suất |

#### 3.3 Deposits & Withdrawals
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/admin/deposits` | Danh sách nạp tiền |
| GET | `/api/admin/deposits/{deposit_id}` | Chi tiết nạp tiền |
| POST | `/api/admin/deposits/{deposit_id}/approve` | Duyệt nạp tiền |
| POST | `/api/admin/deposits/{deposit_id}/reject` | Từ chối nạp tiền |
| GET | `/api/admin/withdrawals` | Danh sách rút tiền |
| GET | `/api/admin/withdrawals/{withdrawal_id}` | Chi tiết rút tiền |
| POST | `/api/admin/withdrawals/{withdrawal_id}/approve` | Duyệt rút tiền |
| POST | `/api/admin/withdrawals/{withdrawal_id}/reject` | Từ chối rút tiền |

#### 3.4 Trade Management
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/admin/trades` | Danh sách giao dịch |
| POST | `/api/admin/trades/{trade_id}/approve` | Duyệt giao dịch |
| POST | `/api/admin/trades/{trade_id}/reject` | Từ chối giao dịch |
| POST | `/api/admin/trades/batch-approve` | Duyệt hàng loạt |

#### 3.5 Trading Adjustments
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/admin/trading-adjustments/win-rate` | Điều chỉnh tỷ lệ thắng |
| POST | `/api/admin/trading-adjustments/position-override` | Ghi đè vị thế |
| POST | `/api/admin/trading-adjustments/reset-win-rate` | Reset tỷ lệ thắng |
| GET | `/api/admin/trading-adjustments/history` | Lịch sử điều chỉnh |

#### 3.6 Invoice & Payment Management
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/admin/invoices` | Danh sách hóa đơn |
| GET | `/api/admin/invoices/{invoice_id}` | Chi tiết hóa đơn |
| POST | `/api/admin/invoices` | Tạo hóa đơn |
| PUT | `/api/admin/invoices/{invoice_id}` | Cập nhật hóa đơn |
| DELETE | `/api/admin/invoices/{invoice_id}` | Xóa hóa đơn |
| POST | `/api/admin/invoices/{invoice_id}/approve` | Duyệt hóa đơn |
| POST | `/api/admin/invoices/{invoice_id}/reject` | Từ chối hóa đơn |
| GET | `/api/admin/payments` | Danh sách thanh toán |
| GET | `/api/admin/payments/{payment_id}` | Chi tiết thanh toán |
| POST | `/api/admin/payments/{payment_id}/process` | Xử lý thanh toán |
| POST | `/api/admin/payments/{payment_id}/refund` | Hoàn tiền |

#### 3.7 Settings & Configuration
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/admin/settings` | Lấy cài đặt |
| PUT | `/api/admin/settings` | Cập nhật cài đặt |
| GET | `/api/admin/settings/market-display` | Cài đặt hiển thị market |
| PUT | `/api/admin/settings/market-display` | Cập nhật hiển thị market |
| GET | `/api/admin/settings/chart-display` | Cài đặt hiển thị chart |
| PATCH | `/api/admin/config/candle` | Cấu hình nến |
| GET | `/api/admin/settings/market-scenarios` | Kịch bản thị trường |
| PUT | `/api/admin/settings/market-scenarios` | Cập nhật kịch bản |
| GET | `/api/admin/settings/registration-fields` | Trường đăng ký |
| PUT | `/api/admin/settings/registration-fields` | Cập nhật trường đăng ký |
| GET | `/api/admin/settings/auto-approve-registration` | Tự động duyệt đăng ký |
| PUT | `/api/admin/settings/auto-approve-registration` | Cập nhật tự động duyệt |
| GET | `/api/admin/settings/cors-origins` | CORS origins |
| POST | `/api/admin/settings/cors-origins` | Thêm CORS origin |
| DELETE | `/api/admin/settings/cors-origins` | Xóa CORS origin |

#### 3.8 Simulation Control
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/admin/simulator/sessions` | Danh sách session |
| POST | `/api/admin/simulator/sessions/start` | Khởi động simulator |
| POST | `/api/admin/simulator/sessions/stop` | Dừng simulator |
| POST | `/api/admin/simulator/sessions/reset` | Reset simulator |
| POST | `/api/admin/simulator/sessions/replay` | Replay simulator |
| GET | `/api/admin/simulator/monitoring` | Giám sát simulator |

#### 3.9 Reports & Logs
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/admin/reports` | Danh sách báo cáo |
| GET | `/api/admin/reports/scheduled` | Báo cáo đã lên lịch |
| PATCH | `/api/admin/reports/scheduled/{report_id}` | Cập nhật báo cáo |
| DELETE | `/api/admin/reports/scheduled/{report_id}` | Xóa báo cáo |
| GET | `/api/admin/logs` | Danh sách logs |

#### 3.10 Registration Management
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/admin/registrations` | Danh sách đăng ký |
| POST | `/api/admin/registrations/{registration_id}/approve` | Duyệt đăng ký |

#### 3.11 Market Preview
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/admin/market-preview` | Xem trước thị trường |
| GET | `/api/admin/market-preview/{symbol}` | Xem trước symbol |

### Module: `admin_trading.py`
**Base URL:** `/api/admin`

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/admin/trading/status` | Trạng thái trading |

### Module: `admin_scenarios.py`
**Base URL:** `/api/admin`

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/admin/scenarios` | Tạo kịch bản |
| GET | `/api/admin/scenarios` | Danh sách kịch bản |
| GET | `/api/admin/scenarios/{scenario_id}` | Chi tiết kịch bản |
| PUT | `/api/admin/scenarios/{scenario_id}` | Cập nhật kịch bản |
| DELETE | `/api/admin/scenarios/{scenario_id}` | Xóa kịch bản |
| POST | `/api/admin/scenarios/{scenario_id}/activate` | Kích hoạt kịch bản |
| POST | `/api/admin/scenarios/deactivate` | Tắt kịch bản |
| GET | `/api/admin/scenarios/active/current` | Kịch bản đang hoạt động |

### Module: `admin_simulation.py`
**Base URL:** `/api/admin`

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/admin/simulation/status` | Trạng thái simulation |
| POST | `/api/admin/simulation/start` | Khởi động simulation |
| POST | `/api/admin/simulation/stop` | Dừng simulation |
| POST | `/api/admin/simulation/restart` | Khởi động lại simulation |
| PUT | `/api/admin/simulation/config` | Cấu hình simulation |
| POST | `/api/admin/simulation/reset-prices` | Reset giá |
| GET | `/api/admin/simulation/metrics` | Metrics simulation |

### Module: `admin_customizations.py`
**Base URL:** `/api/admin`

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/admin/customizations/rules` | Danh sách rules |
| GET | `/api/admin/customizations/rules/{name}` | Chi tiết rule |
| POST | `/api/admin/customizations/rules` | Tạo rule |
| PUT | `/api/admin/customizations/rules/{name}` | Cập nhật rule |
| DELETE | `/api/admin/customizations/rules/{name}` | Xóa rule |
| GET | `/api/admin/customizations/sessions` | Danh sách sessions |
| POST | `/api/admin/customizations/sessions` | Tạo session |
| DELETE | `/api/admin/customizations/sessions/{session_id}` | Xóa session |
| POST | `/api/admin/customizations/sessions/{session_id}/bind` | Bind user |
| POST | `/api/admin/customizations/sessions/{session_id}/unbind` | Unbind user |
| POST | `/api/admin/customizations/sessions/{session_id}/activate` | Kích hoạt session |
| POST | `/api/admin/customizations/sessions/{session_id}/deactivate` | Tắt session |
| POST | `/api/admin/customizations/manual-override` | Override thủ công |
| DELETE | `/api/admin/customizations/manual-override/{symbol}` | Xóa override |
| DELETE | `/api/admin/customizations/manual-override` | Xóa tất cả override |
| GET | `/api/admin/customizations/status` | Trạng thái customizations |

---

## 4. FINANCIAL OPERATIONS

### Module: `financial.py`
**Base URL:** `/api/financial`

| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|-------|---------------|
| POST | `/api/financial/deposit` | Nạp tiền | ✅ |
| GET | `/api/financial/deposits` | Lịch sử nạp tiền | ✅ |
| POST | `/api/financial/withdraw` | Rút tiền | ✅ |
| GET | `/api/financial/withdrawals` | Lịch sử rút tiền | ✅ |
| GET | `/api/financial/balance` | Số dư tài khoản | ✅ |
| GET | `/api/financial/transactions` | Lịch sử giao dịch | ✅ |
| POST | `/api/financial/exchange` | Đổi tiền tệ | ✅ |
| POST | `/api/financial/payments/process` | Xử lý thanh toán | ✅ |
| GET | `/api/financial/reports` | Báo cáo tài chính | ✅ |

#### Example: Deposit Request
```bash
curl -X POST http://localhost:8000/api/financial/deposit \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000,
    "currency": "USD",
    "method": "bank_transfer"
  }'
```

---

## 5. MARKET DATA

### Module: `market.py`
**Base URL:** `/api/market`

| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|-------|---------------|
| GET | `/api/market/prices` | Giá thời gian thực | ❌ |
| GET | `/api/market/trade-history/{symbol}` | Lịch sử giao dịch | ❌ |
| GET | `/api/market/historical-data/{symbol}` | Dữ liệu lịch sử | ❌ |
| GET | `/api/market/analysis/{symbol}` | Phân tích thị trường | ❌ |
| GET | `/api/market/data-feeds` | Nguồn dữ liệu | ❌ |
| GET | `/api/market/instruments` | Danh sách instruments | ❌ |
| GET | `/api/market/summary` | Tổng quan thị trường | ❌ |

### Module: `market_mock.py`
**Base URL:** `/api/market-mock`

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/market-mock/health` | Health check |
| GET | `/api/market-mock/ticker/{symbol}` | Ticker data |
| GET | `/api/market-mock/candles/{symbol}` | Dữ liệu nến |
| GET | `/api/market-mock/orderbook/{symbol}` | Sổ lệnh |
| GET | `/api/market-mock/trades/{symbol}` | Giao dịch |
| GET | `/api/market-mock/symbols` | Danh sách symbols |

### Module: `trading.py`
**Base URL:** `/api/trading`

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/trading/` | Trading info |
| GET | `/api/trading/health` | Health check |
| GET | `/api/trading/signals` | Tín hiệu trading |
| GET | `/api/trading/signals/{symbol}` | Tín hiệu symbol |
| GET | `/api/trading/signals/asset/{asset_class}` | Tín hiệu theo asset |
| GET | `/api/trading/binary` | Binary signals |
| GET | `/api/trading/binary/{symbol}` | Binary signal symbol |
| GET | `/api/trading/binary/stream` | Binary stream |
| GET | `/api/trading/analysis` | Phân tích market |
| GET | `/api/trading/analysis/trends` | Xu hướng |
| GET | `/api/trading/recommendations` | Khuyến nghị |
| GET | `/api/trading/performance` | Hiệu suất |

#### Example: Get Real-time Prices
```bash
curl -X GET http://localhost:8000/api/market/prices
```

#### Example Response
```json
{
  "data": [
    {
      "symbol": "BTC/USD",
      "price": 42500.50,
      "change_24h": 2.5,
      "volume_24h": 1500000000,
      "timestamp": "2025-12-21T02:00:00Z"
    }
  ]
}
```

---

## 6. PORTFOLIO MANAGEMENT

### Module: `portfolio.py`
**Base URL:** `/api/portfolio`

| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|-------|---------------|
| GET | `/api/portfolio/analytics` | Phân tích portfolio | ✅ |
| POST | `/api/portfolio/analytics/report` | Báo cáo phân tích | ✅ |
| GET | `/api/portfolio/metrics` | Metrics portfolio | ✅ |
| POST | `/api/portfolio/metrics/recalculate` | Tính lại metrics | ✅ |
| POST | `/api/portfolio/positions/{position_id}/close` | Đóng vị thế | ✅ |
| POST | `/api/portfolio/rebalancing` | Cân bằng lại | ✅ |
| GET | `/api/portfolio/rebalancing/recommendations` | Khuyến nghị cân bằng | ✅ |
| GET | `/api/portfolio/trading-bots` | Danh sách bots | ✅ |
| POST | `/api/portfolio/trading-bots` | Tạo bot | ✅ |
| PATCH | `/api/portfolio/trading-bots` | Cập nhật bot | ✅ |
| DELETE | `/api/portfolio/trading-bots` | Xóa bot | ✅ |
| GET | `/api/portfolio/watchlist` | Danh sách theo dõi | ✅ |
| POST | `/api/portfolio/watchlist` | Thêm vào watchlist | ✅ |
| DELETE | `/api/portfolio/watchlist/{symbol}` | Xóa khỏi watchlist | ✅ |

---

## 7. COMPLIANCE & RISK

### Module: `compliance.py`
**Base URL:** `/api/compliance`

#### 7.1 KYC Management
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/compliance/kyc` | Lấy thông tin KYC |
| POST | `/api/compliance/kyc` | Tạo KYC request |
| PATCH | `/api/compliance/kyc` | Cập nhật KYC |
| DELETE | `/api/compliance/kyc` | Xóa KYC |

#### 7.2 AML Monitoring
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/compliance/aml` | Thông tin AML |
| POST | `/api/compliance/aml` | Tạo AML check |
| PATCH | `/api/compliance/aml` | Cập nhật AML |
| GET | `/api/compliance/aml/metrics` | Metrics AML |
| POST | `/api/compliance/aml/monitor` | Giám sát AML |

#### 7.3 Audit & Security
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/compliance/audit` | Audit logs |
| POST | `/api/compliance/audit` | Tạo audit log |
| GET | `/api/compliance/audit/security` | Security events |
| POST | `/api/compliance/audit/security` | Tạo security event |
| PATCH | `/api/compliance/audit/security/{event_id}` | Cập nhật event |

#### 7.4 Dashboard & Reports
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/compliance/dashboard` | Dashboard |
| GET | `/api/compliance/dashboard/metrics` | Dashboard metrics |
| POST | `/api/compliance/dashboard/alerts` | Tạo alert |
| PATCH | `/api/compliance/dashboard/alerts/{alert_id}` | Cập nhật alert |
| GET | `/api/compliance/reports` | Danh sách báo cáo |
| POST | `/api/compliance/reports` | Tạo báo cáo |
| PATCH | `/api/compliance/reports/{report_id}` | Cập nhật báo cáo |
| POST | `/api/compliance/reports/auto-generate` | Tự động tạo báo cáo |
| GET | `/api/compliance/reports/metrics` | Metrics báo cáo |

#### 7.5 Rules Engine
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/compliance/rules` | Danh sách rules |
| POST | `/api/compliance/rules` | Tạo rule |
| PATCH | `/api/compliance/rules/{rule_id}` | Cập nhật rule |
| DELETE | `/api/compliance/rules/{rule_id}` | Xóa rule |
| POST | `/api/compliance/rules/{rule_id}/evaluate` | Đánh giá rule |
| GET | `/api/compliance/rules/{rule_id}/executions` | Lịch sử thực thi |

#### 7.6 Sanctions Screening
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/compliance/sanctions` | Danh sách sanctions |
| POST | `/api/compliance/sanctions/screen` | Screening |
| GET | `/api/compliance/sanctions/screenings` | Lịch sử screening |
| PATCH | `/api/compliance/sanctions/screenings/{screening_id}` | Cập nhật screening |

#### 7.7 Transaction Monitoring
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/compliance/transaction-monitoring` | Giám sát giao dịch |
| POST | `/api/compliance/transaction-monitoring` | Tạo monitoring |
| PATCH | `/api/compliance/transaction-monitoring` | Cập nhật monitoring |
| GET | `/api/compliance/transaction-monitoring/suspicious-activities` | Hoạt động đáng ngờ |

### Module: `risk_management.py`
**Base URL:** `/api/risk-management`

| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|-------|---------------|
| GET | `/api/risk-management/assessment` | Đánh giá rủi ro | ✅ |
| POST | `/api/risk-management/assessment/stress-test` | Stress test | ✅ |
| DELETE | `/api/risk-management/assessment/cache` | Xóa cache | ✅ |
| GET | `/api/risk-management/limits` | Giới hạn rủi ro | ✅ |
| POST | `/api/risk-management/limits` | Tạo giới hạn | ✅ |
| PATCH | `/api/risk-management/limits` | Cập nhật giới hạn | ✅ |
| DELETE | `/api/risk-management/limits` | Xóa giới hạn | ✅ |
| GET | `/api/risk-management/alerts` | Cảnh báo rủi ro | ✅ |
| GET | `/api/risk-management/margin-calls` | Margin calls | ✅ |
| GET | `/api/risk-management/metrics` | Metrics rủi ro | ✅ |

---

## 8. USER MANAGEMENT

### Module: `users.py`
**Base URL:** `/api`

| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|-------|---------------|
| GET | `/api/users` | Danh sách users | ✅ Admin |
| GET | `/api/users/{user_id}` | Chi tiết user | ✅ Admin |
| PUT | `/api/users/{user_id}` | Cập nhật user | ✅ Admin |
| DELETE | `/api/users/{user_id}` | Xóa user | ✅ Admin |

### Module: `staff_referrals.py`
**Base URL:** `/api/staff`

| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|-------|---------------|
| GET | `/api/staff/referrals` | Danh sách referrals | ✅ |
| POST | `/api/staff/referrals` | Tạo referral | ✅ |
| GET | `/api/staff/referrals/{referral_id}` | Chi tiết referral | ✅ |
| DELETE | `/api/staff/referrals/{referral_id}` | Xóa referral | ✅ |

---

## 9. MONITORING & DIAGNOSTICS

### Module: `diagnostics.py`
**Base URL:** `/api/diagnostics`

| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|-------|---------------|
| POST | `/api/diagnostics/trading-report` | Tạo báo cáo trading | ✅ |
| GET | `/api/diagnostics/trading-reports` | Danh sách báo cáo | ✅ |
| GET | `/api/diagnostics/trading-reports/{report_id}` | Chi tiết báo cáo | ✅ |

### Module: `alert_rules.py`
**Base URL:** `/api`

| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|-------|---------------|
| GET | `/api/alert-rules` | Danh sách alert rules | ✅ |
| POST | `/api/alert-rules` | Tạo alert rule | ✅ |
| GET | `/api/alert-rules/{rule_id}` | Chi tiết rule | ✅ |
| PUT | `/api/alert-rules/{rule_id}` | Cập nhật rule | ✅ |
| DELETE | `/api/alert-rules/{rule_id}` | Xóa rule | ✅ |
| GET | `/api/alert-history` | Lịch sử alerts | ✅ |
| POST | `/api/alert-history/{alert_id}/acknowledge` | Xác nhận alert | ✅ |
| POST | `/api/alert-history/{alert_id}/resolve` | Giải quyết alert | ✅ |

### Module: `notifications.py`
**Base URL:** `/api`

| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|-------|---------------|
| POST | `/api/notifications` | Tạo notification | ✅ |
| GET | `/api/notifications` | Danh sách notifications | ✅ |
| GET | `/api/notifications/unread-count` | Số lượng chưa đọc | ✅ |
| POST | `/api/notifications/{notification_id}/read` | Đánh dấu đã đọc | ✅ |
| POST | `/api/notifications/mark-all-read` | Đánh dấu tất cả | ✅ |
| POST | `/api/notifications/{notification_id}/dismiss` | Dismiss notification | ✅ |
| GET | `/api/notification-preferences` | Preferences | ✅ |
| PUT | `/api/notification-preferences/{category}` | Cập nhật preferences | ✅ |

### Module: `audit.py`
**Base URL:** `/api`

| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|-------|---------------|
| GET | `/api/logs` | Danh sách logs | ✅ Admin |
| GET | `/api/logs/stats` | Thống kê logs | ✅ Admin |
| GET | `/api/logs/{log_id}` | Chi tiết log | ✅ Admin |

### Module: `performance.py`
**Base URL:** `/api`

| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|-------|---------------|
| GET | `/api/metrics` | Metrics hệ thống | ✅ Admin |
| POST | `/api/metrics/reset` | Reset metrics | ✅ Admin |

---

## 10. EDUCATION & ANALYSIS

### Module: `education.py`
**Base URL:** `/api/education`

| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|-------|---------------|
| GET | `/api/education/videos` | Danh sách video | ✅ |
| GET | `/api/education/videos/{video_id}` | Chi tiết video | ✅ |
| GET | `/api/education/ebooks` | Danh sách ebooks | ✅ |
| GET | `/api/education/ebooks/{ebook_id}` | Chi tiết ebook | ✅ |
| GET | `/api/education/calendar` | Lịch sự kiện | ✅ |
| GET | `/api/education/reports` | Báo cáo nghiên cứu | ✅ |
| GET | `/api/education/reports/{report_id}` | Chi tiết báo cáo | ✅ |
| POST | `/api/education/progress` | Cập nhật tiến độ | ✅ |

### Module: `analysis.py`
**Base URL:** `/api/analysis`

| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|-------|---------------|
| GET | `/api/analysis/technical/{symbol}` | Phân tích kỹ thuật | ✅ |
| GET | `/api/analysis/fundamental/{symbol}` | Phân tích cơ bản | ✅ |
| GET | `/api/analysis/sentiment` | Phân tích tâm lý | ✅ |
| GET | `/api/analysis/signals` | Tín hiệu giao dịch | ✅ |
| POST | `/api/analysis/backtest` | Backtest chiến lược | ✅ |

---

## 11. SUPPORT & LEGAL

### Module: `support.py`
**Base URL:** `/api/support`

| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|-------|---------------|
| GET | `/api/support/articles` | Danh sách bài viết | ❌ |
| GET | `/api/support/articles/{article_id}` | Chi tiết bài viết | ❌ |
| GET | `/api/support/categories` | Danh mục hỗ trợ | ❌ |
| POST | `/api/support/search` | Tìm kiếm bài viết | ❌ |
| POST | `/api/support/contact` | Liên hệ support | ✅ |
| GET | `/api/support/offices` | Danh sách văn phòng | ❌ |
| GET | `/api/support/channels` | Kênh hỗ trợ | ❌ |
| GET | `/api/support/faq` | Câu hỏi thường gặp | ❌ |
| GET | `/api/support/faq/{category}` | FAQ theo danh mục | ❌ |
| POST | `/api/support/faq/search` | Tìm kiếm FAQ | ❌ |

### Module: `chat.py`
**Base URL:** `/api`

| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|-------|---------------|
| POST | `/api/conversations` | Tạo cuộc hội thoại | ✅ |
| GET | `/api/conversations` | Danh sách hội thoại | ✅ |
| GET | `/api/conversations/{conversation_id}` | Chi tiết hội thoại | ✅ |
| GET | `/api/admin/conversations` | Admin: Tất cả hội thoại | ✅ Admin |

### Module: `legal.py`
**Base URL:** `/api/legal`

| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|-------|---------------|
| GET | `/api/legal/terms` | Điều khoản dịch vụ | ❌ |
| GET | `/api/legal/terms/version/{version}` | Điều khoản phiên bản | ❌ |
| GET | `/api/legal/privacy` | Chính sách bảo mật | ❌ |
| GET | `/api/legal/privacy/version/{version}` | Bảo mật phiên bản | ❌ |
| GET | `/api/legal/risk-warning` | Cảnh báo rủi ro | ❌ |
| GET | `/api/legal/complaints` | Danh sách khiếu nại | ✅ |
| POST | `/api/legal/complaints` | Tạo khiếu nại | ✅ |
| GET | `/api/legal/complaints/{complaint_id}` | Chi tiết khiếu nại | ✅ |
| PUT | `/api/legal/complaints/{complaint_id}` | Cập nhật khiếu nại | ✅ |

---

## 12. SIMULATION & TESTING

### Module: `simulator.py`
**Base URL:** `/api/sim`

| Method | Endpoint | Mô tả | Auth Required |
|--------|----------|-------|---------------|
| GET | `/api/sim/trades` | Giao dịch mô phỏng | ✅ |
| GET | `/api/sim/orderbook` | Sổ lệnh mô phỏng | ✅ |
| GET | `/api/sim/candles` | Nến mô phỏng | ✅ |
| GET | `/api/sim/snapshot` | Snapshot hệ thống | ✅ |

---

## 13. WEBSOCKET ENDPOINTS

### Real-time Trading Updates
**Endpoint:** `ws://localhost:8000/ws`

#### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws?token=<your_jwt_token>');

ws.onopen = () => {
  console.log('Connected to trading WebSocket');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

#### Message Types
- **order_update**: Cập nhật lệnh
- **position_update**: Cập nhật vị thế
- **price_update**: Cập nhật giá

#### Example Messages

**Order Update:**
```json
{
  "type": "order_update",
  "data": {
    "order_id": "ORD-12345",
    "symbol": "BTC/USD",
    "side": "buy",
    "quantity": 0.5,
    "price": 42500,
    "status": "filled"
  }
}
```

**Price Update:**
```json
{
  "type": "price_update",
  "data": {
    "symbol": "BTC/USD",
    "price": 42550.25,
    "change": 0.12,
    "timestamp": "2025-12-21T02:00:00Z"
  }
}
```

### Real-time Chat
**Endpoint:** `ws://localhost:8000/ws/chat`

#### Connection
```javascript
const chatWs = new WebSocket('ws://localhost:8000/ws/chat?token=<your_jwt_token>');

chatWs.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('New message:', message);
};
```

#### Send Message
```javascript
chatWs.send(JSON.stringify({
  conversation_id: "conv-123",
  content: "Hello, I need help",
  type: "text"
}));
```

---

## AUTHENTICATION GUIDE

### 1. Register Account
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "full_name": "Nguyễn Văn A",
    "phone": "+84912345678"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 3. Use Token
```bash
curl -X GET http://localhost:8000/api/client/dashboard \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 4. Refresh Token
```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

---

## ERROR HANDLING

### Error Response Format
```json
{
  "error": true,
  "message": "Mô tả lỗi bằng tiếng Việt",
  "detail": "Chi tiết lỗi",
  "status_code": 400,
  "timestamp": "2025-12-21T02:00:00.000Z"
}
```

### Common HTTP Status Codes

| Code | Ý nghĩa | Mô tả |
|------|---------|-------|
| 200 | OK | Thành công |
| 201 | Created | Tạo mới thành công |
| 400 | Bad Request | Yêu cầu không hợp lệ |
| 401 | Unauthorized | Chưa đăng nhập |
| 403 | Forbidden | Không có quyền truy cập |
| 404 | Not Found | Không tìm thấy |
| 422 | Unprocessable Entity | Dữ liệu không hợp lệ |
| 429 | Too Many Requests | Quá nhiều requests |
| 500 | Internal Server Error | Lỗi máy chủ |

### Example Error Responses

**401 Unauthorized:**
```json
{
  "error": true,
  "message": "Token không hợp lệ hoặc đã hết hạn",
  "status_code": 401,
  "timestamp": "2025-12-21T02:00:00.000Z"
}
```

**403 Forbidden:**
```json
{
  "error": true,
  "message": "Bạn không có quyền truy cập tài nguyên này",
  "status_code": 403,
  "timestamp": "2025-12-21T02:00:00.000Z"
}
```

**422 Validation Error:**
```json
{
  "error": true,
  "message": "Dữ liệu không hợp lệ",
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Email không đúng định dạng",
      "type": "value_error.email"
    }
  ],
  "status_code": 422,
  "timestamp": "2025-12-21T02:00:00.000Z"
}
```

---

## ADVANCED FEATURES

### 1. Pagination
Nhiều endpoints hỗ trợ pagination:

```bash
GET /api/admin/users?page=1&limit=50
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 1000,
    "total_pages": 20
  }
}
```

### 2. Filtering & Sorting
```bash
GET /api/admin/deposits?status=pending&sort_by=created_at&order=desc
```

### 3. Search
```bash
GET /api/admin/users?search=nguyen&fields=full_name,email
```

### 4. Date Range
```bash
GET /api/financial/transactions?start_date=2025-01-01&end_date=2025-12-31
```

### 5. Custom Headers

**Session Customization:**
```http
X-Session-Id: custom-session-123
```

**Language:**
```http
Accept-Language: vi-VN
```

---

## RATE LIMITING

### Limits
- **Standard Users:** 60 requests/minute, 1000 requests/hour
- **Premium Users:** 120 requests/minute, 5000 requests/hour
- **Admin Users:** Unlimited

### Rate Limit Headers
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640995200
```

### Exceeded Response
```json
{
  "error": true,
  "message": "Bạn đã vượt quá giới hạn số lượng requests",
  "status_code": 429,
  "retry_after": 60
}
```

---

## MONITORING ENDPOINTS

### Health Check
```bash
GET /api/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "backend",
  "version": "2.1.0",
  "uptime": "123456.789s",
  "memory": {
    "rss": "45.2%",
    "available": "2048.5 MB"
  },
  "database": "connected",
  "redis": "connected",
  "timestamp": "2025-12-21T02:00:00.000Z"
}
```

### Prometheus Metrics
```bash
GET /metrics
```

### API Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## DEPLOYMENT INFORMATION

### Development
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker
```bash
docker-compose up backend
```

### Environment Variables
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/cmeetrading
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

---

## SUPPORT & CONTACT

- **Email:** support@digitalutopia.com
- **Documentation:** http://localhost:8000/docs
- **Repository:** Internal GitLab
- **Issue Tracker:** Internal Jira

---

## CHANGELOG

### Version 2.1.0 (2025-12-21)
- ✅ Hoàn thiện 263 API endpoints
- ✅ Tích hợp WebSocket real-time
- ✅ Admin customization engine
- ✅ Market scenarios management
- ✅ Simulation control system
- ✅ Enhanced compliance monitoring
- ✅ Customer support chat system

### Version 2.0.0 (2025-12-05)
- 🚀 Migration từ Next.js sang FastAPI
- ✅ JWT Authentication
- ✅ Redis caching
- ✅ PostgreSQL database
- ✅ Prometheus monitoring

---

**© 2025 CMEETRADING - All Rights Reserved**
