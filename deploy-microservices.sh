#!/bin/bash
# Microservices Deployment Script
# Deploy complete stack with Backend API + TradingSystemAPI + Nginx Gateway

set -e

echo "=================================================="
echo "🚀 CMEETRADING Microservices Deployment"
echo "=================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo "Creating .env from .env.microservices template..."
    cp .env.microservices .env
    echo -e "${GREEN}✅ .env file created${NC}"
    echo -e "${YELLOW}⚠️  Please update .env with your configuration before continuing${NC}"
    echo "Press Enter to continue or Ctrl+C to abort..."
    read
fi

# Load environment variables
source .env

echo "📋 Deployment Configuration:"
echo "  - Backend API: Port 8000 (internal)"
echo "  - TradingSystemAPI: Port 8001 (external)"
echo "  - Nginx Gateway: Port 80"
echo "  - Client App: Port ${CLIENT_PORT:-3002}"
echo "  - Admin App: Port ${ADMIN_PORT:-3001}"
echo ""

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose -f docker-compose.microservices.yml down 2>/dev/null || true
echo -e "${GREEN}✅ Services stopped${NC}"
echo ""

# Build images
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.microservices.yml build --no-cache
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Images built successfully${NC}"
else
    echo -e "${RED}❌ Failed to build images${NC}"
    exit 1
fi
echo ""

# Start infrastructure services first
echo "🗄️  Starting infrastructure services (PostgreSQL, Redis)..."
docker-compose -f docker-compose.microservices.yml up -d postgres redis
echo "⏳ Waiting for database to be ready (30 seconds)..."
sleep 30
echo -e "${GREEN}✅ Infrastructure ready${NC}"
echo ""

# Start backend services
echo "🚀 Starting backend services..."
docker-compose -f docker-compose.microservices.yml up -d backend trading-system-api
echo "⏳ Waiting for backend services to start (20 seconds)..."
sleep 20
echo -e "${GREEN}✅ Backend services started${NC}"
echo ""

# Start nginx gateway
echo "🌐 Starting Nginx API Gateway..."
docker-compose -f docker-compose.microservices.yml up -d nginx
echo "⏳ Waiting for nginx to start (10 seconds)..."
sleep 10
echo -e "${GREEN}✅ Nginx gateway started${NC}"
echo ""

# Start frontend applications
echo "🎨 Starting frontend applications..."
docker-compose -f docker-compose.microservices.yml up -d client-app admin-app
echo "⏳ Waiting for frontend to start (15 seconds)..."
sleep 15
echo -e "${GREEN}✅ Frontend applications started${NC}"
echo ""

# Check service health
echo "🏥 Checking service health..."
echo ""

check_service() {
    local name=$1
    local url=$2
    local response=$(curl -s -o /dev/null -w "%{http_code}" $url 2>/dev/null)
    if [ "$response" = "200" ] || [ "$response" = "301" ] || [ "$response" = "302" ]; then
        echo -e "  ${GREEN}✅ $name: OK ($response)${NC}"
        return 0
    else
        echo -e "  ${RED}❌ $name: FAILED ($response)${NC}"
        return 1
    fi
}

check_service "Backend API" "http://localhost:8000/api/health"
check_service "TradingSystemAPI" "http://localhost:8001/health"
check_service "Nginx Gateway" "http://localhost/health"

echo ""
echo "=================================================="
echo "🎉 Deployment Complete!"
echo "=================================================="
echo ""
echo "📊 Service URLs:"
echo "  🌐 API Gateway:        http://localhost"
echo "  🔧 Backend API:        http://localhost/api/*"
echo "  📈 Trading API:        http://localhost/trading/*"
echo "  🔌 WebSocket:          ws://localhost/ws"
echo "  💻 Client App:         http://localhost:${CLIENT_PORT:-3002}"
echo "  ⚙️  Admin App:          http://localhost:${ADMIN_PORT:-3001}"
echo ""
echo "📖 API Documentation:"
echo "  🔧 Backend Swagger:    http://localhost:8000/docs"
echo "  📈 Trading Market:     http://localhost:8001/market/docs"
echo "  📊 Trading Features:   http://localhost:8001/trading/docs"
echo ""
echo "🔍 Service Status:"
echo "  docker-compose -f docker-compose.microservices.yml ps"
echo ""
echo "📋 View Logs:"
echo "  docker-compose -f docker-compose.microservices.yml logs -f [service]"
echo ""
echo "🛑 Stop Services:"
echo "  docker-compose -f docker-compose.microservices.yml down"
echo ""
echo "=================================================="
