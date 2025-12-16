#!/bin/bash

# Data Cleansing Script
# Cleanse data: remove duplicates, normalize, etc.
#
# Usage:
#   ./scripts/cleanse-data.sh [--backup] [--confirm]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

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

confirm_cleansing() {
  if [ "$SKIP_CONFIRM" = true ]; then
    return
  fi
  
  echo ""
  log_warning "⚠️  WARNING: This will cleanse data"
  echo ""
  read -p "Are you sure you want to continue? (yes/no): " confirm
  
  if [ "$confirm" != "yes" ]; then
    log_info "Cleansing cancelled"
    exit 0
  fi
}

backup_before_cleansing() {
  if [ "$CREATE_BACKUP" = false ]; then
    return
  fi
  
  log_info "Creating backup before cleansing..."
  
  if [ -f "$PROJECT_ROOT/scripts/data-backup.sh" ]; then
    "$PROJECT_ROOT/scripts/data-backup.sh" --name="pre-cleansing-$(date +%Y%m%d-%H%M%S)" || {
      log_error "Backup failed"
      exit 1
    }
  fi
}

remove_duplicates() {
  log_info "Removing duplicate records..."
  
  # Remove duplicate emails (keep first)
  docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "
    DELETE FROM users u1
    USING users u2
    WHERE u1.id > u2.id 
    AND u1.email = u2.email 
    AND u1.email IS NOT NULL;
  " > /dev/null 2>&1 && log_success "Duplicates removed" || log_info "No duplicates found"
}

normalize_data() {
  log_info "Normalizing data..."
  
  # Normalize email addresses (lowercase)
  docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "
    UPDATE users 
    SET email = LOWER(email)
    WHERE email IS NOT NULL;
  " > /dev/null 2>&1 && log_success "Data normalized" || log_warning "Normalization had issues"
}

main() {
  echo "=========================================="
  echo "  Data Cleansing"
  echo "=========================================="
  echo ""
  
  confirm_cleansing
  backup_before_cleansing
  remove_duplicates
  normalize_data
  
  echo ""
  echo "=========================================="
  log_success "Data cleansing completed!"
  echo "=========================================="
}

main "$@"

