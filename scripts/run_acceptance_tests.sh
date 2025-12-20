#!/bin/bash

# Acceptance Testing Automation Script
# Runs comprehensive acceptance tests and generates reports

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ACCEPTANCE_DIR="$PROJECT_ROOT/tests/acceptance"
REPORTS_DIR="$PROJECT_ROOT/reports/acceptance"

# Default values
ENVIRONMENT="local"
OUTPUT_PREFIX=""
SKIP_API_TESTS=false
SKIP_MANUAL_TESTS=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_PREFIX="$2"
            shift 2
            ;;
        --skip-api)
            SKIP_API_TESTS=true
            shift
            ;;
        --skip-manual)
            SKIP_MANUAL_TESTS=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -e, --environment ENV    Environment to test (local, staging, production)"
            echo "  -o, --output PREFIX       Output file prefix for reports"
            echo "  --skip-api                Skip automated API tests"
            echo "  --skip-manual             Skip manual testing reminders"
            echo "  -h, --help                Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Acceptance Testing Automation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed${NC}"
    exit 1
fi

# Check if acceptance test directory exists
if [ ! -d "$ACCEPTANCE_DIR" ]; then
    echo -e "${RED}Error: Acceptance test directory not found: $ACCEPTANCE_DIR${NC}"
    exit 1
fi

# Change to acceptance directory
cd "$ACCEPTANCE_DIR"

# Step 1: Verify environment configuration
echo -e "${YELLOW}[Step 1] Verifying environment configuration...${NC}"
if [ ! -f "acceptance_config.json" ]; then
    echo -e "${RED}Error: acceptance_config.json not found${NC}"
    exit 1
fi

# Check if environment is configured
ENV_CHECK=$(python3 -c "
import json
with open('acceptance_config.json', 'r') as f:
    config = json.load(f)
    envs = config.get('environments', {})
    if '$ENVIRONMENT' not in envs:
        print('ERROR')
        exit(1)
    else:
        env = envs['$ENVIRONMENT']
        print(f\"API: {env.get('api_url', 'N/A')}\")
        print(f\"Client: {env.get('client_url', 'N/A')}\")
        print(f\"Admin: {env.get('admin_url', 'N/A')}\")
" 2>&1)

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Environment '$ENVIRONMENT' not configured${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Environment configured${NC}"
echo "$ENV_CHECK"
echo ""

# Step 2: Run automated API tests
if [ "$SKIP_API_TESTS" = false ]; then
    echo -e "${YELLOW}[Step 2] Running automated API tests...${NC}"
    
    # Check if services are running
    API_URL=$(python3 -c "
import json
with open('acceptance_config.json', 'r') as f:
    config = json.load(f)
    print(config['environments']['$ENVIRONMENT']['api_url'])
")
    
    echo "Checking API availability at $API_URL..."
    if curl -s -f "$API_URL/api/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API is accessible${NC}"
    else
        echo -e "${RED}✗ API is not accessible at $API_URL${NC}"
        echo -e "${YELLOW}Warning: Continuing anyway...${NC}"
    fi
    
    # Run API tests
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    RESULTS_FILE="$REPORTS_DIR/test_results/api_test_results_${TIMESTAMP}.json"
    mkdir -p "$(dirname "$RESULTS_FILE")"
    
    echo "Running API test framework..."
    python3 -c "
import sys
sys.path.insert(0, '$ACCEPTANCE_DIR')
from acceptance_test_framework import AcceptanceTestFramework

framework = AcceptanceTestFramework(environment='$ENVIRONMENT')
framework.test_all_api_endpoints()
framework.save_results('$RESULTS_FILE')
summary = framework.get_summary()
print(f\"\nAPI Test Summary:\")
print(f\"  Total: {summary['total']}\")
print(f\"  Passed: {summary['passed']}\")
print(f\"  Failed: {summary['failed']}\")
print(f\"  Pass Rate: {summary['pass_rate']*100:.2f}%\")
print(f\"  Avg Response Time: {summary['average_response_time']*1000:.2f}ms\")
" 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ API tests completed${NC}"
        echo "Results saved to: $RESULTS_FILE"
    else
        echo -e "${RED}✗ API tests failed${NC}"
        exit 1
    fi
    echo ""
else
    echo -e "${YELLOW}[Step 2] Skipping automated API tests${NC}"
    RESULTS_FILE=""
    echo ""
fi

# Step 3: Manual testing reminders
if [ "$SKIP_MANUAL_TESTS" = false ]; then
    echo -e "${YELLOW}[Step 3] Manual Testing Reminders${NC}"
    echo ""
    echo "Please complete manual testing using the checklists:"
    echo "  - Client Checklist: $ACCEPTANCE_DIR/checklists/client_checklist.md"
    echo "  - Admin Checklist: $ACCEPTANCE_DIR/checklists/admin_checklist.md"
    echo "  - API Checklist: $ACCEPTANCE_DIR/checklists/api_checklist.md"
    echo ""
    echo -e "${BLUE}After completing manual tests, update the checklists and run:${NC}"
    echo "  python3 $ACCEPTANCE_DIR/generate_acceptance_report.py <results_file>"
    echo ""
    read -p "Press Enter to continue after manual testing is complete..."
    echo ""
fi

# Step 4: Generate reports
echo -e "${YELLOW}[Step 4] Generating reports...${NC}"

if [ -z "$RESULTS_FILE" ] || [ ! -f "$RESULTS_FILE" ]; then
    echo -e "${YELLOW}Warning: No test results file found.${NC}"
    echo "Please provide a test results file:"
    echo "  python3 $ACCEPTANCE_DIR/generate_acceptance_report.py <results_file> [output_prefix]"
    exit 0
fi

# Generate reports
if [ -z "$OUTPUT_PREFIX" ]; then
    OUTPUT_PREFIX="acceptance_report_$(date +%Y%m%d_%H%M%S)"
fi

python3 "$ACCEPTANCE_DIR/generate_acceptance_report.py" "$RESULTS_FILE" "$OUTPUT_PREFIX"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Reports generated successfully${NC}"
    echo ""
    echo -e "${BLUE}Report files:${NC}"
    echo "  - Markdown: $REPORTS_DIR/${OUTPUT_PREFIX}.md"
    echo "  - HTML: $REPORTS_DIR/${OUTPUT_PREFIX}.html"
    echo "  - JSON: $REPORTS_DIR/${OUTPUT_PREFIX}.json"
    echo ""
else
    echo -e "${RED}✗ Report generation failed${NC}"
    exit 1
fi

# Step 5: Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Acceptance Testing Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Review the generated reports"
echo "  2. Address any critical or high priority issues"
echo "  3. Re-run tests after fixes"
echo "  4. Obtain stakeholder sign-off"
echo ""

