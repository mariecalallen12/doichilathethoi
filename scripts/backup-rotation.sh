#!/bin/bash

# Backup Rotation Script
# Rotate old backups based on retention policy
#
# Usage:
#   ./scripts/backup-rotation.sh [--retention=<days>] [--dry-run]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

RETENTION_DAYS=7
DRY_RUN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --retention=*)
      RETENTION_DAYS="${1#*=}"
      shift
      ;;
    --dry-run)
      DRY_RUN=true
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

log_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

rotate_backups() {
  log_info "Rotating backups older than $RETENTION_DAYS days..."
  
  local backup_dir="$PROJECT_ROOT/backups"
  local deleted_count=0
  
  if [ "$DRY_RUN" = true ]; then
    log_warning "DRY RUN MODE - No backups will be deleted"
  fi
  
  # Find and delete old backup directories
  while IFS= read -r backup; do
    if [ -n "$backup" ]; then
      local age=$(find "$backup" -maxdepth 0 -mtime +$RETENTION_DAYS 2>/dev/null | wc -l)
      if [ "$age" -gt 0 ]; then
        log_info "Found old backup: $(basename "$backup")"
        if [ "$DRY_RUN" = false ]; then
          rm -rf "$backup"
          deleted_count=$((deleted_count + 1))
        fi
      fi
    fi
  done < <(find "$backup_dir" -maxdepth 1 -type d ! -path "$backup_dir" 2>/dev/null)
  
  if [ "$DRY_RUN" = true ]; then
    log_info "DRY RUN: Would delete old backups"
  else
    log_success "Deleted $deleted_count old backup(s)"
  fi
}

main() {
  echo "=========================================="
  echo "  Backup Rotation"
  echo "=========================================="
  echo ""
  echo "Retention: $RETENTION_DAYS days"
  echo ""
  
  rotate_backups
  
  echo ""
  echo "=========================================="
  log_success "Backup rotation completed!"
  echo "=========================================="
}

main "$@"

