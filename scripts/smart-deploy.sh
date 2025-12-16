#!/bin/bash
# Smart Deploy Script
# Digital Utopia Platform - Deploy with error handling, retry, and auto-fix

set -e

# Source libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/error-handler.sh"
source "$SCRIPT_DIR/lib/retry.sh"
source "$SCRIPT_DIR/lib/log-parser.sh"
source "$SCRIPT_DIR/config/build-config.sh"
source "$SCRIPT_DIR/error-detector.sh"
source "$SCRIPT_DIR/auto-fix.sh"
source "$SCRIPT_DIR/monitor-logs.sh"
source "$SCRIPT_DIR/status-monitor.sh"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Deployment tracking
DEPLOY_START_TIME=$(date +%s)
DEPLOYMENTS_SUCCEEDED=0
DEPLOYMENTS_FAILED=0

# Load environment
load_environment() {
    if [ ! -f .env ]; then
        log_error $ERROR_TYPE_CONFIG $SEVERITY_CRITICAL ".env file not found" ""
        echo "❌ .env file not found. Please create it from .env.example first:"
        echo "   cp .env.example .env"
        echo "   nano .env"
        exit 1
    fi
    
    set -a
    source .env
    set +a
}

# Initialize deployment
init_deploy() {
    echo "🚀 Smart Deploy - Digital Utopia Platform"
    echo "=========================================="
    echo ""
    
    # Initialize error log
    init_error_log
    
    # Load environment
    load_environment
    
    # Check prerequisites
    echo "📋 Pre-deployment validation..."
    check_prerequisites
    
    echo "✅ Pre-deployment checks passed"
    echo ""
}

# Check prerequisites
check_prerequisites() {
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error $ERROR_TYPE_CONFIG $SEVERITY_CRITICAL "Docker is not installed" ""
        exit 1
    fi
    
    # Check docker-compose
    if ! command -v docker-compose &> /dev/null; then
        log_error $ERROR_TYPE_CONFIG $SEVERITY_CRITICAL "docker-compose is not installed" ""
        exit 1
    fi
    
    # Check if images are built
    local images_missing=false
    for service in "${BUILD_ORDER[@]}"; do
        if ! docker images | grep -q "$(basename $(pwd))_${service}"; then
            echo "⚠️  Image for $service not found. Building..."
            "$SCRIPT_DIR/smart-build.sh" "$service" || images_missing=true
        fi
    done
    
    if [ "$images_missing" = true ]; then
        echo "❌ Some images are missing. Please build first:"
        echo "   ./scripts/smart-build.sh"
        exit 1
    fi
    
    echo "  ✅ All images are built"
}

# Deploy database services
deploy_databases() {
    echo ""
    echo "📊 Step 1: Deploying database services..."
    echo "=========================================="
    
    # Start PostgreSQL
    echo "📦 Starting PostgreSQL..."
    if docker-compose up -d postgres; then
        # Wait for PostgreSQL with retry
        echo "⏳ Waiting for PostgreSQL to be ready..."
        retry_database $MAX_DATABASE_RETRIES \
            "docker-compose exec -T postgres pg_isready -U \${POSTGRES_USER:-postgres}" > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            echo "✅ PostgreSQL is ready!"
            DEPLOYMENTS_SUCCEEDED=$((DEPLOYMENTS_SUCCEEDED + 1))
        else
            echo "❌ PostgreSQL failed to start"
            DEPLOYMENTS_FAILED=$((DEPLOYMENTS_FAILED + 1))
            return 1
        fi
    else
        echo "❌ Failed to start PostgreSQL"
        DEPLOYMENTS_FAILED=$((DEPLOYMENTS_FAILED + 1))
        return 1
    fi
    
    # Start Redis
    echo ""
    echo "📦 Starting Redis..."
    if docker-compose up -d redis; then
        # Wait for Redis with retry
        echo "⏳ Waiting for Redis to be ready..."
        retry_network $MAX_NETWORK_RETRIES \
            "docker-compose exec -T redis redis-cli ping" > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            echo "✅ Redis is ready!"
            DEPLOYMENTS_SUCCEEDED=$((DEPLOYMENTS_SUCCEEDED + 1))
        else
            echo "❌ Redis failed to start"
            DEPLOYMENTS_FAILED=$((DEPLOYMENTS_FAILED + 1))
            return 1
        fi
    else
        echo "❌ Failed to start Redis"
        DEPLOYMENTS_FAILED=$((DEPLOYMENTS_FAILED + 1))
        return 1
    fi
}

# Deploy backend
deploy_backend() {
    echo ""
    echo "📦 Step 2: Deploying backend service..."
    echo "======================================="
    
    # Start backend
    echo "📦 Starting backend..."
    if docker-compose up -d backend; then
        # Monitor logs in background
        monitor_service "backend" &
        local monitor_pid=$!
        
        # Wait for backend with retry
        echo "⏳ Waiting for backend to be ready..."
        wait_for_condition \
            "curl -f -s http://localhost:\${BACKEND_PORT:-8000}/api/health > /dev/null 2>&1" \
            $HEALTH_CHECK_TIMEOUT \
            2 \
            "Backend health check"
        
        if [ $? -eq 0 ]; then
            echo "✅ Backend is ready!"
            DEPLOYMENTS_SUCCEEDED=$((DEPLOYMENTS_SUCCEEDED + 1))
            
            # Stop monitoring
            kill $monitor_pid 2>/dev/null || true
            wait $monitor_pid 2>/dev/null || true
            
            # Run migrations
            echo ""
            echo "🔍 Step 3: Running database migrations..."
            run_migrations
            
            return 0
        else
            echo "❌ Backend failed to start"
            
            # Check for errors
            local errors=$(get_recent_errors "backend" 20)
            if [ -n "$errors" ]; then
                echo ""
                echo "Errors detected:"
                echo "$errors" | head -5 | sed 's/^/  /'
                
                # Try auto-fix
                echo ""
                echo "🔧 Attempting to auto-fix..."
                while IFS= read -r error_line; do
                    if [ -n "$error_line" ]; then
                        auto_fix_error "$error_line" || true
                    fi
                done <<< "$errors"
                
                # Retry deployment
                echo ""
                echo "🔄 Retrying backend deployment..."
                docker-compose restart backend
                sleep 5
                
                wait_for_condition \
                    "curl -f -s http://localhost:\${BACKEND_PORT:-8000}/api/health > /dev/null 2>&1" \
                    $HEALTH_CHECK_TIMEOUT \
                    2 \
                    "Backend health check (retry)"
                
                if [ $? -eq 0 ]; then
                    echo "✅ Backend started after fix!"
                    DEPLOYMENTS_SUCCEEDED=$((DEPLOYMENTS_SUCCEEDED + 1))
                    return 0
                fi
            fi
            
            # Stop monitoring
            kill $monitor_pid 2>/dev/null || true
            wait $monitor_pid 2>/dev/null || true
            
            DEPLOYMENTS_FAILED=$((DEPLOYMENTS_FAILED + 1))
            return 1
        fi
    else
        echo "❌ Failed to start backend"
        DEPLOYMENTS_FAILED=$((DEPLOYMENTS_FAILED + 1))
        return 1
    fi
}

# Run migrations
run_migrations() {
    echo "⏳ Running migrations..."
    
    # Check migration status
    local migration_status=$(docker-compose exec -T backend alembic current 2>&1)
    if [ $? -eq 0 ]; then
        echo "✅ Migrations are up to date"
        echo "$migration_status" | head -1
    else
        echo "⚠️  Running migrations..."
        retry_database $MAX_DATABASE_RETRIES \
            "docker-compose exec -T backend alembic upgrade head" > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            echo "✅ Migrations completed"
        else
            echo "❌ Migration failed!"
            log_error $ERROR_TYPE_DATABASE $SEVERITY_HIGH "Migration failed" ""
            return 1
        fi
    fi
}

# Deploy frontend services
deploy_frontend() {
    echo ""
    echo "🌐 Step 4: Deploying frontend services..."
    echo "========================================="
    
    # Start client-app
    echo "📦 Starting client-app..."
    if docker-compose up -d client-app; then
        sleep 5
        if check_service_health_from_logs "client-app" 30; then
            echo "✅ Client app is ready!"
            DEPLOYMENTS_SUCCEEDED=$((DEPLOYMENTS_SUCCEEDED + 1))
        else
            echo "⚠️  Client app started but health check uncertain"
        fi
    else
        echo "❌ Failed to start client-app"
        DEPLOYMENTS_FAILED=$((DEPLOYMENTS_FAILED + 1))
    fi
    
    # Start admin-app
    echo ""
    echo "📦 Starting admin-app..."
    if docker-compose up -d admin-app; then
        sleep 5
        if check_service_health_from_logs "admin-app" 30; then
            echo "✅ Admin app is ready!"
            DEPLOYMENTS_SUCCEEDED=$((DEPLOYMENTS_SUCCEEDED + 1))
        else
            echo "⚠️  Admin app started but health check uncertain"
        fi
    else
        echo "❌ Failed to start admin-app"
        DEPLOYMENTS_FAILED=$((DEPLOYMENTS_FAILED + 1))
    fi
}

# Post-deployment verification
post_deploy_verification() {
    echo ""
    echo "🔍 Step 5: Post-deployment verification..."
    echo "=========================================="
    
    # Run health checks
    if [ -f "$SCRIPT_DIR/health-check.sh" ]; then
        "$SCRIPT_DIR/health-check.sh"
    else
        # Basic health checks
        echo "Checking service health..."
        
        local all_healthy=true
        
        # Check PostgreSQL
        if docker-compose exec -T postgres pg_isready -U ${POSTGRES_USER:-postgres} > /dev/null 2>&1; then
            echo "  ✅ PostgreSQL: healthy"
        else
            echo "  ❌ PostgreSQL: unhealthy"
            all_healthy=false
        fi
        
        # Check Redis
        if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
            echo "  ✅ Redis: healthy"
        else
            echo "  ❌ Redis: unhealthy"
            all_healthy=false
        fi
        
        # Check Backend
        if curl -f -s http://localhost:${BACKEND_PORT:-8000}/api/health > /dev/null 2>&1; then
            echo "  ✅ Backend: healthy"
        else
            echo "  ❌ Backend: unhealthy"
            all_healthy=false
        fi
        
        if [ "$all_healthy" = true ]; then
            echo ""
            echo "✅ All services are healthy"
            return 0
        else
            echo ""
            echo "❌ Some services are unhealthy"
            return 1
        fi
    fi
}

# Deployment summary
deploy_summary() {
    local deploy_end_time=$(date +%s)
    local deploy_duration=$((deploy_end_time - DEPLOY_START_TIME))
    
    echo ""
    echo "=========================================="
    echo "📊 Deployment Summary"
    echo "=========================================="
    echo "Deployment duration: ${deploy_duration}s"
    echo "Deployments succeeded: $DEPLOYMENTS_SUCCEEDED"
    echo "Deployments failed: $DEPLOYMENTS_FAILED"
    echo ""
    
    # Error summary
    get_error_summary
    
    # Fix summary
    get_fix_summary
    
    echo ""
    echo "🌐 Access URLs:"
    echo "   Backend API:    http://localhost:${BACKEND_PORT:-8000}"
    echo "   API Docs:       http://localhost:${BACKEND_PORT:-8000}/docs"
    echo "   Client App:     http://localhost:${CLIENT_PORT:-3002}"
    echo "   Admin App:      http://localhost:${ADMIN_PORT:-3001}"
    echo ""
    
    if [ $DEPLOYMENTS_FAILED -eq 0 ]; then
        echo "✅ Deployment completed successfully!"
        return 0
    else
        echo "❌ Some deployments failed"
        return 1
    fi
}

# Main function
main() {
    # Initialize
    init_deploy
    
    # Deploy databases
    deploy_databases || {
        echo "❌ Database deployment failed"
        deploy_summary
        exit 1
    }
    
    # Deploy backend
    deploy_backend || {
        echo "❌ Backend deployment failed"
        deploy_summary
        exit 1
    }
    
    # Deploy frontend
    deploy_frontend
    
    # Post-deployment verification
    post_deploy_verification
    
    # Summary
    deploy_summary
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi

