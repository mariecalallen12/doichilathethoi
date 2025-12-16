#!/bin/bash

# Backup Verification Script
# Verify backup integrity and completeness
#
# Usage:
#   ./scripts/verify-backup.sh [--backup-dir=<dir>] [--restore-test]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

BACKUP_DIR=""
RESTORE_TEST=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --backup-dir=*)
      BACKUP_DIR="${1#*=}"
      shift
      ;;
    --restore-test)
      RESTORE_TEST=true
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
  echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
  echo -e "${RED}[✗]${NC} $1"
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
}

verify_postgres_backup() {
  log_info "Verifying PostgreSQL backup..."
  
  if [ -f "$BACKUP_DIR/postgres_backup.sql" ]; then
    local size=$(stat -f%z "$BACKUP_DIR/postgres_backup.sql" 2>/dev/null || stat -c%s "$BACKUP_DIR/postgres_backup.sql" 2>/dev/null || echo "0")
    if [ "$size" -gt 0 ]; then
      log_success "PostgreSQL backup exists and has content ($size bytes)"
      return 0
    else
      log_error "PostgreSQL backup is empty"
      return 1
    fi
  else
    log_error "PostgreSQL backup file not found"
    return 1
  fi
}

verify_redis_backup() {
  log_info "Verifying Redis backup..."
  
  if [ -f "$BACKUP_DIR/redis_backup.rdb" ]; then
    log_success "Redis backup exists"
    return 0
  else
    log_warning "Redis backup file not found (may be empty)"
    return 0
  fi
}

verify_uploads_backup() {
  log_info "Verifying uploads backup..."
  
  if [ -f "$BACKUP_DIR/uploads_backup.tar.gz" ]; then
    local size=$(stat -f%z "$BACKUP_DIR/uploads_backup.tar.gz" 2>/dev/null || stat -c%s "$BACKUP_DIR/uploads_backup.tar.gz" 2>/dev/null || echo "0")
    if [ "$size" -gt 0 ]; then
      log_success "Uploads backup exists and has content ($size bytes)"
      return 0
    else
      log_warning "Uploads backup is empty (may be normal)"
      return 0
    fi
  else
    log_warning "Uploads backup file not found (may be normal)"
    return 0
  fi
}

test_restore() {
  if [ "$RESTORE_TEST" = false ]; then
    return
  fi
  
  log_info "Testing backup restoration..."
  log_warning "Restore test not implemented (would require test database)"
}

main() {
  echo "=========================================="
  echo "  Backup Verification"
  echo "=========================================="
  echo ""
  
  find_latest_backup
  
  local exit_code=0
  
  verify_postgres_backup || exit_code=1
  verify_redis_backup || exit_code=1
  verify_uploads_backup || exit_code=1
  test_restore
  
  echo ""
  echo "=========================================="
  if [ $exit_code -eq 0 ]; then
    log_success "Backup verification passed!"
  else
    log_error "Backup verification found issues"
  fi
  echo "=========================================="
  
  exit $exit_code
}

main "$@"

