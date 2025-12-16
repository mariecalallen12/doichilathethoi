#!/bin/bash
# Real-time Log Monitor
# Digital Utopia Platform - Monitor logs with error detection

set -e

# Source libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/log-parser.sh"
source "$SCRIPT_DIR/lib/error-handler.sh"

# Configuration
MONITOR_INTERVAL=1
MONITOR_TIMEOUT=3600
ERROR_THRESHOLD=10

# Global variables
MONITORING_ACTIVE=true
ERROR_COUNT=0
LAST_ERROR_TIME=0

# Signal handler
cleanup() {
    MONITORING_ACTIVE=false
    echo ""
    echo "🛑 Log monitoring stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Monitor service logs
monitor_service() {
    local service="$1"
    local log_callback="${2:-}"
    
    echo "📊 Monitoring logs for service: $service"
    
    # Start monitoring in background
    (
        docker-compose logs -f "$service" 2>&1 | while IFS= read -r line; do
            if [ "$MONITORING_ACTIVE" = false ]; then
                break
            fi
            
            # Parse log line
            local parsed=$(parse_compose_log "$line")
            
            if [ -n "$parsed" ]; then
                # Extract error details
                local error_type=$(echo "$parsed" | cut -d: -f1)
                local service_name=$(echo "$parsed" | cut -d: -f2)
                local message=$(echo "$parsed" | cut -d: -f3-)
                
                # Log error
                local err_type_code=$(get_error_type "$message")
                local severity=$(get_error_severity "$message" "$err_type_code")
                log_error "$err_type_code" "$severity" "$message" "$service_name"
                
                ERROR_COUNT=$((ERROR_COUNT + 1))
                LAST_ERROR_TIME=$(date +%s)
                
                # Call callback if provided
                if [ -n "$log_callback" ]; then
                    $log_callback "$error_type" "$service_name" "$message"
                fi
                
                # Display error
                echo "⚠️  [$error_type] $service_name: $message"
            else
                # Display normal log
                echo "$line"
            fi
        done
    ) &
    
    local monitor_pid=$!
    echo "$monitor_pid" > "/tmp/monitor_${service}.pid"
    
    return 0
}

# Monitor all services
monitor_all_services() {
    local services=("postgres" "redis" "backend" "client-app" "admin-app")
    local callback="${1:-}"
    
    echo "📊 Starting log monitoring for all services..."
    echo ""
    
    # Start monitoring for each service
    for service in "${services[@]}"; do
        if docker-compose ps "$service" | grep -q "Up"; then
            monitor_service "$service" "$callback" &
        fi
    done
    
    # Wait for monitoring
    wait
}

# Monitor build logs
monitor_build_logs() {
    local service="$1"
    local build_output="/tmp/build_${service}.log"
    
    echo "📦 Monitoring build logs for: $service"
    
    # Start build and capture output
    docker-compose build "$service" 2>&1 | tee "$build_output" | while IFS= read -r line; do
        # Parse build log
        local parsed=$(parse_build_log "$line" "$service")
        
        if [ -n "$parsed" ]; then
            local error_type=$(echo "$parsed" | cut -d: -f1)
            local message=$(echo "$parsed" | cut -d: -f3-)
            
            echo "⚠️  [$error_type] $message"
            
            # Log error
            local err_type_code=$(get_error_type "$message")
            local severity=$(get_error_severity "$message" "$err_type_code")
            log_error "$err_type_code" "$severity" "$message" "$service"
        else
            # Extract progress if available
            local progress=$(extract_build_progress "$line")
            if [ -n "$progress" ]; then
                local percent=$(echo "$progress" | cut -d'|' -f1)
                local step=$(echo "$progress" | cut -d'|' -f2)
                echo "📊 Build progress: $step ($percent%)"
            else
                echo "$line"
            fi
        fi
    done
    
    return ${PIPESTATUS[0]}
}

# Get error summary
get_monitor_summary() {
    echo ""
    echo "📊 Monitoring Summary"
    echo "===================="
    echo "Total errors detected: $ERROR_COUNT"
    
    if [ -f "$ERROR_LOG_FILE" ] && [ -s "$ERROR_LOG_FILE" ]; then
        echo ""
        echo "Recent errors:"
        tail -5 "$ERROR_LOG_FILE" | sed 's/^/  /'
    fi
}

# Stop monitoring
stop_monitoring() {
    MONITORING_ACTIVE=false
    
    # Kill all monitor processes
    for pid_file in /tmp/monitor_*.pid; do
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            kill "$pid" 2>/dev/null || true
            rm -f "$pid_file"
        fi
    done
    
    echo "🛑 Monitoring stopped"
}

# Main function
main() {
    local service="${1:-}"
    local mode="${2:-deploy}"
    
    # Initialize error log
    init_error_log
    
    if [ -z "$service" ]; then
        # Monitor all services
        monitor_all_services
    elif [ "$mode" = "build" ]; then
        # Monitor build
        monitor_build_logs "$service"
    else
        # Monitor single service
        monitor_service "$service"
    fi
    
    # Wait for interrupt
    wait
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi

