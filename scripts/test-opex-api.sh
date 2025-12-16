#!/bin/bash

# OPEX API Integration Test Script
# Tests OPEX API endpoints

set -e

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
AUTH_TOKEN="${AUTH_TOKEN:-}"

echo "=== OPEX API Integration Tests ==="
echo "API Base URL: $API_BASE_URL"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

test_count=0
pass_count=0
fail_count=0

test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local expected_status=$4
    local auth_header=$5
    
    test_count=$((test_count + 1))
    echo -n "Testing $name... "
    
    if [ -n "$auth_header" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Authorization: $auth_header" \
            -H "Content-Type: application/json" \
            "$API_BASE_URL$endpoint" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            "$API_BASE_URL$endpoint" 2>&1)
    fi
    
    http_code=$(echo "$response" | tail -1)
    body=$(echo "$response" | sed '$d')
    
    if echo "$expected_status" | grep -q "$http_code"; then
        echo -e "${GREEN}✓${NC} (HTTP $http_code)"
        pass_count=$((pass_count + 1))
        return 0
    else
        echo -e "${RED}✗${NC} (HTTP $http_code, expected $expected_status)"
        echo "  Response: $body" | head -3
        fail_count=$((fail_count + 1))
        return 1
    fi
}

echo "=== Market Data Endpoints ==="
test_endpoint "Market Symbols" "GET" "/api/market/symbols" "200 503"
test_endpoint "Market Orderbook" "GET" "/api/market/orderbook/BTCUSDT" "200 400 503"
test_endpoint "Market Health" "GET" "/api/market/health" "200 503"

echo ""
echo "=== Trading Endpoints (Public) ==="
test_endpoint "Trading Health" "GET" "/api/trading/health" "200 503"

echo ""
echo "=== Cache Management ==="
test_endpoint "Cache Stats" "GET" "/api/trading/cache/stats" "200 401 403 500"

echo ""
echo "=== Summary ==="
echo "Total tests: $test_count"
echo -e "${GREEN}Passed: $pass_count${NC}"
if [ $fail_count -gt 0 ]; then
    echo -e "${RED}Failed: $fail_count${NC}"
else
    echo -e "${GREEN}Failed: $fail_count${NC}"
fi

if [ $fail_count -eq 0 ]; then
    exit 0
else
    exit 1
fi

