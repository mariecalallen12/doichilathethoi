#!/bin/bash
# High Availability Setup Script
# Configures HA with multiple backends, load balancing, and database replication

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if docker-compose.ha.yml exists
    if [ ! -f "$PROJECT_ROOT/docker-compose.ha.yml" ]; then
        log_error "docker-compose.ha.yml not found"
        exit 1
    fi
    
    # Check if nginx-ha.conf exists
    if [ ! -f "$PROJECT_ROOT/nginx/nginx-ha.conf" ]; then
        log_error "nginx-ha.conf not found"
        exit 1
    fi
    
    log_success "Prerequisites checked"
}

# Setup PostgreSQL replication
setup_postgres_replication() {
    log_info "Setting up PostgreSQL replication..."
    
    # Create replication user
    docker exec digital_utopia_postgres_primary psql -U postgres -c "
        CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'replicator_password';
        ALTER USER replicator WITH REPLICATION;
    " || log_warn "Replication user may already exist"
    
    log_success "PostgreSQL replication configured"
}

# Setup Redis Sentinel
setup_redis_sentinel() {
    log_info "Setting up Redis Sentinel..."
    
    # Create sentinel config directory if it doesn't exist
    mkdir -p "$PROJECT_ROOT/redis"
    
    if [ ! -f "$PROJECT_ROOT/redis/sentinel.conf" ]; then
        log_error "sentinel.conf not found"
        exit 1
    fi
    
    log_success "Redis Sentinel configuration ready"
}

# Start HA services
start_ha_services() {
    log_info "Starting HA services..."
    
    # Start with HA compose file
    docker compose -f docker-compose.yml -f docker-compose.ha.yml up -d || {
        log_error "Failed to start HA services"
        exit 1
    }
    
    log_success "HA services started"
}

# Verify HA setup
verify_ha_setup() {
    log_info "Verifying HA setup..."
    
    # Check backend instances
    backend_1=$(docker ps --format '{{.Names}}' | grep -c "backend_1" || echo "0")
    backend_2=$(docker ps --format '{{.Names}}' | grep -c "backend_2" || echo "0")
    
    if [ "$backend_1" -eq 1 ] && [ "$backend_2" -eq 1 ]; then
        log_success "Both backend instances are running"
    else
        log_error "Backend instances are not running correctly"
    fi
    
    # Check PostgreSQL replication
    if docker ps --format '{{.Names}}' | grep -q "postgres_replica"; then
        log_success "PostgreSQL replica is running"
    else
        log_warn "PostgreSQL replica is not running"
    fi
    
    # Check Redis Sentinels
    sentinel_count=$(docker ps --format '{{.Names}}' | grep -c "redis_sentinel" || echo "0")
    if [ "$sentinel_count" -ge 2 ]; then
        log_success "$sentinel_count Redis Sentinels are running"
    else
        log_warn "Not enough Redis Sentinels running"
    fi
    
    # Check load balancer
    if docker ps --format '{{.Names}}' | grep -q "nginx_loadbalancer"; then
        log_success "Nginx load balancer is running"
    else
        log_error "Nginx load balancer is not running"
    fi
}

# Main execution
main() {
    echo "=========================================="
    echo "High Availability Setup"
    echo "Date: $(date)"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    echo ""
    setup_postgres_replication
    echo ""
    setup_redis_sentinel
    echo ""
    start_ha_services
    echo ""
    sleep 10
    verify_ha_setup
    echo ""
    log_success "HA setup complete!"
}

main
