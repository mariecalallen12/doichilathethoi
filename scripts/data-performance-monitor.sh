#!/bin/bash

# Data Performance Monitoring Script
# Monitor database performance metrics
#
# Usage:
#   ./scripts/data-performance-monitor.sh [--verbose]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

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

check_database_size() {
  log_info "Checking database size..."
  
  local db_size=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
    SELECT pg_size_pretty(pg_database_size('digital_utopia'));
  " 2>/dev/null | tr -d ' ' || echo "unknown")
  
  log_info "Database size: $db_size"
  log_success "Database size check completed"
}

check_table_sizes() {
  log_info "Checking table sizes..."
  
  if [ "$VERBOSE" = true ]; then
    docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "
      SELECT 
        schemaname,
        tablename,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
      FROM pg_tables
      WHERE schemaname = 'public'
      ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
      LIMIT 10;
    " 2>/dev/null || true
  fi
}

check_index_usage() {
  log_info "Checking index usage..."
  
  local index_count=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
    SELECT COUNT(*) 
    FROM pg_indexes 
    WHERE schemaname = 'public';
  " 2>/dev/null | tr -d ' ' || echo "0")
  
  log_info "Total indexes: $index_count"
  log_success "Index usage check completed"
}

main() {
  echo "=========================================="
  echo "  Data Performance Monitoring"
  echo "=========================================="
  echo ""
  
  check_database_size
  check_table_sizes
  check_index_usage
  
  echo ""
  echo "=========================================="
  log_success "Performance monitoring completed!"
  echo "=========================================="
}

main "$@"

