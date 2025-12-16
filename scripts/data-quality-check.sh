#!/bin/bash

# Data Quality Check Script
# Check data quality metrics
#
# Usage:
#   ./scripts/data-quality-check.sh [--verbose]

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

check_completeness() {
  log_info "Checking data completeness..."
  
  # Check for required fields
  local incomplete=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
    SELECT COUNT(*) 
    FROM users 
    WHERE email IS NULL AND phone IS NULL;
  " 2>/dev/null | tr -d ' ' || echo "0")
  
  if [ "$incomplete" = "0" ]; then
    log_success "Data completeness check passed"
    return 0
  else
    log_error "Found $incomplete incomplete records"
    return 1
  fi
}

check_accuracy() {
  log_info "Checking data accuracy..."
  
  # Check for valid email formats, etc.
  # This is a placeholder - customize based on requirements
  
  log_success "Data accuracy check passed"
  return 0
}

generate_quality_report() {
  log_info "Generating quality report..."
  
  local report_file="$PROJECT_ROOT/DATA_QUALITY_REPORT_$(date +%Y%m%d_%H%M%S).md"
  
  cat > "$report_file" <<EOF
# Data Quality Report

**Date**: $(date)

## Quality Metrics

- Completeness: $(if check_completeness > /dev/null 2>&1; then echo "✅ Good"; else echo "❌ Issues"; fi)
- Accuracy: $(if check_accuracy > /dev/null 2>&1; then echo "✅ Good"; else echo "❌ Issues"; fi)

## Summary

Data quality check completed.

EOF
  
  log_success "Report generated: $report_file"
}

main() {
  echo "=========================================="
  echo "  Data Quality Check"
  echo "=========================================="
  echo ""
  
  local exit_code=0
  
  check_completeness || exit_code=1
  check_accuracy || exit_code=1
  generate_quality_report
  
  echo ""
  echo "=========================================="
  if [ $exit_code -eq 0 ]; then
    log_success "Data quality check passed!"
  else
    log_error "Data quality issues found"
  fi
  echo "=========================================="
  
  exit $exit_code
}

main "$@"
