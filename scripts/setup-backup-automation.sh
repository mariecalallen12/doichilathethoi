#!/bin/bash
set -e

echo "💾 Setting up Automated Backups"
echo "================================="
echo ""

BACKUP_DIR="${BACKUP_DIR:-/root/forexxx/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

# Create backup directory
mkdir -p "$BACKUP_DIR"/{postgres,redis,uploads}

# Create backup script
cat > "$BACKUP_DIR/backup-all.sh" << 'EOF'
#!/bin/bash
set -e

BACKUP_DIR="/root/forexxx/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

echo "🔄 Starting backup at $(date)"

# Backup PostgreSQL
echo "📦 Backing up PostgreSQL..."
docker exec digital_utopia_postgres pg_dump -U postgres digital_utopia | gzip > "$BACKUP_DIR/postgres/backup_${TIMESTAMP}.sql.gz"
echo "✅ PostgreSQL backup completed"

# Backup Redis
echo "📦 Backing up Redis..."
docker exec digital_utopia_redis redis-cli --rdb /backups/redis_backup_${TIMESTAMP}.rdb
docker cp digital_utopia_redis:/backups/redis_backup_${TIMESTAMP}.rdb "$BACKUP_DIR/redis/"
echo "✅ Redis backup completed"

# Backup uploads
echo "📦 Backing up uploads..."
docker run --rm \
    -v digital_utopia_backend_uploads:/data \
    -v "$BACKUP_DIR/uploads:/backup" \
    alpine tar czf /backup/uploads_${TIMESTAMP}.tar.gz -C /data .
echo "✅ Uploads backup completed"

# Cleanup old backups
echo "🧹 Cleaning up backups older than ${RETENTION_DAYS} days..."
find "$BACKUP_DIR/postgres" -name "*.sql.gz" -mtime +${RETENTION_DAYS} -delete
find "$BACKUP_DIR/redis" -name "*.rdb" -mtime +${RETENTION_DAYS} -delete
find "$BACKUP_DIR/uploads" -name "*.tar.gz" -mtime +${RETENTION_DAYS} -delete
echo "✅ Cleanup completed"

echo "✅ Backup completed at $(date)"
EOF

chmod +x "$BACKUP_DIR/backup-all.sh"

# Create restore script
cat > "$BACKUP_DIR/restore-all.sh" << 'EOF'
#!/bin/bash
set -e

BACKUP_DIR="/root/forexxx/backups"
BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_timestamp>"
    echo "Example: $0 20250109_120000"
    exit 1
fi

TIMESTAMP="$BACKUP_FILE"

echo "🔄 Restoring from backup: $TIMESTAMP"
echo "⚠️  WARNING: This will overwrite current data!"

read -p "Are you sure? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled"
    exit 1
fi

# Restore PostgreSQL
if [ -f "$BACKUP_DIR/postgres/backup_${TIMESTAMP}.sql.gz" ]; then
    echo "📦 Restoring PostgreSQL..."
    gunzip -c "$BACKUP_DIR/postgres/backup_${TIMESTAMP}.sql.gz" | \
        docker exec -i digital_utopia_postgres psql -U postgres -d digital_utopia
    echo "✅ PostgreSQL restored"
else
    echo "⚠️  PostgreSQL backup not found"
fi

# Restore Redis
if [ -f "$BACKUP_DIR/redis/redis_backup_${TIMESTAMP}.rdb" ]; then
    echo "📦 Restoring Redis..."
    docker cp "$BACKUP_DIR/redis/redis_backup_${TIMESTAMP}.rdb" digital_utopia_redis:/data/dump.rdb
    docker restart digital_utopia_redis
    echo "✅ Redis restored"
else
    echo "⚠️  Redis backup not found"
fi

# Restore uploads
if [ -f "$BACKUP_DIR/uploads/uploads_${TIMESTAMP}.tar.gz" ]; then
    echo "📦 Restoring uploads..."
    docker run --rm \
        -v digital_utopia_backend_uploads:/data \
        -v "$BACKUP_DIR/uploads:/backup" \
        alpine sh -c "cd /data && rm -rf * && tar xzf /backup/uploads_${TIMESTAMP}.tar.gz"
    echo "✅ Uploads restored"
else
    echo "⚠️  Uploads backup not found"
fi

echo "✅ Restore completed"
EOF

chmod +x "$BACKUP_DIR/restore-all.sh"

# Setup cron job
echo "⏰ Setting up cron job for daily backups at 2 AM..."
(crontab -l 2>/dev/null | grep -v "backup-all.sh"; echo "0 2 * * * $BACKUP_DIR/backup-all.sh >> $BACKUP_DIR/backup.log 2>&1") | crontab -

echo ""
echo "✅ Backup automation setup completed!"
echo ""
echo "📋 Backup location: $BACKUP_DIR"
echo "🔄 Daily backups scheduled at 2 AM"
echo "📝 Manual backup: $BACKUP_DIR/backup-all.sh"
echo "📥 Restore backup: $BACKUP_DIR/restore-all.sh <timestamp>"
echo ""

