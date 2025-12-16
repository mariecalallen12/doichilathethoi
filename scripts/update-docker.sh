#!/bin/bash
# Script để cập nhật Docker containers sau khi có thay đổi code

set -e

echo "🔄 Cập nhật Docker containers cho Digital Utopia Platform"
echo "=========================================================="

cd "$(dirname "$0")/.."

# Kiểm tra Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker không được cài đặt"
    exit 1
fi

# 1. Restart backend để chạy migration mới
echo ""
echo "📦 Đang restart backend container để chạy migrations..."
docker-compose restart backend || echo "⚠️  Không thể restart backend (có thể container chưa chạy)"

# Đợi backend khởi động
echo "⏳ Đợi backend khởi động..."
sleep 10

# 2. Chạy migration thủ công (nếu cần)
echo ""
echo "🔄 Đang chạy database migrations..."
docker-compose exec -T backend alembic upgrade head || {
    echo "⚠️  Không thể chạy migration qua docker-compose exec"
    echo "💡 Bạn có thể chạy thủ công: docker exec -it digital_utopia_backend alembic upgrade head"
}

# 3. Rebuild admin-app nếu có thay đổi frontend
echo ""
echo "🔨 Đang rebuild admin-app với code mới..."
docker-compose build admin-app || echo "⚠️  Không thể rebuild admin-app"

echo ""
echo "🚀 Đang restart admin-app..."
docker-compose up -d admin-app || echo "⚠️  Không thể restart admin-app"

# 4. Kiểm tra trạng thái containers
echo ""
echo "📊 Kiểm tra trạng thái containers..."
docker-compose ps

echo ""
echo "✅ Hoàn tất! Các thay đổi đã được cập nhật."
echo ""
echo "📝 Lưu ý:"
echo "   - Backend đã được restart và migrations đã chạy"
echo "   - Admin-app đã được rebuild và restart"
echo "   - Nếu có lỗi, kiểm tra logs: docker-compose logs backend"
echo "   - Kiểm tra migration: docker exec -it digital_utopia_backend alembic current"

