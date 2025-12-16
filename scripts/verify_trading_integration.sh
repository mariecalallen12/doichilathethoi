#!/bin/bash
# Script to verify trading integration with core-main (OPEX)

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$BASE_DIR/backend"
CORE_MAIN_DIR="$BASE_DIR/core-main"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Trading Integration Verification"
echo "=========================================="
echo ""

# 1. Check OPEX configuration
echo "1. Checking OPEX Configuration..."
echo "-----------------------------------"

if [ -f "$BACKEND_DIR/app/core/config.py" ]; then
    OPEX_URL=$(grep -E "OPEX_API_URL" "$BACKEND_DIR/app/core/config.py" | head -1 | sed -n "s/.*OPEX_API_URL.*=.*['\"]([^'\"]*)['\"].*/\1/p" || echo "http://opex-api:8080")
    echo "   OPEX_API_URL: $OPEX_URL"
    
    if [ -f "$BACKEND_DIR/.env" ]; then
        ENV_OPEX=$(grep -E "^OPEX_API_URL" "$BACKEND_DIR/.env" | cut -d'=' -f2 || echo "")
        if [ -n "$ENV_OPEX" ]; then
            echo "   Found in .env: $ENV_OPEX"
            OPEX_URL="$ENV_OPEX"
        fi
    fi
else
    echo -e "${RED}   ❌ config.py not found${NC}"
fi

echo ""

# 2. Check if core-main docker-compose exists
echo "2. Checking core-main setup..."
echo "-----------------------------------"

if [ -f "$CORE_MAIN_DIR/docker-compose.yml" ]; then
    echo -e "${GREEN}   ✅ docker-compose.yml found${NC}"
    
    # Check if services are defined
    SERVICES=$(grep -E "^  [a-z-]+:" "$CORE_MAIN_DIR/docker-compose.yml" | grep -v "version:" | sed 's/://' | tr '\n' ' ')
    echo "   Services found: $SERVICES"
    
    # Check for key services
    if grep -q "api:" "$CORE_MAIN_DIR/docker-compose.yml"; then
        echo -e "${GREEN}   ✅ API service found${NC}"
    else
        echo -e "${YELLOW}   ⚠️  API service not found${NC}"
    fi
    
    if grep -q "matching-engine:" "$CORE_MAIN_DIR/docker-compose.yml"; then
        echo -e "${GREEN}   ✅ Matching engine service found${NC}"
    else
        echo -e "${YELLOW}   ⚠️  Matching engine service not found${NC}"
    fi
else
    echo -e "${RED}   ❌ docker-compose.yml not found${NC}"
fi

echo ""

# 3. Check if core-main services are running
echo "3. Checking core-main services status..."
echo "-----------------------------------"

if command -v docker &> /dev/null; then
    if docker ps | grep -q "opex"; then
        echo -e "${GREEN}   ✅ OPEX containers are running${NC}"
        docker ps | grep "opex" | awk '{print "   - " $2 " (" $1 ")"}'
    else
        echo -e "${YELLOW}   ⚠️  No OPEX containers found running${NC}"
        echo "   To start: cd $CORE_MAIN_DIR && docker-compose up -d"
    fi
else
    echo -e "${YELLOW}   ⚠️  Docker not available${NC}"
fi

echo ""

# 4. Test OPEX API health check
echo "4. Testing OPEX API health check..."
echo "-----------------------------------"

# Try different possible URLs
OPEX_URLS=(
    "$OPEX_URL"
    "http://localhost:8080"
    "http://opex-api:8080"
    "http://127.0.0.1:8080"
)

HEALTH_CHECKED=false
for URL in "${OPEX_URLS[@]}"; do
    if [ -n "$URL" ] && [ "$URL" != "null" ]; then
        echo "   Trying: $URL/actuator/health"
        if curl -s -f --max-time 5 "$URL/actuator/health" > /dev/null 2>&1; then
            echo -e "${GREEN}   ✅ OPEX API is accessible at $URL${NC}"
            HEALTH_CHECKED=true
            
            # Get health status
            HEALTH_RESPONSE=$(curl -s "$URL/actuator/health" 2>/dev/null || echo "{}")
            echo "   Health response: $HEALTH_RESPONSE"
            break
        fi
    fi
done

if [ "$HEALTH_CHECKED" = false ]; then
    echo -e "${RED}   ❌ Could not reach OPEX API${NC}"
    echo "   Please ensure:"
    echo "   1. core-main services are running"
    echo "   2. OPEX_API_URL is correctly configured"
    echo "   3. Network connectivity is available"
fi

echo ""

# 5. Check backend OPEX client
echo "5. Checking backend OPEX client..."
echo "-----------------------------------"

if [ -f "$BACKEND_DIR/app/services/opex_client.py" ]; then
    echo -e "${GREEN}   ✅ OPEX client service found${NC}"
    
    # Check for key methods
    if grep -q "def place_order" "$BACKEND_DIR/app/services/opex_client.py"; then
        echo -e "${GREEN}   ✅ place_order method found${NC}"
    fi
    
    if grep -q "def get_orderbook" "$BACKEND_DIR/app/services/opex_client.py"; then
        echo -e "${GREEN}   ✅ get_orderbook method found${NC}"
    fi
    
    if grep -q "def health_check" "$BACKEND_DIR/app/services/opex_client.py"; then
        echo -e "${GREEN}   ✅ health_check method found${NC}"
    fi
else
    echo -e "${RED}   ❌ OPEX client service not found${NC}"
fi

echo ""

# 6. Check trading endpoints
echo "6. Checking trading endpoints..."
echo "-----------------------------------"

TRADING_ENDPOINTS=(
    "/api/trading/health"
    "/api/trading/orders"
    "/api/trading/positions"
    "/api/market/orderbook/BTCUSDT"
    "/api/market/symbols"
)

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

for ENDPOINT in "${TRADING_ENDPOINTS[@]}"; do
    echo "   Testing: $ENDPOINT"
    if curl -s -f --max-time 5 "$BACKEND_URL$ENDPOINT" > /dev/null 2>&1; then
        echo -e "${GREEN}   ✅ $ENDPOINT is accessible${NC}"
    else
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$BACKEND_URL$ENDPOINT" 2>/dev/null || echo "000")
        if [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
            echo -e "${YELLOW}   ⚠️  $ENDPOINT requires authentication (HTTP $HTTP_CODE)${NC}"
        elif [ "$HTTP_CODE" = "404" ]; then
            echo -e "${RED}   ❌ $ENDPOINT not found (HTTP 404)${NC}"
        else
            echo -e "${RED}   ❌ $ENDPOINT failed (HTTP $HTTP_CODE)${NC}"
        fi
    fi
done

echo ""

# 7. Check WebSocket configuration
echo "7. Checking WebSocket configuration..."
echo "-----------------------------------"

if [ -f "$BASE_DIR/client-app/src/services/opex_websocket.js" ]; then
    echo -e "${GREEN}   ✅ WebSocket service found in client-app${NC}"
    
    WS_PATH=$(grep -E "wsPath|'/ws" "$BASE_DIR/client-app/src/services/opex_websocket.js" | head -1 | sed -n "s/.*['\"]([^'\"]*)['\"].*/\1/p" || echo "/ws/opex")
    echo "   WebSocket path: $WS_PATH"
else
    echo -e "${YELLOW}   ⚠️  WebSocket service not found${NC}"
fi

# Check backend WebSocket
if [ -f "$BACKEND_DIR/app/api/websocket_opex.py" ] || grep -q "websocket_opex" "$BACKEND_DIR/main.py"; then
    echo -e "${GREEN}   ✅ Backend WebSocket endpoint found${NC}"
else
    echo -e "${YELLOW}   ⚠️  Backend WebSocket endpoint not found${NC}"
fi

echo ""

# 8. Check trading dashboard
echo "8. Checking trading dashboard components..."
echo "-----------------------------------"

DASHBOARD_FILE="$BASE_DIR/client-app/src/views/OpexTradingDashboard.vue"
if [ -f "$DASHBOARD_FILE" ]; then
    echo -e "${GREEN}   ✅ Trading dashboard found${NC}"
    
    # Check for components
    COMPONENTS=("MarketWatch" "OrderBook" "TradingChart" "PositionList" "OrderHistory" "AccountSummary")
    for COMP in "${COMPONENTS[@]}"; do
        if grep -q "$COMP" "$DASHBOARD_FILE"; then
            echo -e "${GREEN}   ✅ $COMP component used${NC}"
        else
            echo -e "${YELLOW}   ⚠️  $COMP component not found${NC}"
        fi
    done
else
    echo -e "${RED}   ❌ Trading dashboard not found${NC}"
fi

echo ""

# 9. Summary
echo "=========================================="
echo "Summary"
echo "=========================================="

if [ "$HEALTH_CHECKED" = true ]; then
    echo -e "${GREEN}✅ OPEX API is accessible${NC}"
else
    echo -e "${RED}❌ OPEX API is not accessible${NC}"
fi

if [ -f "$BACKEND_DIR/app/services/opex_client.py" ]; then
    echo -e "${GREEN}✅ Backend OPEX client exists${NC}"
else
    echo -e "${RED}❌ Backend OPEX client missing${NC}"
fi

if [ -f "$DASHBOARD_FILE" ]; then
    echo -e "${GREEN}✅ Trading dashboard exists${NC}"
else
    echo -e "${RED}❌ Trading dashboard missing${NC}"
fi

echo ""
echo "For detailed testing, run:"
echo "  python3 scripts/test_all_apis.py"
echo ""

