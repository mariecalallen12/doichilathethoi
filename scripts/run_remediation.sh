#!/bin/bash
# Script to run remediation tasks automatically
# Based on REMEDIATION_PLAN.md

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Remediation Script"
echo "=========================================="
echo ""

# Function to print section header
print_section() {
    echo ""
    echo -e "${BLUE}==========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo ""
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Update endpoints list
print_section "1. Updating Endpoints List"
if [ -f "scripts/list_all_endpoints.py" ]; then
    echo "Running list_all_endpoints.py..."
    python3 scripts/list_all_endpoints.py
    if [ $? -eq 0 ]; then
        print_success "Endpoints list updated"
    else
        print_error "Failed to update endpoints list"
        exit 1
    fi
else
    print_error "scripts/list_all_endpoints.py not found"
    exit 1
fi

# 2. Update admin features mapping
print_section "2. Updating Admin Features Mapping"
if [ -f "scripts/map_admin_features.py" ]; then
    echo "Running map_admin_features.py..."
    python3 scripts/map_admin_features.py
    if [ $? -eq 0 ]; then
        print_success "Admin features mapping updated"
    else
        print_error "Failed to update admin features mapping"
        exit 1
    fi
else
    print_error "scripts/map_admin_features.py not found"
    exit 1
fi

# 3. Check if backend is running
print_section "3. Checking Backend Status"
BACKEND_URL="${API_BASE_URL:-http://localhost:8000}"
if curl -s -f --max-time 5 "$BACKEND_URL/api/health" > /dev/null 2>&1; then
    print_success "Backend is running at $BACKEND_URL"
    BACKEND_RUNNING=true
else
    print_warning "Backend is not running at $BACKEND_URL"
    echo "Please start the backend before running API tests"
    BACKEND_RUNNING=false
fi

# 4. Run API tests (if backend is running)
if [ "$BACKEND_RUNNING" = true ]; then
    print_section "4. Running API Tests"
    if [ -f "scripts/test_all_apis.py" ]; then
        echo "Running test_all_apis.py..."
        echo "This may take several minutes..."
        python3 scripts/test_all_apis.py
        if [ $? -eq 0 ]; then
            print_success "API tests completed"
            echo "Results saved to: scripts/api_test_results.json"
            echo "Report saved to: scripts/api_test_report.md"
        else
            print_error "API tests failed"
        fi
    else
        print_error "scripts/test_all_apis.py not found"
    fi
else
    print_warning "Skipping API tests (backend not running)"
fi

# 5. Verify trading integration
print_section "5. Verifying Trading Integration"
if [ -f "scripts/verify_trading_integration.sh" ]; then
    bash scripts/verify_trading_integration.sh
    if [ $? -eq 0 ]; then
        print_success "Trading integration verification completed"
    else
        print_warning "Trading integration verification had issues"
    fi
else
    print_error "scripts/verify_trading_integration.sh not found"
fi

# 6. Test trading operations (if backend is running)
if [ "$BACKEND_RUNNING" = true ]; then
    print_section "6. Testing Trading Operations"
    if [ -f "scripts/test_trading_operations.py" ]; then
        echo "Running test_trading_operations.py..."
        python3 scripts/test_trading_operations.py
        if [ $? -eq 0 ]; then
            print_success "Trading operations tests completed"
        else
            print_warning "Trading operations tests had issues"
        fi
    else
        print_error "scripts/test_trading_operations.py not found"
    fi
else
    print_warning "Skipping trading operations tests (backend not running)"
fi

# 7. Verify admin app
print_section "7. Verifying Admin App"
if [ -f "scripts/verify_admin_app.sh" ]; then
    bash scripts/verify_admin_app.sh
    if [ $? -eq 0 ]; then
        print_success "Admin app verification completed"
    else
        print_warning "Admin app verification had issues"
    fi
else
    print_error "scripts/verify_admin_app.sh not found"
fi

# 8. Generate updated evaluation report
print_section "8. Generating Updated Evaluation Report"
if [ -f "scripts/generate_evaluation_report.py" ]; then
    echo "Running generate_evaluation_report.py..."
    python3 scripts/generate_evaluation_report.py
    if [ $? -eq 0 ]; then
        print_success "Evaluation report generated"
        echo "Report saved to: EVALUATION_REPORT.md"
    else
        print_error "Failed to generate evaluation report"
    fi
else
    print_error "scripts/generate_evaluation_report.py not found"
fi

# Summary
print_section "Summary"
echo "Remediation script completed!"
echo ""
echo "Next steps:"
echo "1. Review the generated reports:"
echo "   - scripts/api_test_report.md"
echo "   - scripts/api_test_results.json"
echo "   - EVALUATION_REPORT.md"
echo ""
echo "2. Fix any issues found in the reports"
echo ""
echo "3. Re-run this script after fixes to verify"
echo ""
echo "For detailed remediation plan, see: REMEDIATION_PLAN.md"

