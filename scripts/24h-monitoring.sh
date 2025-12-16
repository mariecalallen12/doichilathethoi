#!/bin/bash
# 24-Hour Post-Deployment Monitoring Script
# Runs every 5 minutes to monitor system health

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="/var/log/cmeetrading_24h_monitoring.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_message() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

log_section() {
    echo "" | tee -a "$LOG_FILE"
    echo "=== $1 ===" | tee -a "$LOG_FILE"
}

# Check container status
check_containers() {
    log_section "Container Status"
    cd "$PROJECT_ROOT"
    
    containers=("digital_utopia_postgres" "digital_utopia_redis" "digital_utopia_backend" 
                "digital_utopia_client" "digital_utopia_admin" "digital_utopia_nginx_proxy")
    
    for container in "${containers[@]}"; do
        if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
            status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "unknown")
            health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "none")
            
            if [ "$status" = "running" ]; then
                if [ "$health" = "healthy" ] || [ "$health" = "none" ]; then
                    log_message "✓ $container: Running ($health)"
                else
                    log_message "⚠ $container: Running but unhealthy ($health)"
                fi
            else
                log_message "✗ $container: Not running (status: $status)"
            fi
        else
            log_message "✗ $container: Container not found"
        fi
    done
}

# Check backend health
check_backend_health() {
    log_section "Backend Health"
    if curl -f -s http://localhost:8000/api/health > /tmp/backend_health.json 2>&1; then
        log_message "✓ Backend health endpoint: Accessible"
        if command -v python3 &> /dev/null; then
            status=$(python3 -c "import json; f=open('/tmp/backend_health.json'); d=json.load(f); print(d.get('status', 'unknown'))" 2>/dev/null || echo "unknown")
            log_message "  Status: $status"
        fi
        rm -f /tmp/backend_health.json
    else
        log_message "✗ Backend health endpoint: Not accessible"
    fi
}

# Check database connectivity
check_database() {
    log_section "Database Connectivity"
    if docker exec digital_utopia_postgres pg_isready -U postgres &> /dev/null; then
        log_message "✓ PostgreSQL: Connected"
    else
        log_message "✗ PostgreSQL: Connection failed"
    fi
}

# Check Redis connectivity
check_redis() {
    log_section "Redis Connectivity"
    if docker exec digital_utopia_redis redis-cli ping &> /dev/null; then
        log_message "✓ Redis: Connected"
    else
        log_message "✗ Redis: Connection failed"
    fi
}

# Check HTTP endpoints
check_endpoints() {
    log_section "HTTP Endpoints"
    
    endpoints=(
        "http://localhost:8000/api/health:Backend Health"
        "http://localhost:3002/health:Client App"
        "http://localhost:3001/health:Admin App"
    )
    
    for endpoint_info in "${endpoints[@]}"; do
        IFS=':' read -r url name <<< "$endpoint_info"
        if curl -f -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|301\|302"; then
            log_message "✓ $name: Accessible"
        else
            log_message "✗ $name: Not accessible"
        fi
    done
}

# Check system resources
check_resources() {
    log_section "System Resources"
    
    # CPU Load
    load=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
    log_message "CPU Load (1min): $load"
    
    # Memory Usage
    mem_info=$(free -h | grep Mem)
    mem_total=$(echo $mem_info | awk '{print $2}')
    mem_used=$(echo $mem_info | awk '{print $3}')
    mem_percent=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    log_message "Memory: $mem_used / $mem_total ($mem_percent%)"
    
    # Disk Usage
    disk_usage=$(df -h / | tail -1 | awk '{print $5}')
    log_message "Disk Usage: $disk_usage"
}

# Check error rates
check_errors() {
    log_section "Error Monitoring"
    
    # Check backend logs for errors in last 5 minutes
    error_count=$(docker logs --since 5m digital_utopia_backend 2>&1 | grep -i "error\|exception\|failed" | wc -l)
    if [ "$error_count" -gt 0 ]; then
        log_message "⚠ Found $error_count errors in backend logs (last 5 minutes)"
    else
        log_message "✓ No errors in backend logs (last 5 minutes)"
    fi
}

# Main execution
main() {
    log_section "24-Hour Monitoring Check"
    log_message "Starting monitoring check at $TIMESTAMP"
    
    check_containers
    check_backend_health
    check_database
    check_redis
    check_endpoints
    check_resources
    check_errors
    
    log_message "Monitoring check completed"
    log_section "End of Check"
}

main
