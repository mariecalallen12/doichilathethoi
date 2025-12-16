#!/bin/bash

# Script to fix nginx proxy network connectivity issues
# Usage: ./scripts/fix-nginx-network.sh

set -e

echo "=========================================="
echo "Fix Nginx Proxy Network Connectivity"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Detect nginx network automatically
NGINX_CONTAINER="digital_utopia_nginx_proxy"
CLIENT_CONTAINER="digital_utopia_client"
ADMIN_CONTAINER="digital_utopia_admin"
BACKEND_CONTAINER="digital_utopia_backend"

# Get the network that nginx proxy is actually using
NGINX_NETWORK=$(docker inspect "$NGINX_CONTAINER" 2>/dev/null | grep -A 10 "Networks" | grep -oP '"([^"]+_network)":' | head -1 | sed 's/":$//' | sed 's/"//g')

if [ -z "$NGINX_NETWORK" ]; then
    # Fallback: try common network names
    if docker network inspect "digital_utopia_network" > /dev/null 2>&1; then
        NGINX_NETWORK="digital_utopia_network"
    elif docker network inspect "forexxx_digital_utopia_network" > /dev/null 2>&1; then
        NGINX_NETWORK="forexxx_digital_utopia_network"
    else
        echo -e "${RED}✗ Cannot determine nginx network${NC}"
        exit 1
    fi
fi

echo -e "${YELLOW}Detected nginx network: $NGINX_NETWORK${NC}"
echo -e "${YELLOW}Step 1: Checking network connectivity...${NC}"

# Check if nginx can resolve client container
if docker exec "$NGINX_CONTAINER" getent hosts "$CLIENT_CONTAINER" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Nginx can resolve $CLIENT_CONTAINER${NC}"
else
    echo -e "${RED}✗ Nginx cannot resolve $CLIENT_CONTAINER${NC}"
    echo -e "${YELLOW}Connecting $CLIENT_CONTAINER to $NGINX_NETWORK...${NC}"
    docker network connect "$NGINX_NETWORK" "$CLIENT_CONTAINER" 2>/dev/null || true
fi

# Check admin container
if docker exec "$NGINX_CONTAINER" getent hosts "$ADMIN_CONTAINER" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Nginx can resolve $ADMIN_CONTAINER${NC}"
else
    echo -e "${YELLOW}Connecting $ADMIN_CONTAINER to $NGINX_NETWORK...${NC}"
    docker network connect "$NGINX_NETWORK" "$ADMIN_CONTAINER" 2>/dev/null || true
fi

# Check backend container
if docker exec "$NGINX_CONTAINER" getent hosts "$BACKEND_CONTAINER" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Nginx can resolve $BACKEND_CONTAINER${NC}"
else
    echo -e "${YELLOW}Connecting $BACKEND_CONTAINER to $NGINX_NETWORK...${NC}"
    docker network connect "$NGINX_NETWORK" "$BACKEND_CONTAINER" 2>/dev/null || true
fi

echo -e "\n${YELLOW}Step 2: Restarting nginx proxy...${NC}"
docker restart "$NGINX_CONTAINER" > /dev/null
sleep 3

echo -e "\n${YELLOW}Step 3: Verifying connectivity...${NC}"

# Test client app
if docker exec "$NGINX_CONTAINER" curl -f -s http://digital_utopia_client/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Client app is reachable${NC}"
else
    echo -e "${RED}✗ Client app is not reachable${NC}"
fi

# Test backend
if docker exec "$NGINX_CONTAINER" curl -f -s http://digital_utopia_backend:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend API is reachable${NC}"
else
    echo -e "${YELLOW}⚠ Backend API check skipped${NC}"
fi

echo -e "\n${YELLOW}Step 4: Testing HTTP endpoint...${NC}"
sleep 2
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ HTTP endpoint returns 200${NC}"
else
    echo -e "${RED}✗ HTTP endpoint returned: $HTTP_CODE${NC}"
fi

echo -e "\n${GREEN}Network fix complete!${NC}"

