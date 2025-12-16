#!/bin/bash
# Investigate Service Stoppage Script
# Reviews logs and analyzes why services stopped

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

# Check container status
check_container_status() {
    log_info "Checking container status..."
    
    containers=("digital_utopia_postgres" "digital_utopia_redis" "digital_utopia_backend" 
                "digital_utopia_client" "digital_utopia_admin" "digital_utopia_nginx_proxy")
    
    for container in "${containers[@]}"; do
        status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "not found")
        restart_count=$(docker inspect --format='{{.RestartCount}}' "$container" 2>/dev/null || echo "0")
        
        if [ "$status" = "running" ]; then
            log_success "$container: Running (restarts: $restart_count)"
        else
            log_error "$container: $status (restarts: $restart_count)"
        fi
    done
}

# Check restart policies
check_restart_policies() {
    log_info "Checking restart policies..."
    
    containers=("digital_utopia_postgres" "digital_utopia_redis" "digital_utopia_backend" 
                "digital_utopia_client" "digital_utopia_admin" "digital_utopia_nginx_proxy")
    
    for container in "${containers[@]}"; do
        restart_policy=$(docker inspect --format='{{.HostConfig.RestartPolicy.Name}}' "$container" 2>/dev/null || echo "unknown")
        log_info "$container: restart policy = $restart_policy"
    done
}

# Analyze container logs for errors
analyze_logs() {
    log_info "Analyzing container logs for errors..."
    
    containers=("digital_utopia_backend" "digital_utopia_postgres" "digital_utopia_redis")
    
    for container in "${containers[@]}"; do
        if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
            log_info "Analyzing logs for $container..."
            
            # Check for OOM (Out of Memory) errors
            oom_count=$(docker logs "$container" 2>&1 | grep -i "out of memory\|oom\|killed" | wc -l)
            if [ "$oom_count" -gt 0 ]; then
                log_error "Found $oom_count OOM-related errors in $container logs"
            fi
            
            # Check for connection errors
            conn_errors=$(docker logs "$container" 2>&1 | grep -i "connection\|timeout\|refused" | wc -l)
            if [ "$conn_errors" -gt 0 ]; then
                log_warn "Found $conn_errors connection-related errors in $container logs"
            fi
            
            # Check for critical errors
            critical_errors=$(docker logs "$container" 2>&1 | grep -i "fatal\|critical\|panic" | wc -l)
            if [ "$critical_errors" -gt 0 ]; then
                log_error "Found $critical_errors critical errors in $container logs"
            fi
        fi
    done
}

# Check system resources
check_system_resources() {
    log_info "Checking system resources..."
    
    # Memory
    mem_info=$(free -h | grep Mem)
    mem_total=$(echo $mem_info | awk '{print $2}')
    mem_used=$(echo $mem_info | awk '{print $3}')
    mem_percent=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    
    log_info "Memory: $mem_used / $mem_total ($mem_percent%)"
    
    if (( $(echo "$mem_percent > 90" | bc -l) )); then
        log_error "Memory usage is above 90% - may cause OOM kills"
    fi
    
    # Disk
    disk_usage=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
    log_info "Disk usage: ${disk_usage}%"
    
    if [ "$disk_usage" -gt 85 ]; then
        log_warn "Disk usage is above 85%"
    fi
    
    # CPU Load
    load=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
    log_info "CPU Load (1min): $load"
    
    if (( $(echo "$load > 4.0" | bc -l) )); then
        log_warn "CPU load is high: $load"
    fi
}

# Check Docker events
check_docker_events() {
    log_info "Checking recent Docker events..."
    
    # Get events from last hour
    docker events --since 1h --until now --format "{{.Time}} {{.Status}} {{.Actor.Attributes.name}}" 2>/dev/null | \
        grep -E "die|stop|kill|oom" | tail -20 || log_info "No relevant events found"
}

# Generate report
generate_report() {
    log_info "Generating investigation report..."
    
    report_file="/tmp/service-stoppage-report-$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "Service Stoppage Investigation Report"
        echo "Generated: $(date)"
        echo "=========================================="
        echo ""
        echo "Container Status:"
        check_container_status
        echo ""
        echo "Restart Policies:"
        check_restart_policies
        echo ""
        echo "System Resources:"
        check_system_resources
        echo ""
        echo "Log Analysis:"
        analyze_logs
    } > "$report_file"
    
    log_success "Report saved to: $report_file"
    cat "$report_file"
}

# Main execution
main() {
    echo "=========================================="
    echo "Service Stoppage Investigation"
    echo "Date: $(date)"
    echo "=========================================="
    echo ""
    
    check_container_status
    echo ""
    check_restart_policies
    echo ""
    check_system_resources
    echo ""
    analyze_logs
    echo ""
    check_docker_events
    echo ""
    generate_report
}

main
