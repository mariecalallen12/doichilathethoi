#!/bin/bash
# Script to verify Admin-app features and routes

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ADMIN_APP_DIR="$BASE_DIR/Admin-app"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Admin-app Verification"
echo "=========================================="
echo ""

# 1. Check router configuration
echo "1. Checking router configuration..."
echo "-----------------------------------"

ROUTER_FILE="$ADMIN_APP_DIR/src/router/index.js"
if [ -f "$ROUTER_FILE" ]; then
    echo -e "${GREEN}   ✅ Router file found${NC}"
    
    # Extract routes
    ROUTES=$(grep -E "path:|name:" "$ROUTER_FILE" | grep -E "path:|name:" | sed 's/.*["'\'']\([^"'\'']*\)["'\''].*/\1/' | paste - - | awk '{print "   - " $2 " (" $1 ")"}')
    echo "   Routes found:"
    echo "$ROUTES" | head -20
    
    ROUTE_COUNT=$(grep -c "path:" "$ROUTER_FILE" || echo "0")
    echo "   Total routes: $ROUTE_COUNT"
else
    echo -e "${RED}   ❌ Router file not found${NC}"
fi

echo ""

# 2. Check views
echo "2. Checking views..."
echo "-----------------------------------"

VIEWS_DIR="$ADMIN_APP_DIR/src/views"
if [ -d "$VIEWS_DIR" ]; then
    echo -e "${GREEN}   ✅ Views directory found${NC}"
    
    VIEWS=$(find "$VIEWS_DIR" -name "*.vue" -type f | sed "s|$VIEWS_DIR/||" | sed 's|\.vue||')
    VIEW_COUNT=$(echo "$VIEWS" | wc -l)
    echo "   Views found ($VIEW_COUNT):"
    echo "$VIEWS" | sed 's/^/   - /'
else
    echo -e "${RED}   ❌ Views directory not found${NC}"
fi

echo ""

# 3. Check services
echo "3. Checking API services..."
echo "-----------------------------------"

SERVICES_DIR="$ADMIN_APP_DIR/src/services"
if [ -d "$SERVICES_DIR" ]; then
    echo -e "${GREEN}   ✅ Services directory found${NC}"
    
    SERVICES=$(find "$SERVICES_DIR" -name "*.js" -type f | sed "s|$SERVICES_DIR/||")
    echo "   Services found:"
    echo "$SERVICES" | sed 's/^/   - /'
    
    # Check for API client
    if [ -f "$SERVICES_DIR/api.js" ]; then
        echo -e "${GREEN}   ✅ API client found${NC}"
    fi
    
    # Check for admin trading service
    if [ -f "$SERVICES_DIR/admin_trading.js" ]; then
        echo -e "${GREEN}   ✅ Admin trading service found${NC}"
    fi
else
    echo -e "${RED}   ❌ Services directory not found${NC}"
fi

echo ""

# 4. Map features to backend endpoints
echo "4. Mapping features to backend endpoints..."
echo "-----------------------------------"

# Expected features based on router
EXPECTED_FEATURES=(
    "Dashboard:/api/admin/dashboard"
    "UserManagement:/api/admin/users"
    "OpexTradingManagement:/api/admin/trading"
    "FinancialManagement:/api/admin/deposits:/api/admin/withdrawals"
    "AnalyticsReports:/api/admin/analytics:/api/admin/reports"
    "SystemSettings:/api/admin/settings"
    "AdminTradingControls:/api/admin/trading/orders:/api/admin/trading/positions"
    "DiagnosticsManagement:/api/diagnostics"
    "AlertManagement:/api/alert-rules"
    "MarketPreview:/api/admin/market-preview"
)

echo "   Feature -> Backend Endpoint mapping:"
for FEATURE_MAP in "${EXPECTED_FEATURES[@]}"; do
    FEATURE=$(echo "$FEATURE_MAP" | cut -d':' -f1)
    ENDPOINTS=$(echo "$FEATURE_MAP" | cut -d':' -f2-)
    echo "   - $FEATURE"
    echo "$ENDPOINTS" | tr ':' '\n' | sed 's/^/     → /'
done

echo ""

# 5. Check component structure
echo "5. Checking component structure..."
echo "-----------------------------------"

COMPONENTS_DIR="$ADMIN_APP_DIR/src/components"
if [ -d "$COMPONENTS_DIR" ]; then
    COMPONENT_COUNT=$(find "$COMPONENTS_DIR" -name "*.vue" -type f | wc -l)
    echo -e "${GREEN}   ✅ Components directory found ($COMPONENT_COUNT components)${NC}"
else
    echo -e "${YELLOW}   ⚠️  Components directory not found${NC}"
fi

echo ""

# 6. Check package.json for dependencies
echo "6. Checking dependencies..."
echo "-----------------------------------"

if [ -f "$ADMIN_APP_DIR/package.json" ]; then
    echo -e "${GREEN}   ✅ package.json found${NC}"
    
    # Check key dependencies
    if grep -q "vue-router" "$ADMIN_APP_DIR/package.json"; then
        echo -e "${GREEN}   ✅ vue-router installed${NC}"
    fi
    
    if grep -q "axios" "$ADMIN_APP_DIR/package.json"; then
        echo -e "${GREEN}   ✅ axios installed${NC}"
    fi
    
    if grep -q "pinia" "$ADMIN_APP_DIR/package.json"; then
        echo -e "${GREEN}   ✅ pinia installed${NC}"
    fi
else
    echo -e "${RED}   ❌ package.json not found${NC}"
fi

echo ""

# 7. Summary
echo "=========================================="
echo "Summary"
echo "=========================================="

if [ -f "$ROUTER_FILE" ]; then
    echo -e "${GREEN}✅ Router configuration exists${NC}"
else
    echo -e "${RED}❌ Router configuration missing${NC}"
fi

if [ -d "$VIEWS_DIR" ] && [ "$VIEW_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Views exist ($VIEW_COUNT views)${NC}"
else
    echo -e "${RED}❌ Views missing or empty${NC}"
fi

if [ -d "$SERVICES_DIR" ]; then
    echo -e "${GREEN}✅ Services directory exists${NC}"
else
    echo -e "${RED}❌ Services directory missing${NC}"
fi

echo ""
echo "For detailed API testing, run:"
echo "  python3 scripts/test_all_apis.py"
echo ""

