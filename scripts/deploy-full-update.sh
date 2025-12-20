#!/bin/bash
# Script triển khai toàn diện - Đảm bảo cập nhật tất cả thay đổi và xóa container cũ
# Digital Utopia Platform - Full Deployment with Cleanup

set -e

# Màu sắc cho output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Thư mục gốc của project
PROJECT_ROOT="/root/forexxx"
cd "$PROJECT_ROOT"

# Xác định lệnh docker compose (ưu tiên v2)
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker compose"
fi

# Cấu hình
FORCE_REBUILD=${1:-true}  # Mặc định rebuild images
CLEAN_IMAGES=${2:-false}   # Có xóa images cũ không (mặc định false để tránh mất thời gian)
KEEP_VOLUMES=${3:-true}    # Giữ lại volumes (database data)

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}🚀 Triển khai toàn diện - Full Deployment${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Kiểm tra .env file
if [ ! -f .env ]; then
    echo -e "${RED}❌ File .env không tồn tại. Vui lòng tạo từ .env.example:${NC}"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

# Load environment variables (safely)
# Use export to avoid command execution issues
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs) 2>/dev/null || true
fi

# Hàm log với timestamp
log() {
    echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Bước 1: Dừng và xóa tất cả containers cũ
cleanup_containers() {
    echo -e "${BLUE}📋 Bước 1: Dọn dẹp containers cũ...${NC}"
    echo "=========================================="
    
    # Liệt kê tất cả containers liên quan
    log "Đang tìm containers của dự án..."
    
    # Tìm containers theo tên pattern
    CONTAINERS=$(docker ps -a --filter "name=digital_utopia" --format "{{.Names}}" 2>/dev/null || true)
    
    if [ -n "$CONTAINERS" ]; then
        echo -e "${YELLOW}Containers tìm thấy:${NC}"
        echo "$CONTAINERS" | sed 's/^/  - /'
        echo ""
        
        # Dừng containers
        log "Đang dừng containers..."
        echo "$CONTAINERS" | xargs -r docker stop 2>/dev/null || true
        sleep 2
        
        # Xóa containers
        log "Đang xóa containers..."
        echo "$CONTAINERS" | xargs -r docker rm -f 2>/dev/null || true
        echo -e "${GREEN}✅ Đã xóa tất cả containers cũ${NC}"
    else
        echo -e "${GREEN}✅ Không có containers cũ cần xóa${NC}"
    fi
    
    # Xóa containers từ docker compose nếu có
    log "Đang dừng và xóa containers từ docker compose..."
    docker compose down --remove-orphans 2>/dev/null || docker compose down --remove-orphans 2>/dev/null || true
    
    echo ""
}

# Bước 2: Xóa images cũ (tùy chọn)
cleanup_images() {
    if [ "$CLEAN_IMAGES" = "true" ]; then
        echo -e "${BLUE}📋 Bước 2: Xóa images cũ...${NC}"
        echo "=========================================="
        
        # Xóa images của project
        log "Đang xóa images cũ..."
        
        # Tìm và xóa images
        IMAGES=$(docker images --filter "reference=digital_utopia*" --format "{{.Repository}}:{{.Tag}}" 2>/dev/null || true)
        
        if [ -n "$IMAGES" ]; then
            echo -e "${YELLOW}Images sẽ bị xóa:${NC}"
            echo "$IMAGES" | sed 's/^/  - /'
            echo ""
            
            echo "$IMAGES" | xargs -r docker rmi -f 2>/dev/null || true
            echo -e "${GREEN}✅ Đã xóa images cũ${NC}"
        else
            echo -e "${GREEN}✅ Không có images cũ cần xóa${NC}"
        fi
        
        # Dọn dẹp hệ thống Docker
        log "Đang dọn dẹp hệ thống Docker..."
        docker system prune -f --volumes=false 2>/dev/null || true
        
        echo ""
    else
        echo -e "${BLUE}📋 Bước 2: Bỏ qua xóa images (để tiết kiệm thời gian)${NC}"
        echo "=========================================="
        echo -e "${YELLOW}💡 Để xóa images cũ, chạy: ./scripts/deploy-full-update.sh true true${NC}"
        echo ""
    fi
}

# Bước 3: Build images mới
build_images() {
    echo -e "${BLUE}📋 Bước 3: Build images mới với code mới nhất...${NC}"
    echo "=========================================="
    
    if [ "$FORCE_REBUILD" = "true" ]; then
        log "Đang build lại tất cả images (--no-cache)..."
        docker compose build --no-cache --pull
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Build images thành công${NC}"
        else
            echo -e "${RED}❌ Build images thất bại${NC}"
            exit 1
        fi
    else
        log "Đang build images (sử dụng cache nếu có)..."
        docker compose build --pull
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Build images thành công${NC}"
        else
            echo -e "${RED}❌ Build images thất bại${NC}"
            exit 1
        fi
    fi
    
    echo ""
}

# Bước 4: Khởi động database services
start_databases() {
    echo -e "${BLUE}📋 Bước 4: Khởi động database services...${NC}"
    echo "=========================================="
    
    log "Đang khởi động PostgreSQL và Redis..."
    docker compose up -d postgres redis
    
    # Chờ PostgreSQL sẵn sàng
    log "Đang chờ PostgreSQL sẵn sàng..."
    MAX_WAIT=60
    WAIT_COUNT=0
    until docker compose exec -T postgres pg_isready -U "${POSTGRES_USER:-postgres}" > /dev/null 2>&1; do
        WAIT_COUNT=$((WAIT_COUNT + 1))
        if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
            echo -e "${RED}❌ PostgreSQL không khởi động được trong ${MAX_WAIT} giây${NC}"
            docker compose logs --tail=50 postgres
            exit 1
        fi
        echo -n "."
        sleep 2
    done
    echo ""
    echo -e "${GREEN}✅ PostgreSQL sẵn sàng${NC}"
    
    # Chờ Redis sẵn sàng
    log "Đang chờ Redis sẵn sàng..."
    WAIT_COUNT=0
    until docker compose exec -T redis redis-cli ping > /dev/null 2>&1; do
        WAIT_COUNT=$((WAIT_COUNT + 1))
        if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
            echo -e "${RED}❌ Redis không khởi động được trong ${MAX_WAIT} giây${NC}"
            docker compose logs --tail=50 redis
            exit 1
        fi
        echo -n "."
        sleep 2
    done
    echo ""
    echo -e "${GREEN}✅ Redis sẵn sàng${NC}"
    echo ""
}

# Bước 5: Khởi động backend
start_backend() {
    echo -e "${BLUE}📋 Bước 5: Khởi động backend service...${NC}"
    echo "=========================================="
    
    log "Đang khởi động backend..."
    docker compose up -d backend
    
    # Chờ backend sẵn sàng
    log "Đang chờ backend sẵn sàng..."
    MAX_WAIT=120
    WAIT_COUNT=0
    until curl -f -s http://localhost:${BACKEND_PORT:-8000}/api/health > /dev/null 2>&1; do
        WAIT_COUNT=$((WAIT_COUNT + 1))
        if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
            echo ""
            echo -e "${RED}❌ Backend không khởi động được trong ${MAX_WAIT} giây${NC}"
            echo -e "${YELLOW}📋 Backend logs:${NC}"
            docker compose logs --tail=50 backend
            exit 1
        fi
        echo -n "."
        sleep 2
    done
    echo ""
    echo -e "${GREEN}✅ Backend sẵn sàng${NC}"
    
    # Chạy migrations
    log "Đang kiểm tra và chạy database migrations..."
    MIGRATION_CHECK=$(docker compose exec -T backend alembic current 2>&1 || true)
    if echo "$MIGRATION_CHECK" | grep -q "alembic"; then
        log "Đang chạy migrations..."
        docker compose exec -T backend alembic upgrade head
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Migrations hoàn tất${NC}"
        else
            echo -e "${RED}❌ Migration thất bại${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ Migrations đã cập nhật${NC}"
    fi
    
    echo ""
}

# Bước 6: Khởi động frontend services
start_frontend() {
    echo -e "${BLUE}📋 Bước 6: Khởi động frontend services...${NC}"
    echo "=========================================="
    
    log "Đang khởi động client-app và admin-app..."
    docker compose up -d client-app admin-app
    
    # Chờ frontend services
    log "Đang chờ frontend services khởi động..."
    sleep 15
    
    # Kiểm tra client-app
    if docker ps | grep -q "digital_utopia_client"; then
        echo -e "${GREEN}✅ Client-app đang chạy${NC}"
    else
        echo -e "${YELLOW}⚠️  Client-app có thể chưa sẵn sàng${NC}"
    fi
    
    # Kiểm tra admin-app
    if docker ps | grep -q "digital_utopia_admin"; then
        echo -e "${GREEN}✅ Admin-app đang chạy${NC}"
    else
        echo -e "${YELLOW}⚠️  Admin-app có thể chưa sẵn sàng${NC}"
    fi
    
    echo ""
}

# Bước 7: Khởi động nginx proxy
start_nginx() {
    echo -e "${BLUE}📋 Bước 7: Khởi động nginx proxy...${NC}"
    echo "=========================================="
    
    log "Đang khởi động nginx-proxy..."
    docker compose up -d nginx-proxy
    
    sleep 5
    
    if docker ps | grep -q "digital_utopia_nginx_proxy"; then
        echo -e "${GREEN}✅ Nginx-proxy đang chạy${NC}"
    else
        echo -e "${YELLOW}⚠️  Nginx-proxy có thể chưa sẵn sàng${NC}"
    fi
    
    echo ""
}

# Bước 8: Kiểm tra health
health_check() {
    echo -e "${BLUE}📋 Bước 8: Kiểm tra health của tất cả services...${NC}"
    echo "=========================================="
    
    local all_healthy=true
    
    # Kiểm tra PostgreSQL
    if docker compose exec -T postgres pg_isready -U ${POSTGRES_USER:-postgres} > /dev/null 2>&1; then
        echo -e "${GREEN}  ✅ PostgreSQL: healthy${NC}"
    else
        echo -e "${RED}  ❌ PostgreSQL: unhealthy${NC}"
        all_healthy=false
    fi
    
    # Kiểm tra Redis
    if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}  ✅ Redis: healthy${NC}"
    else
        echo -e "${RED}  ❌ Redis: unhealthy${NC}"
        all_healthy=false
    fi
    
    # Kiểm tra Backend
    if curl -f -s http://localhost:${BACKEND_PORT:-8000}/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}  ✅ Backend: healthy${NC}"
    else
        echo -e "${RED}  ❌ Backend: unhealthy${NC}"
        all_healthy=false
    fi
    
    # Kiểm tra Client-app
    if curl -f -s http://localhost:${CLIENT_PORT:-3002}/health > /dev/null 2>&1; then
        echo -e "${GREEN}  ✅ Client-app: healthy${NC}"
    else
        echo -e "${YELLOW}  ⚠️  Client-app: health check không khả dụng (có thể vẫn đang chạy)${NC}"
    fi
    
    # Kiểm tra Admin-app
    if curl -f -s http://localhost:${ADMIN_PORT:-3001}/health > /dev/null 2>&1; then
        echo -e "${GREEN}  ✅ Admin-app: healthy${NC}"
    else
        echo -e "${YELLOW}  ⚠️  Admin-app: health check không khả dụng (có thể vẫn đang chạy)${NC}"
    fi
    
    echo ""
    
    if [ "$all_healthy" = true ]; then
        echo -e "${GREEN}✅ Tất cả services chính đều healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ Một số services không healthy${NC}"
        return 1
    fi
}

# Hiển thị summary
show_summary() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}📊 Tóm tắt triển khai${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    
    echo -e "${BLUE}📦 Containers đang chạy:${NC}"
    docker compose ps
    echo ""
    
    echo -e "${BLUE}🌐 URLs truy cập:${NC}"
    echo "   Backend API:    http://localhost:${BACKEND_PORT:-8000}"
    echo "   API Docs:       http://localhost:${BACKEND_PORT:-8000}/docs"
    echo "   Client App:     http://localhost:${CLIENT_PORT:-3002}"
    echo "   Admin App:      http://localhost:${ADMIN_PORT:-3001}"
    echo ""
    
    echo -e "${BLUE}📋 Lệnh hữu ích:${NC}"
    echo "   Xem logs:       docker compose logs -f [service_name]"
    echo "   Xem tất cả:     docker compose logs -f"
    echo "   Dừng services:  docker compose down"
    echo "   Restart:        docker compose restart [service_name]"
    echo "   Status:         docker compose ps"
    echo ""
}

# Main execution
main() {
    START_TIME=$(date +%s)
    
    # Bước 1: Dọn dẹp containers cũ
    cleanup_containers
    
    # Bước 2: Xóa images cũ (tùy chọn)
    cleanup_images
    
    # Bước 3: Build images mới
    build_images
    
    # Bước 4: Khởi động databases
    start_databases
    
    # Bước 5: Khởi động backend
    start_backend
    
    # Bước 6: Khởi động frontend
    start_frontend
    
    # Bước 7: Khởi động nginx
    start_nginx
    
    # Bước 8: Health check
    health_check
    
    # Hiển thị summary
    show_summary
    
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✅ Triển khai hoàn tất thành công!${NC}"
    echo -e "${GREEN}⏱️  Thời gian: ${DURATION} giây${NC}"
    echo -e "${GREEN}========================================${NC}"
}

# Chạy main function
main "$@"

