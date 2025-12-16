#!/bin/bash

# Production Deployment Script for Real-time Updates
# Deploys updated backend and frontend with real-time optimizations

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="/root/forexxx"
VERSION_TAG="v2.1.1-realtime-$(date +%Y%m%d-%H%M%S)"
BACKUP_TAG="backup-$(date +%Y%m%d-%H%M%S)"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

cd "$PROJECT_ROOT"

log_info "=== Production Deployment: Real-time Updates ==="
log_info "Version: $VERSION_TAG"
log_info "Backup Tag: $BACKUP_TAG"
echo ""

# Step 1: Create backups
log_info "Step 1: Creating backups..."
docker tag digital_utopia_backend:latest digital_utopia_backend:$BACKUP_TAG 2>/dev/null || true
docker tag digital_utopia_client:latest digital_utopia_client:$BACKUP_TAG 2>/dev/null || true
docker tag digital_utopia_admin:latest digital_utopia_admin:$BACKUP_TAG 2>/dev/null || true
log_success "Backups created"

# Step 2: Build backend with new code
log_info "Step 2: Building backend with real-time updates..."
cd "$PROJECT_ROOT/backend"
docker build -t digital_utopia_backend:$VERSION_TAG -t digital_utopia_backend:latest .
if [ $? -eq 0 ]; then
    log_success "Backend built successfully"
else
    log_error "Backend build failed"
    exit 1
fi

# Step 3: Build client-app with new code
log_info "Step 3: Building client-app with real-time updates..."
cd "$PROJECT_ROOT/client-app"
docker build -t digital_utopia_client:$VERSION_TAG -t digital_utopia_client:latest .
if [ $? -eq 0 ]; then
    log_success "Client-app built successfully"
else
    log_error "Client-app build failed"
    exit 1
fi

# Step 4: Build admin-app (optional, no changes but rebuild for consistency)
log_info "Step 4: Building admin-app..."
cd "$PROJECT_ROOT/Admin-app"
docker build -t digital_utopia_admin:$VERSION_TAG -t digital_utopia_admin:latest .
if [ $? -eq 0 ]; then
    log_success "Admin-app built successfully"
else
    log_warning "Admin-app build failed (non-critical)"
fi

# Step 5: Stop and remove old containers
log_info "Step 5: Stopping old containers..."
docker stop digital_utopia_backend digital_utopia_client digital_utopia_admin 2>/dev/null || true
docker rm digital_utopia_backend digital_utopia_client digital_utopia_admin 2>/dev/null || true
log_success "Old containers stopped"

# Step 6: Start new containers
log_info "Step 6: Starting new containers..."
cd "$PROJECT_ROOT"

# Start backend
log_info "Starting backend..."
docker run -d \
    --name digital_utopia_backend \
    --network digital_utopia_network \
    --restart unless-stopped \
    -p 8000:8000 \
    -e POSTGRES_SERVER=digital_utopia_postgres \
    -e POSTGRES_PORT=5432 \
    -e POSTGRES_USER=${POSTGRES_USER:-postgres} \
    -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres} \
    -e POSTGRES_DB=${POSTGRES_DB:-digital_utopia} \
    -e REDIS_HOST=digital_utopia_redis \
    -e REDIS_PORT=6379 \
    -e REDIS_PASSWORD=${REDIS_PASSWORD:-} \
    -e DEBUG=false \
    -e ENVIRONMENT=production \
    -e LOG_LEVEL=WARNING \
    -e SECRET_KEY=${SECRET_KEY:-CHANGE-THIS} \
    -e CORS_ORIGINS=${CORS_ORIGINS:-https://cmeetrading.com,http://cmeetrading.com} \
    digital_utopia_backend:latest \
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --no-access-log

if [ $? -eq 0 ]; then
    log_success "Backend started"
else
    log_error "Backend start failed"
    exit 1
fi

# Wait for backend to be ready
log_info "Waiting for backend to be ready..."
sleep 10
for i in {1..30}; do
    if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
        log_success "Backend is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        log_error "Backend health check failed"
        exit 1
    fi
    sleep 2
done

# Start client-app
log_info "Starting client-app..."
docker run -d \
    --name digital_utopia_client \
    --network digital_utopia_network \
    --restart unless-stopped \
    -p 3002:80 \
    digital_utopia_client:latest

if [ $? -eq 0 ]; then
    log_success "Client-app started"
else
    log_error "Client-app start failed"
    exit 1
fi

# Start admin-app
log_info "Starting admin-app..."
docker run -d \
    --name digital_utopia_admin \
    --network digital_utopia_network \
    --restart unless-stopped \
    -p 3001:80 \
    digital_utopia_admin:latest

if [ $? -eq 0 ]; then
    log_success "Admin-app started"
else
    log_warning "Admin-app start failed (non-critical)"
fi

# Step 7: Verify deployment
log_info "Step 7: Verifying deployment..."
sleep 5

# Check backend
if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    log_success "✅ Backend health check passed"
else
    log_error "❌ Backend health check failed"
    exit 1
fi

# Check client-app
if curl -f http://localhost:3002 > /dev/null 2>&1; then
    log_success "✅ Client-app is accessible"
else
    log_error "❌ Client-app is not accessible"
    exit 1
fi

# Check admin-app
if curl -f http://localhost:3001 > /dev/null 2>&1; then
    log_success "✅ Admin-app is accessible"
else
    log_warning "⚠️  Admin-app check failed (non-critical)"
fi

# Step 8: Verify real-time updates
log_info "Step 8: Verifying real-time updates..."
if curl -f http://localhost:8000/api/trading-simulator/snapshot > /dev/null 2>&1; then
    log_success "✅ Trading simulator is running"
else
    log_warning "⚠️  Trading simulator check failed"
fi

echo ""
log_success "=== Deployment Completed Successfully ==="
log_info "Version: $VERSION_TAG"
log_info "Backup Tag: $BACKUP_TAG"
log_info ""
log_info "Services:"
log_info "  - Backend: http://localhost:8000"
log_info "  - Client-app: http://localhost:3002"
log_info "  - Admin-app: http://localhost:3001"
log_info ""
log_info "To rollback if needed:"
log_info "  docker tag digital_utopia_backend:$BACKUP_TAG digital_utopia_backend:latest"
log_info "  docker tag digital_utopia_client:$BACKUP_TAG digital_utopia_client:latest"
log_info "  docker tag digital_utopia_admin:$BACKUP_TAG digital_utopia_admin:latest"
log_info "  # Then restart containers"

