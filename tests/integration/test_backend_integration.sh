#!/bin/bash
# Backend Integration Test Script
# Runs all backend integration tests and generates a report

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
REPORTS_DIR="$PROJECT_ROOT/reports/integration"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="$REPORTS_DIR/backend_integration_test_${TIMESTAMP}.json"

# Create reports directory if it doesn't exist
mkdir -p "$REPORTS_DIR"

# Counters
PASSED=0
FAILED=0
SKIPPED=0
TOTAL=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Backend Integration Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print test result
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
        ((FAILED++))
    fi
    ((TOTAL++))
}

# Function to check if backend is running
check_backend_running() {
    echo -e "${YELLOW}Checking if backend is running...${NC}"
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is running${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Backend is not running${NC}"
        echo -e "${YELLOW}   Some tests may be skipped${NC}"
        return 1
    fi
}

# Function to check if database is available
check_database() {
    echo -e "${YELLOW}Checking database connection...${NC}"
    cd "$BACKEND_DIR"
    if python -c "from app.db.session import check_db_connection; exit(0 if check_db_connection(max_retries=1, retry_delay=1) else 1)" 2>/dev/null; then
        echo -e "${GREEN}✅ Database is available${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Database is not available${NC}"
        echo -e "${YELLOW}   Some tests may be skipped${NC}"
        return 1
    fi
}

# Function to check if Redis is available
check_redis() {
    echo -e "${YELLOW}Checking Redis connection...${NC}"
    cd "$BACKEND_DIR"
    if python -c "from app.db.redis_client import init_redis; exit(0 if init_redis() else 1)" 2>/dev/null; then
        echo -e "${GREEN}✅ Redis is available${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Redis is not available${NC}"
        echo -e "${YELLOW}   Some tests may be skipped${NC}"
        return 1
    fi
}

# Function to run pytest tests
run_pytest_tests() {
    local test_file=$1
    local test_name=$2
    
    echo ""
    echo -e "${BLUE}Running: $test_name${NC}"
    echo "----------------------------------------"
    
    cd "$BACKEND_DIR"
    
    if [ ! -f "$test_file" ]; then
        echo -e "${RED}Test file not found: $test_file${NC}"
        return 1
    fi
    
    # Run pytest with output
    if pytest "$test_file" -v --tb=short 2>&1 | tee "$REPORTS_DIR/pytest_${test_name}_${TIMESTAMP}.log"; then
        test_result 0 "$test_name"
        return 0
    else
        test_result 1 "$test_name"
        return 1
    fi
}

# Main execution
echo -e "${BLUE}1. Pre-flight Checks${NC}"
echo "-------------------"

BACKEND_RUNNING=false
DATABASE_AVAILABLE=false
REDIS_AVAILABLE=false

if check_backend_running; then
    BACKEND_RUNNING=true
fi

if check_database; then
    DATABASE_AVAILABLE=true
fi

if check_redis; then
    REDIS_AVAILABLE=true
fi

echo ""
echo -e "${BLUE}2. Running Integration Tests${NC}"
echo "----------------------------"

# Test files to run
TEST_FILES=(
    "tests/test_backend_integration.py:Backend Integration"
    "tests/test_websocket_integration.py:WebSocket Integration"
    "tests/test_trade_broadcaster_integration.py:Trade Broadcaster Integration"
)

# Run each test file
for test_entry in "${TEST_FILES[@]}"; do
    IFS=':' read -r test_file test_name <<< "$test_entry"
    run_pytest_tests "$test_file" "$test_name"
done

echo ""
echo -e "${BLUE}3. Test Summary${NC}"
echo "-------------"
echo -e "Total Tests: ${TOTAL}"
echo -e "${GREEN}Passed: ${PASSED}${NC}"
echo -e "${RED}Failed: ${FAILED}${NC}"
echo -e "${YELLOW}Skipped: ${SKIPPED}${NC}"

# Calculate pass rate
if [ $TOTAL -gt 0 ]; then
    PASS_RATE=$(echo "scale=2; $PASSED * 100 / $TOTAL" | bc)
    echo -e "Pass Rate: ${PASS_RATE}%"
else
    PASS_RATE=0
    echo -e "Pass Rate: N/A"
fi

# Generate JSON report
echo ""
echo -e "${BLUE}4. Generating Report${NC}"
echo "-------------------"

cat > "$REPORT_FILE" << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "environment": {
    "backend_running": $BACKEND_RUNNING,
    "database_available": $DATABASE_AVAILABLE,
    "redis_available": $REDIS_AVAILABLE
  },
  "summary": {
    "total": $TOTAL,
    "passed": $PASSED,
    "failed": $FAILED,
    "skipped": $SKIPPED,
    "pass_rate": $PASS_RATE
  },
  "test_files": [
    {
      "name": "Backend Integration",
      "file": "tests/test_backend_integration.py",
      "status": "$([ $FAILED -eq 0 ] && echo "passed" || echo "failed")"
    },
    {
      "name": "WebSocket Integration",
      "file": "tests/test_websocket_integration.py",
      "status": "$([ $FAILED -eq 0 ] && echo "passed" || echo "failed")"
    },
    {
      "name": "Trade Broadcaster Integration",
      "file": "tests/test_trade_broadcaster_integration.py",
      "status": "$([ $FAILED -eq 0 ] && echo "passed" || echo "failed")"
    }
  ],
  "report_file": "$REPORT_FILE"
}
EOF

echo -e "${GREEN}✅ Report saved to: $REPORT_FILE${NC}"

# Final status
echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo -e "${GREEN}========================================${NC}"
    exit 0
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}❌ Some tests failed${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo -e "${YELLOW}Check logs in: $REPORTS_DIR${NC}"
    exit 1
fi

