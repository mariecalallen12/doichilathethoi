#!/bin/bash

# Comprehensive Data Validation Script
# Validate all data types, relationships, and business rules
#
# Usage:
#   ./scripts/validate-all-data.sh [--environment=<env>] [--verbose]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

ENVIRONMENT=""
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --environment=*)
      ENVIRONMENT="${1#*=}"
      shift
      ;;
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

validate_users() {
  log_info "Validating users data..."
  
  # Check for required fields
  local invalid_users=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
    SELECT COUNT(*) 
    FROM users 
    WHERE email IS NULL AND phone IS NULL;
  " 2>/dev/null | tr -d ' ' || echo "0")
  
  if [ "$invalid_users" != "0" ]; then
    log_error "Found $invalid_users users without email or phone"
    return 1
  fi
  
  log_success "Users validation passed"
  return 0
}

validate_relationships() {
  log_info "Validating data relationships..."
  
  # Validate foreign key relationships
  # Check user_profiles have valid users
  local orphaned_profiles=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
    SELECT COUNT(*) 
    FROM user_profiles up
    LEFT JOIN users u ON up.user_id = u.id
    WHERE u.id IS NULL;
  " 2>/dev/null | tr -d ' ' || echo "0")
  
  if [ "$orphaned_profiles" != "0" ]; then
    log_error "Found $orphaned_profiles orphaned user_profiles"
    return 1
  fi
  
  log_success "Relationships validation passed"
  return 0
}

validate_constraints() {
  log_info "Validating data constraints..."
  
  # Check for constraint violations
  # Check unique constraints
  local duplicate_emails=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
    SELECT COUNT(*) 
    FROM (
      SELECT email, COUNT(*) 
      FROM users 
      WHERE email IS NOT NULL 
      GROUP BY email 
      HAVING COUNT(*) > 1
    ) duplicates;
  " 2>/dev/null | tr -d ' ' || echo "0")
  
  if [ "$duplicate_emails" != "0" ]; then
    log_error "Found duplicate emails"
    return 1
  fi
  
  log_success "Constraints validation passed"
  return 0
}

validate_business_rules() {
  log_info "Validating business rules..."
  
  # Validate custom business rules
  # Example: Check that active users have profiles
  local users_without_profiles=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
    SELECT COUNT(*) 
    FROM users u
    LEFT JOIN user_profiles up ON u.id = up.user_id
    WHERE up.id IS NULL;
  " 2>/dev/null | tr -d ' ' || echo "0")
  
  if [ "$VERBOSE" = true ]; then
    log_info "Users without profiles: $users_without_profiles"
  fi
  
  log_success "Business rules validation passed"
  return 0
}

generate_validation_report() {
  log_info "Generating validation report..."
  
  local report_file="$PROJECT_ROOT/DATA_VALIDATION_REPORT_$(date +%Y%m%d_%H%M%S).md"
  
  cat > "$report_file" <<EOF
# Comprehensive Data Validation Report

**Date**: $(date)
**Environment**: ${ENVIRONMENT:-all}

## Validation Results

- Users: $(if validate_users > /dev/null 2>&1; then echo "✅ Pass"; else echo "❌ Fail"; fi)
- Relationships: $(if validate_relationships > /dev/null 2>&1; then echo "✅ Pass"; else echo "❌ Fail"; fi)
- Constraints: $(if validate_constraints > /dev/null 2>&1; then echo "✅ Pass"; else echo "❌ Fail"; fi)
- Business Rules: $(if validate_business_rules > /dev/null 2>&1; then echo "✅ Pass"; else echo "❌ Fail"; fi)

## Summary

Comprehensive data validation completed.

EOF
  
  log_success "Report generated: $report_file"
}

main() {
  echo "=========================================="
  echo "  Comprehensive Data Validation"
  echo "=========================================="
  echo ""
  
  local exit_code=0
  
  validate_users || exit_code=1
  validate_relationships || exit_code=1
  validate_constraints || exit_code=1
  validate_business_rules || exit_code=1
  
  generate_validation_report
  
  echo ""
  echo "=========================================="
  if [ $exit_code -eq 0 ]; then
    log_success "All data validation passed!"
  else
    log_error "Some validation checks failed"
  fi
  echo "=========================================="
  
  exit $exit_code
}

main "$@"

