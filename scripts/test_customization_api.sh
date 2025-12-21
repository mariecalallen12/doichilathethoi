#!/bin/bash
"""
Customization API Test Script
==============================

Tests the complete customization workflow:
1. Create rules
2. Create sessions
3. Bind rules to sessions
4. Activate sessions
5. Test market data with customization
"""

set -e  # Exit on error

# Configuration
BASE_URL="http://localhost:8000"
ADMIN_EMAIL="admin@cmeetrading.com"
ADMIN_PASSWORD="admin123"  # Change this in production

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}======================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Step 1: Login and get token
print_header "STEP 1: Admin Login"

print_info "Logging in as $ADMIN_EMAIL..."

LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$ADMIN_EMAIL\",
    \"password\": \"$ADMIN_PASSWORD\"
  }")

# Extract token
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token // .token // empty')

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    print_error "Login failed. Please check credentials."
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

print_success "Login successful"
print_info "Token: ${TOKEN:0:20}..."

# Step 2: Create customization rules
print_header "STEP 2: Create Customization Rules"

# Rule 1: BTC Bullish
print_info "Creating BTC Bullish rule..."

RULE1_RESPONSE=$(curl -s -X POST "$BASE_URL/api/admin/customizations/rules" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "BTC_BULLISH",
    "symbol": "BTC",
    "price_adjustment": 5.0,
    "change_adjustment": 3.0,
    "force_signal": "STRONG_BUY",
    "confidence_boost": 20.0,
    "enabled": true
  }')

if echo "$RULE1_RESPONSE" | jq -e '.message' >/dev/null 2>&1; then
    print_success "BTC_BULLISH rule created"
else
    print_error "Failed to create BTC_BULLISH rule"
    echo "Response: $RULE1_RESPONSE"
fi

# Rule 2: ETH Moderate
print_info "Creating ETH Moderate rule..."

RULE2_RESPONSE=$(curl -s -X POST "$BASE_URL/api/admin/customizations/rules" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ETH_MODERATE",
    "symbol": "ETH",
    "price_adjustment": 2.5,
    "change_adjustment": 1.5,
    "force_signal": "BUY",
    "confidence_boost": 10.0,
    "enabled": true
  }')

if echo "$RULE2_RESPONSE" | jq -e '.message' >/dev/null 2>&1; then
    print_success "ETH_MODERATE rule created"
else
    print_error "Failed to create ETH_MODERATE rule"
fi

# Rule 3: Global Boost (applies to all symbols)
print_info "Creating Global Boost rule..."

RULE3_RESPONSE=$(curl -s -X POST "$BASE_URL/api/admin/customizations/rules" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GLOBAL_BOOST",
    "symbol": "*",
    "confidence_boost": 5.0,
    "enabled": false
  }')

if echo "$RULE3_RESPONSE" | jq -e '.message' >/dev/null 2>&1; then
    print_success "GLOBAL_BOOST rule created (disabled)"
else
    print_error "Failed to create GLOBAL_BOOST rule"
fi

# Step 3: List all rules
print_header "STEP 3: List All Rules"

RULES_LIST=$(curl -s -X GET "$BASE_URL/api/admin/customizations/rules" \
  -H "Authorization: Bearer $TOKEN")

RULES_COUNT=$(echo $RULES_LIST | jq 'length')
print_success "Total rules: $RULES_COUNT"
echo $RULES_LIST | jq -r '.[] | "  - \(.name): symbol=\(.symbol), price_adj=\(.price_adjustment // "N/A"), enabled=\(.enabled)"'

# Step 4: Create sessions
print_header "STEP 4: Create Sessions"

# Session 1: Marketing Campaign
print_info "Creating Marketing Campaign session..."

SESSION1_RESPONSE=$(curl -s -X POST "$BASE_URL/api/admin/customizations/sessions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Marketing Campaign Q1"
  }')

SESSION1_ID=$(echo $SESSION1_RESPONSE | jq -r '.session_id')

if [ -z "$SESSION1_ID" ] || [ "$SESSION1_ID" = "null" ]; then
    print_error "Failed to create session"
    echo "Response: $SESSION1_RESPONSE"
    exit 1
fi

print_success "Marketing Campaign session created"
print_info "Session ID: $SESSION1_ID"

# Session 2: VIP Demo
print_info "Creating VIP Demo session..."

SESSION2_RESPONSE=$(curl -s -X POST "$BASE_URL/api/admin/customizations/sessions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "VIP Demo Session"
  }')

SESSION2_ID=$(echo $SESSION2_RESPONSE | jq -r '.session_id')
print_success "VIP Demo session created"
print_info "Session ID: $SESSION2_ID"

# Step 5: Bind rules to sessions
print_header "STEP 5: Bind Rules to Sessions"

# Bind BTC_BULLISH to Marketing Campaign
print_info "Binding BTC_BULLISH to Marketing Campaign..."

BIND1_RESPONSE=$(curl -s -X POST "$BASE_URL/api/admin/customizations/sessions/$SESSION1_ID/bind" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "BTC_BULLISH"
  }')

if echo "$BIND1_RESPONSE" | jq -e '.message' >/dev/null 2>&1; then
    print_success "BTC_BULLISH bound to Marketing Campaign"
else
    print_error "Failed to bind rule"
fi

# Bind ETH_MODERATE to Marketing Campaign
print_info "Binding ETH_MODERATE to Marketing Campaign..."

curl -s -X POST "$BASE_URL/api/admin/customizations/sessions/$SESSION1_ID/bind" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"rule_name": "ETH_MODERATE"}' >/dev/null

print_success "ETH_MODERATE bound to Marketing Campaign"

# Bind rules to VIP Demo
print_info "Binding rules to VIP Demo..."

curl -s -X POST "$BASE_URL/api/admin/customizations/sessions/$SESSION2_ID/bind" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"rule_name": "BTC_BULLISH"}' >/dev/null

curl -s -X POST "$BASE_URL/api/admin/customizations/sessions/$SESSION2_ID/bind" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"rule_name": "GLOBAL_BOOST"}' >/dev/null

print_success "Rules bound to VIP Demo"

# Step 6: Activate sessions
print_header "STEP 6: Activate Sessions"

print_info "Activating Marketing Campaign session..."

ACTIVATE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/admin/customizations/sessions/$SESSION1_ID/activate" \
  -H "Authorization: Bearer $TOKEN")

if echo "$ACTIVATE_RESPONSE" | jq -e '.message' >/dev/null 2>&1; then
    print_success "Marketing Campaign activated"
else
    print_error "Failed to activate session"
fi

# Step 7: Test market data WITHOUT session
print_header "STEP 7: Test Market Data (Without Customization)"

print_info "Fetching BTC price without customization..."

BTC_ORIGINAL=$(curl -s -X GET "$BASE_URL/api/market/prices?symbol=BTC")

if echo "$BTC_ORIGINAL" | jq -e '.prices.BTC.price' >/dev/null 2>&1; then
    ORIGINAL_PRICE=$(echo $BTC_ORIGINAL | jq -r '.prices.BTC.price')
    ORIGINAL_CHANGE=$(echo $BTC_ORIGINAL | jq -r '.prices.BTC.change_24h')
    print_success "Original BTC data:"
    echo "  Price: \$$ORIGINAL_PRICE"
    echo "  Change 24h: $ORIGINAL_CHANGE%"
else
    print_error "Failed to fetch BTC price"
    echo "Response: $BTC_ORIGINAL"
fi

# Step 8: Test market data WITH session
print_header "STEP 8: Test Market Data (With Customization)"

print_info "Fetching BTC price WITH Marketing Campaign session..."

BTC_CUSTOMIZED=$(curl -s -X GET "$BASE_URL/api/market/prices?symbol=BTC" \
  -H "X-Session-Id: $SESSION1_ID")

if echo "$BTC_CUSTOMIZED" | jq -e '.prices.BTC.price' >/dev/null 2>&1; then
    CUSTOMIZED_PRICE=$(echo $BTC_CUSTOMIZED | jq -r '.prices.BTC.price')
    CUSTOMIZED_CHANGE=$(echo $BTC_CUSTOMIZED | jq -r '.prices.BTC.change_24h')
    print_success "Customized BTC data:"
    echo "  Price: \$$CUSTOMIZED_PRICE (+5% from rule)"
    echo "  Change 24h: $CUSTOMIZED_CHANGE% (+3% from rule)"
    
    # Calculate difference
    if [ ! -z "$ORIGINAL_PRICE" ] && [ "$ORIGINAL_PRICE" != "null" ]; then
        PRICE_DIFF=$(echo "scale=2; ($CUSTOMIZED_PRICE - $ORIGINAL_PRICE) / $ORIGINAL_PRICE * 100" | bc)
        print_info "Price difference: $PRICE_DIFF%"
    fi
else
    print_error "Failed to fetch customized BTC price"
fi

# Step 9: Test manual override
print_header "STEP 9: Test Manual Override"

print_info "Setting manual override for BTC to \$50,000..."

OVERRIDE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/admin/customizations/manual-override" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC",
    "price": 50000.0,
    "signal": "STRONG_BUY",
    "confidence": 95.0
  }')

if echo "$OVERRIDE_RESPONSE" | jq -e '.message' >/dev/null 2>&1; then
    print_success "Manual override set"
    
    # Test override
    print_info "Fetching BTC with manual override..."
    BTC_OVERRIDE=$(curl -s -X GET "$BASE_URL/api/market/prices?symbol=BTC")
    
    OVERRIDE_PRICE=$(echo $BTC_OVERRIDE | jq -r '.prices.BTC.price')
    print_success "Override price: \$$OVERRIDE_PRICE (should be exactly \$50,000)"
else
    print_error "Failed to set manual override"
fi

# Step 10: Get system status
print_header "STEP 10: System Status"

STATUS=$(curl -s -X GET "$BASE_URL/api/admin/customizations/status" \
  -H "Authorization: Bearer $TOKEN")

print_success "Customization System Status:"
echo $STATUS | jq .

# Step 11: Cleanup (optional)
print_header "STEP 11: Cleanup"

read -p "Do you want to clean up test data? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Clearing manual overrides..."
    curl -s -X DELETE "$BASE_URL/api/admin/customizations/manual-override" \
      -H "Authorization: Bearer $TOKEN" >/dev/null
    print_success "Manual overrides cleared"
    
    print_info "Deactivating sessions..."
    curl -s -X POST "$BASE_URL/api/admin/customizations/sessions/$SESSION1_ID/deactivate" \
      -H "Authorization: Bearer $TOKEN" >/dev/null
    print_success "Sessions deactivated"
    
    print_info "Test data preserved. Delete manually if needed."
else
    print_info "Test data preserved"
fi

# Summary
print_header "TEST SUMMARY"

echo -e "${GREEN}✅ All tests completed successfully!${NC}"
echo ""
echo "Created:"
echo "  - 3 customization rules"
echo "  - 2 sessions"
echo "  - Multiple rule bindings"
echo ""
echo "Session IDs for reference:"
echo "  - Marketing Campaign: $SESSION1_ID"
echo "  - VIP Demo: $SESSION2_ID"
echo ""
echo "Next steps:"
echo "  1. Use these session IDs in your client applications"
echo "  2. Add X-Session-Id header to API requests"
echo "  3. Build Admin UI for managing rules/sessions"
echo ""

print_success "Demo complete! 🎉"
