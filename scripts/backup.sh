#!/bin/bash
# Backup script for CMEETRADING platform

BACKUP_DIR="/root/backups/cmeetrading"
DATE=$(date +%Y%m%d_%H%M%S)

echo "Starting backup at $(date)"
mkdir -p "$BACKUP_DIR"

# Backup database
echo "Backing up PostgreSQL database..."
docker exec digital_utopia_postgres pg_dump -U postgres digital_utopia | \
  gzip > "$BACKUP_DIR/database_$DATE.sql.gz"
echo "✅ Database backed up: database_$DATE.sql.gz"

# Backup Redis
echo "Backing up Redis..."
docker exec digital_utopia_redis redis-cli SAVE
docker cp digital_utopia_redis:/data/dump.rdb "$BACKUP_DIR/redis_$DATE.rdb"
echo "✅ Redis backed up: redis_$DATE.rdb"

# Backup uploaded files (if exists)
if [ -d "/root/forexxx/uploads" ]; then
  echo "Backing up uploaded files..."
  tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" -C /root/forexxx uploads/
  echo "✅ Uploads backed up: uploads_$DATE.tar.gz"
fi

# Backup configuration files
echo "Backing up configuration..."
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" \
  /root/forexxx/.env \
  /root/forexxx/docker-compose.yml \
  /root/forexxx/nginx/nginx.conf 2>/dev/null
echo "✅ Config backed up: config_$DATE.tar.gz"

# Show backup summary
echo ""
echo "=== Backup Summary ==="
ls -lh "$BACKUP_DIR" | grep "$DATE"
echo "=== Backup completed at $(date) ==="
