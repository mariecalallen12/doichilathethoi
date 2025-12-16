#!/bin/bash
# Test Production URLs Script
# Verifies HTTPS endpoints, security headers, and SSL certificates

set -e

# Configuration
DOMAIN="${PRODUCTION_DOMAIN:-cmeetrading.com}"
ADMIN_DOMAIN="${ADMIN_DOMAIN:-admin.cmeetrading.com}"
LOCAL_TEST="${LOCAL_TEST:-false}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
PASSED=0
FAILED=0
WARNINGS=0

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    ((PASSED++))
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
    ((FAILED++))
}

log_warn() {
    echo -e "${YELLOW}[⚠]${NC} $1"
    ((WARNINGS++))
}

# Test HTTPS endpoint
test_https_endpoint() {
    local url=$1
    local name=$2
    
    log_info "Testing HTTPS endpoint: $name ($url)"
    
    # Test if endpoint is accessible
    if curl -k -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|301\|302"; then
        log_success "$name is accessible via HTTPS"
        return 0
    else
        log_error "$name is not accessible via HTTPS"
        return 1
    fi
}

# Test SSL certificate
test_ssl_certificate() {
    local domain=$1
    local name=$2
    
    log_info "Testing SSL certificate for: $name ($domain)"
    
    if [ "$LOCAL_TEST" = "true" ]; then
        # For local testing, skip certificate validation
        log_warn "Skipping SSL certificate validation (local test mode)"
        return 0
    fi
    
    # Check certificate validity
    cert_info=$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
    
    if [ -n "$cert_info" ]; then
        log_success "SSL certificate is valid for $domain"
        
        # Extract expiration date
        not_after=$(echo "$cert_info" | grep "notAfter" | cut -d= -f2)
        log_info "Certificate expires: $not_after"
        
        # Check if certificate is expired or expiring soon
        expiry_epoch=$(date -d "$not_after" +%s 2>/dev/null || echo 0)
        current_epoch=$(date +%s)
        days_until_expiry=$(( (expiry_epoch - current_epoch) / 86400 ))
        
        if [ $days_until_expiry -lt 0 ]; then
            log_error "Certificate has expired!"
            return 1
        elif [ $days_until_expiry -lt 30 ]; then
            log_warn "Certificate expires in $days_until_expiry days"
        else
            log_success "Certificate is valid for $days_until_expiry more days"
        fi
        
        return 0
    else
        log_error "Could not retrieve SSL certificate for $domain"
        return 1
    fi
}

# Test security headers
test_security_headers() {
    local url=$1
    local name=$2
    
    log_info "Testing security headers for: $name"
    
    headers=$(curl -k -s -I "$url" 2>/dev/null)
    missing_headers=()
    
    # Required security headers
    required_headers=(
        "Strict-Transport-Security"
        "X-Content-Type-Options"
        "X-Frame-Options"
        "X-XSS-Protection"
    )
    
    # Recommended security headers
    recommended_headers=(
        "Content-Security-Policy"
        "Referrer-Policy"
        "Permissions-Policy"
    )
    
    # Check required headers
    for header in "${required_headers[@]}"; do
        if echo "$headers" | grep -qi "$header:"; then
            header_value=$(echo "$headers" | grep -i "$header:" | cut -d: -f2 | xargs)
            log_success "$header: $header_value"
        else
            log_error "Missing required header: $header"
            missing_headers+=("$header")
        fi
    done
    
    # Check recommended headers
    for header in "${recommended_headers[@]}"; do
        if echo "$headers" | grep -qi "$header:"; then
            header_value=$(echo "$headers" | grep -i "$header:" | cut -d: -f2 | xargs)
            log_info "$header: $header_value"
        else
            log_warn "Missing recommended header: $header"
        fi
    done
    
    if [ ${#missing_headers[@]} -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

# Test HTTP to HTTPS redirect
test_https_redirect() {
    local domain=$1
    local name=$2
    
    log_info "Testing HTTP to HTTPS redirect for: $name"
    
    redirect_url=$(curl -s -o /dev/null -w "%{redirect_url}" "http://$domain" 2>/dev/null)
    
    if echo "$redirect_url" | grep -q "https://"; then
        log_success "HTTP to HTTPS redirect is working"
        return 0
    else
        log_error "HTTP to HTTPS redirect is not working"
        return 1
    fi
}

# Test API endpoints
test_api_endpoints() {
    local base_url=$1
    
    log_info "Testing API endpoints"
    
    api_endpoints=(
        "/api/health"
        "/api/auth/login"
    )
    
    for endpoint in "${api_endpoints[@]}"; do
        url="${base_url}${endpoint}"
        status_code=$(curl -k -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
        
        if [ "$status_code" = "200" ] || [ "$status_code" = "401" ] || [ "$status_code" = "404" ]; then
            log_success "API endpoint $endpoint: HTTP $status_code"
        else
            log_error "API endpoint $endpoint: HTTP $status_code"
        fi
    done
}

# Test response time
test_response_time() {
    local url=$1
    local name=$2
    local max_time=2  # seconds
    
    log_info "Testing response time for: $name"
    
    response_time=$(curl -k -s -o /dev/null -w "%{time_total}" "$url" 2>/dev/null)
    
    if (( $(echo "$response_time < $max_time" | bc -l) )); then
        log_success "Response time: ${response_time}s (target: <${max_time}s)"
    else
        log_warn "Response time: ${response_time}s (target: <${max_time}s)"
    fi
}

# Main execution
main() {
    echo "=========================================="
    echo "Production URLs Test"
    echo "Date: $(date)"
    echo "=========================================="
    echo ""
    
    if [ "$LOCAL_TEST" = "true" ]; then
        log_info "Running in LOCAL TEST mode"
        DOMAIN="localhost"
        ADMIN_DOMAIN="localhost"
    fi
    
    # Test main domain
    echo "=== Testing Main Domain: $DOMAIN ==="
    test_https_endpoint "https://$DOMAIN" "Main Domain"
    test_ssl_certificate "$DOMAIN" "Main Domain"
    test_security_headers "https://$DOMAIN" "Main Domain"
    test_https_redirect "$DOMAIN" "Main Domain"
    test_response_time "https://$DOMAIN" "Main Domain"
    test_api_endpoints "https://$DOMAIN"
    echo ""
    
    # Test admin domain
    echo "=== Testing Admin Domain: $ADMIN_DOMAIN ==="
    test_https_endpoint "https://$ADMIN_DOMAIN" "Admin Domain"
    test_ssl_certificate "$ADMIN_DOMAIN" "Admin Domain"
    test_security_headers "https://$ADMIN_DOMAIN" "Admin Domain"
    test_https_redirect "$ADMIN_DOMAIN" "Admin Domain"
    test_response_time "https://$ADMIN_DOMAIN" "Admin Domain"
    echo ""
    
    # Summary
    echo "=========================================="
    echo "Test Summary"
    echo "=========================================="
    echo -e "${GREEN}Passed: $PASSED${NC}"
    echo -e "${RED}Failed: $FAILED${NC}"
    echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
    echo ""
    
    if [ $FAILED -eq 0 ]; then
        log_success "All critical tests passed!"
        exit 0
    else
        log_error "Some tests failed. Please review the output above."
        exit 1
    fi
}

# Run main function
main
