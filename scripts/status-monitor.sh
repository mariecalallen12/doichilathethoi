#!/bin/bash
# Status Monitor
# Digital Utopia Platform - Real-time status monitoring

set -e

# Source libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/error-handler.sh"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Monitor status
MONITORING=true
UPDATE_INTERVAL=2

# Service status tracking
declare -A SERVICE_STATUS
declare -A SERVICE_HEALTH

# Initialize status
init_status() {
    local services=("postgres" "redis" "backend" "client-app" "admin-app")
    for service in "${services[@]}"; do
        SERVICE_STATUS["$service"]="unknown"
        SERVICE_HEALTH["$service"]="unknown"
    done
}

# Get service status
get_service_status() {
    local service="$1"
    
    if docker-compose ps "$service" 2>/dev/null | grep -q "Up"; then
        echo "running"
    elif docker-compose ps "$service" 2>/dev/null | grep -q "Exit"; then
        echo "stopped"
    else
        echo "not_running"
    fi
}

# Get service health
get_service_health() {
    local service="$1"
    
    case "$service" in
        postgres)
            if docker-compose exec -T postgres pg_isready -U ${POSTGRES_USER:-postgres} > /dev/null 2>&1; then
                echo "healthy"
            else
                echo "unhealthy"
            fi
            ;;
        redis)
            if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
                echo "healthy"
            else
                echo "unhealthy"
            fi
            ;;
        backend)
            if curl -f -s http://localhost:${BACKEND_PORT:-8000}/api/health > /dev/null 2>&1; then
                echo "healthy"
            else
                echo "unhealthy"
            fi
            ;;
        client-app|admin-app)
            local port=""
            if [ "$service" = "client-app" ]; then
                port="${CLIENT_PORT:-3002}"
            else
                port="${ADMIN_PORT:-3001}"
            fi
            if curl -f -s http://localhost:$port > /dev/null 2>&1; then
                echo "healthy"
            else
                echo "unhealthy"
            fi
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Update service status
update_service_status() {
    local service="$1"
    SERVICE_STATUS["$service"]=$(get_service_status "$service")
    SERVICE_HEALTH["$service"]=$(get_service_health "$service")
}

# Display status
display_status() {
    clear
    echo "📊 Digital Utopia Platform - Service Status"
    echo "==========================================="
    echo ""
    echo "Last update: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    printf "%-15s %-12s %-10s\n" "SERVICE" "STATUS" "HEALTH"
    echo "----------------------------------------"
    
    for service in "${!SERVICE_STATUS[@]}"; do
        local status="${SERVICE_STATUS[$service]}"
        local health="${SERVICE_HEALTH[$service]}"
        
        local status_color=""
        local health_color=""
        
        case "$status" in
            running) status_color="$GREEN" ;;
            stopped) status_color="$RED" ;;
            *) status_color="$YELLOW" ;;
        esac
        
        case "$health" in
            healthy) health_color="$GREEN" ;;
            unhealthy) health_color="$RED" ;;
            *) health_color="$YELLOW" ;;
        esac
        
        printf "%-15s ${status_color}%-12s${NC} ${health_color}%-10s${NC}\n" \
            "$service" "$status" "$health"
    done
    
    echo ""
    echo "Press Ctrl+C to stop monitoring"
}

# Monitor loop
monitor_loop() {
    while [ "$MONITORING" = true ]; do
        # Update all service statuses
        for service in "${!SERVICE_STATUS[@]}"; do
            update_service_status "$service"
        done
        
        # Display status
        display_status
        
        # Wait before next update
        sleep $UPDATE_INTERVAL
    done
}

# Signal handler
cleanup() {
    MONITORING=false
    echo ""
    echo "🛑 Status monitoring stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Get single service status
get_status() {
    local service="${1:-}"
    
    if [ -z "$service" ]; then
        # Get all services
        init_status
        for service in "${!SERVICE_STATUS[@]}"; do
            update_service_status "$service"
            local status="${SERVICE_STATUS[$service]}"
            local health="${SERVICE_HEALTH[$service]}"
            echo "$service: $status ($health)"
        done
    else
        # Get single service
        update_service_status "$service"
        local status="${SERVICE_STATUS[$service]}"
        local health="${SERVICE_HEALTH[$service]}"
        echo "$service: $status ($health)"
    fi
}

# Main function
main() {
    local command="${1:-monitor}"
    
    case "$command" in
        monitor)
            init_status
            monitor_loop
            ;;
        status)
            get_status "${2:-}"
            ;;
        *)
            echo "Usage: $0 {monitor|status} [service]"
            exit 1
            ;;
    esac
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi

