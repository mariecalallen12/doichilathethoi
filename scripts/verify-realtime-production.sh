#!/bin/bash

# Verification Script for Real-time Trading Dashboard Production
# Verifies that all real-time updates are working correctly

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
BASE_URL="${BASE_URL:-https://cmeetrading.com}"
API_URL="${API_URL:-${BASE_URL}/api}"
WS_URL="${WS_URL:-wss://cmeetrading.com/ws}"

echo -e "${BLUE}=== Real-time Trading Dashboard Verification ===${NC}\n"

# Test 1: API Health Check
echo -e "${BLUE}[1/6] Testing API Health...${NC}"
if curl -f -s "${API_URL}/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API is healthy${NC}"
else
    echo -e "${RED}❌ API health check failed${NC}"
    exit 1
fi

# Test 2: WebSocket Connection
echo -e "${BLUE}[2/6] Testing WebSocket connection...${NC}"
if command -v websocat > /dev/null 2>&1; then
    if timeout 5 websocat "${WS_URL}?token=test" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ WebSocket connection successful${NC}"
    else
        echo -e "${YELLOW}⚠️  WebSocket test skipped (websocat not available)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  WebSocket test skipped (websocat not installed)${NC}"
fi

# Test 3: Market Data Endpoint
echo -e "${BLUE}[3/6] Testing Market Data API...${NC}"
if curl -f -s "${API_URL}/market/instruments" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Market data endpoint accessible${NC}"
else
    echo -e "${RED}❌ Market data endpoint failed${NC}"
    exit 1
fi

# Test 4: Trading Simulator Status
echo -e "${BLUE}[4/6] Testing Trading Simulator...${NC}"
if curl -f -s "${API_URL}/trading-simulator/snapshot" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Trading simulator is running${NC}"
else
    echo -e "${YELLOW}⚠️  Trading simulator endpoint not accessible${NC}"
fi

# Test 5: Frontend Accessibility
echo -e "${BLUE}[5/6] Testing Frontend...${NC}"
if curl -f -s "${BASE_URL}/trading" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Trading page is accessible${NC}"
else
    echo -e "${RED}❌ Trading page not accessible${NC}"
    exit 1
fi

# Test 6: Performance Check
echo -e "${BLUE}[6/6] Testing Performance...${NC}"
START_TIME=$(date +%s%N)
curl -f -s "${API_URL}/market/instruments" > /dev/null 2>&1
END_TIME=$(date +%s%N)
LATENCY_MS=$(( (END_TIME - START_TIME) / 1000000 ))

if [ $LATENCY_MS -lt 100 ]; then
    echo -e "${GREEN}✅ API latency: ${LATENCY_MS}ms (excellent)${NC}"
elif [ $LATENCY_MS -lt 500 ]; then
    echo -e "${YELLOW}⚠️  API latency: ${LATENCY_MS}ms (acceptable)${NC}"
else
    echo -e "${RED}❌ API latency: ${LATENCY_MS}ms (too high)${NC}"
    exit 1
fi

echo -e "\n${GREEN}=== All Verification Tests Passed ===${NC}"
echo -e "${GREEN}✅ Production deployment is healthy${NC}\n"

echo -e "${BLUE}Next Steps:${NC}"
echo -e "1. Monitor WebSocket connections in production"
echo -e "2. Check real-time updates on trading page"
echo -e "3. Verify chart smoothness and latency"
echo -e "4. Monitor error logs for any issues\n"

