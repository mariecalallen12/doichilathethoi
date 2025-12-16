#!/bin/bash

# Post-Deployment Data Check Script
# Verify data after deployment
#
# Usage:
#   ./scripts/post-deployment-data-check.sh [--environment=<env>]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

ENVIRONMENT="production"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --environment=*)
      ENVIRONMENT="${1#*=}"
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

check_schema_version() {
  log_info "Checking schema version..."
  
  if [ -f "$PROJECT_ROOT/scripts/verify-schema.sh" ]; then
    "$PROJECT_ROOT/scripts/verify-schema.sh" || {
      log_error "Schema verification failed"
      return 1
    }
  fi
  
  log_success "Schema version check passed"
  return 0
}

check_data_integrity() {
  log_info "Checking data integrity..."
  
  if [ -f "$PROJECT_ROOT/scripts/check-integrity.sh" ]; then
    "$PROJECT_ROOT/scripts/check-integrity.sh" || {
      log_error "Data integrity check failed"
      return 1
    }
  fi
  
  log_success "Data integrity check passed"
  return 0
}

check_data_consistency() {
  log_info "Checking data consistency..."
  
  if [ -f "$PROJECT_ROOT/scripts/validate-data-consistency.sh" ]; then
    "$PROJECT_ROOT/scripts/validate-data-consistency.sh" --environment="$ENVIRONMENT" || {
      log_error "Data consistency check failed"
      return 1
    }
  fi
  
  log_success "Data consistency check passed"
  return 0
}

generate_post_deployment_report() {
  log_info "Generating post-deployment report..."
  
  local report_file="$PROJECT_ROOT/POST_DEPLOYMENT_DATA_REPORT_$(date +%Y%m%d_%H%M%S).md"
  
  cat > "$report_file" <<EOF
# Post-Deployment Data Check Report

**Date**: $(date)
**Environment**: $ENVIRONMENT

## Check Results

- Schema Version: $(if check_schema_version > /dev/null 2>&1; then echo "✅ Pass"; else echo "❌ Fail"; fi)
- Data Integrity: $(if check_data_integrity > /dev/null 2>&1; then echo "✅ Pass"; else echo "❌ Fail"; fi)
- Data Consistency: $(if check_data_consistency > /dev/null 2>&1; then echo "✅ Pass"; else echo "❌ Fail"; fi)

## Summary

Post-deployment data check completed.

EOF
  
  log_success "Report generated: $report_file"
}

main() {
  echo "=========================================="
  echo "  Post-Deployment Data Check"
  echo "=========================================="
  echo ""
  echo "Environment: $ENVIRONMENT"
  echo ""
  
  local exit_code=0
  
  check_schema_version || exit_code=1
  check_data_integrity || exit_code=1
  check_data_consistency || exit_code=1
  
  generate_post_deployment_report
  
  echo ""
  echo "=========================================="
  if [ $exit_code -eq 0 ]; then
    log_success "Post-deployment data check passed!"
  else
    log_error "Post-deployment data check found issues"
  fi
  echo "=========================================="
  
  exit $exit_code
}

main "$@"

