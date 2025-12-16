#!/bin/bash
# Script cleanup dữ liệu unified
# Xóa duplicates, orphans, test data và optimize database

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPORT_DIR="$PROJECT_ROOT/reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$REPORT_DIR/data_cleanup_${TIMESTAMP}.md"

mkdir -p "$REPORT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$REPORT_FILE"
}

cat > "$REPORT_FILE" << EOF
# Báo Cáo Cleanup Dữ Liệu

**Ngày thực hiện:** $(date +'%Y-%m-%d %H:%M:%S')
**Script:** data-cleanup-unified.sh

---

EOF

CONTAINER="${1:-digital_utopia_postgres}"
DB_NAME="${2:-digital_utopia}"

log "Bắt đầu cleanup database: $CONTAINER/$DB_NAME"

# 1. Xóa duplicate emails (giữ record mới nhất)
log "1. Xóa duplicate emails..."
docker exec "$CONTAINER" psql -U postgres -d "$DB_NAME" << EOF | tee -a "$REPORT_FILE"
DELETE FROM users u1
USING users u2
WHERE u1.email = u2.email
AND u1.id < u2.id;
EOF

# 2. Xóa orphaned records
log "2. Xóa orphaned records..."
docker exec "$CONTAINER" psql -U postgres -d "$DB_NAME" << EOF | tee -a "$REPORT_FILE"
DELETE FROM user_profiles WHERE user_id NOT IN (SELECT id FROM users);
DELETE FROM refresh_tokens WHERE user_id NOT IN (SELECT id FROM users);
DELETE FROM wallet_balances WHERE user_id NOT IN (SELECT id FROM users);
DELETE FROM trading_orders WHERE user_id NOT IN (SELECT id FROM users);
EOF

# 3. Xóa test/demo data
log "3. Xóa test/demo data..."
docker exec "$CONTAINER" psql -U postgres -d "$DB_NAME" << EOF | tee -a "$REPORT_FILE"
DELETE FROM users WHERE email LIKE '%test%' OR email LIKE '%example%' OR email LIKE '%demo%';
EOF

# 4. Optimize database
log "4. Optimize database..."
docker exec "$CONTAINER" psql -U postgres -d "$DB_NAME" << EOF | tee -a "$REPORT_FILE"
VACUUM ANALYZE;
REINDEX DATABASE $DB_NAME;
EOF

log "Hoàn thành cleanup!"
log "Báo cáo: $REPORT_FILE"

