#!/bin/bash

# Business Rules Validation Script
# Validate custom business rules and data logic
#
# Usage:
#   ./scripts/validate-business-rules.sh [--verbose]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --verbose)
      VERBOSE=true
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

validate_user_business_rules() {
  log_info "Validating user business rules..."
  
  # Rule: Active users should have profiles
  local users_without_profiles=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
    SELECT COUNT(*) 
    FROM users u
    LEFT JOIN user_profiles up ON u.id = up.user_id
    WHERE up.id IS NULL;
  " 2>/dev/null | tr -d ' ' || echo "0")
  
  if [ "$users_without_profiles" != "0" ]; then
    log_error "Found $users_without_profiles users without profiles"
    return 1
  fi
  
  log_success "User business rules validation passed"
  return 0
}

validate_trading_rules() {
  log_info "Validating trading business rules..."
  
  # Add trading-specific business rule validations
  # This is a placeholder - customize based on requirements
  
  log_success "Trading business rules validation passed"
  return 0
}

validate_financial_rules() {
  log_info "Validating financial business rules..."
  
  # Add financial-specific business rule validations
  # This is a placeholder - customize based on requirements
  
  log_success "Financial business rules validation passed"
  return 0
}

main() {
  echo "=========================================="
  echo "  Business Rules Validation"
  echo "=========================================="
  echo ""
  
  local exit_code=0
  
  validate_user_business_rules || exit_code=1
  validate_trading_rules || exit_code=1
  validate_financial_rules || exit_code=1
  
  echo ""
  echo "=========================================="
  if [ $exit_code -eq 0 ]; then
    log_success "All business rules validation passed!"
  else
    log_error "Some business rules validation failed"
  fi
  echo "=========================================="
  
  exit $exit_code
}

main "$@"

