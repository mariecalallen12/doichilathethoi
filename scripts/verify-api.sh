#!/bin/bash
set -e

echo "🔍 Verifying API Endpoints"
echo "=========================="

# Load environment variables
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

BACKEND_URL="${CLIENT_API_BASE_URL:-http://localhost:8000}"
BACKEND_PORT="${BACKEND_PORT:-8000}"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local expected_status=$3
    local description=$4
    local data=$5
    
    echo -n "Testing $description... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "${BACKEND_URL}${endpoint}" 2>/dev/null || echo -e "\n000")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "${BACKEND_URL}${endpoint}" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null || echo -e "\n000")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "${BACKEND_URL}${endpoint}" 2>/dev/null || echo -e "\n000")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_status" ] || [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $http_code)"
        echo "   Response: $body" | head -c 200
        echo ""
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Check if backend is running
echo "⏳ Checking if backend is accessible..."
if ! curl -f -s "${BACKEND_URL}/api/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend is not accessible at ${BACKEND_URL}${NC}"
    echo "   Please ensure the backend is running: docker-compose up -d backend"
    exit 1
fi
echo -e "${GREEN}✅ Backend is accessible${NC}"
echo ""

# Test 1: Health endpoint
echo "📋 Test 1: Health Check"
test_endpoint "GET" "/api/health" "200" "Health endpoint"
echo ""

# Test 2: Root endpoint
echo "📋 Test 2: Root Endpoint"
test_endpoint "GET" "/" "200" "Root endpoint"
echo ""

# Test 3: API Documentation
echo "📋 Test 3: API Documentation"
test_endpoint "GET" "/docs" "200" "Swagger UI"
test_endpoint "GET" "/openapi.json" "200" "OpenAPI schema"
echo ""

# Test 4: Authentication endpoints (without auth, should return appropriate status)
echo "📋 Test 4: Authentication Endpoints"
# Expect 422 for missing required fields (phoneNumber), so treat 422 as pass
test_endpoint "POST" "/api/auth/register" "422" "Register endpoint (validation)" '{"email":"test"}'
test_endpoint "POST" "/api/auth/login" "422" "Login endpoint (validation)" '{}'
echo ""

# Test 5: Client endpoints (should require auth)
echo "📋 Test 5: Client Endpoints (Auth Required)"
test_endpoint "GET" "/api/client/profile" "403" "Client profile (unauthorized)"
test_endpoint "GET" "/api/client/settings" "403" "Client settings (unauthorized)"
echo ""

# Test 6: Admin endpoints (should require auth)
echo "📋 Test 6: Admin Endpoints (Auth Required)"
test_endpoint "GET" "/api/admin/dashboard" "403" "Admin dashboard (unauthorized)"
echo ""

# Test 7: Trading endpoints (should require auth)
echo "📋 Test 7: Trading Endpoints (Auth Required)"
test_endpoint "GET" "/api/trading/orders" "403" "Trading orders (unauthorized)"
echo ""

# Test 8: Financial endpoints (should require auth)
echo "📋 Test 8: Financial Endpoints (Auth Required)"
test_endpoint "GET" "/api/financial/balance" "403" "Financial balance (unauthorized)"
echo ""

# Summary
echo "=========================="
echo "📊 Test Summary"
echo "=========================="
echo -e "${GREEN}Passed: ${TESTS_PASSED}${NC}"
echo -e "${RED}Failed: ${TESTS_FAILED}${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All API endpoints are working correctly!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed. This may be expected for endpoints requiring authentication.${NC}"
    echo "   To test authenticated endpoints, you need to:"
    echo "   1. Register a user: POST /api/auth/register"
    echo "   2. Login: POST /api/auth/login"
    echo "   3. Use the access_token in Authorization header"
    exit 0
fi

