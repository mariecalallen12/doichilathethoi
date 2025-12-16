#!/bin/bash

# Scheduled Backup Script
# Automated scheduled backups with rotation
#
# Usage:
#   ./scripts/backup-scheduled.sh [--retention=<days>] [--type=<full|incremental>]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

RETENTION_DAYS=7
BACKUP_TYPE="full"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --retention=*)
      RETENTION_DAYS="${1#*=}"
      shift
      ;;
    --type=*)
      BACKUP_TYPE="${1#*=}"
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

run_backup() {
  log_info "Running scheduled backup..."
  log_info "Type: $BACKUP_TYPE"
  log_info "Retention: $RETENTION_DAYS days"
  
  if [ -f "$PROJECT_ROOT/scripts/data-backup.sh" ]; then
    "$PROJECT_ROOT/scripts/data-backup.sh" --name="scheduled-$(date +%Y%m%d-%H%M%S)" || {
      log_error "Backup failed"
      exit 1
    }
  else
    log_error "Backup script not found"
    exit 1
  fi
}

rotate_backups() {
  log_info "Rotating old backups (retention: $RETENTION_DAYS days)..."
  
  find "$PROJECT_ROOT/backups" -type d -name "scheduled-*" -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true
  
  log_success "Backup rotation completed"
}

main() {
  echo "=========================================="
  echo "  Scheduled Backup"
  echo "=========================================="
  echo ""
  
  run_backup
  rotate_backups
  
  echo ""
  echo "=========================================="
  log_success "Scheduled backup completed!"
  echo "=========================================="
}

main "$@"

