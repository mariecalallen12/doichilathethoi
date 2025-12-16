#!/bin/bash

# Test script for Customer Wallet Balances endpoint
# Tests the new endpoint according to checklist

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BASE_URL="${BASE_URL:-http://localhost:8000}"
ENDPOINT="/api/admin/customers/wallet-balances"

log_info() {
  echo -e "${BLUE}[TEST]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[PASS]${NC} $1"
}

log_error() {
  echo -e "${RED}[FAIL]${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

test_no_auth() {
  log_info "Test 1: No authentication token"
  response=$(curl -s -w "\n%{http_code}" -X GET "${BASE_URL}${ENDPOINT}")
  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | head -n-1)
  
  if [ "$http_code" = "401" ] || [ "$http_code" = "403" ]; then
    log_success "Correctly returns ${http_code} (authentication required)"
    return 0
  else
    log_error "Expected 401 or 403, got $http_code"
    echo "Response: $body"
    return 1
  fi
}

test_endpoint_exists() {
  log_info "Test 2: Endpoint exists (checking with OPTIONS)"
  response=$(curl -s -w "\n%{http_code}" -X OPTIONS "${BASE_URL}${ENDPOINT}")
  http_code=$(echo "$response" | tail -n1)
  
  if [ "$http_code" = "200" ] || [ "$http_code" = "401" ] || [ "$http_code" = "405" ]; then
    log_success "Endpoint exists (HTTP $http_code)"
    return 0
  else
    log_error "Endpoint might not exist (HTTP $http_code)"
    return 1
  fi
}

test_with_admin_token() {
  if [ -z "$ADMIN_TOKEN" ]; then
    log_warning "ADMIN_TOKEN not set, skipping authenticated tests"
    log_info "Set ADMIN_TOKEN environment variable to test with authentication"
    return 0
  fi
  
  log_info "Test 3: With admin token"
  response=$(curl -s -w "\n%{http_code}" -X GET "${BASE_URL}${ENDPOINT}" \
    -H "Authorization: Bearer $ADMIN_TOKEN")
  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | head -n-1)
  
  if [ "$http_code" = "200" ]; then
    log_success "Correctly returns 200 OK with admin token"
    
    # Check response structure
    if echo "$body" | jq -e '.success' > /dev/null 2>&1; then
      log_success "Response has 'success' field"
    else
      log_error "Response missing 'success' field"
      return 1
    fi
    
    if echo "$body" | jq -e '.data' > /dev/null 2>&1; then
      log_success "Response has 'data' field"
    else
      log_error "Response missing 'data' field"
      return 1
    fi
    
    if echo "$body" | jq -e '.pagination' > /dev/null 2>&1; then
      log_success "Response has 'pagination' field"
    else
      log_error "Response missing 'pagination' field"
      return 1
    fi
    
    if echo "$body" | jq -e '.summary' > /dev/null 2>&1; then
      log_success "Response has 'summary' field"
    else
      log_error "Response missing 'summary' field"
      return 1
    fi
    
    # Show sample data
    data_count=$(echo "$body" | jq '.data | length')
    log_info "Received $data_count customer wallet balances"
    
    return 0
  elif [ "$http_code" = "403" ]; then
    log_error "Got 403 Forbidden - token might not have admin role"
    return 1
  else
    log_error "Expected 200, got $http_code"
    echo "Response: $body"
    return 1
  fi
}

test_pagination() {
  if [ -z "$ADMIN_TOKEN" ]; then
    return 0
  fi
  
  log_info "Test 4: Pagination (page=1, limit=5)"
  response=$(curl -s -w "\n%{http_code}" -X GET "${BASE_URL}${ENDPOINT}?page=1&limit=5" \
    -H "Authorization: Bearer $ADMIN_TOKEN")
  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | head -n-1)
  
  if [ "$http_code" = "200" ]; then
    data_count=$(echo "$body" | jq '.data | length')
    if [ "$data_count" -le 5 ]; then
      log_success "Pagination works correctly (got $data_count items)"
    else
      log_error "Pagination failed (got $data_count items, expected <= 5)"
      return 1
    fi
  else
    log_error "Pagination test failed (HTTP $http_code)"
    return 1
  fi
}

test_filters() {
  if [ -z "$ADMIN_TOKEN" ]; then
    return 0
  fi
  
  log_info "Test 5: Currency filter (currency=USDT)"
  response=$(curl -s -w "\n%{http_code}" -X GET "${BASE_URL}${ENDPOINT}?currency=USDT" \
    -H "Authorization: Bearer $ADMIN_TOKEN")
  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | head -n-1)
  
  if [ "$http_code" = "200" ]; then
    log_success "Currency filter works (HTTP 200)"
    # Could add more validation here
  else
    log_error "Currency filter test failed (HTTP $http_code)"
    return 1
  fi
}

main() {
  echo "=========================================="
  echo "  Customer Wallet Balances Endpoint Test"
  echo "=========================================="
  echo ""
  echo "Base URL: $BASE_URL"
  echo "Endpoint: $ENDPOINT"
  echo ""
  
  passed=0
  failed=0
  
  # Run tests
  test_no_auth && ((passed++)) || ((failed++))
  echo ""
  
  test_endpoint_exists && ((passed++)) || ((failed++))
  echo ""
  
  test_with_admin_token && ((passed++)) || ((failed++))
  echo ""
  
  test_pagination && ((passed++)) || ((failed++))
  echo ""
  
  test_filters && ((passed++)) || ((failed++))
  echo ""
  
  echo "=========================================="
  echo "Test Results: $passed passed, $failed failed"
  echo "=========================================="
  
  if [ $failed -eq 0 ]; then
    exit 0
  else
    exit 1
  fi
}

main "$@"

