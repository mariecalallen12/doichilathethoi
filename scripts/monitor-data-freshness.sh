#!/bin/bash

# Data Freshness Monitoring Script
# Monitor how fresh/recent the data is
#
# Usage:
#   ./scripts/monitor-data-freshness.sh [--threshold=<hours>]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

THRESHOLD_HOURS=24

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --threshold=*)
      THRESHOLD_HOURS="${1#*=}"
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

check_table_freshness() {
  local table=$1
  local updated_column=${2:-updated_at}
  
  local last_update=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
    SELECT MAX($updated_column) 
    FROM $table;
  " 2>/dev/null | tr -d ' ' || echo "unknown")
  
  if [ "$last_update" != "unknown" ] && [ -n "$last_update" ]; then
    log_info "$table: Last update: $last_update"
  fi
}

main() {
  echo "=========================================="
  echo "  Data Freshness Monitoring"
  echo "=========================================="
  echo ""
  echo "Threshold: $THRESHOLD_HOURS hours"
  echo ""
  
  check_table_freshness "users" "updated_at"
  check_table_freshness "audit_logs" "created_at"
  check_table_freshness "exchange_rates" "updated_at"
  
  echo ""
  echo "=========================================="
  log_success "Data freshness monitoring completed!"
  echo "=========================================="
}

main "$@"

