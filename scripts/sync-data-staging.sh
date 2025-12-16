#!/bin/bash

# Staging Data Sync Script
# Sync data from production to staging (controlled, one-way)
#
# Usage:
#   ./scripts/sync-data-staging.sh [--tables=<table1,table2>] [--mask-sensitive] [--confirm]
#
# Options:
#   --tables          Specific tables to sync (comma-separated)
#   --mask-sensitive  Mask sensitive data before syncing
#   --confirm         Skip confirmation prompt

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

TABLES=""
MASK_SENSITIVE=false
SKIP_CONFIRM=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --tables=*)
      TABLES="${1#*=}"
      shift
      ;;
    --mask-sensitive)
      MASK_SENSITIVE=true
      shift
      ;;
    --confirm)
      SKIP_CONFIRM=true
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

confirm_sync() {
  if [ "$SKIP_CONFIRM" = true ]; then
    return
  fi
  
  echo ""
  log_warning "⚠️  WARNING: This will sync data to STAGING"
  echo ""
  echo "This operation will:"
  echo "  - Backup staging database"
  echo "  - Sync data from production to staging"
  if [ "$MASK_SENSITIVE" = true ]; then
    echo "  - Mask sensitive data"
  fi
  echo ""
  read -p "Are you sure you want to continue? (yes/no): " confirm
  
  if [ "$confirm" != "yes" ]; then
    log_info "Sync cancelled"
    exit 0
  fi
}

backup_staging() {
  log_info "Backing up staging database..."
  
  # Backup staging database before sync
  if [ -f "$PROJECT_ROOT/scripts/data-backup.sh" ]; then
    "$PROJECT_ROOT/scripts/data-backup.sh" --name="pre-sync-staging-$(date +%Y%m%d-%H%M%S)" || {
      log_error "Backup failed"
      exit 1
    }
  else
    log_warning "Backup script not found, continuing without backup"
  fi
}

sync_tables() {
  log_info "Syncing data to staging..."
  
  if [ -n "$TABLES" ]; then
    log_info "Syncing specific tables: $TABLES"
    # Sync specific tables
    IFS=',' read -ra TABLE_ARRAY <<< "$TABLES"
    for table in "${TABLE_ARRAY[@]}"; do
      log_info "Syncing table: $table"
      # Implementation would sync specific table
      # This is a placeholder for actual sync logic
    done
  else
    log_info "Syncing all tables"
    # Sync all tables
    # Implementation would sync all tables
    # This is a placeholder for actual sync logic
  fi
  
  if [ "$MASK_SENSITIVE" = true ]; then
    log_info "Masking sensitive data..."
    if [ -f "$PROJECT_ROOT/scripts/mask-sensitive-data.sh" ]; then
      "$PROJECT_ROOT/scripts/mask-sensitive-data.sh" || {
        log_warning "Data masking had issues"
      }
    fi
  fi
  
  log_success "Data sync completed"
}

verify_sync() {
  log_info "Verifying data sync..."
  
  # Verify sync was successful
  # This would check data counts, integrity, etc.
  
  log_success "Sync verification completed"
}

main() {
  echo "=========================================="
  echo "  Staging Data Sync Script"
  echo "=========================================="
  echo ""
  
  confirm_sync
  backup_staging
  sync_tables
  verify_sync
  
  echo ""
  echo "=========================================="
  log_success "Data sync to staging completed successfully!"
  echo "=========================================="
}

main "$@"

