#!/bin/bash

# Backup Restoration Script
# Restore data from backup
#
# Usage:
#   ./scripts/restore-backup.sh [--backup-dir=<dir>] [--confirm] [--components=<postgres,redis,uploads>]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

BACKUP_DIR=""
SKIP_CONFIRM=false
COMPONENTS="postgres,redis,uploads"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --backup-dir=*)
      BACKUP_DIR="${1#*=}"
      shift
      ;;
    --confirm)
      SKIP_CONFIRM=true
      shift
      ;;
    --components=*)
      COMPONENTS="${1#*=}"
      shift
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

confirm_restore() {
  if [ "$SKIP_CONFIRM" = true ]; then
    return
  fi
    
  echo ""
  log_warning "⚠️  WARNING: This will RESTORE data from backup"
  echo ""
  echo "This will:"
  echo "  - Replace current data with backup data"
  echo "  - Components: $COMPONENTS"
  echo ""
  read -p "Are you sure you want to continue? (yes/no): " confirm
  
  if [ "$confirm" != "yes" ]; then
    log_info "Restore cancelled"
    exit 0
  fi
}

find_latest_backup() {
  if [ -z "$BACKUP_DIR" ]; then
    BACKUP_DIR=$(ls -td "$PROJECT_ROOT/backups"/*/ 2>/dev/null | head -1)
    if [ -z "$BACKUP_DIR" ]; then
      log_error "No backup directory found"
      exit 1
    fi
  fi
  
  log_info "Using backup directory: $BACKUP_DIR"
  
  if [ ! -d "$BACKUP_DIR" ]; then
    log_error "Backup directory does not exist: $BACKUP_DIR"
    exit 1
  fi
}

backup_before_restore() {
  log_info "Creating backup before restore..."
  
  if [ -f "$PROJECT_ROOT/scripts/data-backup.sh" ]; then
    "$PROJECT_ROOT/scripts/data-backup.sh" --name="pre-restore-$(date +%Y%m%d-%H%M%S)" || {
      log_error "Pre-restore backup failed"
      exit 1
    }
  else
    log_warning "Backup script not found, continuing without pre-restore backup"
  fi
}

restore_postgres() {
  if [[ "$COMPONENTS" != *"postgres"* ]]; then
    return
  fi
  
  log_info "Restoring PostgreSQL database..."
  
  if [ ! -f "$BACKUP_DIR/postgres_backup.sql" ]; then
    log_error "PostgreSQL backup file not found"
    return 1
  fi
  
  # Drop and recreate database (or use --clean)
  docker exec -i digital_utopia_postgres psql -U postgres -d digital_utopia < "$BACKUP_DIR/postgres_backup.sql" || {
    log_error "PostgreSQL restore failed"
    return 1
  }
  
  log_success "PostgreSQL restore completed"
}

restore_redis() {
  if [[ "$COMPONENTS" != *"redis"* ]]; then
    return
  fi
  
  log_info "Restoring Redis data..."
  
  if [ ! -f "$BACKUP_DIR/redis_backup.rdb" ]; then
    log_warning "Redis backup file not found, skipping"
    return 0
  fi
  
  # Stop Redis, copy backup, restart
  docker stop digital_utopia_redis > /dev/null 2>&1 || true
  docker cp "$BACKUP_DIR/redis_backup.rdb" digital_utopia_redis:/data/dump.rdb || {
    log_warning "Redis restore had issues"
  }
  docker start digital_utopia_redis > /dev/null 2>&1 || true
  
  log_success "Redis restore completed"
}

restore_uploads() {
  if [[ "$COMPONENTS" != *"uploads"* ]]; then
    return
  fi
  
  log_info "Restoring uploads..."
  
  if [ ! -f "$BACKUP_DIR/uploads_backup.tar.gz" ]; then
    log_warning "Uploads backup file not found, skipping"
    return 0
  fi
  
  docker run --rm -v forexxx_backend_uploads:/data -v "$BACKUP_DIR":/backup alpine sh -c "cd /data && rm -rf * && tar xzf /backup/uploads_backup.tar.gz" || {
    log_warning "Uploads restore had issues"
  }
  
  log_success "Uploads restore completed"
}

verify_restore() {
  log_info "Verifying restore..."
  
  # Check database connectivity
  if docker exec digital_utopia_postgres pg_isready -U postgres > /dev/null 2>&1; then
    log_success "Database is accessible after restore"
  else
    log_error "Database is not accessible after restore"
    return 1
  fi
}

main() {
  echo "=========================================="
  echo "  Backup Restoration"
  echo "=========================================="
  echo ""
  
  confirm_restore
  find_latest_backup
  backup_before_restore
  restore_postgres
  restore_redis
  restore_uploads
  verify_restore
  
  echo ""
  echo "=========================================="
  log_success "Backup restoration completed!"
  echo "=========================================="
}

main "$@"

