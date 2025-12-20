#!/bin/bash
# Script để khởi động OPEX Core services từ core-main
# Đảm bảo backend có thể lấy dữ liệu trading

set -e

# Màu sắc
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

CORE_MAIN_DIR="/root/forexxx/core-main"

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}🚀 Khởi động OPEX Core Services${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Kiểm tra thư mục core-main
if [ ! -d "$CORE_MAIN_DIR" ]; then
    echo -e "${RED}❌ Thư mục core-main không tồn tại: $CORE_MAIN_DIR${NC}"
    exit 1
fi

cd "$CORE_MAIN_DIR"

# Kiểm tra file .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  File .env không tồn tại${NC}"
    echo -e "${YELLOW}💡 Tạo file .env từ template hoặc sử dụng giá trị mặc định${NC}"
    
    # Tạo .env với giá trị mặc định cơ bản
    cat > .env << 'EOF'
# OPEX Core Environment Variables
DB_USER=opex
DB_PASS=hiopex
DB_READ_ONLY_USER=opex_reader
DB_READ_ONLY_PASS=hiopex
BACKEND_USER=opex-backend
PANEL_PASS=hiopex
KEYCLOAK_ADMIN_USERNAME=opex-admin
KEYCLOAK_ADMIN_PASSWORD=hiopex
OPEX_ADMIN_KEYCLOAK_CLIENT_SECRET=opex-secret
VANDAR_API_KEY=
PREFERENCES=preferences-dev.yml
APP_NAME=OPEX
APP_BASE_URL=http://localhost
KEYCLOAK_FRONTEND_URL=http://localhost:8080
KEYCLOAK_ADMIN_URL=http://localhost:8080
VERIFY_REDIRECT_URL=http://localhost:8080
FORGOT_REDIRECT_URL=http://localhost:8080
WHITELIST_REGISTER_ENABLED=false
WHITELIST_LOGIN_ENABLED=false
API_KEY_CLIENT_SECRET=opex-api-secret
DRIVE_FOLDER_ID=
WALLET_BACKUP_ENABLED=false
EOF
    echo -e "${GREEN}✅ Đã tạo file .env với giá trị mặc định${NC}"
fi

# Kiểm tra docker-compose files
if [ ! -f docker-compose.yml ]; then
    echo -e "${RED}❌ File docker-compose.yml không tồn tại${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Bước 1: Khởi động infrastructure services...${NC}"
echo "=========================================="

# Khởi động infrastructure trước (zookeeper, kafka, consul, vault, redis, postgres)
echo "Đang khởi động: zookeeper, kafka, consul, vault, redis, postgres..."
docker compose up -d zookeeper kafka-1 kafka-2 kafka-3 consul vault redis redis-duo redis-cache \
    postgres-accountant postgres-eventlog postgres-auth postgres-wallet postgres-market postgres-api postgres-bc-gateway 2>&1 | tail -5

echo ""
echo -e "${BLUE}⏳ Đang chờ infrastructure sẵn sàng...${NC}"
sleep 10

echo ""
echo -e "${BLUE}📋 Bước 2: Khởi động core services...${NC}"
echo "=========================================="

# Khởi động core services
echo "Đang khởi động: matching-engine, market, wallet, api..."
docker compose up -d matching-engine matching-gateway market wallet api 2>&1 | tail -5

echo ""
echo -e "${BLUE}⏳ Đang chờ core services khởi động...${NC}"
sleep 15

echo ""
echo -e "${BLUE}📋 Bước 3: Kiểm tra services...${NC}"
echo "=========================================="

# Kiểm tra status
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" | head -20

echo ""
echo -e "${BLUE}📋 Bước 4: Kiểm tra kết nối backend...${NC}"
echo "=========================================="

# Kiểm tra xem backend có thể kết nối với opex-api không
echo "Đang kiểm tra OPEX API..."
sleep 5

# Kiểm tra opex-api có đang chạy không
if docker ps | grep -q "opex-api\|api.*8080"; then
    echo -e "${GREEN}✅ OPEX API service đang chạy${NC}"
    
    # Thử kết nối
    API_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "opex-api|^api$" | head -1)
    if [ -n "$API_CONTAINER" ]; then
        echo "Container: $API_CONTAINER"
        docker exec "$API_CONTAINER" curl -s http://localhost:8080/health 2>/dev/null || echo "Health check endpoint không khả dụng"
    fi
else
    echo -e "${YELLOW}⚠️  OPEX API service chưa sẵn sàng${NC}"
    echo "Kiểm tra logs: docker compose logs api"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Hoàn tất khởi động OPEX services${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📋 Lệnh hữu ích:${NC}"
echo "   Xem logs:     docker compose -f docker-compose.yml logs [service]"
echo "   Xem status:   docker compose -f docker-compose.yml ps"
echo "   Dừng:         docker compose -f docker-compose.yml down"
echo ""

