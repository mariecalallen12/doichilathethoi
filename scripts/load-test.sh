#!/bin/bash

# Load Testing Script for OPEX Trading API
# Uses curl for basic load testing

set -e

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
CONCURRENT_USERS="${CONCURRENT_USERS:-10}"
REQUESTS_PER_USER="${REQUESTS_PER_USER:-100}"

echo "=== Load Testing OPEX Trading API ==="
echo "API Base URL: $API_BASE_URL"
echo "Concurrent Users: $CONCURRENT_USERS"
echo "Requests per User: $REQUESTS_PER_USER"
echo ""

# Test endpoints
test_market_symbols() {
    echo "Testing /api/market/symbols..."
    for i in $(seq 1 $REQUESTS_PER_USER); do
        curl -s -o /dev/null -w "%{http_code}\n" "$API_BASE_URL/api/market/symbols" &
    done
    wait
}

test_market_orderbook() {
    echo "Testing /api/market/orderbook/BTCUSDT..."
    for i in $(seq 1 $REQUESTS_PER_USER); do
        curl -s -o /dev/null -w "%{http_code}\n" "$API_BASE_URL/api/market/orderbook/BTCUSDT" &
    done
    wait
}

test_trading_health() {
    echo "Testing /api/trading/health..."
    for i in $(seq 1 $REQUESTS_PER_USER); do
        curl -s -o /dev/null -w "%{http_code}\n" "$API_BASE_URL/api/trading/health" &
    done
    wait
}

# Run tests
echo "Starting load tests..."
start_time=$(date +%s)

test_market_symbols &
test_market_orderbook &
test_trading_health &

wait

end_time=$(date +%s)
duration=$((end_time - start_time))

echo ""
echo "Load test completed in ${duration} seconds"
echo "Total requests: $((CONCURRENT_USERS * REQUESTS_PER_USER * 3))"

