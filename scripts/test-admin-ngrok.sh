#!/bin/bash
# Script test Admin App qua domain
# Verify tất cả routes, API endpoints và static assets

set -e

DOMAIN="cmeetrading.com"
BASE_URL="https://${DOMAIN}"
ADMIN_URL="${BASE_URL}/admin"
API_URL="${BASE_URL}/api"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

echo "=========================================="
echo "TEST ADMIN APP QUA NGROK"
echo "=========================================="
echo "Domain: ${DOMAIN}"
echo ""

# Function to test endpoint
test_endpoint() {
    local url=$1
    local description=$2
    local expected_status=${3:-200}
    
    echo -n "Testing: ${description}... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "domain-skip-browser-warning: true" \
        -H "User-Agent: Mozilla/5.0" \
        "${url}" 2>&1)
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✓${NC} (HTTP ${response})"
        return 0
    else
        echo -e "${RED}✗${NC} (HTTP ${response}, expected ${expected_status})"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

# Function to test API endpoint
test_api_endpoint() {
    local endpoint=$1
    local description=$2
    local url="${API_URL}${endpoint}"
    
    echo -n "Testing API: ${description}... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "domain-skip-browser-warning: true" \
        -H "Content-Type: application/json" \
        "${url}" 2>&1)
    
    if [ "$response" = "200" ] || [ "$response" = "401" ] || [ "$response" = "404" ]; then
        echo -e "${GREEN}✓${NC} (HTTP ${response})"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} (HTTP ${response})"
        WARNINGS=$((WARNINGS + 1))
        return 1
    fi
}

# 1. Test Admin App Routes
echo -e "${GREEN}[1] Testing Admin App Routes${NC}"
echo "----------------------------------------"
test_endpoint "${ADMIN_URL}/" "Admin App Root"
test_endpoint "${ADMIN_URL}/login" "Login Page"
test_endpoint "${ADMIN_URL}/dashboard" "Dashboard (redirects to login if not auth)"
test_endpoint "${ADMIN_URL}/users" "User Management"
test_endpoint "${ADMIN_URL}/trading" "Trading Management"
test_endpoint "${ADMIN_URL}/financial" "Financial Management"
test_endpoint "${ADMIN_URL}/analytics" "Analytics & Reports"
test_endpoint "${ADMIN_URL}/settings" "System Settings"
test_endpoint "${ADMIN_URL}/admin-controls" "Admin Trading Controls"
echo ""

# 2. Test Static Assets
echo -e "${GREEN}[2] Testing Static Assets${NC}"
echo "----------------------------------------"
# Get asset paths from HTML
html_content=$(curl -s -H "domain-skip-browser-warning: true" "${ADMIN_URL}/" 2>&1)
js_files=$(echo "$html_content" | grep -oP 'src="[^"]*\.js"' | sed 's/src="//;s/"//' | head -5)
css_files=$(echo "$html_content" | grep -oP 'href="[^"]*\.css"' | sed 's/href="//;s/"//' | head -5)

for js in $js_files; do
    if [[ $js == /* ]]; then
        test_endpoint "${BASE_URL}${js}" "JS: $(basename $js)"
    fi
done

for css in $css_files; do
    if [[ $css == /* ]]; then
        test_endpoint "${BASE_URL}${css}" "CSS: $(basename $css)"
    fi
done
echo ""

# 3. Test API Endpoints
echo -e "${GREEN}[3] Testing API Endpoints${NC}"
echo "----------------------------------------"
test_api_endpoint "/health" "Health Check"
test_api_endpoint "/auth/login" "Login Endpoint (POST)"
test_api_endpoint "/admin/users" "Admin Users List"
test_api_endpoint "/admin/platform/stats" "Platform Stats"
test_api_endpoint "/admin/settings/registration-fields" "Registration Fields Config"
echo ""

# 4. Test CORS Headers
echo -e "${GREEN}[4] Testing CORS Headers${NC}"
echo "----------------------------------------"
cors_headers=$(curl -s -I -H "domain-skip-browser-warning: true" \
    -H "Origin: ${BASE_URL}" \
    "${API_URL}/health" 2>&1 | grep -i "access-control")

if echo "$cors_headers" | grep -q "access-control"; then
    echo -e "${GREEN}✓ CORS headers present${NC}"
    echo "$cors_headers"
else
    echo -e "${YELLOW}⚠ CORS headers not found${NC}"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# 5. Test Content-Security-Policy
echo -e "${GREEN}[5] Testing Content-Security-Policy${NC}"
echo "----------------------------------------"
csp_header=$(curl -s -I -H "domain-skip-browser-warning: true" \
    "${ADMIN_URL}/" 2>&1 | grep -i "content-security-policy" || echo "")

if echo "$csp_header" | grep -q "topical-sadly-lacewing.domain-free.app"; then
    echo -e "${GREEN}✓ CSP includes domain domain${NC}"
else
    echo -e "${YELLOW}⚠ CSP may not include domain domain${NC}"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# 6. Test Router Navigation (check HTML content)
echo -e "${GREEN}[6] Testing Router Configuration${NC}"
echo "----------------------------------------"
html_content=$(curl -s -H "domain-skip-browser-warning: true" "${ADMIN_URL}/" 2>&1)

if echo "$html_content" | grep -q 'base href="/admin/"'; then
    echo -e "${GREEN}✓ Base tag configured correctly${NC}"
else
    echo -e "${RED}✗ Base tag not found or incorrect${NC}"
    ERRORS=$((ERRORS + 1))
fi

if echo "$html_content" | grep -q 'id="app"'; then
    echo -e "${GREEN}✓ Vue app root element found${NC}"
else
    echo -e "${RED}✗ Vue app root element not found${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 7. Test API Base URL in JavaScript
echo -e "${GREEN}[7] Testing API Base URL Configuration${NC}"
echo "----------------------------------------"
# Try to extract API base URL from JavaScript
js_content=$(curl -s -H "domain-skip-browser-warning: true" \
    "${ADMIN_URL}/assets/index-C4oQ-404.js" 2>&1 | head -100)

if echo "$js_content" | grep -q "topical-sadly-lacewing.domain-free.app"; then
    echo -e "${GREEN}✓ API base URL includes domain domain${NC}"
else
    echo -e "${YELLOW}⚠ API base URL may not be configured for domain${NC}"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Summary
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo -e "Errors: ${RED}${ERRORS}${NC}"
echo -e "Warnings: ${YELLOW}${WARNINGS}${NC}"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All critical tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please review above.${NC}"
    exit 1
fi

