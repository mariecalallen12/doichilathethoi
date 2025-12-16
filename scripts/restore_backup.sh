#!/bin/bash
# Restore backup script for CMEETRADING platform
# Usage: ./restore_backup.sh <backup_file> [target_database]

set -e

BACKUP_FILE=${1:-}
TARGET_DB=${2:-digital_utopia}

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file> [target_database]"
    echo "Example: $0 /root/backups/cmeetrading/database_20251210_061909.sql.gz digital_utopia"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "=========================================="
echo "CMEETRADING - Database Restore"
echo "=========================================="
echo ""
echo "Backup file: $BACKUP_FILE"
echo "Target database: $TARGET_DB"
echo ""
read -p "This will overwrite the target database. Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo ""
echo "Restoring database..."

# Restore from backup
gunzip -c "$BACKUP_FILE" | docker exec -i digital_utopia_postgres psql -U postgres "$TARGET_DB"

echo ""
echo "✅ Database restored successfully!"
echo ""
echo "Verifying restore..."

# Verify restore
USER_COUNT=$(docker exec digital_utopia_postgres psql -U postgres -d "$TARGET_DB" -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | xargs)
TABLE_COUNT=$(docker exec digital_utopia_postgres psql -U postgres -d "$TARGET_DB" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | xargs)

echo "Users in database: $USER_COUNT"
echo "Tables in database: $TABLE_COUNT"
echo ""
echo "✅ Restore verification complete!"
