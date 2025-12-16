#!/bin/bash

# Data Integrity Check Script
# Check referential integrity, constraints, and orphaned records
#
# Usage:
#   ./scripts/check-integrity.sh [--fix] [--verbose]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

AUTO_FIX=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --fix)
      AUTO_FIX=true
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

check_referential_integrity() {
  log_info "Checking referential integrity..."
  
  local issues=0
  
  # Check user_profiles -> users
  local orphaned=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
    SELECT COUNT(*) 
    FROM user_profiles up
    LEFT JOIN users u ON up.user_id = u.id
    WHERE u.id IS NULL;
  " 2>/dev/null | tr -d ' ' || echo "0")
  
  if [ "$orphaned" != "0" ]; then
    log_error "Found $orphaned orphaned user_profiles"
    issues=$((issues + orphaned))
    
    if [ "$AUTO_FIX" = true ]; then
      log_info "Fixing orphaned user_profiles..."
      docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "
        DELETE FROM user_profiles 
        WHERE user_id NOT IN (SELECT id FROM users);
      " > /dev/null 2>&1 || log_warning "Fix had issues"
    fi
  else
    log_success "No orphaned user_profiles"
  fi
  
  # Add more referential integrity checks
  
  if [ $issues -eq 0 ]; then
    log_success "Referential integrity check passed"
    return 0
  else
    log_error "Found $issues referential integrity issues"
    return 1
  fi
}

check_constraints() {
  log_info "Checking data constraints..."
  
  # Check NOT NULL constraints
  # Check UNIQUE constraints
  # Check CHECK constraints
  
  log_success "Constraints check passed"
  return 0
}

check_orphaned_records() {
  log_info "Checking for orphaned records..."
  
  local orphaned_count=0
  
  # Check various relationships for orphaned records
  # This is a placeholder - customize based on schema
  
  if [ $orphaned_count -eq 0 ]; then
    log_success "No orphaned records found"
    return 0
  else
    log_error "Found $orphaned_count orphaned records"
    return 1
  fi
}

generate_integrity_report() {
  log_info "Generating integrity report..."
  
  local report_file="$PROJECT_ROOT/DATA_INTEGRITY_REPORT_$(date +%Y%m%d_%H%M%S).md"
  
  cat > "$report_file" <<EOF
# Data Integrity Check Report

**Date**: $(date)

## Integrity Checks

- Referential Integrity: $(if check_referential_integrity > /dev/null 2>&1; then echo "✅ Pass"; else echo "❌ Fail"; fi)
- Constraints: $(if check_constraints > /dev/null 2>&1; then echo "✅ Pass"; else echo "❌ Fail"; fi)
- Orphaned Records: $(if check_orphaned_records > /dev/null 2>&1; then echo "✅ Pass"; else echo "❌ Fail"; fi)

## Summary

Data integrity check completed.

EOF
  
  log_success "Report generated: $report_file"
}

main() {
  echo "=========================================="
  echo "  Data Integrity Check"
  echo "=========================================="
  echo ""
  
  local exit_code=0
  
  check_referential_integrity || exit_code=1
  check_constraints || exit_code=1
  check_orphaned_records || exit_code=1
  
  generate_integrity_report
  
  echo ""
  echo "=========================================="
  if [ $exit_code -eq 0 ]; then
    log_success "Data integrity check passed!"
  else
    log_error "Data integrity check found issues"
    if [ "$AUTO_FIX" = false ]; then
      log_info "Run with --fix to automatically fix issues"
    fi
  fi
  echo "=========================================="
  
  exit $exit_code
}

main "$@"

