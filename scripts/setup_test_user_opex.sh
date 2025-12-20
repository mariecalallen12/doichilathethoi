#!/bin/bash
# Script to setup test user account and wallet in OPEX system

set -e

echo "=========================================="
echo "🔧 Setting up Test User in OPEX System"
echo "=========================================="

# Configuration
OPEX_API_URL="${OPEX_API_URL:-http://localhost:8082}"
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
TEST_USER_EMAIL="test@example.com"
TEST_USER_PHONE="+1234567890"
TEST_USER_PASSWORD="testpassword123"

echo ""
echo "📋 Step 1: Registering test user in backend..."
REGISTER_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"phone\": \"${TEST_USER_PHONE}\",
    \"email\": \"${TEST_USER_EMAIL}\",
    \"password\": \"${TEST_USER_PASSWORD}\",
    \"full_name\": \"Test User\",
    \"date_of_birth\": \"1990-01-01\",
    \"nationality\": \"US\"
  }")

if echo "$REGISTER_RESPONSE" | grep -q "access_token\|user_id\|id"; then
  echo "✅ User registered successfully"
elif echo "$REGISTER_RESPONSE" | grep -q "already exists\|duplicate"; then
  echo "ℹ️  User already exists, continuing..."
else
  echo "⚠️  Registration response: $REGISTER_RESPONSE"
fi

echo ""
echo "📋 Step 2: Logging in to get token..."
LOGIN_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"phone\": \"${TEST_USER_PHONE}\",
    \"password\": \"${TEST_USER_PASSWORD}\"
  }")

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get access token"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Login successful"
echo "Token: ${TOKEN:0:20}..."

echo ""
echo "📋 Step 3: Checking OPEX API health..."
OPEX_HEALTH=$(curl -s "${OPEX_API_URL}/actuator/health" || echo "{}")

if echo "$OPEX_HEALTH" | grep -q "UP\|status"; then
  echo "✅ OPEX API is healthy"
else
  echo "⚠️  OPEX API health check failed or service not available"
  echo "Response: $OPEX_HEALTH"
fi

echo ""
echo "📋 Step 4: Checking backend trading service..."
TRADING_HEALTH=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "${BACKEND_URL}/api/trading/health" || echo "{}")

if echo "$TRADING_HEALTH" | grep -q "status"; then
  echo "✅ Backend trading service is available"
  echo "Status: $(echo "$TRADING_HEALTH" | grep -o '"status":"[^"]*' | cut -d'"' -f4)"
else
  echo "⚠️  Backend trading service check failed"
fi

echo ""
echo "=========================================="
echo "✅ Test User Setup Complete"
echo "=========================================="
echo ""
echo "Test User Credentials:"
echo "  Phone: ${TEST_USER_PHONE}"
echo "  Email: ${TEST_USER_EMAIL}"
echo "  Password: ${TEST_USER_PASSWORD}"
echo ""
echo "You can now use this user for testing order placement."
echo ""
echo "To test order placement, run:"
echo "  python tests/test_opex_order_placement.py"
echo ""

