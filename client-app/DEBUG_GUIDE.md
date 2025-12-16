# Hướng Dẫn Debug Trading Dashboard

## Server đang chạy trên:
- **URL**: http://localhost:5174
- **Trading Dashboard**: http://localhost:5174/trading
- **Test Page**: http://localhost:5174/test

## Các bước kiểm tra:

### 1. Kiểm tra Browser Console
Mở Developer Tools (F12) và kiểm tra Console tab:
- Nếu có lỗi màu đỏ, copy và gửi cho tôi
- Kiểm tra xem có lỗi về imports không

### 2. Kiểm tra Network Tab
Trong Developer Tools > Network:
- Xem các file .js và .vue có load được không
- Kiểm tra status code (phải là 200)
- Nếu có file nào fail, ghi lại tên file

### 3. Hard Refresh Browser
- **Windows/Linux**: Ctrl + Shift + R hoặc Ctrl + F5
- **Mac**: Cmd + Shift + R
- Hoặc clear browser cache

### 4. Kiểm tra URL
Đảm bảo bạn đang truy cập đúng URL:
- ✅ http://localhost:5174/trading (Trading Dashboard)
- ✅ http://localhost:5174/test (Test Page - đơn giản hơn)
- ✅ http://localhost:5174/ (Home Page)

### 5. Kiểm tra Terminal Logs
Nếu có lỗi trong terminal khi chạy `npm run dev`, hãy copy và gửi cho tôi.

## Các lỗi thường gặp:

### Lỗi: "Cannot find module"
- **Giải pháp**: Chạy lại `npm install` trong thư mục client-app

### Lỗi: "Port already in use"
- **Giải pháp**: 
  ```bash
  pkill -f vite
  npm run dev
  ```

### Trang trắng không có gì
- **Nguyên nhân**: Có thể do JavaScript error
- **Giải pháp**: Kiểm tra Browser Console (F12)

### Components không hiển thị
- **Nguyên nhân**: Import path sai hoặc component chưa được tạo
- **Giải pháp**: Kiểm tra file structure

## Test nhanh:

1. Mở http://localhost:5174/test
   - Nếu thấy "Test Page - Trading Dashboard" → Vue đang hoạt động
   - Nếu không thấy gì → Có vấn đề với Vue setup

2. Mở http://localhost:5174/trading
   - Nếu thấy Trading Dashboard → Mọi thứ OK
   - Nếu trang trắng → Kiểm tra Browser Console

## Thông tin cần cung cấp khi báo lỗi:

1. Screenshot của Browser Console (F12 > Console)
2. Screenshot của Network Tab (F12 > Network)
3. URL bạn đang truy cập
4. Browser bạn đang dùng (Chrome, Firefox, etc.)
5. Bất kỳ error message nào trong terminal





