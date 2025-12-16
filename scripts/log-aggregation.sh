#!/bin/bash
# Log Aggregation Script
# Collects and aggregates logs from all services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="/var/log/cmeetrading"
AGGREGATED_LOG="$LOG_DIR/aggregated.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

log_message() {
    echo "[$TIMESTAMP] $1" | tee -a "$AGGREGATED_LOG"
}

# Collect logs from all containers
collect_container_logs() {
    log_message "Collecting container logs..."
    
    containers=("digital_utopia_backend" "digital_utopia_client" "digital_utopia_admin" 
                "digital_utopia_postgres" "digital_utopia_redis" "digital_utopia_nginx_proxy")
    
    for container in "${containers[@]}"; do
        if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
            log_message "Collecting logs from $container"
            docker logs --tail 100 "$container" 2>&1 | while IFS= read -r line; do
                echo "[$TIMESTAMP] [$container] $line" >> "$AGGREGATED_LOG"
            done
        fi
    done
}

# Collect system logs
collect_system_logs() {
    log_message "Collecting system logs..."
    
    # System messages
    if [ -f /var/log/syslog ]; then
        tail -50 /var/log/syslog | while IFS= read -r line; do
            echo "[$TIMESTAMP] [SYSTEM] $line" >> "$AGGREGATED_LOG"
        done
    fi
    
    # Application-specific logs
    if [ -f /var/log/cmeetrading_health.log ]; then
        tail -50 /var/log/cmeetrading_health.log | while IFS= read -r line; do
            echo "[$TIMESTAMP] [HEALTH] $line" >> "$AGGREGATED_LOG"
        done
    fi
}

# Analyze logs for errors
analyze_errors() {
    log_message "Analyzing logs for errors..."
    
    error_count=$(grep -i "error\|exception\|failed\|critical" "$AGGREGATED_LOG" | wc -l)
    if [ "$error_count" -gt 0 ]; then
        log_message "⚠️  Found $error_count error entries in logs"
        echo "Recent errors:" >> "$AGGREGATED_LOG"
        grep -i "error\|exception\|failed\|critical" "$AGGREGATED_LOG" | tail -10 >> "$AGGREGATED_LOG"
    else
        log_message "✓ No errors found in logs"
    fi
}

# Rotate logs if too large (keep last 100MB)
rotate_logs() {
    if [ -f "$AGGREGATED_LOG" ]; then
        size=$(stat -f%z "$AGGREGATED_LOG" 2>/dev/null || stat -c%s "$AGGREGATED_LOG" 2>/dev/null || echo 0)
        max_size=$((100 * 1024 * 1024))  # 100MB
        
        if [ "$size" -gt "$max_size" ]; then
            log_message "Rotating log file (size: $size bytes)"
            mv "$AGGREGATED_LOG" "${AGGREGATED_LOG}.$(date +%Y%m%d_%H%M%S)"
            touch "$AGGREGATED_LOG"
        fi
    fi
}

# Main execution
main() {
    log_message "=== Starting Log Aggregation ==="
    
    rotate_logs
    collect_container_logs
    collect_system_logs
    analyze_errors
    
    log_message "=== Log Aggregation Complete ==="
    log_message "Aggregated log saved to: $AGGREGATED_LOG"
}

main
