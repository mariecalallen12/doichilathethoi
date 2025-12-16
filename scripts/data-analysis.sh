#!/bin/bash
# Script phân tích và xác định dữ liệu dư thừa, cũ, không còn dùng

set -e

echo "=========================================="
echo "PHÂN TÍCH DỮ LIỆU DƯ THỪA/CŨ"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Phân tích bảng không có dữ liệu hoặc ít dữ liệu
echo -e "${GREEN}[1] Phân tích bảng không có dữ liệu:${NC}"
docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "
SELECT 
    relname as table_name,
    n_live_tup as row_count,
    CASE 
        WHEN n_live_tup = 0 THEN 'EMPTY - Có thể xóa nếu không cần'
        WHEN n_live_tup < 10 THEN 'LOW - Kiểm tra xem có cần thiết'
        ELSE 'OK'
    END as status
FROM pg_stat_user_tables 
WHERE n_live_tup = 0 OR n_live_tup < 10
ORDER BY n_live_tup, relname;
"
echo ""

# 2. Phân tích foreign key orphans
echo -e "${GREEN}[2] Phân tích orphaned records (không có foreign key hợp lệ):${NC}"
docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "
SELECT 
    'refresh_tokens' as table_name,
    COUNT(*) as orphaned_count
FROM refresh_tokens 
WHERE user_id NOT IN (SELECT id FROM users)
UNION ALL
SELECT 
    'user_profiles' as table_name,
    COUNT(*) as orphaned_count
FROM user_profiles 
WHERE user_id NOT IN (SELECT id FROM users)
UNION ALL
SELECT 
    'wallet_balances' as table_name,
    COUNT(*) as orphaned_count
FROM wallet_balances 
WHERE user_id NOT IN (SELECT id FROM users)
UNION ALL
SELECT 
    'trading_orders' as table_name,
    COUNT(*) as orphaned_count
FROM trading_orders 
WHERE user_id NOT IN (SELECT id FROM users)
UNION ALL
SELECT 
    'iceberg_orders' as table_name,
    COUNT(*) as orphaned_count
FROM iceberg_orders 
WHERE parent_order_id IS NOT NULL AND parent_order_id NOT IN (SELECT id FROM trading_orders)
UNION ALL
SELECT 
    'oco_orders' as table_name,
    COUNT(*) as orphaned_count
FROM oco_orders 
WHERE (primary_order_id IS NOT NULL AND primary_order_id NOT IN (SELECT id FROM trading_orders))
   OR (secondary_order_id IS NOT NULL AND secondary_order_id NOT IN (SELECT id FROM trading_orders));
"
echo ""

# 3. Phân tích dữ liệu cũ (theo thời gian)
echo -e "${GREEN}[3] Phân tích dữ liệu cũ (theo thời gian):${NC}"
docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "
SELECT 
    'audit_logs' as table_name,
    COUNT(*) as old_records,
    MIN(created_at) as oldest_record,
    MAX(created_at) as newest_record
FROM audit_logs 
WHERE created_at < NOW() - INTERVAL '90 days'
UNION ALL
SELECT 
    'analytics_events' as table_name,
    COUNT(*) as old_records,
    MIN(created_at) as oldest_record,
    MAX(created_at) as newest_record
FROM analytics_events 
WHERE created_at < NOW() - INTERVAL '180 days'
UNION ALL
SELECT 
    'market_data_history' as table_name,
    COUNT(*) as old_records,
    MIN(timestamp) as oldest_record,
    MAX(timestamp) as newest_record
FROM market_data_history 
WHERE timestamp < NOW() - INTERVAL '1 year'
UNION ALL
SELECT 
    'refresh_tokens' as table_name,
    COUNT(*) as old_records,
    MIN(created_at) as oldest_record,
    MAX(created_at) as newest_record
FROM refresh_tokens 
WHERE expires_at < NOW() OR revoked = true;
"
echo ""

# 4. Phân tích dữ liệu test/demo
echo -e "${GREEN}[4] Phân tích dữ liệu test/demo:${NC}"
docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "
SELECT 
    'users' as table_name,
    COUNT(*) as test_records
FROM users 
WHERE email LIKE '%test%' OR email LIKE '%example%' OR email LIKE '%demo%' OR email LIKE '%@test.%'
UNION ALL
SELECT 
    'trading_orders' as table_name,
    COUNT(*) as test_records
FROM trading_orders 
WHERE status = 'test' OR source LIKE '%test%'
UNION ALL
SELECT 
    'transactions' as table_name,
    COUNT(*) as test_records
FROM transactions 
WHERE description LIKE '%test%' OR description LIKE '%demo%';
"
echo ""

# 5. Phân tích schema - bảng không có trong migrations hiện tại
echo -e "${GREEN}[5] Kiểm tra schema consistency:${NC}"
echo "Các bảng hiện có trong database:"
docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename NOT LIKE 'pg_%' 
AND tablename != 'alembic_version'
ORDER BY tablename;
"
echo ""

# 6. Tổng hợp báo cáo
echo -e "${GREEN}[6] Tổng hợp báo cáo:${NC}"
TOTAL_TABLES=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "SELECT COUNT(*) FROM pg_stat_user_tables WHERE schemaname = 'public';" | tr -d ' ')
EMPTY_TABLES=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "SELECT COUNT(*) FROM pg_stat_user_tables WHERE n_live_tup = 0;" | tr -d ' ')
TOTAL_ROWS=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "SELECT SUM(n_live_tup) FROM pg_stat_user_tables;" | tr -d ' ')

echo "Tổng số bảng: $TOTAL_TABLES"
echo "Số bảng trống: $EMPTY_TABLES"
echo "Tổng số dòng dữ liệu: $TOTAL_ROWS"
echo ""

echo -e "${GREEN}Phân tích hoàn thành!${NC}"

