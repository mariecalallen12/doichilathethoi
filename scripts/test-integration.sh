#!/bin/bash
# Integration Test Script
# Tests client-backend alignment after fixes

set -e

echo "🧪 Integration Test Suite - Client-Backend Alignment"
echo "======================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="http://localhost:8000"
TRADING_API_URL="http://localhost:8001"  # If separate

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
test_api() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Testing: $name ... "
    
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$status" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $status)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (Expected $expected_status, got $status)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

test_json_field() {
    local name="$1"
    local url="$2"
    local field="$3"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Testing: $name ... "
    
    response=$(curl -s "$url")
    
    if echo "$response" | jq -e "$field" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC} (Field exists)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (Field missing: $field)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

echo "📡 Backend Connectivity Tests"
echo "------------------------------"

# Test 1: Backend health
test_api "Backend health check" "$BACKEND_URL/health" || true

# Test 2: Market prices endpoint
test_api "Market prices endpoint" "$BACKEND_URL/api/market/prices?symbols=BTC,EUR/USD,XAU" || true

# Test 3: Trading signals endpoint  
test_api "Trading signals endpoint" "$BACKEND_URL/trading/signals" || true

# Test 4: Binary array endpoint
test_api "Binary array endpoint" "$BACKEND_URL/trading/binary-array" || true

echo ""
echo "📊 Data Format Tests"
echo "--------------------"

# Test 5: Market prices response format
test_json_field "Market prices has 'prices' field" \
    "$BACKEND_URL/api/market/prices?symbols=BTC" \
    ".prices"

# Test 6: Price data has required fields
test_json_field "Price data has 'price' field" \
    "$BACKEND_URL/api/market/prices?symbols=BTC" \
    ".prices.BTC.price"

test_json_field "Price data has 'change_24h' field" \
    "$BACKEND_URL/api/market/prices?symbols=BTC" \
    ".prices.BTC.change_24h"

# Test 7: Trading signal response format
test_json_field "Signal has 'symbol' field" \
    "$BACKEND_URL/trading/signals/BTC" \
    ".symbol"

test_json_field "Signal has 'signal' field" \
    "$BACKEND_URL/trading/signals/BTC" \
    ".signal"

test_json_field "Signal has 'confidence' field" \
    "$BACKEND_URL/trading/signals/BTC" \
    ".confidence"

echo ""
echo "🔍 Symbol Format Tests"
echo "----------------------"

# Test 8: Crypto symbol (BTC)
TESTS_RUN=$((TESTS_RUN + 1))
echo -n "Testing: BTC symbol format ... "
response=$(curl -s "$BACKEND_URL/api/market/prices?symbols=BTC")
if echo "$response" | jq -e '.prices.BTC' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC} (Key is 'BTC')"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ FAIL${NC} (Key should be 'BTC')"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 9: Forex symbol (EUR/USD)
TESTS_RUN=$((TESTS_RUN + 1))
echo -n "Testing: EUR/USD symbol format ... "
response=$(curl -s "$BACKEND_URL/api/market/prices?symbols=EUR/USD")
if echo "$response" | jq -e '.prices."EUR/USD"' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC} (Key is 'EUR/USD')"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ FAIL${NC} (Key should be 'EUR/USD')"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 10: Metal symbol (XAU)
TESTS_RUN=$((TESTS_RUN + 1))
echo -n "Testing: XAU symbol format ... "
response=$(curl -s "$BACKEND_URL/api/market/prices?symbols=XAU")
if echo "$response" | jq -e '.prices.XAU' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC} (Key is 'XAU')"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ FAIL${NC} (Key should be 'XAU')"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo ""
echo "🎯 Client Store Compatibility Tests"
echo "------------------------------------"

# Test 11: Check if analysis.js can parse signals
TESTS_RUN=$((TESTS_RUN + 1))
echo -n "Testing: Signals API compatibility ... "
response=$(curl -s "$BACKEND_URL/trading/signals")
if echo "$response" | jq -e 'if type=="array" then .[0].symbol else .symbol end' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC} (Response has symbol field)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ FAIL${NC} (Missing symbol field)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 12: Check binary array format
TESTS_RUN=$((TESTS_RUN + 1))
echo -n "Testing: Binary array format ... "
response=$(curl -s "$BACKEND_URL/trading/binary-array")
if echo "$response" | jq -e '.total_signals' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC} (Has total_signals)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ FAIL${NC} (Missing total_signals)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo ""
echo "📝 Summary"
echo "=========="
echo "Tests run:    $TESTS_RUN"
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start client app: cd client-app && npm run dev"
    echo "2. Navigate to http://localhost:3000/market"
    echo "3. Check browser console for errors"
    echo "4. Navigate to http://localhost:3000/analysis"
    echo "5. Verify trading signals display"
    exit 0
else
    echo -e "${RED}❌ Some tests failed!${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check backend is running: curl $BACKEND_URL/health"
    echo "2. Check logs: tail -f /var/log/tradingsystem.log"
    echo "3. Verify API endpoints in browser DevTools"
    exit 1
fi
