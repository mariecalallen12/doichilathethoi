#!/bin/bash
# Script validation dữ liệu sau cleanup - đảm bảo tính nhất quán

set -e

echo "=========================================="
echo "VALIDATION DỮ LIỆU SAU CLEANUP"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ERRORS=0

# 1. Kiểm tra foreign key constraints
echo -e "${GREEN}[1] Kiểm tra foreign key constraints:${NC}"
FK_ERRORS=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
SELECT COUNT(*) FROM refresh_tokens WHERE user_id NOT IN (SELECT id FROM users)
UNION ALL
SELECT COUNT(*) FROM user_profiles WHERE user_id NOT IN (SELECT id FROM users)
UNION ALL
SELECT COUNT(*) FROM wallet_balances WHERE user_id NOT IN (SELECT id FROM users)
UNION ALL
SELECT COUNT(*) FROM trading_orders WHERE user_id NOT IN (SELECT id FROM users);
" | awk '{sum+=$1} END {print sum}')

if [ "$FK_ERRORS" -gt 0 ]; then
    echo -e "${RED}✗ Tìm thấy $FK_ERRORS orphaned records${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓ Không có orphaned records${NC}"
fi
echo ""

# 2. Kiểm tra dữ liệu test còn sót lại
echo -e "${GREEN}[2] Kiểm tra dữ liệu test còn sót lại:${NC}"
TEST_DATA=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
SELECT COUNT(*) FROM users WHERE email LIKE '%test%' OR email LIKE '%example%' OR email LIKE '%demo%'
UNION ALL
SELECT COUNT(*) FROM trading_orders WHERE status = 'test' OR source LIKE '%test%';
" | awk '{sum+=$1} END {print sum}')

if [ "$TEST_DATA" -gt 0 ]; then
    echo -e "${YELLOW}⚠ Tìm thấy $TEST_DATA records test/demo${NC}"
else
    echo -e "${GREEN}✓ Không có dữ liệu test/demo${NC}"
fi
echo ""

# 3. Kiểm tra tính nhất quán của dữ liệu core
echo -e "${GREEN}[3] Kiểm tra tính nhất quán dữ liệu core:${NC}"
CORE_CHECK=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
SELECT 
    (SELECT COUNT(*) FROM users) as users_count,
    (SELECT COUNT(*) FROM user_profiles) as profiles_count,
    (SELECT COUNT(*) FROM roles) as roles_count,
    (SELECT COUNT(*) FROM permissions) as permissions_count,
    (SELECT COUNT(*) FROM role_permissions) as role_permissions_count;
")

echo "$CORE_CHECK"
echo ""

# 4. Kiểm tra index và performance
echo -e "${GREEN}[4] Kiểm tra index và performance:${NC}"
docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "
SELECT 
    schemaname,
    relname as tablename,
    idx_scan as index_scans,
    seq_scan as sequential_scans,
    CASE 
        WHEN idx_scan = 0 AND seq_scan > 0 THEN 'WARNING: Index không được sử dụng'
        ELSE 'OK'
    END as status
FROM pg_stat_user_tables 
WHERE idx_scan = 0 AND seq_scan > 100
ORDER BY seq_scan DESC
LIMIT 10;
"
echo ""

# 5. Kiểm tra database size
echo -e "${GREEN}[5] Kiểm tra database size:${NC}"
docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "
SELECT 
    pg_database.datname,
    pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
WHERE datname = 'digital_utopia';
"
echo ""

# 6. Tổng hợp kết quả
echo -e "${GREEN}[6] Tổng hợp kết quả validation:${NC}"
if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}✓ Validation thành công! Dữ liệu nhất quán và sạch.${NC}"
    exit 0
else
    echo -e "${RED}✗ Validation thất bại! Tìm thấy $ERRORS vấn đề.${NC}"
    exit 1
fi

