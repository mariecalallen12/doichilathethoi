# Báo Cáo Vấn Đề OPEX Services

**Ngày:** 2025-12-16  
**Vấn đề:** Giao diện trading hiển thị lỗi và không có dữ liệu  
**Nguyên nhân:** OPEX Core services chưa được khởi động

---

## 🔍 Phân Tích Vấn Đề

### Hiện Trạng

1. **Frontend đang chạy:** ✅
   - Client-app: http://localhost:3002
   - Admin-app: http://localhost:3001

2. **Backend đang chạy:** ✅
   - Backend API: http://localhost:8000
   - Endpoint `/api/market/orderbook/BTCUSDT` hoạt động nhưng trả về rỗng:
     ```json
     {"symbol":"BTCUSDT","bids":[],"asks":[],"timestamp":1765906736386}
     ```

3. **OPEX Core Services:** ❌ **CHƯA CHẠY**
   - Không có services nào từ core-main đang chạy
   - Backend không thể lấy dữ liệu từ OPEX API

### Kiến Trúc Hệ Thống

```
Frontend (Vue.js)
    ↓
Backend API (FastAPI) - http://localhost:8000
    ↓
OPEX Client - gọi http://opex-api:8080
    ↓
OPEX Core Services (Kotlin) - CHƯA CHẠY ❌
    ├── API Service (port 8080)
    ├── Market Service (port 8083)
    ├── Matching Engine
    ├── Wallet Service (port 8084)
    └── ...
```

### Vấn Đề Cụ Thể

1. **Backend cấu hình:**
   - `OPEX_API_URL = "http://opex-api:8080"` (mặc định)
   - Backend đang cố kết nối với `opex-api:8080` nhưng service không tồn tại

2. **Core-main services:**
   - Thư mục `/root/forexxx/core-main` có đầy đủ docker-compose files
   - Services chưa được khởi động
   - Cần file `.env` với các biến môi trường

3. **Network:**
   - Backend đang ở network: `forexxx_digital_utopia_network`
   - OPEX services sẽ ở network: `default` (từ core-main)
   - Cần đảm bảo backend có thể kết nối với OPEX services

---

## ✅ Giải Pháp

### 1. Khởi Động OPEX Core Services

Đã tạo script: `scripts/start-opex-services.sh`

**Cách sử dụng:**
```bash
cd /root/forexxx
./scripts/start-opex-services.sh
```

**Script sẽ:**
1. Kiểm tra và tạo file `.env` nếu chưa có
2. Khởi động infrastructure services:
   - Zookeeper
   - Kafka (3 instances)
   - Consul
   - Vault
   - Redis (3 instances)
   - PostgreSQL (7 databases)
3. Khởi động core services:
   - Matching Engine
   - Matching Gateway
   - Market Service
   - Wallet Service
   - API Service
4. Kiểm tra kết nối

### 2. Cấu Hình Network

**Option 1: Thêm backend vào OPEX network**
```bash
docker network connect opex-network digital_utopia_backend
```

**Option 2: Thêm OPEX services vào backend network**
```bash
docker network connect forexxx_digital_utopia_network opex-api
```

**Option 3: Sử dụng external network (khuyến nghị)**
- Tạo network chung cho cả hai hệ thống
- Hoặc sử dụng host network mode

### 3. Cấu Hình Backend

Kiểm tra biến môi trường trong `.env`:
```bash
OPEX_API_URL=http://opex-api:8080  # Nếu cùng network
# hoặc
OPEX_API_URL=http://localhost:8082  # Nếu expose port
```

---

## 📋 Các Services Cần Khởi Động

### Infrastructure (Bước 1)
- ✅ Zookeeper (port 2181)
- ✅ Kafka-1, Kafka-2, Kafka-3 (port 9092)
- ✅ Consul (port 8500)
- ✅ Vault (port 8200)
- ✅ Redis, Redis-duo, Redis-cache
- ✅ PostgreSQL (7 databases)

### Core Services (Bước 2)
- ✅ Matching Engine
- ✅ Matching Gateway (port 8081)
- ✅ Market Service (port 8083)
- ✅ Wallet Service (port 8084)
- ✅ API Service (port 8082) - **QUAN TRỌNG**
- ✅ Auth Service
- ✅ Accountant Service
- ✅ Eventlog Service

---

## 🔧 Các Bước Thực Hiện

### Bước 1: Khởi động OPEX services
```bash
cd /root/forexxx
./scripts/start-opex-services.sh
```

### Bước 2: Kiểm tra services đang chạy
```bash
cd /root/forexxx/core-main
docker compose ps
```

### Bước 3: Kiểm tra network connectivity
```bash
# Kiểm tra backend có thể kết nối với opex-api không
docker exec digital_utopia_backend curl -s http://opex-api:8080/health || echo "Không kết nối được"
```

### Bước 4: Cấu hình network (nếu cần)
```bash
# Thêm backend vào OPEX network
docker network connect opex-network digital_utopia_backend

# Hoặc thêm opex-api vào backend network
docker network connect forexxx_digital_utopia_network opex-api
```

### Bước 5: Kiểm tra API endpoint
```bash
# Test từ backend
curl http://localhost:8000/api/market/orderbook/BTCUSDT

# Nếu có dữ liệu, sẽ thấy bids và asks không rỗng
```

### Bước 6: Restart backend (nếu cần)
```bash
docker compose restart backend
```

---

## 📊 Kiểm Tra Sau Khi Khởi Động

### 1. Kiểm tra OPEX API
```bash
# Kiểm tra service đang chạy
docker ps | grep opex-api

# Kiểm tra health
curl http://localhost:8082/health
```

### 2. Kiểm tra Backend kết nối
```bash
# Test endpoint
curl http://localhost:8000/api/market/orderbook/BTCUSDT

# Kiểm tra logs
docker compose logs backend | grep -i opex
```

### 3. Kiểm tra Frontend
- Truy cập: https://cmeetrading.com/trading
- Kiểm tra Orderbook có dữ liệu không
- Kiểm tra console không còn lỗi

---

## ⚠️ Lưu Ý

1. **Thời gian khởi động:**
   - Infrastructure: ~2-3 phút
   - Core services: ~3-5 phút
   - Tổng cộng: ~5-8 phút

2. **Tài nguyên:**
   - OPEX services cần nhiều RAM và CPU
   - Đảm bảo server có đủ tài nguyên

3. **Network:**
   - Backend và OPEX services phải ở cùng network hoặc có thể kết nối được
   - Kiểm tra firewall và port mapping

4. **Environment Variables:**
   - File `.env` trong core-main cần có đầy đủ biến
   - Script sẽ tạo file mặc định nếu chưa có

---

## 🎯 Kết Luận

**Vấn đề:** OPEX Core services chưa được khởi động nên backend không thể lấy dữ liệu trading.

**Giải pháp:** 
1. ✅ Đã tạo script khởi động: `scripts/start-opex-services.sh`
2. ⏳ Cần chạy script để khởi động services
3. ⏳ Cần cấu hình network để backend kết nối được với OPEX API
4. ⏳ Sau đó frontend sẽ có dữ liệu hiển thị

**Bước tiếp theo:** Chạy script khởi động và kiểm tra kết quả.

---

**Báo cáo được tạo:** 2025-12-16 18:40

