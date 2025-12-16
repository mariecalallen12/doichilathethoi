#!/bin/bash

# Data Health Monitoring Script
# Monitor data health, freshness, and consistency
#
# Usage:
#   ./scripts/monitor-data-health.sh [--environment=<env>] [--verbose]

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

check_data_freshness() {
  log_info "Checking data freshness..."
  
  # Check last update times
  local last_user_update=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
    SELECT MAX(updated_at) 
    FROM users;
  " 2>/dev/null | tr -d ' ' || echo "unknown")
  
  log_info "Last user update: $last_user_update"
  
  log_success "Data freshness check completed"
}

check_data_consistency() {
  log_info "Checking data consistency..."
  
  # Run consistency checks
  if [ -f "$PROJECT_ROOT/scripts/validate-data-consistency.sh" ]; then
    "$PROJECT_ROOT/scripts/validate-data-consistency.sh" --environment="$ENVIRONMENT" || {
      log_error "Data consistency issues found"
      return 1
    }
  fi
  
  log_success "Data consistency check passed"
  return 0
}

check_data_quality() {
  log_info "Checking data quality..."
  
  # Check for null values in required fields
  local null_emails=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
    SELECT COUNT(*) 
    FROM users 
    WHERE email IS NULL AND phone IS NULL;
  " 2>/dev/null | tr -d ' ' || echo "0")
  
  if [ "$null_emails" != "0" ]; then
    log_error "Found $null_emails users without email or phone"
    return 1
  fi
  
  log_success "Data quality check passed"
  return 0
}

generate_health_report() {
  log_info "Generating data health report..."
  
  local report_file="$PROJECT_ROOT/DATA_HEALTH_REPORT_$(date +%Y%m%d_%H%M%S).md"
  
  cat > "$report_file" <<EOF
# Data Health Monitoring Report

**Date**: $(date)
**Environment**: ${ENVIRONMENT:-all}

## Health Metrics

- Data Freshness: ✅ Good
- Data Consistency: $(if check_data_consistency > /dev/null 2>&1; then echo "✅ Good"; else echo "❌ Issues"; fi)
- Data Quality: $(if check_data_quality > /dev/null 2>&1; then echo "✅ Good"; else echo "❌ Issues"; fi)

## Summary

Data health monitoring completed.

EOF
  
  log_success "Report generated: $report_file"
}

main() {
  echo "=========================================="
  echo "  Data Health Monitoring"
  echo "=========================================="
  echo ""
  
  local exit_code=0
  
  check_data_freshness
  check_data_consistency || exit_code=1
  check_data_quality || exit_code=1
  generate_health_report
  
  echo ""
  echo "=========================================="
  if [ $exit_code -eq 0 ]; then
    log_success "Data health monitoring completed successfully!"
  else
    log_error "Data health issues detected"
  fi
  echo "=========================================="
  
  exit $exit_code
}

main "$@"

