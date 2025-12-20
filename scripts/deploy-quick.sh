#!/bin/bash
# Script triển khai nhanh - Chỉ rebuild và restart services đã thay đổi
# Digital Utopia Platform - Quick Deployment

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

# Service cần rebuild (có thể truyền từ command line)
SERVICES_TO_REBUILD="${@:-backend client-app admin-app}"

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}⚡ Triển khai nhanh - Quick Deployment${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Kiểm tra .env
if [ ! -f .env ]; then
    echo -e "${RED}❌ File .env không tồn tại${NC}"
    exit 1
fi

set -a
source .env
set +a

log() {
    echo -e "[$(date +'%H:%M:%S')] $1"
}

# Dừng và xóa containers của services cần rebuild
log "Đang dừng containers cũ..."
for service in $SERVICES_TO_REBUILD; do
    docker-compose stop $service 2>/dev/null || true
    docker-compose rm -f $service 2>/dev/null || true
done

# Build lại images
log "Đang build lại images..."
docker-compose build $SERVICES_TO_REBUILD

# Khởi động lại services
log "Đang khởi động services..."
docker-compose up -d $SERVICES_TO_REBUILD

# Chờ services sẵn sàng
log "Đang chờ services sẵn sàng..."
sleep 10

# Kiểm tra status
echo ""
echo -e "${BLUE}📊 Status:${NC}"
docker-compose ps $SERVICES_TO_REBUILD

echo ""
echo -e "${GREEN}✅ Triển khai nhanh hoàn tất!${NC}"

