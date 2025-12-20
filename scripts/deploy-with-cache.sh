#!/bin/bash
# Script triển khai nhanh với cache - Không rebuild từ đầu
# Digital Utopia Platform - Quick Deployment with Cache

set -e

# Màu sắc
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_ROOT="/root/forexxx"
cd "$PROJECT_ROOT"

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}⚡ Triển khai nhanh với cache${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Kiểm tra .env
if [ ! -f .env ]; then
    echo -e "${RED}❌ File .env không tồn tại${NC}"
    exit 1
fi

log() {
    echo -e "[$(date +'%H:%M:%S')] $1"
}

# Dọn dẹp containers cũ
log "Đang dừng containers cũ..."
docker compose down --remove-orphans 2>/dev/null || true

# Build với cache (nhanh hơn)
log "Đang build images với cache..."
docker compose build

# Khởi động services
log "Đang khởi động services..."
docker compose up -d

# Chờ databases
log "Đang chờ databases sẵn sàng..."
sleep 10

# Chờ backend
log "Đang chờ backend sẵn sàng..."
MAX_WAIT=120
WAIT_COUNT=0
until curl -f -s http://localhost:8000/api/health > /dev/null 2>&1; do
    WAIT_COUNT=$((WAIT_COUNT + 1))
    if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
        echo -e "${RED}❌ Backend không khởi động được${NC}"
        docker compose logs --tail=50 backend
        exit 1
    fi
    echo -n "."
    sleep 2
done
echo ""
echo -e "${GREEN}✅ Backend sẵn sàng${NC}"

# Chạy migrations
log "Đang chạy migrations..."
docker compose exec -T backend alembic upgrade head 2>/dev/null || true

# Kiểm tra status
echo ""
echo -e "${BLUE}📊 Status:${NC}"
docker compose ps

echo ""
echo -e "${GREEN}✅ Triển khai hoàn tất!${NC}"

