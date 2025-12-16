#!/bin/bash
# Script backup toàn bộ dữ liệu trước khi thực hiện cleanup

set -e

BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "=========================================="
echo "BACKUP DỮ LIỆU TRƯỚC KHI CLEANUP"
echo "=========================================="
echo "Backup directory: $BACKUP_DIR"
echo ""

# Màu sắc
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Backup PostgreSQL
echo -e "${GREEN}[1] Backup PostgreSQL database...${NC}"
docker exec digital_utopia_postgres pg_dump -U postgres digital_utopia > "$BACKUP_DIR/postgres_backup.sql"
echo "✓ PostgreSQL backup completed: $BACKUP_DIR/postgres_backup.sql"
echo ""

# 2. Backup Redis
echo -e "${GREEN}[2] Backup Redis data...${NC}"
REDIS_PASSWORD="${REDIS_PASSWORD:-}"
if [ -z "$REDIS_PASSWORD" ]; then
    docker exec digital_utopia_redis redis-cli --no-auth-warning SAVE 2>&1 | grep -v "NOAUTH" || true
    docker cp digital_utopia_redis:/data/dump.rdb "$BACKUP_DIR/redis_backup.rdb" 2>&1 || echo "No Redis dump file found"
else
    docker exec digital_utopia_redis redis-cli -a "$REDIS_PASSWORD" SAVE 2>&1 | grep -v "NOAUTH" || true
    docker cp digital_utopia_redis:/data/dump.rdb "$BACKUP_DIR/redis_backup.rdb" 2>&1 || echo "No Redis dump file found"
fi
echo "✓ Redis backup completed: $BACKUP_DIR/redis_backup.rdb"
echo ""

# 3. Backup uploads
echo -e "${GREEN}[3] Backup uploads volume...${NC}"
docker run --rm -v forexxx_backend_uploads:/data -v "$(pwd)/$BACKUP_DIR":/backup alpine tar czf /backup/uploads_backup.tar.gz -C /data . 2>&1 || echo "No uploads to backup"
echo "✓ Uploads backup completed: $BACKUP_DIR/uploads_backup.tar.gz"
echo ""

# 4. Tạo báo cáo metadata
echo -e "${GREEN}[4] Tạo báo cáo metadata...${NC}"
cat > "$BACKUP_DIR/backup_metadata.txt" <<EOF
Backup Date: $(date)
PostgreSQL Database: digital_utopia
Redis Database: 0
Backup Location: $BACKUP_DIR

PostgreSQL Tables:
$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "SELECT relname as table_name, n_live_tup as row_count FROM pg_stat_user_tables ORDER BY relname;")

Redis Keys:
$(if [ -z "$REDIS_PASSWORD" ]; then docker exec digital_utopia_redis redis-cli --no-auth-warning DBSIZE 2>&1 | tail -1; else docker exec digital_utopia_redis redis-cli -a "$REDIS_PASSWORD" DBSIZE 2>&1 | tail -1; fi)
EOF
echo "✓ Metadata report created: $BACKUP_DIR/backup_metadata.txt"
echo ""

echo -e "${GREEN}Backup hoàn thành!${NC}"
echo "Backup location: $BACKUP_DIR"

