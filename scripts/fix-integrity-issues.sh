#!/bin/bash

# Fix Integrity Issues Script
# Automatically fix common data integrity issues
#
# Usage:
#   ./scripts/fix-integrity-issues.sh [--backup] [--confirm]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

CREATE_BACKUP=true
SKIP_CONFIRM=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --no-backup)
      CREATE_BACKUP=false
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

confirm_fix() {
  if [ "$SKIP_CONFIRM" = true ]; then
    return
  fi
  
  echo ""
  log_warning "⚠️  WARNING: This will fix data integrity issues"
  echo ""
  read -p "Are you sure you want to continue? (yes/no): " confirm
  
  if [ "$confirm" != "yes" ]; then
    log_info "Fix cancelled"
    exit 0
  fi
}

backup_before_fix() {
  if [ "$CREATE_BACKUP" = false ]; then
    return
  fi
  
  log_info "Creating backup before fix..."
  
  if [ -f "$PROJECT_ROOT/scripts/data-backup.sh" ]; then
    "$PROJECT_ROOT/scripts/data-backup.sh" --name="pre-integrity-fix-$(date +%Y%m%d-%H%M%S)" || {
      log_error "Backup failed"
      exit 1
    }
  else
    log_warning "Backup script not found"
  fi
}

fix_orphaned_records() {
  log_info "Fixing orphaned records..."
  
  # Fix orphaned user_profiles
  docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "
    DELETE FROM user_profiles 
    WHERE user_id NOT IN (SELECT id FROM users);
  " > /dev/null 2>&1 && log_success "Fixed orphaned user_profiles" || log_warning "No orphaned user_profiles to fix"
  
  # Add more orphaned record fixes as needed
}

fix_duplicate_records() {
  log_info "Fixing duplicate records..."
  
  # Fix duplicate emails (keep first, remove others)
  docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "
    DELETE FROM users u1
    USING users u2
    WHERE u1.id > u2.id 
    AND u1.email = u2.email 
    AND u1.email IS NOT NULL;
  " > /dev/null 2>&1 && log_success "Fixed duplicate emails" || log_warning "No duplicate emails to fix"
}

main() {
  echo "=========================================="
  echo "  Fix Integrity Issues"
  echo "=========================================="
  echo ""
  
  confirm_fix
  backup_before_fix
  fix_orphaned_records
  fix_duplicate_records
  
  echo ""
  echo "=========================================="
  log_success "Integrity issues fixed!"
  echo "=========================================="
}

main "$@"

