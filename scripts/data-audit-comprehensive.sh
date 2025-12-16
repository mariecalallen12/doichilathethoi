#!/bin/bash
# Script quét và phân tích toàn bộ dữ liệu từ tất cả Docker containers và environments
# Phục vụ cho việc đồng bộ hóa dữ liệu toàn dự án

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPORT_DIR="$PROJECT_ROOT/reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$REPORT_DIR/data_audit_${TIMESTAMP}.md"

# Tạo thư mục reports nếu chưa có
mkdir -p "$REPORT_DIR"

# Màu sắc
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Log function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$REPORT_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$REPORT_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$REPORT_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$REPORT_FILE"
}

# Khởi tạo báo cáo
cat > "$REPORT_FILE" << EOF
# Báo Cáo Quét và Phân Tích Dữ Liệu Toàn Dự Án

**Ngày thực hiện:** $(date +'%Y-%m-%d %H:%M:%S')
**Script:** data-audit-comprehensive.sh
**Mục đích:** Quét và phân tích toàn bộ dữ liệu từ tất cả Docker containers và environments

---

## 1. Tổng Quan Docker Containers

EOF

log "Bắt đầu quét và phân tích dữ liệu..."

# 1. Liệt kê tất cả containers liên quan
log "1. Liệt kê tất cả Docker containers..."
{
    echo "### 1.1. Containers đang chạy"
    echo '```'
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}" | tee -a "$REPORT_FILE"
    echo '```'
    echo ""
} >> "$REPORT_FILE"

# 2. Kiểm tra các environments
log "2. Kiểm tra các environments (dev/staging/prod)..."
ENVIRONMENTS=("dev" "staging" "prod")
DETECTED_ENVS=()

for env in "${ENVIRONMENTS[@]}"; do
    if docker ps --format "{{.Names}}" | grep -q "${env}" || \
       docker-compose -f "docker-compose.${env}.yml" ps 2>/dev/null | grep -q "Up"; then
        DETECTED_ENVS+=("$env")
        info "Phát hiện environment: $env"
    fi
done

{
    echo "### 1.2. Environments được phát hiện"
    echo "- Environments: ${DETECTED_ENVS[*]}"
    echo ""
} >> "$REPORT_FILE"

# 3. Quét PostgreSQL databases
log "3. Quét PostgreSQL databases..."
{
    echo "## 2. Phân Tích PostgreSQL Databases"
    echo ""
} >> "$REPORT_FILE"

# Tìm tất cả PostgreSQL containers
PG_CONTAINERS=$(docker ps --format "{{.Names}}" | grep -E "postgres|db" || true)

if [ -z "$PG_CONTAINERS" ]; then
    warning "Không tìm thấy PostgreSQL containers đang chạy"
    {
        echo "### 2.1. Không có PostgreSQL containers đang chạy"
        echo ""
    } >> "$REPORT_FILE"
else
    for container in $PG_CONTAINERS; do
        log "Phân tích PostgreSQL container: $container"
        
        # Lấy thông tin database
        DB_NAME=$(docker exec "$container" psql -U postgres -t -c "SELECT datname FROM pg_database WHERE datistemplate = false AND datname != 'postgres';" 2>/dev/null | head -1 | tr -d ' ' || echo "digital_utopia")
        
        {
            echo "### 2.1. Container: $container"
            echo "- Database: $DB_NAME"
            echo ""
            echo "#### Tables và Row Counts"
            echo '```sql'
        } >> "$REPORT_FILE"
        
        docker exec "$container" psql -U postgres -d "$DB_NAME" -c "
        SELECT 
            schemaname,
            tablename as table_name,
            n_live_tup as row_count,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
            pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as indexes_size
        FROM pg_stat_user_tables 
        ORDER BY n_live_tup DESC, tablename;
        " 2>/dev/null | tee -a "$REPORT_FILE" || warning "Không thể query database trong container $container"
        
        {
            echo '```'
            echo ""
            echo "#### Database Size"
            echo '```sql'
        } >> "$REPORT_FILE"
        
        docker exec "$container" psql -U postgres -d "$DB_NAME" -c "
        SELECT 
            pg_database.datname,
            pg_size_pretty(pg_database_size(pg_database.datname)) AS size
        FROM pg_database
        WHERE datname = '$DB_NAME';
        " 2>/dev/null | tee -a "$REPORT_FILE" || warning "Không thể lấy database size"
        
        {
            echo '```'
            echo ""
            echo "#### Migration Version"
            echo '```sql'
        } >> "$REPORT_FILE"
        
        docker exec "$container" psql -U postgres -d "$DB_NAME" -c "
        SELECT version_num FROM alembic_version LIMIT 1;
        " 2>/dev/null | tee -a "$REPORT_FILE" || warning "Không có alembic_version table"
        
        {
            echo '```'
            echo ""
        } >> "$REPORT_FILE"
    done
fi

# 4. Quét Redis
log "4. Quét Redis cache..."
{
    echo "## 3. Phân Tích Redis Cache"
    echo ""
} >> "$REPORT_FILE"

REDIS_CONTAINERS=$(docker ps --format "{{.Names}}" | grep -E "redis|cache" || true)

if [ -z "$REDIS_CONTAINERS" ]; then
    warning "Không tìm thấy Redis containers"
    {
        echo "### 3.1. Không có Redis containers"
        echo ""
    } >> "$REPORT_FILE"
else
    for container in $REDIS_CONTAINERS; do
        log "Phân tích Redis container: $container"
        
        {
            echo "### 3.1. Container: $container"
            echo ""
        } >> "$REPORT_FILE"
        
        # Kiểm tra Redis password
        REDIS_PASSWORD="${REDIS_PASSWORD:-}"
        if [ -n "$REDIS_PASSWORD" ]; then
            KEY_COUNT=$(docker exec "$container" redis-cli -a "$REDIS_PASSWORD" DBSIZE 2>/dev/null | grep -E "^[0-9]+$" || echo "0")
        else
            KEY_COUNT=$(docker exec "$container" redis-cli --no-auth-warning DBSIZE 2>/dev/null | grep -E "^[0-9]+$" || echo "0")
        fi
        
        {
            echo "- Tổng số keys: $KEY_COUNT"
            echo ""
        } >> "$REPORT_FILE"
        
        if [ "$KEY_COUNT" -gt 0 ] 2>/dev/null; then
            {
                echo "#### Sample Keys (tối đa 50)"
                echo '\`\`\`'
            } >> "$REPORT_FILE"
            
            if [ -n "$REDIS_PASSWORD" ]; then
                docker exec "$container" redis-cli -a "$REDIS_PASSWORD" KEYS "*" 2>/dev/null | head -50 | tee -a "$REPORT_FILE" || true
            else
                docker exec "$container" redis-cli --no-auth-warning KEYS "*" 2>/dev/null | head -50 | tee -a "$REPORT_FILE" || true
            fi
            
            {
                echo '\`\`\`'
                echo ""
            } >> "$REPORT_FILE"
        fi
    done
fi

# 5. Quét file uploads volumes
log "5. Quét file uploads volumes..."
{
    echo "## 4. Phân Tích File Uploads"
    echo ""
} >> "$REPORT_FILE"

UPLOAD_CONTAINERS=$(docker ps --format "{{.Names}}" | grep -E "backend|app" || true)

if [ -z "$UPLOAD_CONTAINERS" ]; then
    warning "Không tìm thấy backend containers"
else
    for container in $UPLOAD_CONTAINERS; do
        log "Phân tích uploads trong container: $container"
        
        {
            echo "### 4.1. Container: $container"
            echo ""
        } >> "$REPORT_FILE"
        
        UPLOAD_COUNT=$(docker exec "$container" find /app/uploads -type f 2>/dev/null | wc -l || echo "0")
        UPLOAD_SIZE=$(docker exec "$container" du -sh /app/uploads 2>/dev/null | awk '{print $1}' || echo "0")
        
        {
            echo "- Số lượng files: $UPLOAD_COUNT"
            echo "- Tổng kích thước: $UPLOAD_SIZE"
            echo ""
        } >> "$REPORT_FILE"
        
        if [ "$UPLOAD_COUNT" -gt 0 ]; then
            {
                echo "#### Sample Files (tối đa 20)"
                echo '```'
            } >> "$REPORT_FILE"
            
            docker exec "$container" find /app/uploads -type f -ls 2>/dev/null | head -20 | tee -a "$REPORT_FILE" || true
            
            {
                echo '```'
                echo ""
            } >> "$REPORT_FILE"
        fi
    done
fi

# 6. Quét Docker volumes
log "6. Quét Docker volumes..."
{
    echo "## 5. Phân Tích Docker Volumes"
    echo ""
    echo "### 5.1. Volumes liên quan đến dự án"
    echo '```'
} >> "$REPORT_FILE"

docker volume ls | grep -E "forexxx|digital_utopia|postgres|redis|backend" | tee -a "$REPORT_FILE" || true

{
    echo '\`\`\`'
    echo ""
} >> "$REPORT_FILE"

# 7. Tổng hợp thống kê
log "7. Tạo tổng hợp thống kê..."
{
    echo "## 6. Tổng Hợp Thống Kê"
    echo ""
    echo "### 6.1. Tổng quan"
    echo "- Số lượng PostgreSQL containers: $(echo "$PG_CONTAINERS" | wc -l)"
    echo "- Số lượng Redis containers: $(echo "$REDIS_CONTAINERS" | wc -l)"
    echo "- Số lượng Backend containers: $(echo "$UPLOAD_CONTAINERS" | wc -l)"
    echo "- Environments phát hiện: ${DETECTED_ENVS[*]}"
    echo ""
    echo "### 6.2. Khuyến nghị"
    echo "1. Xác định master database dựa trên migration version và data completeness"
    echo "2. So sánh schema giữa các environments"
    echo "3. Đồng bộ dữ liệu từ master đến các environments khác"
    echo "4. Chuẩn hóa configurations"
    echo ""
} >> "$REPORT_FILE"

log "Hoàn thành quét và phân tích dữ liệu!"
log "Báo cáo được lưu tại: $REPORT_FILE"

echo ""
echo -e "${GREEN}=========================================="
echo "BÁO CÁO ĐÃ ĐƯỢC TẠO"
echo "==========================================${NC}"
echo "File: $REPORT_FILE"
echo ""

