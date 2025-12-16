#!/bin/bash
set -e

echo "🏥 Production Health Check"
echo "=========================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
CLIENT_URL="${CLIENT_URL:-http://localhost:3002}"
ADMIN_URL="${ADMIN_URL:-http://localhost:3001}"
HEALTH_ENDPOINT="/api/health"

# Track failures
FAILURES=0

# Function to check service
check_service() {
    local name=$1
    local url=$2
    local endpoint=$3
    
    echo -n "Checking $name... "
    
    if response=$(curl -s -f -w "\n%{http_code}" --max-time 5 "$url$endpoint" 2>/dev/null); then
        http_code=$(echo "$response" | tail -n1)
        if [ "$http_code" = "200" ]; then
            echo -e "${GREEN}✅ OK${NC}"
            return 0
        else
            echo -e "${RED}❌ FAILED (HTTP $http_code)${NC}"
            FAILURES=$((FAILURES + 1))
            return 1
        fi
    else
        echo -e "${RED}❌ FAILED (Connection error)${NC}"
        FAILURES=$((FAILURES + 1))
        return 1
    fi
}

# Function to check Docker container
check_container() {
    local name=$1
    
    echo -n "Checking container $name... "
    
    if docker ps --format '{{.Names}}' | grep -q "^${name}$"; then
        if [ "$(docker inspect -f '{{.State.Health.Status}}' "$name" 2>/dev/null)" = "healthy" ] || \
           [ "$(docker inspect -f '{{.State.Status}}' "$name" 2>/dev/null)" = "running" ]; then
            echo -e "${GREEN}✅ RUNNING${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  RUNNING (unhealthy)${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ NOT RUNNING${NC}"
        FAILURES=$((FAILURES + 1))
        return 1
    fi
}

# Check Docker containers
echo "📦 Docker Containers:"
echo "-------------------"
check_container "digital_utopia_postgres"
check_container "digital_utopia_redis"
check_container "digital_utopia_backend"
check_container "digital_utopia_client"
check_container "digital_utopia_admin"
check_container "digital_utopia_nginx_proxy"
echo ""

# Check services
echo "🌐 Services:"
echo "------------"
check_service "Backend API" "$BACKEND_URL" "$HEALTH_ENDPOINT"
check_service "Client App" "$CLIENT_URL" "/health"
check_service "Admin App" "$ADMIN_URL" "/health"
echo ""

# Check database connection
echo "🗄️  Database:"
echo "------------"
echo -n "Checking PostgreSQL connection... "
if docker exec digital_utopia_postgres pg_isready -U postgres >/dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
    FAILURES=$((FAILURES + 1))
fi

# Check Redis connection
echo -n "Checking Redis connection... "
if docker exec digital_utopia_redis redis-cli ping >/dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# Check disk space
echo "💾 Disk Space:"
echo "-------------"
df -h / | tail -1 | awk '{print "Root partition: " $5 " used (" $4 " available)"}'
echo ""

# Check memory
echo "🧠 Memory:"
echo "---------"
free -h | grep Mem | awk '{print "Memory: " $3 "/" $2 " (" $3/$2*100 "%)"}'
echo ""

# Summary
echo "=========================="
if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ All health checks passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ $FAILURES health check(s) failed${NC}"
    exit 1
fi

