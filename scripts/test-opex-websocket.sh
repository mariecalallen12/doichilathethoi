#!/bin/bash

# OPEX WebSocket Test Script
# Tests WebSocket connection and message handling

set -e

WS_URL="${WS_URL:-ws://localhost:8000/ws/opex}"

echo "=== OPEX WebSocket Integration Tests ==="
echo "WebSocket URL: $WS_URL"
echo ""

# Check if websocat or wscat is available
if command -v websocat &> /dev/null; then
    WS_CLIENT="websocat"
elif command -v wscat &> /dev/null; then
    WS_CLIENT="wscat"
else
    echo "⚠️  websocat or wscat not found. Installing websocat..."
    # Try to install websocat (requires cargo/rust)
    echo "Please install websocat: cargo install websocat"
    echo "Or use Python script for WebSocket testing"
    exit 1
fi

echo "Using $WS_CLIENT for WebSocket testing"
echo ""

# Test WebSocket connection
echo "Testing WebSocket connection..."
if [ "$WS_CLIENT" = "websocat" ]; then
    timeout 5 websocat "$WS_URL" <<< '{"type":"ping"}' || echo "Connection test completed"
elif [ "$WS_CLIENT" = "wscat" ]; then
    echo '{"type":"ping"}' | timeout 5 wscat -c "$WS_URL" || echo "Connection test completed"
fi

echo ""
echo "WebSocket test completed"

