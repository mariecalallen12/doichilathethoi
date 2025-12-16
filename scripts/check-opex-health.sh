#!/bin/bash

# OPEX Services Health Check Script
# Checks health of all OPEX services

set -e

echo "=== OPEX Services Health Check ==="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Docker containers
echo "📦 Checking Docker Containers..."
containers=(
    "opex-zookeeper"
    "opex-kafka-1"
    "opex-redis"
    "opex-consul"
    "opex-vault"
    "opex-postgres-api"
    "opex-postgres-market"
    "opex-postgres-wallet"
    "opex-matching-engine"
    "opex-matching-gateway"
    "opex-api"
    "opex-market"
    "opex-wallet"
)

running_count=0
total_count=${#containers[@]}

for container in "${containers[@]}"; do
    if docker ps --format "{{.Names}}" | grep -q "^${container}$"; then
        status=$(docker ps --filter "name=${container}" --format "{{.Status}}")
        echo -e "${GREEN}✓${NC} ${container}: ${status}"
        running_count=$((running_count + 1))
    else
        echo -e "${RED}✗${NC} ${container}: Not running"
    fi
done

echo ""
echo "Running: ${running_count}/${total_count} containers"
echo ""

# Check OPEX API endpoints
echo "🔌 Checking OPEX API Endpoints..."

# OPEX API (port 8082)
if curl -s -f -m 5 http://localhost:8082/actuator/health > /dev/null 2>&1 || \
   curl -s -f -m 5 http://localhost:8082/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} OPEX API (port 8082): Accessible"
else
    echo -e "${RED}✗${NC} OPEX API (port 8082): Not accessible"
fi

# OPEX Market (port 8083)
if curl -s -f -m 5 http://localhost:8083/actuator/health > /dev/null 2>&1 || \
   curl -s -f -m 5 http://localhost:8083/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} OPEX Market (port 8083): Accessible"
else
    echo -e "${RED}✗${NC} OPEX Market (port 8083): Not accessible"
fi

# OPEX Wallet (port 8084)
if curl -s -f -m 5 http://localhost:8084/actuator/health > /dev/null 2>&1 || \
   curl -s -f -m 5 http://localhost:8084/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} OPEX Wallet (port 8084): Accessible"
else
    echo -e "${RED}✗${NC} OPEX Wallet (port 8084): Not accessible"
fi

echo ""

# Check Backend OPEX Integration
echo "🔗 Checking Backend OPEX Integration..."

# Trading health endpoint
if response=$(curl -s -f -m 5 http://localhost:8000/api/trading/health 2>&1); then
    echo -e "${GREEN}✓${NC} Backend Trading Health: OK"
    echo "  Response: $(echo $response | head -c 100)"
else
    echo -e "${RED}✗${NC} Backend Trading Health: Failed"
fi

# Market health endpoint
if response=$(curl -s -f -m 5 http://localhost:8000/api/market/health 2>&1); then
    echo -e "${GREEN}✓${NC} Backend Market Health: OK"
    echo "  Response: $(echo $response | head -c 100)"
else
    echo -e "${RED}✗${NC} Backend Market Health: Failed"
fi

echo ""

# Check Network Connectivity
echo "🌐 Checking Network Connectivity..."

# Check if backend can reach OPEX API
if docker exec digital_utopia_backend ping -c 1 -W 2 opex-api > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Backend → OPEX API: Reachable"
else
    echo -e "${RED}✗${NC} Backend → OPEX API: Not reachable"
fi

# Check if backend can reach OPEX Market
if docker exec digital_utopia_backend ping -c 1 -W 2 opex-market > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Backend → OPEX Market: Reachable"
else
    echo -e "${RED}✗${NC} Backend → OPEX Market: Not reachable"
fi

echo ""

# Summary
echo "=== Summary ==="
if [ $running_count -eq $total_count ]; then
    echo -e "${GREEN}All OPEX services are running${NC}"
    exit 0
else
    echo -e "${YELLOW}Some OPEX services are not running (${running_count}/${total_count})${NC}"
    exit 1
fi

