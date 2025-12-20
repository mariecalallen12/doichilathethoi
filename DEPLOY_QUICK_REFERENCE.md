# Tóm tắt Nhanh - Quick Reference

## 🚀 Triển khai nhanh

### Triển khai toàn diện (Khuyến nghị cho lần đầu hoặc sau nhiều thay đổi)
```bash
./deploy.sh full
```

### Triển khai nhanh (Sau khi chỉnh sửa code nhỏ)
```bash
./deploy.sh quick
```

### Triển khai nhanh chỉ một service
```bash
./deploy.sh quick backend
./deploy.sh quick client-app
./deploy.sh quick admin-app
```

### Triển khai và xóa sạch images cũ
```bash
./deploy.sh clean
```

## 📋 Các bước script thực hiện

### `deploy.sh full` hoặc `deploy-full-update.sh`
1. ✅ Dừng và xóa tất cả containers cũ
2. ✅ (Tùy chọn) Xóa images cũ
3. ✅ Build lại images với code mới nhất
4. ✅ Khởi động PostgreSQL và Redis
5. ✅ Khởi động Backend và chạy migrations
6. ✅ Khởi động Client-app và Admin-app
7. ✅ Khởi động Nginx proxy
8. ✅ Kiểm tra health của tất cả services

### `deploy.sh quick [services]`
1. ✅ Dừng containers của services chỉ định
2. ✅ Build lại images của services
3. ✅ Khởi động lại services

## 🔍 Kiểm tra sau triển khai

```bash
# Xem status
docker-compose ps

# Xem logs
docker-compose logs -f [service_name]

# Kiểm tra health
curl http://localhost:8000/api/health
```

## ⚠️ Lưu ý

- **Backup dữ liệu** trước khi chạy `clean`
- Đảm bảo file `.env` đã được cấu hình
- Kiểm tra ports không bị chiếm (8000, 3001, 3002, 5433, 6379)
- Triển khai toàn diện có thể mất 10-20 phút

## 📚 Tài liệu đầy đủ

Xem `DEPLOYMENT_GUIDE.md` để biết chi tiết.

