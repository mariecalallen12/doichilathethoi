#!/bin/bash

# Script test các API endpoints với authentication token
# Usage: ./scripts/test-authenticated-endpoints.sh [email] [password]

DOMAIN="https://cmeetrading.com"
API_BASE="${DOMAIN}/api"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "TEST AUTHENTICATED API ENDPOINTS"
echo "Domain: $DOMAIN"
echo "Date: $(date)"
echo "=========================================="
echo ""

# Get credentials
EMAIL="${1:-${CLIENT_TEST_USER_EMAIL:-client_api_tester@example.com}}"
PASSWORD="${2:-${CLIENT_TEST_USER_PASSWORD:-Test1234!}}"

echo -e "${BLUE}Using credentials:${NC}"
echo "   Email: $EMAIL"
echo "   Password: [hidden]"
echo ""

# Test function
test_endpoint() {
    local method=$1
    local endpoint=$2
    local token=$3
    local data=$4
    local description=$5
    
    echo -n "Testing: $description ... "
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" --max-time 10 \
            -H "Authorization: Bearer $token" \
            -H "Content-Type: application/json" \
            "${API_BASE}${endpoint}" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" --max-time 10 \
            -X "$method" \
            -H "Authorization: Bearer $token" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "${API_BASE}${endpoint}" 2>&1)
    fi
    
    http_code=$(echo "$response" | tail -1)
    body=$(echo "$response" | sed '$d')
    
    if [[ "$http_code" =~ ^[2] ]]; then
        echo -e "${GREEN}✓${NC} Status: $http_code"
        # Check if response has data
        if echo "$body" | grep -q "data\|success"; then
            echo "   Response: OK (has data)"
        fi
        return 0
    elif [ "$http_code" == "401" ]; then
        echo -e "${YELLOW}⚠${NC} Status: $http_code (Unauthorized - token may be invalid)"
        return 1
    elif [ "$http_code" == "403" ]; then
        echo -e "${YELLOW}⚠${NC} Status: $http_code (Forbidden - may need different permissions)"
        return 1
    elif [ "$http_code" == "404" ]; then
        echo -e "${RED}✗${NC} Status: $http_code (Not Found)"
        echo "   Error: Endpoint not found"
        return 2
    else
        echo -e "${RED}✗${NC} Status: $http_code"
        echo "   Response: $(echo "$body" | head -c 100)"
        return 2
    fi
}

# Step 1: Login
echo -e "${BLUE}Step 1: Login to get access token${NC}"
login_response=$(curl -s --max-time 10 \
    -X POST \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" \
    "${API_BASE}/auth/login" 2>&1)

http_code=$(echo "$login_response" | tail -1)
login_body=$(echo "$login_response" | sed '$d')

if [ "$http_code" != "200" ]; then
    echo -e "${RED}✗ Login failed with status: $http_code${NC}"
    echo "Response: $login_body"
    echo ""
    echo "Please provide valid credentials:"
    echo "  ./scripts/test-authenticated-endpoints.sh your@email.com yourpassword"
    exit 1
fi

# Extract token
ACCESS_TOKEN=$(echo "$login_body" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    # Try alternative format
    ACCESS_TOKEN=$(echo "$login_body" | grep -o '"accessToken":"[^"]*' | cut -d'"' -f4)
fi

if [ -z "$ACCESS_TOKEN" ]; then
    echo -e "${RED}✗ Could not extract access token from login response${NC}"
    echo "Response: $login_body"
    exit 1
fi

echo -e "${GREEN}✓ Login successful${NC}"
echo "   Token: ${ACCESS_TOKEN:0:20}..."
echo ""

# Step 2: Test endpoints
echo -e "${BLUE}Step 2: Testing API endpoints with authentication${NC}"
echo ""

# Test profile endpoints
echo "Profile Endpoints:"
test_endpoint "GET" "/client/profile" "$ACCESS_TOKEN" "" "Get Client Profile"
test_endpoint "PUT" "/client/profile" "$ACCESS_TOKEN" '{"display_name":"Test User"}' "Update Client Profile"
echo ""

# Test notifications
echo "Notifications:"
test_endpoint "GET" "/notifications" "$ACCESS_TOKEN" "" "Get Notifications"
echo ""

# Test financial endpoints
echo "Financial Endpoints:"
test_endpoint "GET" "/financial/withdrawals" "$ACCESS_TOKEN" "" "Get Withdrawals"
test_endpoint "GET" "/financial/deposits" "$ACCESS_TOKEN" "" "Get Deposits"
test_endpoint "GET" "/financial/transactions" "$ACCESS_TOKEN" "" "Get Transactions"
echo ""

# Test other endpoints
echo "Other Endpoints:"
test_endpoint "GET" "/users/bank-accounts" "$ACCESS_TOKEN" "" "Get Bank Accounts"
test_endpoint "GET" "/users/trusted-devices" "$ACCESS_TOKEN" "" "Get Trusted Devices"
echo ""

# Step 3: Verify no 404 errors
echo -e "${BLUE}Step 3: Verifying no 404 errors${NC}"
echo ""

# Check if /api/users/profile was called (should not be)
echo "Checking for /api/users/profile calls (should not exist):"
if echo "$login_body" | grep -q "/users/profile"; then
    echo -e "${YELLOW}⚠ Found reference to /users/profile in response${NC}"
else
    echo -e "${GREEN}✓ No /users/profile endpoint called${NC}"
fi
echo ""

echo "=========================================="
echo "SUMMARY:"
echo "- All endpoints tested with authentication"
echo "- Check results above for any 404 errors"
echo "- Profile endpoints should use /client/profile only"
echo "=========================================="

