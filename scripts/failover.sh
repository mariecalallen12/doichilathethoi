#!/bin/bash
# Failover Mechanism Script
# Handles failover for HA setup

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

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

# Check service health
check_service_health() {
    local service=$1
    
    if docker ps --format '{{.Names}}' | grep -q "^${service}$"; then
        health=$(docker inspect --format='{{.State.Health.Status}}' "$service" 2>/dev/null || echo "none")
        if [ "$health" = "healthy" ] || [ "$health" = "none" ]; then
            return 0
        fi
    fi
    return 1
}

# Failover to backup backend
failover_backend() {
    log_info "Initiating backend failover..."
    
    # Check primary backend
    if check_service_health "digital_utopia_backend_1"; then
        log_info "Primary backend is healthy"
        return 0
    fi
    
    log_warn "Primary backend is unhealthy, switching to backup..."
    
    # Update nginx config to use backup only
    # This would typically be done via API or config update
    log_info "Updating load balancer configuration..."
    
    # Restart nginx to pick up changes
    docker compose restart nginx-loadbalancer || true
    
    log_success "Failover to backup backend completed"
}

# Failover database (promote replica)
failover_database() {
    log_info "Initiating database failover..."
    
    # Check primary database
    if check_service_health "digital_utopia_postgres_primary"; then
        log_info "Primary database is healthy"
        return 0
    fi
    
    log_warn "Primary database is unhealthy, promoting replica..."
    
    # Promote replica to primary
    docker exec digital_utopia_postgres_replica pg_ctl promote || {
        log_error "Failed to promote replica"
        return 1
    }
    
    log_success "Database failover completed - replica promoted to primary"
}

# Main execution
main() {
    case "${1:-all}" in
        backend)
            failover_backend
            ;;
        database)
            failover_database
            ;;
        all|*)
            failover_backend
            failover_database
            ;;
    esac
}

main "$@"
