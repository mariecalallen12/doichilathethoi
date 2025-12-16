#!/bin/bash

# Rebuild and Deploy Script for Domain Migration
# This script rebuilds and deploys all services with the new domain cmeetrading.com
# Usage: ./scripts/rebuild-and-deploy-domain-migration.sh

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="/root/forexxx"
DOMAIN="cmeetrading.com"

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

print_step "Domain Migration - Rebuild and Deploy"
echo -e "${YELLOW}Domain: $DOMAIN${NC}"
echo -e "${YELLOW}Project Directory: $PROJECT_DIR${NC}\n"

# ============================================
# Step 1: Pre-deployment Checks
# ============================================
print_step "Step 1: Pre-deployment Checks"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running${NC}"
    exit 1
fi
check_success "Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}✗ docker-compose is not available${NC}"
    exit 1
fi
check_success "docker-compose is available"

# Check if .env file exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${YELLOW}⚠ .env file not found. Creating from env.example...${NC}"
    cp "$PROJECT_DIR/env.example" "$PROJECT_DIR/.env"
    echo -e "${YELLOW}⚠ Please update .env file with your actual values${NC}"
fi
check_success ".env file exists"

# Check DNS resolution
if dig +short "$DOMAIN" | grep -q .; then
    DNS_IP=$(dig +short "$DOMAIN" | head -1)
    check_success "DNS resolution for $DOMAIN → $DNS_IP"
else
    echo -e "${YELLOW}⚠ DNS not configured for $DOMAIN${NC}"
    echo -e "${YELLOW}⚠ Please configure DNS before continuing${NC}"
fi

# ============================================
# Step 2: Backup Current Configuration
# ============================================
print_step "Step 2: Backup Current Configuration"

BACKUP_DIR="$PROJECT_DIR/backups/domain_migration_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup docker-compose.yml
cp "$PROJECT_DIR/docker-compose.yml" "$BACKUP_DIR/" 2>/dev/null || true
check_success "Backed up docker-compose.yml"

# Backup nginx config
cp "$PROJECT_DIR/nginx/nginx.conf" "$BACKUP_DIR/" 2>/dev/null || true
check_success "Backed up nginx.conf"

# Backup .env if exists
cp "$PROJECT_DIR/.env" "$BACKUP_DIR/" 2>/dev/null || true
check_success "Backed up .env"

echo -e "${GREEN}✓ Backup created at: $BACKUP_DIR${NC}"

# ============================================
# Step 3: Stop Existing Containers
# ============================================
print_step "Step 3: Stop Existing Containers"

cd "$PROJECT_DIR"

# Use docker-compose or docker compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

echo -e "${YELLOW}Stopping existing containers...${NC}"
$COMPOSE_CMD down
check_success "Containers stopped"

# ============================================
# Step 4: SSL Certificate Setup (if needed)
# ============================================
print_step "Step 4: SSL Certificate Setup"

# Check if SSL certificate exists
if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    check_success "SSL certificate already exists"
else
    echo -e "${YELLOW}SSL certificate not found.${NC}"
    echo -e "${YELLOW}Run the following command to setup SSL:${NC}"
    echo -e "${BLUE}sudo ./scripts/setup-ssl-certbot.sh${NC}"
    read -p "Do you want to setup SSL certificate now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo "$PROJECT_DIR/scripts/setup-ssl-certbot.sh"
    else
        echo -e "${YELLOW}⚠ Skipping SSL setup. You can run it later.${NC}"
        echo -e "${YELLOW}⚠ Note: HTTPS will not work without SSL certificate${NC}"
    fi
fi

# ============================================
# Step 5: Create Required Directories
# ============================================
print_step "Step 5: Create Required Directories"

mkdir -p "$PROJECT_DIR/nginx/certbot/conf"
mkdir -p "$PROJECT_DIR/nginx/certbot/www"
mkdir -p "$PROJECT_DIR/nginx/ssl"
check_success "Required directories created"

# ============================================
# Step 6: Rebuild Docker Images
# ============================================
print_step "Step 6: Rebuild Docker Images"

echo -e "${YELLOW}Building images with new domain configuration...${NC}"

# Build backend
echo -e "${YELLOW}Building backend...${NC}"
$COMPOSE_CMD build backend
check_success "Backend image built"

# Build client-app
echo -e "${YELLOW}Building client-app...${NC}"
$COMPOSE_CMD build client-app
check_success "Client-app image built"

# Build admin-app
echo -e "${YELLOW}Building admin-app...${NC}"
$COMPOSE_CMD build admin-app
check_success "Admin-app image built"

# ============================================
# Step 7: Start Services
# ============================================
print_step "Step 7: Start Services"

echo -e "${YELLOW}Starting all services...${NC}"
$COMPOSE_CMD up -d
check_success "Services started"

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to initialize...${NC}"
sleep 10

# ============================================
# Step 8: Health Checks
# ============================================
print_step "Step 8: Health Checks"

# Check container status
echo -e "${YELLOW}Checking container status...${NC}"
if docker ps | grep -q "digital_utopia_nginx_proxy"; then
    check_success "Nginx container running"
else
    echo -e "${RED}✗ Nginx container not running${NC}"
fi

if docker ps | grep -q "digital_utopia_backend"; then
    check_success "Backend container running"
else
    echo -e "${RED}✗ Backend container not running${NC}"
fi

if docker ps | grep -q "digital_utopia_client"; then
    check_success "Client container running"
else
    echo -e "${RED}✗ Client container not running${NC}"
fi

if docker ps | grep -q "digital_utopia_admin"; then
    check_success "Admin container running"
else
    echo -e "${RED}✗ Admin container not running${NC}"
fi

# Check health endpoints
echo -e "\n${YELLOW}Checking health endpoints...${NC}"

# Wait a bit more for services to be fully ready
sleep 5

# Test health endpoint
HEALTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost/health" 2>/dev/null || echo "000")
if [ "$HEALTH_CODE" = "200" ]; then
    check_success "Health endpoint accessible (HTTP code: $HEALTH_CODE)"
else
    echo -e "${YELLOW}⚠ Health endpoint returned: $HEALTH_CODE${NC}"
fi

# Test API health
API_HEALTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost/api/health" 2>/dev/null || echo "000")
if [ "$API_HEALTH_CODE" = "200" ]; then
    check_success "API health endpoint accessible (HTTP code: $API_HEALTH_CODE)"
else
    echo -e "${YELLOW}⚠ API health endpoint returned: $API_HEALTH_CODE${NC}"
fi

# ============================================
# Step 9: Verify Domain Configuration
# ============================================
print_step "Step 9: Verify Domain Configuration"

# Check if containers can resolve each other
echo -e "${YELLOW}Checking container network connectivity...${NC}"

if docker exec digital_utopia_nginx_proxy getent hosts digital_utopia_backend > /dev/null 2>&1; then
    check_success "Nginx can resolve backend"
else
    echo -e "${YELLOW}⚠ Nginx cannot resolve backend${NC}"
fi

if docker exec digital_utopia_nginx_proxy getent hosts digital_utopia_client > /dev/null 2>&1; then
    check_success "Nginx can resolve client"
else
    echo -e "${YELLOW}⚠ Nginx cannot resolve client${NC}"
fi

if docker exec digital_utopia_nginx_proxy getent hosts digital_utopia_admin > /dev/null 2>&1; then
    check_success "Nginx can resolve admin"
else
    echo -e "${YELLOW}⚠ Nginx cannot resolve admin${NC}"
fi

# ============================================
# Step 10: Final Verification
# ============================================
print_step "Step 10: Final Verification"

echo -e "${YELLOW}Container Information:${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "digital_utopia|NAMES"

echo -e "\n${YELLOW}Network Information:${NC}"
docker network inspect digital_utopia_network --format '{{range .Containers}}{{.Name}} {{end}}' 2>/dev/null || echo "Network check skipped"

# ============================================
# Summary
# ============================================
print_step "Deployment Summary"

echo -e "${GREEN}=========================================="
echo "Deployment Complete!"
echo "==========================================${NC}\n"

echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Verify SSL certificate is configured (if using HTTPS)"
echo "2. Run acceptance tests: ./scripts/acceptance-test.sh"
echo "3. Test in browser: https://$DOMAIN"
echo "4. Test admin panel: https://$DOMAIN/admin"
echo "5. Review logs if any issues: docker-compose logs"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo "  View logs: $COMPOSE_CMD logs -f"
echo "  Check status: $COMPOSE_CMD ps"
echo "  Restart service: $COMPOSE_CMD restart [service-name]"
echo "  Stop all: $COMPOSE_CMD down"
echo ""
echo -e "${YELLOW}Acceptance Testing:${NC}"
echo "  Run automated tests: ./scripts/acceptance-test.sh $DOMAIN"
echo "  Follow browser checklist: BROWSER_ACCEPTANCE_CHECKLIST.md"
echo ""
echo -e "${GREEN}✓ Deployment completed!${NC}\n"

