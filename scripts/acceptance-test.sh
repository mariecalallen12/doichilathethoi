#!/bin/bash

# Automated Acceptance Testing Script
# Tests endpoints, health checks, SSL verification, and domain accessibility
# Usage: ./scripts/acceptance-test.sh [domain]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

DOMAIN="${1:-cmeetrading.com}"
BASE_URL="https://${DOMAIN}"
HTTP_URL="http://${DOMAIN}"
REPORT_FILE="acceptance_test_report_$(date +%Y%m%d_%H%M%S).txt"

# Test results
PASSED=0
FAILED=0
WARNINGS=0

# Function to print step
print_step() {
    echo -e "\n${BLUE}=========================================="
    echo -e "$1"
    echo -e "==========================================${NC}\n"
}

# Function to print test result
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS: $2${NC}"
        ((PASSED++))
        echo "[PASS] $2" >> "$REPORT_FILE"
        return 0
    else
        echo -e "${RED}✗ FAIL: $2${NC}"
        ((FAILED++))
        echo "[FAIL] $2" >> "$REPORT_FILE"
        return 1
    fi
}

# Function to print warning
test_warning() {
    echo -e "${YELLOW}⚠ WARN: $1${NC}"
    ((WARNINGS++))
    echo "[WARN] $1" >> "$REPORT_FILE"
}

# Initialize report file
echo "Acceptance Test Report - $(date)" > "$REPORT_FILE"
echo "Domain: $DOMAIN" >> "$REPORT_FILE"
echo "Base URL: $BASE_URL" >> "$REPORT_FILE"
echo "========================================" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

print_step "Acceptance Testing for $DOMAIN"

echo -e "${YELLOW}Test report will be saved to: $REPORT_FILE${NC}\n"

# ============================================
# 1. DNS Resolution Test
# ============================================
print_step "1. DNS Resolution Test"

if dig +short "$DOMAIN" | grep -q .; then
    DNS_IP=$(dig +short "$DOMAIN" | head -1)
    test_result 0 "DNS resolution for $DOMAIN → $DNS_IP"
else
    test_result 1 "DNS resolution for $DOMAIN"
fi

# ============================================
# 2. HTTP to HTTPS Redirect Test
# ============================================
print_step "2. HTTP to HTTPS Redirect Test"

HTTP_REDIRECT=$(curl -s -o /dev/null -w "%{http_code}" -L "$HTTP_URL" 2>/dev/null || echo "000")
if [ "$HTTP_REDIRECT" = "200" ] || [ "$HTTP_REDIRECT" = "301" ] || [ "$HTTP_REDIRECT" = "302" ]; then
    test_result 0 "HTTP redirect test (HTTP code: $HTTP_REDIRECT)"
else
    test_result 1 "HTTP redirect test (HTTP code: $HTTP_REDIRECT)"
fi

# ============================================
# 3. SSL Certificate Test
# ============================================
print_step "3. SSL Certificate Test"

# Check if certificate exists and is valid
SSL_TEST=$(echo | openssl s_client -connect "${DOMAIN}:443" -servername "$DOMAIN" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
if [ -n "$SSL_TEST" ]; then
    test_result 0 "SSL certificate exists and is valid"
    
    # Check certificate expiration
    EXPIRY=$(echo | openssl s_client -connect "${DOMAIN}:443" -servername "$DOMAIN" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
    if [ -n "$EXPIRY" ]; then
        echo -e "${YELLOW}  Certificate expires: $EXPIRY${NC}"
        echo "  Certificate expires: $EXPIRY" >> "$REPORT_FILE"
    fi
else
    test_result 1 "SSL certificate validation"
fi

# Check SSL protocol versions
SSL_PROTO=$(echo | openssl s_client -connect "${DOMAIN}:443" -servername "$DOMAIN" 2>/dev/null | grep "Protocol" | awk '{print $3}')
if [ -n "$SSL_PROTO" ]; then
    echo -e "${YELLOW}  SSL Protocol: $SSL_PROTO${NC}"
    echo "  SSL Protocol: $SSL_PROTO" >> "$REPORT_FILE"
fi

# ============================================
# 4. HTTPS Connectivity Test
# ============================================
print_step "4. HTTPS Connectivity Test"

HTTPS_CODE=$(curl -s -o /dev/null -w "%{http_code}" -k "$BASE_URL" 2>/dev/null || echo "000")
if [ "$HTTPS_CODE" = "200" ]; then
    test_result 0 "HTTPS connectivity (HTTP code: $HTTPS_CODE)"
else
    test_result 1 "HTTPS connectivity (HTTP code: $HTTPS_CODE)"
fi

# ============================================
# 5. Health Check Endpoints
# ============================================
print_step "5. Health Check Endpoints"

# Main health endpoint
HEALTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health" 2>/dev/null || echo "000")
if [ "$HEALTH_CODE" = "200" ]; then
    test_result 0 "Main health endpoint (/health)"
else
    test_result 1 "Main health endpoint (/health) - HTTP code: $HEALTH_CODE"
fi

# API health endpoint
API_HEALTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/health" 2>/dev/null || echo "000")
if [ "$API_HEALTH_CODE" = "200" ]; then
    test_result 0 "API health endpoint (/api/health)"
else
    test_result 1 "API health endpoint (/api/health) - HTTP code: $API_HEALTH_CODE"
fi

# ============================================
# 6. Security Headers Test
# ============================================
print_step "6. Security Headers Test"

HEADERS=$(curl -s -I "$BASE_URL" 2>/dev/null || echo "")

# Check HSTS
if echo "$HEADERS" | grep -qi "strict-transport-security"; then
    test_result 0 "HSTS header present"
else
    test_warning "HSTS header not found"
fi

# Check X-Frame-Options
if echo "$HEADERS" | grep -qi "x-frame-options"; then
    test_result 0 "X-Frame-Options header present"
else
    test_warning "X-Frame-Options header not found"
fi

# Check X-Content-Type-Options
if echo "$HEADERS" | grep -qi "x-content-type-options"; then
    test_result 0 "X-Content-Type-Options header present"
else
    test_warning "X-Content-Type-Options header not found"
fi

# ============================================
# 7. Client Application Routes
# ============================================
print_step "7. Client Application Routes"

# Homepage
HOME_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/" 2>/dev/null || echo "000")
if [ "$HOME_CODE" = "200" ]; then
    test_result 0 "Homepage (/)"
else
    test_result 1 "Homepage (/) - HTTP code: $HOME_CODE"
fi

# Registration page
REG_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/register" 2>/dev/null || echo "000")
if [ "$REG_CODE" = "200" ]; then
    test_result 0 "Registration page (/register)"
else
    test_result 1 "Registration page (/register) - HTTP code: $REG_CODE"
fi

# Login page
LOGIN_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/login" 2>/dev/null || echo "000")
if [ "$LOGIN_CODE" = "200" ]; then
    test_result 0 "Login page (/login)"
else
    test_result 1 "Login page (/login) - HTTP code: $LOGIN_CODE"
fi

# ============================================
# 8. Admin Application Routes
# ============================================
print_step "8. Admin Application Routes"

# Admin login
ADMIN_LOGIN_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/admin/login" 2>/dev/null || echo "000")
if [ "$ADMIN_LOGIN_CODE" = "200" ]; then
    test_result 0 "Admin login page (/admin/login)"
else
    test_result 1 "Admin login page (/admin/login) - HTTP code: $ADMIN_LOGIN_CODE"
fi

# Admin dashboard (may require auth, so 200 or 302/401 is acceptable)
ADMIN_DASH_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/admin/dashboard" 2>/dev/null || echo "000")
if [ "$ADMIN_DASH_CODE" = "200" ] || [ "$ADMIN_DASH_CODE" = "302" ] || [ "$ADMIN_DASH_CODE" = "401" ]; then
    test_result 0 "Admin dashboard (/admin/dashboard) - HTTP code: $ADMIN_DASH_CODE"
else
    test_result 1 "Admin dashboard (/admin/dashboard) - HTTP code: $ADMIN_DASH_CODE"
fi

# ============================================
# 9. API Endpoints Test
# ============================================
print_step "9. API Endpoints Test"

# Public API endpoints (should work without auth)
REG_FIELDS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/client/settings/registration-fields" 2>/dev/null || echo "000")
if [ "$REG_FIELDS_CODE" = "200" ]; then
    test_result 0 "Registration fields API (/api/client/settings/registration-fields)"
else
    test_result 1 "Registration fields API - HTTP code: $REG_FIELDS_CODE"
fi

# ============================================
# 10. CORS Headers Test
# ============================================
print_step "10. CORS Headers Test"

CORS_HEADERS=$(curl -s -I -X OPTIONS "$BASE_URL/api/health" 2>/dev/null || echo "")
if echo "$CORS_HEADERS" | grep -qi "access-control-allow-origin"; then
    test_result 0 "CORS headers present"
else
    test_warning "CORS headers not found"
fi

# ============================================
# 11. Response Time Test
# ============================================
print_step "11. Response Time Test"

RESPONSE_TIME=$(curl -s -o /dev/null -w "%{time_total}" "$BASE_URL/" 2>/dev/null || echo "999")
RESPONSE_TIME_MS=$(echo "$RESPONSE_TIME * 1000" | bc | cut -d. -f1)

if [ "$RESPONSE_TIME_MS" -lt 3000 ]; then
    test_result 0 "Response time acceptable (${RESPONSE_TIME_MS}ms)"
else
    test_warning "Response time slow (${RESPONSE_TIME_MS}ms)"
fi

echo -e "${YELLOW}  Response time: ${RESPONSE_TIME_MS}ms${NC}"
echo "  Response time: ${RESPONSE_TIME_MS}ms" >> "$REPORT_FILE"

# ============================================
# 12. Docker Container Status
# ============================================
print_step "12. Docker Container Status"

if command -v docker &> /dev/null; then
    # Check nginx container
    if docker ps | grep -q "digital_utopia_nginx_proxy"; then
        test_result 0 "Nginx container running"
    else
        test_result 1 "Nginx container not running"
    fi
    
    # Check backend container
    if docker ps | grep -q "digital_utopia_backend"; then
        test_result 0 "Backend container running"
    else
        test_result 1 "Backend container not running"
    fi
    
    # Check client container
    if docker ps | grep -q "digital_utopia_client"; then
        test_result 0 "Client container running"
    else
        test_result 1 "Client container not running"
    fi
    
    # Check admin container
    if docker ps | grep -q "digital_utopia_admin"; then
        test_result 0 "Admin container running"
    else
        test_result 1 "Admin container not running"
    fi
else
    test_warning "Docker not available for container checks"
fi

# ============================================
# Summary
# ============================================
print_step "Test Summary"

TOTAL=$((PASSED + FAILED + WARNINGS))

echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
echo -e "${BLUE}Total: $TOTAL${NC}"

echo "" >> "$REPORT_FILE"
echo "========================================" >> "$REPORT_FILE"
echo "Summary:" >> "$REPORT_FILE"
echo "  Passed: $PASSED" >> "$REPORT_FILE"
echo "  Failed: $FAILED" >> "$REPORT_FILE"
echo "  Warnings: $WARNINGS" >> "$REPORT_FILE"
echo "  Total: $TOTAL" >> "$REPORT_FILE"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ All critical tests passed!${NC}"
    echo "Status: PASSED" >> "$REPORT_FILE"
    exit 0
else
    echo -e "\n${RED}✗ Some tests failed. Please review the report.${NC}"
    echo "Status: FAILED" >> "$REPORT_FILE"
    exit 1
fi

