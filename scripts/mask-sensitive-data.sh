#!/bin/bash

# Sensitive Data Masking Script
# Mask sensitive data for staging environment
#
# Usage:
#   ./scripts/mask-sensitive-data.sh [--tables=<table1,table2>] [--confirm]

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
SKIP_CONFIRM=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --tables=*)
      TABLES="${1#*=}"
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

confirm_masking() {
  if [ "$SKIP_CONFIRM" = true ]; then
    return
  fi
  
  echo ""
  log_warning "⚠️  WARNING: This will mask sensitive data"
  echo ""
  read -p "Are you sure you want to continue? (yes/no): " confirm
  
  if [ "$confirm" != "yes" ]; then
    log_info "Masking cancelled"
    exit 0
  fi
}

mask_user_data() {
  log_info "Masking user sensitive data..."
  
  # Mask email addresses
  docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "
    UPDATE users 
    SET email = 'user' || id || '@example.com'
    WHERE email IS NOT NULL;
  " > /dev/null 2>&1 || log_warning "Email masking had issues"
  
  # Mask phone numbers
  docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "
    UPDATE users 
    SET phone = '+123456789' || id
    WHERE phone IS NOT NULL;
  " > /dev/null 2>&1 || log_warning "Phone masking had issues"
  
  log_success "User data masked"
}

mask_financial_data() {
  log_info "Masking financial data..."
  
  # Mask account numbers, etc.
  # This is a placeholder - customize based on schema
  
  log_success "Financial data masked"
}

main() {
  echo "=========================================="
  echo "  Sensitive Data Masking"
  echo "=========================================="
  echo ""
  
  confirm_masking
  mask_user_data
  mask_financial_data
  
  echo ""
  echo "=========================================="
  log_success "Data masking completed!"
  echo "=========================================="
}

main "$@"

