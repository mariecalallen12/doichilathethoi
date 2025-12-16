#!/bin/bash
set -e

echo "🚀 Deploying Digital Utopia Platform"
echo "===================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it from .env.example first:"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

# Step 1: Start database services
echo ""
echo "📊 Step 1: Starting database services..."
docker-compose up -d postgres redis

# Wait for databases to be ready
echo "⏳ Waiting for databases to be ready..."
MAX_WAIT=60
WAIT_COUNT=0
until docker-compose exec -T postgres pg_isready -U "${POSTGRES_USER:-postgres}" > /dev/null 2>&1; do
    WAIT_COUNT=$((WAIT_COUNT + 1))
    if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
        echo "❌ PostgreSQL failed to start within ${MAX_WAIT} seconds"
        exit 1
    fi
    echo "   Waiting for PostgreSQL... (${WAIT_COUNT}/${MAX_WAIT})"
    sleep 2
done
echo "✅ PostgreSQL is ready!"

WAIT_COUNT=0
until docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; do
    WAIT_COUNT=$((WAIT_COUNT + 1))
    if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
        echo "❌ Redis failed to start within ${MAX_WAIT} seconds"
        exit 1
    fi
    echo "   Waiting for Redis... (${WAIT_COUNT}/${MAX_WAIT})"
    sleep 2
done
echo "✅ Redis is ready!"

# Step 2: Start backend
echo ""
echo "📦 Step 2: Starting backend service..."
docker-compose up -d backend

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
WAIT_COUNT=0
MAX_WAIT=120
until curl -f http://localhost:${BACKEND_PORT:-8000}/api/health > /dev/null 2>&1; do
    WAIT_COUNT=$((WAIT_COUNT + 1))
    if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
        echo "❌ Backend failed to start within ${MAX_WAIT} seconds"
        echo "📋 Backend logs:"
        docker-compose logs --tail=50 backend
        exit 1
    fi
    echo "   Waiting for backend... (${WAIT_COUNT}/${MAX_WAIT})"
    sleep 2
done
echo "✅ Backend is ready!"

# Step 3: Verify migrations
echo ""
echo "🔍 Step 3: Verifying database migrations..."
MIGRATION_CHECK=$(docker-compose exec -T backend alembic current 2>&1)
if [ $? -eq 0 ]; then
    echo "✅ Migrations are up to date"
    echo "$MIGRATION_CHECK"
else
    echo "⚠️  Running migrations..."
    docker-compose exec -T backend alembic upgrade head
    if [ $? -eq 0 ]; then
        echo "✅ Migrations completed"
    else
        echo "❌ Migration failed!"
        exit 1
    fi
fi

# Step 4: Start frontend services
echo ""
echo "🌐 Step 4: Starting frontend services..."
docker-compose up -d client-app admin-app

# Wait for frontend services
echo "⏳ Waiting for frontend services to be ready..."
sleep 10

# Step 5: Health check
echo ""
echo "🏥 Step 5: Running health checks..."
./scripts/health-check.sh

# Summary
echo ""
echo "===================================="
echo "✅ Deployment completed successfully!"
echo "===================================="
echo ""
echo "📊 Service Status:"
docker-compose ps
echo ""
echo "🌐 Access URLs:"
echo "   Backend API:    http://localhost:${BACKEND_PORT:-8000}"
echo "   API Docs:       http://localhost:${BACKEND_PORT:-8000}/docs"
echo "   Client App:     http://localhost:${CLIENT_PORT:-3002}"
echo "   Admin App:      http://localhost:${ADMIN_PORT:-3001}"
echo ""
echo "📋 Useful commands:"
echo "   View logs:      docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart:        docker-compose restart"

