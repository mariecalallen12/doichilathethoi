#!/bin/bash

# Data Profiling Script
# Profile data to analyze patterns and identify anomalies
#
# Usage:
#   ./scripts/data-profiling.sh [--table=<table>] [--verbose]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

TABLE=""
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --table=*)
      TABLE="${1#*=}"
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

profile_table() {
  local table=$1
  
  log_info "Profiling table: $table"
  
  # Get row count
  local row_count=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
    SELECT COUNT(*) 
    FROM $table;
  " 2>/dev/null | tr -d ' ' || echo "0")
  
  log_info "  Row count: $row_count"
  
  # Get column info
  if [ "$VERBOSE" = true ]; then
    docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "
      SELECT column_name, data_type 
      FROM information_schema.columns 
      WHERE table_name = '$table' 
      AND table_schema = 'public';
    " 2>/dev/null || true
  fi
}

main() {
  echo "=========================================="
  echo "  Data Profiling"
  echo "=========================================="
  echo ""
  
  if [ -n "$TABLE" ]; then
    profile_table "$TABLE"
  else
    log_info "Profiling all tables..."
    # Profile key tables
    profile_table "users"
    profile_table "user_profiles"
    profile_table "roles"
  fi
  
  echo ""
  echo "=========================================="
  log_success "Data profiling completed!"
  echo "=========================================="
}

main "$@"

