#!/bin/bash

# Real-time Sync Verification Script
# Verify WebSocket and cache synchronization
#
# Usage:
#   ./scripts/verify-realtime-sync.sh [--verbose]

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

check_websocket_service() {
  log_info "Checking WebSocket service..."
  
  # Check if WebSocket endpoint is accessible
  if curl -f -s http://localhost:8000/ws > /dev/null 2>&1; then
    log_success "WebSocket endpoint is accessible"
    return 0
  else
    log_error "WebSocket endpoint is not accessible"
    return 1
  fi
}

check_redis_cache() {
  log_info "Checking Redis cache..."
  
  if docker exec digital_utopia_redis redis-cli ping > /dev/null 2>&1; then
    log_success "Redis cache is accessible"
    
    # Check cache stats
    local keys=$(docker exec digital_utopia_redis redis-cli DBSIZE 2>/dev/null | tr -d '\r' || echo "0")
    log_info "Redis keys: $keys"
    
    return 0
  else
    log_error "Redis cache is not accessible"
    return 1
  fi
}

check_cache_sync() {
  log_info "Checking cache synchronization..."
  
  # Test cache write and read
  local test_key="sync_test_$(date +%s)"
  local test_value="test_value"
  
  docker exec digital_utopia_redis redis-cli SET "$test_key" "$test_value" > /dev/null 2>&1
  local retrieved=$(docker exec digital_utopia_redis redis-cli GET "$test_key" 2>/dev/null | tr -d '\r' || echo "")
  docker exec digital_utopia_redis redis-cli DEL "$test_key" > /dev/null 2>&1
  
  if [ "$retrieved" = "$test_value" ]; then
    log_success "Cache read/write working"
    return 0
  else
    log_error "Cache read/write failed"
    return 1
  fi
}

main() {
  echo "=========================================="
  echo "  Real-time Sync Verification"
  echo "=========================================="
  echo ""
  
  local exit_code=0
  
  check_websocket_service || exit_code=1
  check_redis_cache || exit_code=1
  check_cache_sync || exit_code=1
  
  echo ""
  echo "=========================================="
  if [ $exit_code -eq 0 ]; then
    log_success "Real-time sync verification passed!"
  else
    log_error "Real-time sync verification found issues"
  fi
  echo "=========================================="
  
  exit $exit_code
}

main "$@"

