#!/bin/bash

# Script monitor production errors và 404 requests
# Usage: ./scripts/monitor-production-errors.sh [--follow]

DOMAIN="https://cmeetrading.com"
CLIENT_CONTAINER="digital_utopia_client"
BACKEND_CONTAINER=$(docker ps --filter "name=backend" --format "{{.Names}}" | head -1)

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "PRODUCTION ERROR MONITOR"
echo "Date: $(date)"
echo "=========================================="
echo ""

# Function to check 404 errors
check_404_errors() {
    echo -e "${BLUE}1. Checking for 404 errors in client logs:${NC}"
    local count=$(docker logs --tail 100 "$CLIENT_CONTAINER" 2>&1 | grep -c "404")
    if [ "$count" -gt 0 ]; then
        echo -e "${RED}   ⚠️  Found $count 404 errors in recent logs${NC}"
        echo "   Recent 404 errors:"
        docker logs --tail 100 "$CLIENT_CONTAINER" 2>&1 | grep "404" | tail -5 | sed 's/^/   /'
    else
        echo -e "${GREEN}   ✓ No 404 errors found in recent logs${NC}"
    fi
    echo ""
}

# Function to check for /api/users/profile requests
check_users_profile_endpoint() {
    echo -e "${BLUE}2. Checking for /api/users/profile requests:${NC}"
    local count=$(docker logs --tail 200 "$CLIENT_CONTAINER" 2>&1 | grep -c "/api/users/profile")
    if [ "$count" -gt 0 ]; then
        echo -e "${YELLOW}   ⚠️  Found $count requests to /api/users/profile${NC}"
        echo "   This endpoint returns 404 - should be removed from fallback"
    else
        echo -e "${GREEN}   ✓ No requests to /api/users/profile found${NC}"
    fi
    echo ""
}

# Function to check backend errors
check_backend_errors() {
    if [ -n "$BACKEND_CONTAINER" ]; then
        echo -e "${BLUE}3. Checking backend logs for errors:${NC}"
        local error_count=$(docker logs --tail 100 "$BACKEND_CONTAINER" 2>&1 | grep -iE "error|exception|traceback" | wc -l)
        if [ "$error_count" -gt 0 ]; then
            echo -e "${YELLOW}   ⚠️  Found $error_count errors in backend logs${NC}"
            docker logs --tail 100 "$BACKEND_CONTAINER" 2>&1 | grep -iE "error|exception" | tail -3 | sed 's/^/   /'
        else
            echo -e "${GREEN}   ✓ No errors found in backend logs${NC}"
        fi
    else
        echo -e "${YELLOW}   3. Backend container not found${NC}"
    fi
    echo ""
}

# Function to check API endpoint health
check_api_health() {
    echo -e "${BLUE}4. Checking API endpoint health:${NC}"
    
    endpoints=(
        "/api/health"
        "/api/client/profile"
        "/api/notifications"
        "/api/financial/withdrawals"
    )
    
    for endpoint in "${endpoints[@]}"; do
        status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "${DOMAIN}${endpoint}" 2>&1)
        if [[ "$status" =~ ^[23] ]]; then
            echo -e "   ${GREEN}✓${NC} $endpoint: $status"
        elif [ "$status" == "404" ]; then
            echo -e "   ${RED}✗${NC} $endpoint: $status (Not Found)"
        else
            echo -e "   ${YELLOW}⚠${NC} $endpoint: $status"
        fi
    done
    echo ""
}

# Function to analyze access patterns
analyze_access_patterns() {
    echo -e "${BLUE}5. Analyzing API access patterns (last 200 requests):${NC}"
    docker logs --tail 200 "$CLIENT_CONTAINER" 2>&1 | \
        grep -oE "(GET|POST|PUT|DELETE) /api/[^ ]*" | \
        sort | uniq -c | sort -rn | head -10 | \
        sed 's/^/   /'
    echo ""
}

# Function to check for duplicate /api/api/ patterns
check_duplicate_api() {
    echo -e "${BLUE}6. Checking for duplicate /api/api/ patterns:${NC}"
    local count=$(docker logs --tail 200 "$CLIENT_CONTAINER" 2>&1 | grep -c "/api/api/")
    if [ "$count" -gt 0 ]; then
        echo -e "${RED}   ✗ Found $count requests with duplicate /api/api/ pattern${NC}"
        docker logs --tail 200 "$CLIENT_CONTAINER" 2>&1 | grep "/api/api/" | tail -3 | sed 's/^/   /'
    else
        echo -e "${GREEN}   ✓ No duplicate /api/api/ patterns found${NC}"
    fi
    echo ""
}

# Main execution
check_404_errors
check_users_profile_endpoint
check_backend_errors
check_api_health
analyze_access_patterns
check_duplicate_api

echo "=========================================="
echo "SUMMARY:"
echo "- Monitor completed at $(date)"
echo "- Check logs above for any issues"
echo "=========================================="

# Follow mode
if [ "$1" == "--follow" ]; then
    echo ""
    echo "Following logs (Ctrl+C to stop)..."
    docker logs -f "$CLIENT_CONTAINER" 2>&1 | grep --line-buffered -E "404|error|Error|/api/users/profile"
fi

