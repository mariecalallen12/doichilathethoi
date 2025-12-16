#!/bin/bash

# Load Testing Script
# Run k6 load tests for WebSocket and REST API

set -e

echo "=========================================="
echo "k6 Load Testing Script"
echo "=========================================="

# Check if k6 is installed
if ! command -v k6 &> /dev/null; then
    echo "❌ k6 is not installed"
    echo ""
    echo "Installing k6..."
    if [ -f "$(dirname $0)/install_k6.sh" ]; then
        bash "$(dirname $0)/install_k6.sh"
    else
        echo "Please install k6 first:"
        echo "  Run: ./tests/load/install_k6.sh"
        echo "  Or use Docker: docker run --rm -i grafana/k6 run - <tests/load/websocket_test.js"
        exit 1
    fi
    
    # Check again
    if ! command -v k6 &> /dev/null; then
        echo "❌ k6 installation failed"
        echo "Please install manually or use Docker"
        exit 1
    fi
fi

echo "✅ k6 is installed"
k6 version

# Configuration
WS_URL=${WS_URL:-"ws://localhost:8000/ws"}
API_BASE=${API_BASE:-"http://localhost:8000/api"}
ADMIN_EMAIL=${ADMIN_EMAIL:-"admin@example.com"}
ADMIN_PASSWORD=${ADMIN_PASSWORD:-"admin123"}

echo ""
echo "Configuration:"
echo "  WS_URL: $WS_URL"
echo "  API_BASE: $API_BASE"
echo "  ADMIN_EMAIL: $ADMIN_EMAIL"
echo ""

# Check if server is running
echo "Checking server status..."
if curl -s -f "$API_BASE/health" > /dev/null 2>&1; then
    echo "✅ Server is running"
else
    echo "⚠️  Server might not be running at $API_BASE"
    echo "   Please start the server first: docker-compose up -d"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "Starting WebSocket Load Test"
echo "=========================================="
echo ""

# Run WebSocket test
export WS_URL
export API_BASE
k6 run --out json=results_websocket.json tests/load/websocket_test.js

echo ""
echo "=========================================="
echo "Starting REST API Load Test"
echo "=========================================="
echo ""

# Run REST API test
export API_BASE
export ADMIN_EMAIL
export ADMIN_PASSWORD
k6 run --out json=results_rest_api.json tests/load/rest_api_test.js

echo ""
echo "=========================================="
echo "Load Testing Complete!"
echo "=========================================="
echo ""
echo "Results saved to:"
echo "  - results_websocket.json"
echo "  - results_rest_api.json"
echo ""
echo "To view results, use k6 cloud or k6 dashboard"

