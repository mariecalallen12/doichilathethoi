# Báo Cáo Sửa Lỗi API - Double /api/api/ Path

**Ngày:** 2025-12-16  
**Lỗi:** `/api/api/market/orderbook/BTCUSDT` - Double API path  
**Trạng thái:** ✅ Đã sửa

---

## 🔍 Phân Tích Vấn Đề

### Lỗi Gốc
Trên trang https://cmeetrading.com/trading, có lỗi:
```
Không tìm thấy tài nguyên: /api/api/market/orderbook/BTCUSDT
```

### Nguyên Nhân
1. **Base URL đã có `/api`**: Trong `client-app/src/services/api/client.js`, axios instance được tạo với:
   ```javascript
   const API_BASE_URL = getApiBaseUrl(); // Trả về "/api"
   const api = axios.create({
     baseURL: API_BASE_URL, // baseURL = "/api"
   });
   ```

2. **Path cũng có `/api`**: Trong các component, code gọi:
   ```javascript
   api.get(`/api/market/orderbook/${symbol}`) // Path đã có "/api"
   ```

3. **Kết quả**: Axios tạo URL = baseURL + path = `/api` + `/api/market/orderbook/...` = `/api/api/market/orderbook/...`

---

## ✅ Giải Pháp

### Đã Sửa Các File

#### 1. `client-app/src/components/opex-trading/OrderBook.vue`
**Trước:**
```javascript
const response = await api.get(`/api/market/orderbook/${props.symbol}`)
```

**Sau:**
```javascript
const response = await api.get(`/market/orderbook/${props.symbol}`)
```

#### 2. `client-app/src/components/opex-trading/MarketWatch.vue`
**Trước:**
```javascript
const response = await api.get('/api/market/symbols')
```

**Sau:**
```javascript
const response = await api.get('/market/symbols')
```

#### 3. `client-app/src/views/OpexTradingDashboard.vue`
**Sửa:** Format lại debug log code để tránh lỗi syntax khi build

---

## 📋 Các File Khác Đã Đúng

Các file sau đã sử dụng đúng format (không có `/api` prefix):
- ✅ `client-app/src/services/api/market.js` - Đã đúng
  ```javascript
  api.get(`/market/orderbook/${normalizedSymbol}`)
  api.get('/market/prices')
  api.get('/market/instruments')
  ```

---

## 🔄 Các Bước Triển Khai

### 1. Rebuild Client App
```bash
cd /root/forexxx
docker compose build client-app
```

### 2. Restart Container
```bash
docker compose restart client-app
```

### 3. Kiểm Tra
- Truy cập: https://cmeetrading.com/trading
- Kiểm tra console không còn lỗi `/api/api/`
- Orderbook hiển thị dữ liệu đúng

---

## 🧪 Kiểm Tra Sau Khi Sửa

### Test API Endpoint
```bash
# Kiểm tra endpoint đúng
curl https://cmeetrading.com/api/market/orderbook/BTCUSDT

# Không nên có lỗi 404
```

### Test Trong Browser
1. Mở https://cmeetrading.com/trading
2. Mở Developer Console (F12)
3. Kiểm tra Network tab:
   - Request đến `/api/market/orderbook/BTCUSDT` ✅
   - Không còn request đến `/api/api/market/orderbook/BTCUSDT` ✅

---

## 📝 Lưu Ý

### Quy Tắc Sử Dụng API Client

Khi sử dụng `api` từ `services/api/client.js`:
- ✅ **ĐÚNG**: `api.get('/market/orderbook/BTCUSDT')`
- ❌ **SAI**: `api.get('/api/market/orderbook/BTCUSDT')`

**Lý do:** BaseURL đã là `/api`, không cần thêm prefix `/api` vào path.

### Các Endpoint Đã Sửa

| Component | Endpoint Cũ (SAI) | Endpoint Mới (ĐÚNG) |
|-----------|-------------------|---------------------|
| OrderBook.vue | `/api/market/orderbook/{symbol}` | `/market/orderbook/{symbol}` |
| MarketWatch.vue | `/api/market/symbols` | `/market/symbols` |

---

## ✅ Kết Luận

- ✅ Đã xác định nguyên nhân: Double `/api/api/` path
- ✅ Đã sửa 2 file component
- ✅ Đã format lại debug log code
- ⏳ Đang rebuild và deploy

**Sau khi rebuild xong, lỗi sẽ được khắc phục hoàn toàn.**

---

**Báo cáo được tạo:** 2025-12-16 18:30

