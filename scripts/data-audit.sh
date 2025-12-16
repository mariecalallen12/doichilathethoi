#!/bin/bash
# Script kiểm tra và đánh giá trạng thái dữ liệu thực tế đang chạy trên Docker

set -e

echo "=========================================="
echo "KIỂM TRA VÀ ĐÁNH GIÁ DỮ LIỆU TRÊN DOCKER"
echo "=========================================="
echo ""

# Màu sắc cho output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Liệt kê tất cả các container có dữ liệu
echo -e "${GREEN}[1] Liệt kê containers có dữ liệu:${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "postgres|redis|backend"
echo ""

# 2. Kiểm tra các bảng/tập dữ liệu trong PostgreSQL
echo -e "${GREEN}[2] Kiểm tra các bảng trong PostgreSQL:${NC}"
docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "
SELECT 
    relname as table_name, 
    n_live_tup as row_count,
    pg_size_pretty(pg_total_relation_size(relid)) as total_size
FROM pg_stat_user_tables 
ORDER BY n_live_tup DESC, relname;
"
echo ""

# 3. Kiểm tra các key trong Redis
echo -e "${GREEN}[3] Kiểm tra các key trong Redis:${NC}"
REDIS_PASSWORD="${REDIS_PASSWORD:-}"
if [ -z "$REDIS_PASSWORD" ]; then
    KEY_COUNT=$(docker exec digital_utopia_redis redis-cli --no-auth-warning DBSIZE 2>&1 | grep -E "^[0-9]+$" | tail -1 || echo "0")
    if [ -z "$KEY_COUNT" ] || [ "$KEY_COUNT" = "0" ]; then
        KEY_COUNT=0
    fi
    echo "Số lượng keys trong Redis: $KEY_COUNT"
    if [ "$KEY_COUNT" -gt 0 ] 2>/dev/null; then
        echo "Các key mẫu (tối đa 20):"
        docker exec digital_utopia_redis redis-cli --no-auth-warning KEYS "*" 2>&1 | grep -v "NOAUTH" | head -20
    fi
else
    KEY_COUNT=$(docker exec digital_utopia_redis redis-cli -a "$REDIS_PASSWORD" DBSIZE 2>&1 | grep -E "^[0-9]+$" | tail -1 || echo "0")
    if [ -z "$KEY_COUNT" ] || [ "$KEY_COUNT" = "0" ]; then
        KEY_COUNT=0
    fi
    echo "Số lượng keys trong Redis: $KEY_COUNT"
    if [ "$KEY_COUNT" -gt 0 ] 2>/dev/null; then
        echo "Các key mẫu (tối đa 20):"
        docker exec digital_utopia_redis redis-cli -a "$REDIS_PASSWORD" KEYS "*" 2>&1 | head -20
    fi
fi
echo ""

# 4. Kiểm tra file uploads/static trong volume
echo -e "${GREEN}[4] Kiểm tra file uploads trong volume:${NC}"
UPLOAD_COUNT=$(docker exec digital_utopia_backend find /app/uploads -type f 2>/dev/null | wc -l)
echo "Số lượng file uploads: $UPLOAD_COUNT"
if [ "$UPLOAD_COUNT" -gt 0 ]; then
    echo "Danh sách file uploads:"
    docker exec digital_utopia_backend find /app/uploads -type f -ls 2>/dev/null | head -20
fi
echo ""

# 5. Kiểm tra volumes Docker
echo -e "${GREEN}[5] Kiểm tra volumes Docker:${NC}"
docker volume ls | grep -E "forexxx|digital_utopia"
echo ""

# 6. Tổng hợp: Xác định nguồn dữ liệu
echo -e "${GREEN}[6] Tổng hợp nguồn dữ liệu:${NC}"
echo "- PostgreSQL: digital_utopia_postgres (database: digital_utopia)"
echo "- Redis: digital_utopia_redis"
echo "- Uploads: backend_uploads volume"
echo ""

# 7. Kiểm tra dữ liệu seed/test
echo -e "${GREEN}[7] Kiểm tra dữ liệu seed/test:${NC}"
docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "
SELECT 
    'users' as table_name,
    COUNT(*) as total_rows,
    COUNT(CASE WHEN email LIKE '%test%' OR email LIKE '%example%' OR email LIKE '%demo%' THEN 1 END) as test_rows
FROM users
UNION ALL
SELECT 
    'trading_orders' as table_name,
    COUNT(*) as total_rows,
    COUNT(CASE WHEN status = 'test' OR source LIKE '%test%' THEN 1 END) as test_rows
FROM trading_orders
UNION ALL
SELECT 
    'transactions' as table_name,
    COUNT(*) as total_rows,
    COUNT(CASE WHEN description LIKE '%test%' OR description LIKE '%demo%' THEN 1 END) as test_rows
FROM transactions;
"
echo ""

echo -e "${GREEN}Hoàn thành kiểm tra dữ liệu!${NC}"

