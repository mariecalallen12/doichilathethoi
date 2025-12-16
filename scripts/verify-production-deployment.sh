#!/bin/bash
set -e

echo "🔍 Production Deployment Verification"
echo "====================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
API_BASE="${API_BASE:-http://localhost:8000}"
CLIENT_URL="${CLIENT_URL:-http://localhost:3002}"
ADMIN_URL="${ADMIN_URL:-http://localhost:3001}"

FAILURES=0
WARNINGS=0

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local expected_status=$3
    local description=$4
    local auth_header=$5
    
    echo -n "Testing $description... "
    
    headers=()
    if [ -n "$auth_header" ]; then
        headers+=(-H "Authorization: Bearer $auth_header")
    fi
    
    if [ "$method" = "GET" ]; then
        http_code=$(curl -s -o /dev/null -w "%{http_code}" "${headers[@]}" --max-time 10 "$endpoint" 2>/dev/null || echo "000")
    else
        http_code=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "${headers[@]}" --max-time 10 "$endpoint" 2>/dev/null || echo "000")
    fi
    
    if [ "$http_code" = "$expected_status" ] || [ "$http_code" = "200" ] || [ "$http_code" = "401" ]; then
        echo -e "${GREEN}✅ OK (HTTP $http_code)${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED (HTTP $http_code, expected $expected_status)${NC}"
        FAILURES=$((FAILURES + 1))
        return 1
    fi
}

# Verify Docker services are running
echo "📦 Verifying Docker Services:"
echo "-----------------------------"
services=("digital_utopia_postgres" "digital_utopia_redis" "digital_utopia_backend" 
          "digital_utopia_client" "digital_utopia_admin" "digital_utopia_nginx_proxy")

for service in "${services[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${service}$"; then
        echo -e "${GREEN}✅ $service is running${NC}"
    else
        echo -e "${RED}❌ $service is not running${NC}"
        FAILURES=$((FAILURES + 1))
    fi
done
echo ""

# Verify backend endpoints
echo "🔌 Verifying Backend Endpoints:"
echo "-------------------------------"

# Health check
test_endpoint "GET" "$API_BASE/api/health" "200" "Health check"

# Education endpoints
test_endpoint "GET" "$API_BASE/api/education/videos" "200" "Education - Videos"
test_endpoint "GET" "$API_BASE/api/education/ebooks" "200" "Education - Ebooks"
test_endpoint "GET" "$API_BASE/api/education/calendar" "200" "Education - Calendar"
test_endpoint "GET" "$API_BASE/api/education/reports" "200" "Education - Reports"

# Analysis endpoints
test_endpoint "GET" "$API_BASE/api/analysis/technical/BTCUSDT" "200" "Analysis - Technical"
test_endpoint "GET" "$API_BASE/api/analysis/fundamental/BTCUSDT" "200" "Analysis - Fundamental"
test_endpoint "GET" "$API_BASE/api/analysis/sentiment" "200" "Analysis - Sentiment"
test_endpoint "GET" "$API_BASE/api/analysis/signals" "200" "Analysis - Signals"

# Support endpoints
test_endpoint "GET" "$API_BASE/api/support/articles" "200" "Support - Articles"
test_endpoint "GET" "$API_BASE/api/support/categories" "200" "Support - Categories"
test_endpoint "GET" "$API_BASE/api/support/offices" "200" "Support - Offices"
test_endpoint "GET" "$API_BASE/api/support/channels" "200" "Support - Channels"
test_endpoint "GET" "$API_BASE/api/support/faq" "200" "Support - FAQ"

# Legal endpoints
test_endpoint "GET" "$API_BASE/api/legal/terms" "200" "Legal - Terms"
test_endpoint "GET" "$API_BASE/api/legal/privacy" "200" "Legal - Privacy"
test_endpoint "GET" "$API_BASE/api/legal/risk-warning" "200" "Legal - Risk Warning"

echo ""

# Verify frontend apps
echo "🌐 Verifying Frontend Apps:"
echo "--------------------------"
test_endpoint "GET" "$CLIENT_URL/health" "200" "Client App"
test_endpoint "GET" "$ADMIN_URL/health" "200" "Admin App"
echo ""

# Verify database
echo "🗄️  Verifying Database:"
echo "----------------------"
if docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "SELECT 1" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Database connection OK${NC}"
    
    # Check if tables exist
    table_count=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
    if [ -n "$table_count" ] && [ "$table_count" -gt 0 ]; then
        echo -e "${GREEN}✅ Database has $table_count tables${NC}"
    else
        echo -e "${YELLOW}⚠️  Warning: Could not verify table count${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${RED}❌ Database connection FAILED${NC}"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# Verify Redis
echo "🔴 Verifying Redis:"
echo "------------------"
if docker exec digital_utopia_redis redis-cli ping >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis connection OK${NC}"
else
    echo -e "${RED}❌ Redis connection FAILED${NC}"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# Summary
echo "====================================="
if [ $FAILURES -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All verifications passed!${NC}"
    exit 0
elif [ $FAILURES -eq 0 ]; then
    echo -e "${YELLOW}⚠️  All critical checks passed, but $WARNINGS warning(s)${NC}"
    exit 0
else
    echo -e "${RED}❌ Deployment verification failed: $FAILURES failure(s), $WARNINGS warning(s)${NC}"
    exit 1
fi

