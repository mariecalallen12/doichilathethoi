#!/bin/bash
# Script to fix deployment issues automatically
# Fixes network connectivity, restarts services, and verifies deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if docker and docker compose are available
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed or not in PATH"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    log_error "Docker Compose is not available"
    exit 1
fi

log_info "Starting deployment issue fixes..."

# Step 1: Verify network exists
log_info "Step 1: Verifying Docker network..."
NETWORK_NAME="digital_utopia_network"
if ! docker network inspect "$NETWORK_NAME" &> /dev/null; then
    log_warn "Network $NETWORK_NAME does not exist, creating it..."
    docker network create "$NETWORK_NAME" || true
else
    log_info "Network $NETWORK_NAME exists"
fi

# Step 2: Check and fix container network connectivity
log_info "Step 2: Checking container network connectivity..."

CONTAINERS=(
    "digital_utopia_postgres"
    "digital_utopia_redis"
    "digital_utopia_backend"
    "digital_utopia_client"
    "digital_utopia_admin"
    "digital_utopia_nginx_proxy"
)

for container in "${CONTAINERS[@]}"; do
    if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
        # Check if container is on the network
        if ! docker inspect "$container" 2>/dev/null | grep -q "$NETWORK_NAME"; then
            log_warn "Container $container is not on network $NETWORK_NAME, connecting..."
            docker network connect "$NETWORK_NAME" "$container" 2>/dev/null || log_warn "Could not connect $container to network (may already be connected)"
        else
            log_info "Container $container is on network $NETWORK_NAME"
        fi
    fi
done

# Step 3: Verify environment file
log_info "Step 3: Verifying environment configuration..."
if [ -f ".env.production" ]; then
    log_info "Found .env.production"
    # Check critical variables
    if grep -q "POSTGRES_SERVER=postgres" .env.production 2>/dev/null; then
        log_info "POSTGRES_SERVER is correctly set to service name"
    else
        log_warn "POSTGRES_SERVER may not be set correctly in .env.production"
    fi
    
    if grep -q "REDIS_HOST=redis" .env.production 2>/dev/null; then
        log_info "REDIS_HOST is correctly set to service name"
    else
        log_warn "REDIS_HOST may not be set correctly in .env.production"
    fi
else
    log_warn ".env.production not found, using defaults"
fi

# Step 4: Stop existing containers gracefully
log_info "Step 4: Stopping existing containers..."
docker compose -f docker-compose.yml down --timeout 30 || true

# Step 5: Start services in correct order
log_info "Step 5: Starting services..."
docker compose -f docker-compose.yml up -d postgres redis

# Wait for database and redis to be healthy
log_info "Waiting for PostgreSQL and Redis to be healthy..."
sleep 10

MAX_WAIT=60
WAIT_COUNT=0
while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    if docker exec digital_utopia_postgres pg_isready -U postgres &> /dev/null; then
        log_info "PostgreSQL is ready"
        break
    fi
    WAIT_COUNT=$((WAIT_COUNT + 2))
    sleep 2
done

if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
    log_warn "PostgreSQL may not be ready, continuing anyway..."
fi

# Start backend
log_info "Starting backend..."
docker compose -f docker-compose.yml up -d backend

# Wait a bit for backend to start
sleep 5

# Start frontend apps
log_info "Starting frontend applications..."
docker compose -f docker-compose.yml up -d client-app admin-app

# Start nginx (should start now that dependencies are met)
log_info "Starting nginx proxy..."
docker compose -f docker-compose.yml up -d nginx-proxy

# Step 6: Verify services are running
log_info "Step 6: Verifying services..."
sleep 5

ALL_HEALTHY=true
for container in "${CONTAINERS[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        STATUS=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "unknown")
        if [ "$STATUS" = "running" ]; then
            log_info "✓ Container $container is running"
        else
            log_error "✗ Container $container is not running (status: $STATUS)"
            ALL_HEALTHY=false
        fi
    else
        log_error "✗ Container $container is not found"
        ALL_HEALTHY=false
    fi
done

# Step 7: Test connectivity
log_info "Step 7: Testing connectivity..."

# Test backend health
if curl -f -s http://localhost:8000/api/health > /dev/null 2>&1; then
    log_info "✓ Backend health check passed"
else
    log_warn "✗ Backend health check failed (may still be starting)"
fi

# Test client app
if curl -f -s http://localhost:3002/health > /dev/null 2>&1; then
    log_info "✓ Client app health check passed"
else
    log_warn "✗ Client app health check failed"
fi

# Test admin app
if curl -f -s http://localhost:3001/health > /dev/null 2>&1; then
    log_info "✓ Admin app health check passed"
else
    log_warn "✗ Admin app health check failed"
fi

# Summary
echo ""
log_info "=== Deployment Fix Summary ==="
if [ "$ALL_HEALTHY" = true ]; then
    log_info "All containers are running"
    log_info "Deployment fixes completed successfully!"
    exit 0
else
    log_warn "Some containers may not be running properly"
    log_warn "Please check logs: docker compose logs"
    exit 1
fi
