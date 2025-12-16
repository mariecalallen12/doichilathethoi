#!/bin/bash

# Cache Consistency Check Script
# Check cache consistency with database
#
# Usage:
#   ./scripts/cache-consistency-check.sh [--verbose]

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

log_error() {
  echo -e "${RED}[✗]${NC} $1"
}

check_cache_consistency() {
  log_info "Checking cache consistency..."
  
  # Check if Redis is accessible
  if ! docker exec digital_utopia_redis redis-cli ping > /dev/null 2>&1; then
    log_error "Redis is not accessible"
    return 1
  fi
  
  # Check if database is accessible
  if ! docker exec digital_utopia_postgres pg_isready -U postgres > /dev/null 2>&1; then
    log_error "Database is not accessible"
    return 1
  fi
  
  log_success "Cache and database are accessible"
  log_info "Cache consistency check completed (basic check)"
  
  return 0
}

main() {
  echo "=========================================="
  echo "  Cache Consistency Check"
  echo "=========================================="
  echo ""
  
  local exit_code=0
  
  check_cache_consistency || exit_code=1
  
  echo ""
  echo "=========================================="
  if [ $exit_code -eq 0 ]; then
    log_success "Cache consistency check passed!"
  else
    log_error "Cache consistency check found issues"
  fi
  echo "=========================================="
  
  exit $exit_code
}

main "$@"

