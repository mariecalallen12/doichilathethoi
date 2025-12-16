#!/bin/bash
# Script to verify deployment health
# Checks all services, connectivity, and generates a report

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_section() {
    echo ""
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Report file
REPORT_FILE="deployment_verification_$(date +%Y%m%d_%H%M%S).txt"
REPORT_DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Initialize report
{
    echo "Deployment Verification Report"
    echo "Generated: $REPORT_DATE"
    echo "========================================"
    echo ""
} > "$REPORT_FILE"

# Check container status
check_container() {
    local container_name=$1
    local service_name=$2
    
    if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
        local status=$(docker inspect --format='{{.State.Status}}' "$container_name" 2>/dev/null || echo "unknown")
        local health=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "none")
        
        if [ "$status" = "running" ]; then
            if [ "$health" = "healthy" ] || [ "$health" = "none" ]; then
                log_info "✓ $service_name: Running ($health)"
                echo "✓ $service_name: Running ($health)" >> "$REPORT_FILE"
                return 0
            else
                log_warn "⚠ $service_name: Running but unhealthy ($health)"
                echo "⚠ $service_name: Running but unhealthy ($health)" >> "$REPORT_FILE"
                return 1
            fi
        else
            log_error "✗ $service_name: Not running (status: $status)"
            echo "✗ $service_name: Not running (status: $status)" >> "$REPORT_FILE"
            return 1
        fi
    else
        log_error "✗ $service_name: Container not found"
        echo "✗ $service_name: Container not found" >> "$REPORT_FILE"
        return 1
    fi
}

# Test HTTP endpoint
test_endpoint() {
    local url=$1
    local name=$2
    
    if curl -f -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|301\|302"; then
        log_info "✓ $name: Accessible"
        echo "✓ $name: Accessible" >> "$REPORT_FILE"
        return 0
    else
        log_error "✗ $name: Not accessible"
        echo "✗ $name: Not accessible" >> "$REPORT_FILE"
        return 1
    fi
}

# Test database connection
test_database() {
    if docker exec digital_utopia_postgres pg_isready -U postgres &> /dev/null; then
        log_info "✓ PostgreSQL: Connected"
        echo "✓ PostgreSQL: Connected" >> "$REPORT_FILE"
        return 0
    else
        log_error "✗ PostgreSQL: Connection failed"
        echo "✗ PostgreSQL: Connection failed" >> "$REPORT_FILE"
        return 1
    fi
}

# Test Redis connection
test_redis() {
    if docker exec digital_utopia_redis redis-cli ping &> /dev/null; then
        log_info "✓ Redis: Connected"
        echo "✓ Redis: Connected" >> "$REPORT_FILE"
        return 0
    else
        log_error "✗ Redis: Connection failed"
        echo "✗ Redis: Connection failed" >> "$REPORT_FILE"
        return 1
    fi
}

# Main verification
log_section "Container Status"
check_container "digital_utopia_postgres" "PostgreSQL"
check_container "digital_utopia_redis" "Redis"
check_container "digital_utopia_backend" "Backend API"
check_container "digital_utopia_client" "Client App"
check_container "digital_utopia_admin" "Admin App"
check_container "digital_utopia_nginx_proxy" "Nginx Proxy"

log_section "Database Connectivity"
test_database

log_section "Redis Connectivity"
test_redis

log_section "HTTP Endpoints"
test_endpoint "http://localhost:8000/api/health" "Backend Health"
test_endpoint "http://localhost:3002/health" "Client App"
test_endpoint "http://localhost:3001/health" "Admin App"

# Test backend health endpoint response
log_section "Backend Health Details"
if curl -f -s http://localhost:8000/api/health > /tmp/backend_health.json 2>&1; then
    log_info "Backend health response:"
    cat /tmp/backend_health.json | python3 -m json.tool 2>/dev/null || cat /tmp/backend_health.json
    echo "" >> "$REPORT_FILE"
    echo "Backend health response:" >> "$REPORT_FILE"
    cat /tmp/backend_health.json >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    rm -f /tmp/backend_health.json
else
    log_warn "Could not fetch backend health details"
fi

# Network verification
log_section "Network Configuration"
NETWORK_NAME="digital_utopia_network"
if docker network inspect "$NETWORK_NAME" &> /dev/null; then
    log_info "✓ Network $NETWORK_NAME exists"
    echo "✓ Network $NETWORK_NAME exists" >> "$REPORT_FILE"
    
    # Check containers on network
    CONTAINERS_ON_NETWORK=$(docker network inspect "$NETWORK_NAME" --format '{{range .Containers}}{{.Name}} {{end}}')
    log_info "Containers on network: $CONTAINERS_ON_NETWORK"
    echo "Containers on network: $CONTAINERS_ON_NETWORK" >> "$REPORT_FILE"
else
    log_error "✗ Network $NETWORK_NAME does not exist"
    echo "✗ Network $NETWORK_NAME does not exist" >> "$REPORT_FILE"
fi

# Summary
echo "" >> "$REPORT_FILE"
echo "========================================" >> "$REPORT_FILE"
echo "Verification completed: $REPORT_DATE" >> "$REPORT_FILE"

log_section "Summary"
log_info "Verification report saved to: $REPORT_FILE"
log_info "Review the report for detailed status of all services"
