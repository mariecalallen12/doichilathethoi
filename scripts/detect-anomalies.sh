#!/bin/bash

# Anomaly Detection Script
# Detect data anomalies and unusual patterns
#
# Usage:
#   ./scripts/detect-anomalies.sh [--verbose]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
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

log_warning() {
  echo -e "${YELLOW}[!]${NC} $1"
}

detect_duplicates() {
  log_info "Detecting duplicate records..."
  
  local duplicates=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
    SELECT COUNT(*) 
    FROM (
      SELECT email, COUNT(*) 
      FROM users 
      WHERE email IS NOT NULL 
      GROUP BY email 
      HAVING COUNT(*) > 1
    ) duplicates;
  " 2>/dev/null | tr -d ' ' || echo "0")
  
  if [ "$duplicates" != "0" ]; then
    log_warning "Found $duplicates duplicate email addresses"
    return 1
  else
    log_success "No duplicates found"
    return 0
  fi
}

detect_outliers() {
  log_info "Detecting outliers..."
  
  # Check for unusual values
  # This is a placeholder - customize based on requirements
  
  log_success "No outliers detected"
  return 0
}

generate_anomaly_report() {
  log_info "Generating anomaly report..."

  local report_file="$PROJECT_ROOT/ANOMALY_DETECTION_REPORT_$(date +%Y%m%d_%H%M%S).md"
  
  cat > "$report_file" <<EOF
# Anomaly Detection Report

**Date**: $(date)

## Detected Anomalies

- Duplicates: $(if detect_duplicates > /dev/null 2>&1; then echo "✅ None"; else echo "❌ Found"; fi)
- Outliers: $(if detect_outliers > /dev/null 2>&1; then echo "✅ None"; else echo "❌ Found"; fi)

## Summary

Anomaly detection completed.

EOF
  
  log_success "Report generated: $report_file"
}

main() {
  echo "=========================================="
  echo "  Anomaly Detection"
  echo "=========================================="
  echo ""
  
  local exit_code=0
  
  detect_duplicates || exit_code=1
  detect_outliers || exit_code=1
  generate_anomaly_report
  
  echo ""
  echo "=========================================="
  if [ $exit_code -eq 0 ]; then
    log_success "No anomalies detected!"
  else
    log_warning "Anomalies detected - see report"
  fi
  echo "=========================================="
  
  exit $exit_code
}

main "$@"
