#!/bin/bash

# Script kiểm tra các API endpoints trên production
# Domain: https://cmeetrading.com

DOMAIN="https://cmeetrading.com"
API_BASE="${DOMAIN}/api"

echo "=========================================="
echo "KIỂM TRA PRODUCTION API ENDPOINTS"
echo "Domain: $DOMAIN"
echo "Date: $(date)"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local description=$3
    
    echo -n "Testing: $description ... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "${API_BASE}${endpoint}" 2>&1)
    status_code="${response: -3}"
    
    if [[ "$status_code" == "$expected_status" ]] || [[ "$status_code" =~ ^[23] ]]; then
        echo -e "${GREEN}✓${NC} Status: $status_code"
        return 0
    elif [[ "$status_code" == "404" ]]; then
        echo -e "${RED}✗${NC} Status: $status_code (404 Not Found - Có thể do duplicate /api/ prefix)"
        return 1
    else
        echo -e "${YELLOW}⚠${NC} Status: $status_code"
        return 2
    fi
}

# Test endpoints
echo "1. Health Check:"
test_endpoint "/health" "200" "API Health"
echo ""

echo "2. Profile Endpoints:"
test_endpoint "/client/profile" "401" "Client Profile (expect 401 - requires auth)"
test_endpoint "/users/profile" "401" "Users Profile (expect 401 - requires auth)"
echo ""

echo "3. Notifications:"
test_endpoint "/notifications" "401" "Notifications (expect 401 - requires auth)"
echo ""

echo "4. Financial Endpoints:"
test_endpoint "/financial/withdrawals" "401" "Withdrawals (expect 401 - requires auth)"
test_endpoint "/financial/deposits" "401" "Deposits (expect 401 - requires auth)"
test_endpoint "/financial/transactions" "401" "Transactions (expect 401 - requires auth)"
echo ""

echo "5. Kiểm tra duplicate /api/api/ prefix:"
echo -n "   Checking for duplicate patterns ... "
if curl -s --max-time 10 "${DOMAIN}/" 2>&1 | grep -q "/api/api/"; then
    echo -e "${RED}✗${NC} Tìm thấy duplicate /api/api/ trong HTML"
else
    echo -e "${GREEN}✓${NC} Không tìm thấy duplicate /api/api/"
fi
echo ""

echo "6. Kiểm tra SSL Certificate:"
echo -n "   SSL Status ... "
ssl_check=$(echo | openssl s_client -connect cmeetrading.com:443 -servername cmeetrading.com 2>&1 | grep -c "Verify return code: 0")
if [[ $ssl_check -gt 0 ]]; then
    echo -e "${GREEN}✓${NC} SSL Certificate hợp lệ"
else
    echo -e "${YELLOW}⚠${NC} Không thể xác minh SSL"
fi
echo ""

echo "=========================================="
echo "KẾT QUẢ:"
echo "- Các endpoint trả về 401 là bình thường (cần authentication)"
echo "- Các endpoint trả về 404 có thể do duplicate /api/ prefix"
echo "- Kiểm tra kỹ các endpoint trả về 404"
echo "=========================================="

