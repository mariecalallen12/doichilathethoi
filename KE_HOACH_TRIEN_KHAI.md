# Kế hoạch Triển khai - Deployment Plan

## ✅ Đã hoàn thành

Đã thiết lập hệ thống triển khai toàn diện để đảm bảo:
- ✅ Tất cả thay đổi từ nhiều phiên làm việc được cập nhật vào Docker
- ✅ Xóa bỏ containers và images cũ để tránh nhầm lẫn
- ✅ Logic hoạt động chính xác với code mới nhất

## 📦 Các Script đã tạo

### 1. `deploy.sh` - Script chính (Thư mục gốc)
Script master để quản lý tất cả các loại triển khai.

**Vị trí:** `/root/forexxx/deploy.sh`

**Cách sử dụng:**
```bash
cd /root/forexxx
./deploy.sh full    # Triển khai toàn diện
./deploy.sh quick   # Triển khai nhanh
./deploy.sh clean   # Triển khai và xóa sạch
```

### 2. `scripts/deploy-full-update.sh` - Triển khai toàn diện
Script chi tiết thực hiện đầy đủ các bước:
- Dừng và xóa containers cũ
- (Tùy chọn) Xóa images cũ
- Build lại images với code mới nhất
- Khởi động databases (PostgreSQL, Redis)
- Khởi động backend và chạy migrations
- Khởi động frontend (client-app, admin-app)
- Khởi động nginx proxy
- Kiểm tra health của tất cả services

**Vị trí:** `/root/forexxx/scripts/deploy-full-update.sh`

### 3. `scripts/deploy-quick.sh` - Triển khai nhanh
Script để nhanh chóng rebuild và restart các services đã thay đổi.

**Vị trí:** `/root/forexxx/scripts/deploy-quick.sh`

## 🎯 Quy trình Triển khai

### Bước 1: Chuẩn bị
```bash
cd /root/forexxx

# Kiểm tra file .env đã có chưa
ls -la .env

# Nếu chưa có, tạo từ template
cp .env.example .env
nano .env  # Cấu hình các biến môi trường
```

### Bước 2: Triển khai

#### Lần đầu tiên hoặc sau nhiều thay đổi lớn:
```bash
./deploy.sh full
```

Script sẽ tự động:
1. Tìm và xóa tất cả containers cũ có tên "digital_utopia*"
2. Build lại tất cả images với code mới nhất (--no-cache)
3. Khởi động databases và chờ sẵn sàng
4. Khởi động backend, chạy migrations tự động
5. Khởi động frontend services
6. Khởi động nginx proxy
7. Kiểm tra health và hiển thị kết quả

#### Sau khi chỉnh sửa code nhỏ:
```bash
# Chỉ rebuild service đã thay đổi
./deploy.sh quick backend
./deploy.sh quick client-app
```

#### Khi cần dọn dẹp hoàn toàn:
```bash
./deploy.sh clean
```
Sẽ xóa cả images cũ và build lại từ đầu.

### Bước 3: Kiểm tra
```bash
# Xem status của tất cả containers
docker-compose ps

# Xem logs
docker-compose logs -f

# Kiểm tra health endpoints
curl http://localhost:8000/api/health
curl http://localhost:3002/health
curl http://localhost:3001/health
```

## 🔍 Chi tiết các Bước Script Thực hiện

### `deploy-full-update.sh` thực hiện:

1. **Dọn dẹp Containers cũ**
   - Tìm tất cả containers: `docker ps -a --filter "name=digital_utopia"`
   - Dừng containers: `docker stop`
   - Xóa containers: `docker rm -f`
   - Chạy `docker-compose down --remove-orphans`

2. **Xóa Images cũ (Tùy chọn)**
   - Tìm images: `docker images --filter "reference=digital_utopia*"`
   - Xóa images: `docker rmi -f`
   - Dọn dẹp hệ thống: `docker system prune -f`

3. **Build Images mới**
   - Build với `--no-cache` để đảm bảo code mới nhất
   - Pull base images mới nhất với `--pull`

4. **Khởi động Databases**
   - Start PostgreSQL và Redis
   - Health check: `pg_isready` và `redis-cli ping`
   - Chờ tối đa 60 giây

5. **Khởi động Backend**
   - Start backend service
   - Health check: `curl http://localhost:8000/api/health`
   - Chờ tối đa 120 giây
   - Tự động chạy migrations: `alembic upgrade head`

6. **Khởi động Frontend**
   - Start client-app và admin-app
   - Chờ 15 giây để services khởi động

7. **Khởi động Nginx**
   - Start nginx-proxy
   - Chờ 5 giây

8. **Health Check**
   - Kiểm tra tất cả services
   - Hiển thị status và URLs

## 📊 Output mẫu

Khi chạy thành công, bạn sẽ thấy:

```
========================================
🚀 Triển khai toàn diện - Full Deployment
========================================

📋 Bước 1: Dọn dẹp containers cũ...
  - digital_utopia_backend
  - digital_utopia_client
✅ Đã xóa tất cả containers cũ

📋 Bước 3: Build images mới...
✅ Build images thành công

📋 Bước 4: Khởi động database services...
✅ PostgreSQL sẵn sàng
✅ Redis sẵn sàng

📋 Bước 5: Khởi động backend service...
✅ Backend sẵn sàng
✅ Migrations hoàn tất

📋 Bước 6: Khởi động frontend services...
✅ Client-app đang chạy
✅ Admin-app đang chạy

📋 Bước 8: Kiểm tra health...
  ✅ PostgreSQL: healthy
  ✅ Redis: healthy
  ✅ Backend: healthy

========================================
✅ Triển khai hoàn tất thành công!
⏱️  Thời gian: 450 giây
========================================
```

## ⚠️ Lưu ý Quan trọng

1. **Backup dữ liệu**: Trước khi chạy `clean`, đảm bảo đã backup database
2. **Environment**: File `.env` phải được cấu hình đúng
3. **Ports**: Đảm bảo ports không bị chiếm (8000, 3001, 3002, 5433, 6379)
4. **Disk space**: Build images tốn nhiều dung lượng, kiểm tra với `df -h`
5. **Thời gian**: Triển khai toàn diện mất khoảng 10-20 phút

## 🛠️ Xử lý Lỗi

### Nếu build thất bại:
```bash
# Xem logs chi tiết
docker-compose logs [service_name]

# Build lại từng service
docker-compose build [service_name] --no-cache
```

### Nếu container không khởi động:
```bash
# Xem logs
docker-compose logs [service_name]

# Kiểm tra environment
cat .env

# Kiểm tra ports
netstat -tulpn | grep :8000
```

### Nếu migration thất bại:
```bash
# Kiểm tra database
docker-compose exec postgres psql -U postgres -d digital_utopia

# Chạy migration thủ công
docker-compose exec backend alembic upgrade head
```

## 📚 Tài liệu Tham khảo

- `DEPLOYMENT_GUIDE.md` - Hướng dẫn chi tiết đầy đủ
- `DEPLOY_QUICK_REFERENCE.md` - Tóm tắt nhanh các lệnh

## ✅ Kết luận

Hệ thống triển khai đã được thiết lập hoàn chỉnh với:
- ✅ Script tự động dọn dẹp containers/images cũ
- ✅ Build và deploy với code mới nhất
- ✅ Health check tự động
- ✅ Xử lý migrations tự động
- ✅ Tài liệu đầy đủ bằng tiếng Việt

Bạn có thể bắt đầu sử dụng ngay với lệnh:
```bash
cd /root/forexxx
./deploy.sh full
```

