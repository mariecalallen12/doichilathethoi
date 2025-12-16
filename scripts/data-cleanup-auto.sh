#!/bin/bash
# Script dọn dẹp dữ liệu tự động (không cần xác nhận) - dùng cho CI/CD

set -e

echo "=========================================="
echo "DỌN DẸP DỮ LIỆU TỰ ĐỘNG"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Xóa dữ liệu test trong PostgreSQL
echo -e "${GREEN}[1] Xóa dữ liệu test trong PostgreSQL...${NC}"
docker exec digital_utopia_postgres psql -U postgres -d digital_utopia <<EOF
-- Xóa users test (nếu có)
DELETE FROM users WHERE email LIKE '%test%' OR email LIKE '%example%' OR email LIKE '%demo%' OR email LIKE '%@test.%';

-- Xóa trading orders test
DELETE FROM trading_orders WHERE status = 'test' OR source LIKE '%test%';

-- Xóa transactions test
DELETE FROM transactions WHERE description LIKE '%test%' OR description LIKE '%demo%';

-- Xóa refresh tokens đã hết hạn
DELETE FROM refresh_tokens WHERE expires_at < NOW() OR revoked = true;

-- Xóa audit logs cũ hơn 90 ngày (giữ lại logs quan trọng)
DELETE FROM audit_logs WHERE created_at < NOW() - INTERVAL '90 days' AND severity = 'info';

-- Xóa analytics events cũ hơn 180 ngày
DELETE FROM analytics_events WHERE created_at < NOW() - INTERVAL '180 days';

-- Xóa market data history cũ hơn 1 năm (giữ lại dữ liệu gần đây)
DELETE FROM market_data_history WHERE timestamp < NOW() - INTERVAL '1 year';

-- Cleanup orphaned records
DELETE FROM refresh_tokens WHERE user_id NOT IN (SELECT id FROM users);
DELETE FROM user_profiles WHERE user_id NOT IN (SELECT id FROM users);
DELETE FROM wallet_balances WHERE user_id NOT IN (SELECT id FROM users);
DELETE FROM transactions WHERE user_id NOT IN (SELECT id FROM users);
DELETE FROM trading_orders WHERE user_id NOT IN (SELECT id FROM users);
DELETE FROM portfolio_positions WHERE user_id NOT IN (SELECT id FROM users);
DELETE FROM kyc_documents WHERE user_id NOT IN (SELECT id FROM users);
DELETE FROM compliance_events WHERE user_id IS NOT NULL AND user_id NOT IN (SELECT id FROM users);
DELETE FROM risk_assessments WHERE user_id NOT IN (SELECT id FROM users);
DELETE FROM aml_screenings WHERE user_id NOT IN (SELECT id FROM users);
DELETE FROM trading_bots WHERE user_id NOT IN (SELECT id FROM users);
DELETE FROM watchlists WHERE user_id NOT IN (SELECT id FROM users);
DELETE FROM referral_registrations WHERE referred_user_id NOT IN (SELECT id FROM users);
DELETE FROM referral_registrations WHERE referral_code_id NOT IN (SELECT id FROM referral_codes);
DELETE FROM referral_codes WHERE staff_id NOT IN (SELECT id FROM users);
DELETE FROM iceberg_orders WHERE user_id NOT IN (SELECT id FROM users);
DELETE FROM oco_orders WHERE user_id NOT IN (SELECT id FROM users);
DELETE FROM trailing_stop_orders WHERE user_id NOT IN (SELECT id FROM users);
DELETE FROM audit_logs WHERE user_id IS NOT NULL AND user_id NOT IN (SELECT id FROM users);
DELETE FROM analytics_events WHERE user_id IS NOT NULL AND user_id NOT IN (SELECT id FROM users);

-- Cleanup foreign key orphans
DELETE FROM iceberg_orders WHERE parent_order_id IS NOT NULL AND parent_order_id NOT IN (SELECT id FROM trading_orders);
DELETE FROM oco_orders WHERE primary_order_id IS NOT NULL AND primary_order_id NOT IN (SELECT id FROM trading_orders);
DELETE FROM oco_orders WHERE secondary_order_id IS NOT NULL AND secondary_order_id NOT IN (SELECT id FROM trading_orders);
DELETE FROM trailing_stop_orders WHERE parent_order_id IS NOT NULL AND parent_order_id NOT IN (SELECT id FROM trading_orders);

VACUUM ANALYZE;
EOF
echo "✓ PostgreSQL cleanup completed"
echo ""

# 2. Xóa cache dư thừa trong Redis
echo -e "${GREEN}[2] Xóa cache dư thừa trong Redis...${NC}"
REDIS_PASSWORD="${REDIS_PASSWORD:-}"
if [ -z "$REDIS_PASSWORD" ]; then
    # Xóa các key cache cũ (nếu có pattern)
    docker exec digital_utopia_redis redis-cli --no-auth-warning --scan --pattern "cache:*" 2>&1 | grep -v "NOAUTH" | xargs -r docker exec digital_utopia_redis redis-cli --no-auth-warning DEL 2>&1 || true
    # Xóa session cũ (nếu có)
    docker exec digital_utopia_redis redis-cli --no-auth-warning --scan --pattern "session:*" 2>&1 | grep -v "NOAUTH" | xargs -r docker exec digital_utopia_redis redis-cli --no-auth-warning DEL 2>&1 || true
else
    docker exec digital_utopia_redis redis-cli -a "$REDIS_PASSWORD" --scan --pattern "cache:*" | xargs -r docker exec digital_utopia_redis redis-cli -a "$REDIS_PASSWORD" DEL 2>&1 || true
    docker exec digital_utopia_redis redis-cli -a "$REDIS_PASSWORD" --scan --pattern "session:*" | xargs -r docker exec digital_utopia_redis redis-cli -a "$REDIS_PASSWORD" DEL 2>&1 || true
fi
echo "✓ Redis cleanup completed"
echo ""

# 3. Xóa file uploads test/cũ
echo -e "${GREEN}[3] Xóa file uploads test/cũ...${NC}"
docker exec digital_utopia_backend find /app/uploads -type f -mtime +365 -delete 2>&1 || true
echo "✓ Uploads cleanup completed"
echo ""

# 4. Reindex và optimize database
echo -e "${GREEN}[4] Tối ưu hóa database...${NC}"
docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "REINDEX DATABASE digital_utopia;" 2>&1 || true
docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "VACUUM FULL ANALYZE;" 2>&1 || true
echo "✓ Database optimization completed"
echo ""

echo -e "${GREEN}Cleanup tự động hoàn thành!${NC}"

