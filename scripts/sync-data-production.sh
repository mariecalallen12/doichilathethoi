#!/bin/bash

# Production Data Sync Script
# Controlled one-way sync of data TO production.
# This script is intentionally conservative and requires explicit confirmation.
#
# Usage:
#   ./scripts/sync-data-production.sh [--tables=<table1,table2>] [--dry-run] [--confirm]
#
# Options:
#   --tables      Specific tables to sync (comma-separated)
#   --dry-run     Show planned actions without executing
#   --confirm     Skip interactive confirmation (for automation, still logged)

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
DRY_RUN=false
SKIP_CONFIRM=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --tables=*)
      TABLES="${1#*=}"
      shift
      ;;
    --dry-run)
      DRY_RUN=true
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

log_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

confirm_sync() {
  if [ "$SKIP_CONFIRM" = true ]; then
    return
  fi

  echo ""
  log_warning "⚠️  WARNING: You are about to sync data TO PRODUCTION"
  echo ""
  echo "This operation is intended for carefully controlled cases only."
  echo "Recommended safeguards:"
  echo "  - Recent verified backup of production"
  echo "  - Change request / approval documented"
  echo "  - Sync scope clearly defined (tables/rows)"
  echo ""
  if [ -n "$TABLES" ]; then
    echo "Planned scope:"
    echo "  - Target tables: $TABLES"
  else
    echo "Planned scope:"
    echo "  - ALL eligible tables (high risk)"
  fi
  echo ""
  read -p "Type 'production-sync' to continue: " confirm_token

  if [ "$confirm_token" != "production-sync" ]; then
    log_info "Production sync cancelled"
    exit 0
  fi
}

backup_production() {
  log_info "Creating production backup snapshot before sync..."

  if [ -f "$PROJECT_ROOT/scripts/data-backup.sh" ]; then
    "$PROJECT_ROOT/scripts/data-backup.sh" --name="pre-production-sync-$(date +%Y%m%d-%H%M%S)" || {
      log_warning "Backup reported issues – review before proceeding"
    }
  else
    log_warning "Backup script not found, proceeding WITHOUT backup is not recommended"
  fi
}

plan_sync() {
  log_info "Planning production sync..."

  if [ -n "$TABLES" ]; then
    IFS=',' read -ra TABLE_ARRAY <<< "$TABLES"
    for table in "${TABLE_ARRAY[@]}"; do
      log_info "Will sync table to production: $table"
    done
  else
    log_info "Will sync all standard business tables to production"
  fi

  log_info "Source:   STAGING (or designated lower env)"
  log_info "Target:   PRODUCTION"
  log_info "Dry-run:  $DRY_RUN"
}

execute_sync() {
  if [ "$DRY_RUN" = true ]; then
    log_warning "DRY RUN MODE - No changes will be made to production"
    return
  fi

  log_info "Executing production sync..."

  # NOTE:
  # The actual implementation depends on your infrastructure (logical replication,
  # pg_dump/pg_restore, ETL, etc.). This placeholder is intentionally non-destructive
  # and should be customized by the ops team.

  if [ -n "$TABLES" ]; then
    IFS=',' read -ra TABLE_ARRAY <<< "$TABLES"
    for table in "${TABLE_ARRAY[@]}"; do
      log_info "[PLACEHOLDER] Syncing table '$table' to production (implement actual logic here)"
    done
  else
    log_info "[PLACEHOLDER] Syncing all configured tables to production (implement actual logic here)"
  fi

  log_success "Production sync placeholder completed (no data changed by default)"
}

verify_sync() {
  log_info "Verifying production sync results..."

  # Placeholder for row counts / checksum comparisons between environments.
  log_info "[PLACEHOLDER] Implement row-count and checksum comparison between staging & production"

  log_success "Sync verification step completed"
}

main() {
  echo "=========================================="
  echo "  Production Data Sync (Controlled)"
  echo "=========================================="
  echo ""

  confirm_sync
  plan_sync
  backup_production
  execute_sync
  verify_sync

  echo ""
  echo "=========================================="
  log_success "Production data sync workflow finished (see logs for details)"
  echo "=========================================="
}

main "$@"

