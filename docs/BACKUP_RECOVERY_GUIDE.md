# Backup & Recovery Guide

Hướng dẫn chi tiết về backup và recovery cho Digital Utopia Platform.

## Tổng Quan

Hệ thống cần backup định kỳ các thành phần sau:
- PostgreSQL database (TimescaleDB)
- Redis data (nếu có persistent data)
- Docker volumes
- Configuration files

## PostgreSQL Backup

### Manual Backup

#### 1. Full Database Backup

```bash
# Backup to file
docker exec digital_utopia_postgres pg_dump -U postgres -d digital_utopia -F c -f /backups/backup_$(date +%Y%m%d_%H%M%S).dump

# Copy backup to host
docker cp digital_utopia_postgres:/backups/backup_$(date +%Y%m%d_%H%M%S).dump ./backups/
```

#### 2. Backup Specific Tables

```bash
# Backup specific table
docker exec digital_utopia_postgres pg_dump -U postgres -d digital_utopia -t table_name -F c -f /backups/table_backup.dump
```

#### 3. Backup với Compression

```bash
docker exec digital_utopia_postgres pg_dump -U postgres -d digital_utopia -F c -Z 9 -f /backups/backup_compressed.dump
```

### Automated Backup Script

Tạo script tự động backup:

```bash
#!/bin/bash
# scripts/backup-database.sh

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.dump"

mkdir -p "$BACKUP_DIR"

# Full backup
docker exec digital_utopia_postgres pg_dump \
  -U postgres \
  -d digital_utopia \
  -F c \
  -Z 9 \
  -f "/backups/backup_$TIMESTAMP.dump"

# Copy to host
docker cp "digital_utopia_postgres:/backups/backup_$TIMESTAMP.dump" "$BACKUP_FILE"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "backup_*.dump" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
```

### Scheduled Backups với Cron

Thêm vào crontab:

```bash
# Backup daily at 2 AM
0 2 * * * /path/to/scripts/backup-database.sh

# Backup every 6 hours
0 */6 * * * /path/to/scripts/backup-database.sh
```

## PostgreSQL Restore

### Full Database Restore

```bash
# Stop services that use database
docker-compose stop backend

# Drop existing database (CẨN THẬN - mất data)
docker exec -i digital_utopia_postgres psql -U postgres -c "DROP DATABASE IF EXISTS digital_utopia;"
docker exec -i digital_utopia_postgres psql -U postgres -c "CREATE DATABASE digital_utopia;"

# Restore from backup
docker exec -i digital_utopia_postgres pg_restore \
  -U postgres \
  -d digital_utopia \
  -c \
  /backups/backup_YYYYMMDD_HHMMSS.dump

# Or from host file
docker cp ./backups/backup_YYYYMMDD_HHMMSS.dump digital_utopia_postgres:/backups/
docker exec digital_utopia_postgres pg_restore \
  -U postgres \
  -d digital_utopia \
  -c \
  /backups/backup_YYYYMMDD_HHMMSS.dump
```

### Restore Specific Tables

```bash
docker exec -i digital_utopia_postgres pg_restore \
  -U postgres \
  -d digital_utopia \
  -t table_name \
  /backups/table_backup.dump
```

### Restore Script

```bash
#!/bin/bash
# scripts/restore-database.sh

if [ -z "$1" ]; then
  echo "Usage: $0 <backup_file>"
  exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
  echo "Backup file not found: $BACKUP_FILE"
  exit 1
fi

echo "Stopping backend service..."
docker-compose stop backend

echo "Restoring database from $BACKUP_FILE..."

# Copy backup to container
docker cp "$BACKUP_FILE" digital_utopia_postgres:/backups/restore.dump

# Restore
docker exec digital_utopia_postgres pg_restore \
  -U postgres \
  -d digital_utopia \
  -c \
  --if-exists \
  /backups/restore.dump

echo "Restore completed. Starting backend..."
docker-compose start backend
```

## Redis Backup

### Manual Backup

```bash
# Save Redis data
docker exec digital_utopia_redis redis-cli --rdb /data/dump.rdb

# Copy to host
docker cp digital_utopia_redis:/data/dump.rdb ./backups/redis/dump_$(date +%Y%m%d_%H%M%S).rdb
```

### Automated Redis Backup

```bash
#!/bin/bash
# scripts/backup-redis.sh

BACKUP_DIR="./backups/redis"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

docker exec digital_utopia_redis redis-cli SAVE
docker cp digital_utopia_redis:/data/dump.rdb "$BACKUP_DIR/dump_$TIMESTAMP.rdb"

# Keep only last 7 days
find "$BACKUP_DIR" -name "dump_*.rdb" -mtime +7 -delete

echo "Redis backup completed: $BACKUP_DIR/dump_$TIMESTAMP.rdb"
```

## Redis Restore

```bash
# Stop Redis
docker-compose stop redis

# Copy backup to container
docker cp ./backups/redis/dump_YYYYMMDD_HHMMSS.rdb digital_utopia_redis:/data/dump.rdb

# Start Redis
docker-compose start redis
```

## Docker Volumes Backup

### Backup All Volumes

```bash
#!/bin/bash
# scripts/backup-volumes.sh

BACKUP_DIR="./backups/volumes"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

# Backup postgres volume
docker run --rm \
  -v digital_utopia_postgres_data:/data \
  -v "$(pwd)/$BACKUP_DIR":/backup \
  alpine tar czf /backup/postgres_data_$TIMESTAMP.tar.gz /data

# Backup redis volume
docker run --rm \
  -v digital_utopia_redis_data:/data \
  -v "$(pwd)/$BACKUP_DIR":/backup \
  alpine tar czf /backup/redis_data_$TIMESTAMP.tar.gz /data

# Backup backend uploads
docker run --rm \
  -v digital_utopia_backend_uploads:/data \
  -v "$(pwd)/$BACKUP_DIR":/backup \
  alpine tar czf /backup/backend_uploads_$TIMESTAMP.tar.gz /data

echo "Volumes backup completed"
```

## Configuration Backup

```bash
# Backup configuration files
tar czf backups/config_$(date +%Y%m%d_%H%M%S).tar.gz \
  .env.production \
  docker-compose.yml \
  docker-compose.prod.yml \
  nginx/nginx.conf
```

## Disaster Recovery Plan

### Scenario 1: Database Corruption

1. **Stop affected services:**
   ```bash
   docker-compose stop backend
   ```

2. **Restore from latest backup:**
   ```bash
   ./scripts/restore-database.sh ./backups/backup_YYYYMMDD_HHMMSS.dump
   ```

3. **Verify data integrity:**
   ```bash
   docker-compose exec backend python -c "from app.db.session import check_db_connection; print(check_db_connection())"
   ```

4. **Start services:**
   ```bash
   docker-compose start backend
   ```

### Scenario 2: Complete System Failure

1. **Restore Docker volumes:**
   ```bash
   docker run --rm \
     -v digital_utopia_postgres_data:/data \
     -v "$(pwd)/backups/volumes":/backup \
     alpine sh -c "cd /data && tar xzf /backup/postgres_data_YYYYMMDD_HHMMSS.tar.gz"
   ```

2. **Restore database:**
   ```bash
   ./scripts/restore-database.sh ./backups/backup_YYYYMMDD_HHMMSS.dump
   ```

3. **Restore Redis:**
   ```bash
   docker cp ./backups/redis/dump_YYYYMMDD_HHMMSS.rdb digital_utopia_redis:/data/dump.rdb
   ```

4. **Start all services:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

### Scenario 3: Data Loss (Accidental Deletion)

1. **Identify affected tables/data**
2. **Restore specific tables from backup:**
   ```bash
   docker exec -i digital_utopia_postgres pg_restore \
     -U postgres \
     -d digital_utopia \
     -t affected_table \
     /backups/backup_YYYYMMDD_HHMMSS.dump
   ```

## Backup Verification

### Verify Backup File

```bash
# Check backup file integrity
docker exec digital_utopia_postgres pg_restore --list /backups/backup_YYYYMMDD_HHMMSS.dump

# Test restore to temporary database
docker exec -i digital_utopia_postgres psql -U postgres -c "CREATE DATABASE test_restore;"
docker exec digital_utopia_postgres pg_restore \
  -U postgres \
  -d test_restore \
  /backups/backup_YYYYMMDD_HHMMSS.dump
docker exec -i digital_utopia_postgres psql -U postgres -c "DROP DATABASE test_restore;"
```

## Backup Retention Policy

- **Daily backups:** Keep for 7 days
- **Weekly backups:** Keep for 4 weeks
- **Monthly backups:** Keep for 12 months

## Monitoring Backups

### Check Backup Status

```bash
# List all backups
ls -lh ./backups/

# Check backup sizes
du -sh ./backups/*

# Verify latest backup
ls -lt ./backups/ | head -5
```

### Alert on Backup Failure

Thêm vào backup script:

```bash
if [ $? -ne 0 ]; then
  echo "Backup failed!" | mail -s "Backup Alert" admin@example.com
  exit 1
fi
```

## Best Practices

1. **Automate backups:** Use cron jobs for scheduled backups
2. **Test restores:** Regularly test restore procedures
3. **Off-site storage:** Store backups in separate location
4. **Encryption:** Encrypt sensitive backups
5. **Documentation:** Keep detailed records of backup/restore procedures
6. **Monitoring:** Monitor backup success/failure
7. **Retention:** Follow retention policy strictly

## Backup Scripts Location

All backup scripts should be in `scripts/` directory:
- `scripts/backup-database.sh` - PostgreSQL backup
- `scripts/backup-redis.sh` - Redis backup
- `scripts/backup-volumes.sh` - Docker volumes backup
- `scripts/restore-database.sh` - Database restore
- `scripts/verify-backup.sh` - Backup verification

## Emergency Contacts

- **Database Admin:** [Contact Info]
- **DevOps Team:** [Contact Info]
- **On-call Engineer:** [Contact Info]

