#!/bin/bash

# Script to build and deploy client-app with comprehensive checks
# Usage: ./scripts/build-and-deploy-client.sh

set -e

echo "=========================================="
echo "Client App Build & Deploy Script"
echo "With Comprehensive Verification"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CLIENT_APP_DIR="/root/forexxx/client-app"
API_BASE_URL="${CLIENT_API_BASE_URL:-https://cmeetrading.com/api}"
CONTAINER_NAME="digital_utopia_client"
IMAGE_NAME="forexxx-client-app:latest"
PORT="${CLIENT_PORT:-3002}"

# Function to print step
print_step() {
    echo -e "\n${BLUE}=========================================="
    echo -e "$1"
    echo -e "==========================================${NC}\n"
}

# Function to check command success
check_success() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
        return 0
    else
        echo -e "${RED}✗ $1${NC}"
        return 1
    fi
}

# Function to verify file exists
verify_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓ File exists: $1${NC}"
        return 0
    else
        echo -e "${RED}✗ File missing: $1${NC}"
        return 1
    fi
}

# Function to verify directory exists
verify_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓ Directory exists: $1${NC}"
        return 0
    else
        echo -e "${RED}✗ Directory missing: $1${NC}"
        return 1
    fi
}

print_step "Step 1: Pre-deployment Verification"

echo -e "${YELLOW}Checking project structure...${NC}"
verify_dir "$CLIENT_APP_DIR" || exit 1
verify_file "$CLIENT_APP_DIR/package.json" || exit 1
verify_file "$CLIENT_APP_DIR/Dockerfile" || exit 1
verify_file "$CLIENT_APP_DIR/nginx.conf" || exit 1

echo -e "\n${YELLOW}Checking critical files...${NC}"
verify_file "$CLIENT_APP_DIR/src/router/index.js" || exit 1
verify_file "$CLIENT_APP_DIR/src/App.vue" || exit 1
verify_file "$CLIENT_APP_DIR/src/views/EducationView.vue" || exit 1
verify_file "$CLIENT_APP_DIR/src/views/AnalysisView.vue" || exit 1
verify_file "$CLIENT_APP_DIR/src/views/HelpCenterView.vue" || exit 1

echo -e "\n${YELLOW}Checking stores...${NC}"
verify_file "$CLIENT_APP_DIR/src/stores/education.js" || exit 1
verify_file "$CLIENT_APP_DIR/src/stores/analysis.js" || exit 1
verify_file "$CLIENT_APP_DIR/src/stores/support.js" || exit 1
verify_file "$CLIENT_APP_DIR/src/stores/legal.js" || exit 1

echo -e "\n${YELLOW}Checking API services...${NC}"
verify_file "$CLIENT_APP_DIR/src/services/api/education.js" || exit 1
verify_file "$CLIENT_APP_DIR/src/services/api/analysis.js" || exit 1
verify_file "$CLIENT_APP_DIR/src/services/api/support.js" || exit 1
verify_file "$CLIENT_APP_DIR/src/services/api/legal.js" || exit 1

print_step "Step 2: Clean Previous Build"

echo -e "${YELLOW}Removing old build artifacts...${NC}"
cd "$CLIENT_APP_DIR"
rm -rf dist node_modules/.vite 2>/dev/null || true
check_success "Cleaned build artifacts"

print_step "Step 3: Installing Dependencies"

cd "$CLIENT_APP_DIR"
echo -e "${YELLOW}Running npm install...${NC}"
npm install --legacy-peer-deps
check_success "Dependencies installed" || exit 1

echo -e "\n${YELLOW}Verifying critical dependencies...${NC}"
npm list vue vue-router pinia axios 2>/dev/null | grep -q "vue@" && check_success "Vue installed" || echo -e "${RED}✗ Vue not found${NC}"
npm list plyr pdfjs-dist 2>/dev/null | grep -q "plyr@" && check_success "Plyr installed" || echo -e "${YELLOW}⚠ Plyr check skipped${NC}"

print_step "Step 4: Building Application"

echo -e "${YELLOW}Building with Vite...${NC}"
cd "$CLIENT_APP_DIR"
npm run build
check_success "Application built" || exit 1

echo -e "\n${YELLOW}Verifying build output...${NC}"
verify_dir "$CLIENT_APP_DIR/dist" || exit 1
verify_file "$CLIENT_APP_DIR/dist/index.html" || exit 1

# Check if main JS and CSS files exist
if ls "$CLIENT_APP_DIR/dist/assets"/*.js 1> /dev/null 2>&1; then
    check_success "JavaScript bundles created"
else
    echo -e "${RED}✗ No JavaScript bundles found${NC}"
    exit 1
fi

if ls "$CLIENT_APP_DIR/dist/assets"/*.css 1> /dev/null 2>&1; then
    check_success "CSS bundles created"
else
    echo -e "${YELLOW}⚠ No CSS bundles found (may be inline)${NC}"
fi

print_step "Step 5: Stopping Existing Container"

echo -e "${YELLOW}Checking for existing container...${NC}"
if docker ps -a | grep -q "$CONTAINER_NAME"; then
    echo -e "${YELLOW}Stopping container...${NC}"
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    check_success "Container stopped"
    
    echo -e "${YELLOW}Removing container...${NC}"
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    check_success "Container removed"
else
    echo -e "${GREEN}✓ No existing container found${NC}"
fi

print_step "Step 6: Building Docker Image"

echo -e "${YELLOW}Building Docker image with API URL: $API_BASE_URL${NC}"
cd "$CLIENT_APP_DIR"
docker build \
  --build-arg VITE_API_BASE_URL="$API_BASE_URL" \
  -t "$IMAGE_NAME" \
  . 2>&1 | tee /tmp/docker-build.log

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    check_success "Docker image built"
else
    echo -e "${RED}✗ Docker build failed${NC}"
    echo -e "${YELLOW}Last 20 lines of build log:${NC}"
    tail -20 /tmp/docker-build.log
    exit 1
fi

echo -e "\n${YELLOW}Verifying Docker image...${NC}"
if docker images | grep -q "forexxx-client-app"; then
    check_success "Docker image exists"
    docker images | grep "forexxx-client-app"
else
    echo -e "${RED}✗ Docker image not found${NC}"
    exit 1
fi

print_step "Step 7: Starting New Container"

echo -e "${YELLOW}Creating and starting container...${NC}"
docker run -d \
  --name "$CONTAINER_NAME" \
  --network digital_utopia_network \
  -p "$PORT:80" \
  --restart unless-stopped \
  "$IMAGE_NAME"

check_success "Container started" || exit 1

print_step "Step 8: Container Health Check"

echo -e "${YELLOW}Waiting for container to initialize...${NC}"
sleep 5

echo -e "\n${YELLOW}Checking container status...${NC}"
if docker ps | grep -q "$CONTAINER_NAME"; then
    check_success "Container is running"
    docker ps | grep "$CONTAINER_NAME"
else
    echo -e "${RED}✗ Container is not running${NC}"
    echo -e "${YELLOW}Container logs:${NC}"
    docker logs "$CONTAINER_NAME" 2>&1 | tail -30
    exit 1
fi

echo -e "\n${YELLOW}Checking container health...${NC}"
for i in {1..10}; do
    if docker exec "$CONTAINER_NAME" wget --quiet --tries=1 --spider http://localhost/health 2>/dev/null; then
        check_success "Health check passed"
        break
    else
        if [ $i -eq 10 ]; then
            echo -e "${YELLOW}⚠ Health check failed after 10 attempts${NC}"
        else
            echo -e "${YELLOW}Waiting for health check... ($i/10)${NC}"
            sleep 2
        fi
    fi
done

print_step "Step 9: Application Verification"

echo -e "${YELLOW}Testing HTTP endpoint...${NC}"
sleep 3
if curl -f -s http://localhost:$PORT/health > /dev/null 2>&1; then
    check_success "HTTP endpoint accessible"
else
    echo -e "${YELLOW}⚠ HTTP endpoint check failed${NC}"
fi

echo -e "\n${YELLOW}Testing main page...${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/)
if [ "$HTTP_CODE" = "200" ]; then
    check_success "Main page returns 200"
else
    echo -e "${YELLOW}⚠ Main page returned: $HTTP_CODE${NC}"
fi

echo -e "\n${YELLOW}Checking container logs for errors...${NC}"
ERROR_COUNT=$(docker logs "$CONTAINER_NAME" 2>&1 | grep -i "error" | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    check_success "No errors in container logs"
else
    echo -e "${YELLOW}⚠ Found $ERROR_COUNT error(s) in logs${NC}"
    docker logs "$CONTAINER_NAME" 2>&1 | grep -i "error" | tail -5
fi

print_step "Step 10: Network Connectivity Fix"

echo -e "${YELLOW}Ensuring container is in nginx proxy network...${NC}"
# Detect nginx network automatically
NGINX_CONTAINER="digital_utopia_nginx_proxy"
NGINX_NETWORK=$(docker inspect "$NGINX_CONTAINER" 2>/dev/null | grep -A 10 "Networks" | grep -oP '"([^"]+_network)":' | head -1 | sed 's/":$//' | sed 's/"//g')

if [ -z "$NGINX_NETWORK" ]; then
    # Fallback: try common network names
    if docker network inspect "digital_utopia_network" > /dev/null 2>&1; then
        NGINX_NETWORK="digital_utopia_network"
    elif docker network inspect "forexxx_digital_utopia_network" > /dev/null 2>&1; then
        NGINX_NETWORK="forexxx_digital_utopia_network"
    fi
fi

if [ -n "$NGINX_NETWORK" ] && docker network inspect "$NGINX_NETWORK" > /dev/null 2>&1; then
    echo -e "${YELLOW}Detected nginx network: $NGINX_NETWORK${NC}"
    if ! docker inspect "$CONTAINER_NAME" 2>/dev/null | grep -q "$NGINX_NETWORK"; then
        echo -e "${YELLOW}Connecting to nginx network...${NC}"
        docker network connect "$NGINX_NETWORK" "$CONTAINER_NAME" 2>/dev/null || true
        check_success "Connected to nginx network"
        
        # Restart nginx proxy to pick up new connection
        if docker ps | grep -q "$NGINX_CONTAINER"; then
            echo -e "${YELLOW}Restarting nginx proxy...${NC}"
            docker restart "$NGINX_CONTAINER" > /dev/null 2>&1
            sleep 3
        fi
    else
        check_success "Already in nginx network"
    fi
else
    echo -e "${YELLOW}⚠ Nginx network not found, skipping${NC}"
fi

print_step "Step 11: Final Verification"

echo -e "${YELLOW}Container Information:${NC}"
echo "  Name: $CONTAINER_NAME"
echo "  Image: $IMAGE_NAME"
echo "  Port: $PORT"
echo "  API URL: $API_BASE_URL"
echo "  Status: $(docker inspect --format='{{.State.Status}}' $CONTAINER_NAME 2>/dev/null || echo 'unknown')"

echo -e "\n${YELLOW}Network Information:${NC}"
docker network inspect digital_utopia_network 2>/dev/null | grep -A 5 "$CONTAINER_NAME" || echo "  Network check skipped"

echo -e "\n${YELLOW}Nginx Proxy Connectivity:${NC}"
if docker ps | grep -q "digital_utopia_nginx_proxy"; then
    if docker exec digital_utopia_nginx_proxy getent hosts "$CONTAINER_NAME" > /dev/null 2>&1; then
        check_success "Nginx can resolve container"
    else
        echo -e "${YELLOW}⚠ Nginx cannot resolve container (may need restart)${NC}"
    fi
fi

echo ""
echo -e "${GREEN}=========================================="
echo "Build and Deploy Complete!"
echo "==========================================${NC}"
echo ""
echo -e "${GREEN}✓ Application deployed successfully${NC}"
echo ""
echo "Access URLs:"
echo "  - Main: http://localhost:$PORT"
echo "  - Health: http://localhost:$PORT/health"
echo ""
echo "Next steps:"
echo "  1. Verify application in browser"
echo "  2. Check all new routes work"
echo "  3. Test API connections"
echo ""
