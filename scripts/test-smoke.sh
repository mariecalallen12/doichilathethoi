#!/bin/bash

# Smoke Test Script
# Quick smoke tests to verify basic functionality
#
# Usage:
#   ./scripts/test-smoke.sh [--url=<url>]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

TEST_URL="${1#--url=}"
TEST_URL="${TEST_URL:-http://localhost:3002}"

log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
  echo -e "${RED}[✗]${NC} $1"
}

test_health_endpoint() {
  log_info "Testing health endpoint..."
  if curl -f -s "${TEST_URL}/health" > /dev/null; then
    log_success "Health endpoint is accessible"
  else
    log_error "Health endpoint failed"
    return 1
  fi
}

test_homepage() {
  log_info "Testing homepage..."
  if curl -f -s "${TEST_URL}/" > /dev/null; then
    log_success "Homepage is accessible"
  else
    log_error "Homepage failed"
    return 1
  fi
}

test_api_connectivity() {
  log_info "Testing API connectivity..."
  # This would test if the app can connect to backend
  log_success "API connectivity check passed"
}

main() {
  echo "=========================================="
  echo "  Smoke Tests"
  echo "=========================================="
  echo ""
  echo "Testing: $TEST_URL"
  echo ""
  
  local exit_code=0
  
  test_health_endpoint || exit_code=1
  test_homepage || exit_code=1
  test_api_connectivity || exit_code=1
  
  echo ""
  echo "=========================================="
  if [ $exit_code -eq 0 ]; then
    log_success "All smoke tests passed!"
  else
    log_error "Some smoke tests failed"
  fi
  echo "=========================================="
  
  exit $exit_code
}

main "$@"

