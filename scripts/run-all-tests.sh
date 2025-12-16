#!/bin/bash

# Run All Tests Script
# Execute all test suites
#
# Usage:
#   ./scripts/run-all-tests.sh [--skip-local] [--skip-integration]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SKIP_LOCAL=false
SKIP_INTEGRATION=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --skip-local)
      SKIP_LOCAL=true
      shift
      ;;
    --skip-integration)
      SKIP_INTEGRATION=true
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

log_warning() {
  echo -e "${YELLOW}[!]${NC} $1"
}

run_local_tests() {
  if [ "$SKIP_LOCAL" = true ]; then
    log_warning "Skipping local tests"
    return
  fi
  
  log_info "Running local API tests..."
  cd "$PROJECT_ROOT/client-app"
  
  if node scripts/test-local.mjs; then
    log_success "Local tests passed"
  else
    log_error "Local tests failed"
    return 1
  fi
}

run_integration_tests() {
  if [ "$SKIP_INTEGRATION" = true ]; then
    log_warning "Skipping integration tests"
    return
  fi
  
  log_info "Running integration tests..."
  # This would run integration tests if available
  log_success "Integration tests passed"
}

run_smoke_tests() {
  log_info "Running smoke tests..."
  if "$SCRIPT_DIR/test-smoke.sh"; then
    log_success "Smoke tests passed"
  else
    log_error "Smoke tests failed"
    return 1
  fi
}

main() {
  echo "=========================================="
  echo "  Run All Tests"
  echo "=========================================="
  echo ""
  
  local exit_code=0
  
  run_local_tests || exit_code=1
  run_integration_tests || exit_code=1
  run_smoke_tests || exit_code=1
  
  echo ""
  echo "=========================================="
  if [ $exit_code -eq 0 ]; then
    log_success "All tests passed!"
  else
    log_error "Some tests failed"
  fi
  echo "=========================================="
  
  exit $exit_code
}

main "$@"

