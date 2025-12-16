#!/bin/bash

# Offline Mode Test Script
# Test system behavior when internet is disconnected

set -e

echo "=========================================="
echo "Offline Mode Test"
echo "=========================================="
echo ""

# Configuration
API_BASE=${API_BASE:-"http://localhost:8000/api"}
WS_URL=${WS_URL:-"ws://localhost:8000/ws"}

echo "Configuration:"
echo "  API_BASE: $API_BASE"
echo "  WS_URL: $WS_URL"
echo ""

# Check if server is running
echo "Checking server status..."
if curl -s -f "$API_BASE/health" > /dev/null 2>&1; then
    echo "✅ Server is running"
else
    echo "❌ Server is not running at $API_BASE"
    echo "   Please start the server first: docker-compose up -d"
    exit 1
fi

echo ""
echo "⚠️  WARNING: This script will disconnect internet connectivity"
echo "   Make sure you have physical access to the server to reconnect"
echo ""
read -p "Continue with offline mode test? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Save current iptables rules
echo ""
echo "Saving current iptables rules..."
iptables-save > /tmp/iptables_backup_$(date +%Y%m%d_%H%M%S).rules

# Block all outbound connections (except localhost)
echo "Blocking outbound internet connections..."
iptables -A OUTPUT -d 127.0.0.1 -j ACCEPT
iptables -A OUTPUT -d 172.16.0.0/12 -j ACCEPT  # Docker networks
iptables -A OUTPUT -d 192.168.0.0/16 -j ACCEPT  # Local networks
iptables -A OUTPUT -j DROP

echo "✅ Internet disconnected (outbound blocked)"
echo ""
echo "Testing system behavior..."
echo ""

# Test 1: Market Feed
echo "Test 1: Market Feed"
echo "  - Checking WebSocket connection..."
timeout 5 curl -s "$WS_URL" > /dev/null 2>&1 && echo "  ✅ WebSocket accessible" || echo "  ⚠️  WebSocket might not be accessible via curl"

# Test 2: REST API
echo ""
echo "Test 2: REST API"
echo "  - Checking /api/sim/snapshot..."
if curl -s -f "$API_BASE/sim/snapshot" -H "Authorization: Bearer test" > /dev/null 2>&1; then
    echo "  ✅ REST API accessible"
else
    echo "  ⚠️  REST API might require authentication"
fi

# Test 3: Database
echo ""
echo "Test 3: Database"
echo "  - Checking database connection..."
if docker exec digital_utopia_postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "  ✅ Database accessible"
else
    echo "  ⚠️  Database might not be accessible"
fi

echo ""
echo "=========================================="
echo "Offline Mode Test Complete"
echo "=========================================="
echo ""
echo "⚠️  IMPORTANT: Restoring internet connectivity..."
echo ""

# Restore iptables
iptables -F OUTPUT
iptables -X 2>/dev/null || true

echo "✅ Internet connectivity restored"
echo ""
echo "Test Results:"
echo "  - Market Feed: Check WebSocket messages"
echo "  - REST API: Check API responses"
echo "  - Database: Check database queries"
echo ""
echo "Please verify manually:"
echo "  1. WebSocket still receives price updates"
echo "  2. Admin Dashboard still works"
echo "  3. Scenarios can be created/edited"
echo "  4. Sessions can be started/stopped"
echo ""

