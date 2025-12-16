#!/bin/bash
# Run Automated Tests Script
# Runs integration and performance tests

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if pytest is installed
check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v pytest &> /dev/null; then
        log_error "pytest is not installed. Installing..."
        pip3 install pytest requests || {
            log_error "Failed to install pytest"
            exit 1
        }
    fi
    
    if ! python3 -c "import requests" 2>/dev/null; then
        log_info "Installing requests library..."
        pip3 install requests || {
            log_error "Failed to install requests"
            exit 1
        }
    fi
    
    log_success "Dependencies checked"
}

# Run integration tests
run_integration_tests() {
    log_info "Running integration tests..."
    
    if [ -f "$PROJECT_ROOT/tests/integration/test_health_checks.py" ]; then
        pytest "$PROJECT_ROOT/tests/integration/test_health_checks.py" -v || {
            log_error "Integration tests failed"
            return 1
        }
        log_success "Integration tests passed"
    else
        log_error "Integration test file not found"
        return 1
    fi
}

# Run performance tests
run_performance_tests() {
    log_info "Running performance tests..."
    
    if [ -f "$PROJECT_ROOT/tests/performance/test_api_performance.py" ]; then
        pytest "$PROJECT_ROOT/tests/performance/test_api_performance.py" -v || {
            log_error "Performance tests failed"
            return 1
        }
        log_success "Performance tests passed"
    else
        log_error "Performance test file not found"
        return 1
    fi
}

# Run all tests
run_all_tests() {
    log_info "Running all tests..."
    
    check_dependencies
    
    integration_result=0
    performance_result=0
    
    run_integration_tests || integration_result=1
    run_performance_tests || performance_result=1
    
    echo ""
    echo "=========================================="
    echo "Test Summary"
    echo "=========================================="
    
    if [ $integration_result -eq 0 ]; then
        log_success "Integration tests: PASSED"
    else
        log_error "Integration tests: FAILED"
    fi
    
    if [ $performance_result -eq 0 ]; then
        log_success "Performance tests: PASSED"
    else
        log_error "Performance tests: FAILED"
    fi
    
    if [ $integration_result -eq 0 ] && [ $performance_result -eq 0 ]; then
        log_success "All tests passed!"
        exit 0
    else
        log_error "Some tests failed"
        exit 1
    fi
}

# Main execution
main() {
    echo "=========================================="
    echo "Automated Test Runner"
    echo "Date: $(date)"
    echo "=========================================="
    echo ""
    
    case "${1:-all}" in
        integration)
            check_dependencies
            run_integration_tests
            ;;
        performance)
            check_dependencies
            run_performance_tests
            ;;
        all|*)
            run_all_tests
            ;;
    esac
}

main "$@"
