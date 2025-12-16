#!/bin/bash
# Log Parser Library
# Digital Utopia Platform - Real-time Log Parsing

# Parse Docker build logs
parse_build_log() {
    local log_line="$1"
    local service="$2"
    
    # Extract error patterns
    if [[ "$log_line" =~ ERROR|error|Error ]]; then
        echo "ERROR:$service:$log_line"
    elif [[ "$log_line" =~ WARNING|warning|Warning ]]; then
        echo "WARNING:$service:$log_line"
    elif [[ "$log_line" =~ "failed"|"FAILED" ]]; then
        echo "FAILED:$service:$log_line"
    fi
}

# Parse Docker compose logs
parse_compose_log() {
    local log_line="$1"
    
    # Extract service name and message
    if [[ "$log_line" =~ ^([a-zA-Z0-9_-]+)\s+\|\s+(.+)$ ]]; then
        local service="${BASH_REMATCH[1]}"
        local message="${BASH_REMATCH[2]}"
        
        # Check for errors
        if [[ "$message" =~ ERROR|error|Error|failed|FAILED|exception|Exception ]]; then
            echo "ERROR:$service:$message"
        elif [[ "$message" =~ WARNING|warning|Warning ]]; then
            echo "WARNING:$service:$message"
        fi
    fi
}

# Extract error details from log
extract_error_details() {
    local log_line="$1"
    local error_type=""
    local error_message=""
    
    # Extract error type
    if [[ "$log_line" =~ "connection"|"timeout"|"refused" ]]; then
        error_type="NETWORK"
    elif [[ "$log_line" =~ "permission"|"denied"|"access" ]]; then
        error_type="PERMISSION"
    elif [[ "$log_line" =~ "disk"|"space"|"memory" ]]; then
        error_type="RESOURCE"
    elif [[ "$log_line" =~ "database"|"postgres"|"migration" ]]; then
        error_type="DATABASE"
    elif [[ "$log_line" =~ "config"|"environment"|".env" ]]; then
        error_type="CONFIG"
    else
        error_type="UNKNOWN"
    fi
    
    # Extract error message (last part after colon)
    if [[ "$log_line" =~ :(.+)$ ]]; then
        error_message="${BASH_REMATCH[1]}"
    else
        error_message="$log_line"
    fi
    
    echo "$error_type|$error_message"
}

# Monitor logs in real-time
monitor_logs() {
    local service="$1"
    local log_file="$2"
    local callback="$3"
    
    if [ -z "$log_file" ]; then
        # Monitor docker-compose logs
        docker-compose logs -f "$service" 2>&1 | while IFS= read -r line; do
            if [ -n "$callback" ]; then
                $callback "$line" "$service"
            else
                echo "$line"
            fi
        done
    else
        # Monitor file logs
        tail -f "$log_file" 2>/dev/null | while IFS= read -r line; do
            if [ -n "$callback" ]; then
                $callback "$line" "$service"
            else
                echo "$line"
            fi
        done
    fi
}

# Filter logs by pattern
filter_logs() {
    local pattern="$1"
    local log_source="$2"
    
    if [ -z "$log_source" ]; then
        docker-compose logs --tail=1000 2>&1 | grep -i "$pattern"
    else
        grep -i "$pattern" "$log_source" 2>/dev/null
    fi
}

# Get recent errors
get_recent_errors() {
    local service="$1"
    local lines="${2:-50}"
    
    if [ -n "$service" ]; then
        docker-compose logs --tail="$lines" "$service" 2>&1 | grep -iE "error|failed|exception|fatal" || true
    else
        docker-compose logs --tail="$lines" 2>&1 | grep -iE "error|failed|exception|fatal" || true
    fi
}

# Count errors in logs
count_errors() {
    local service="$1"
    local log_source="$2"
    
    if [ -n "$log_source" ]; then
        grep -icE "error|failed|exception|fatal" "$log_source" 2>/dev/null || echo "0"
    elif [ -n "$service" ]; then
        docker-compose logs "$service" 2>&1 | grep -icE "error|failed|exception|fatal" || echo "0"
    else
        docker-compose logs 2>&1 | grep -icE "error|failed|exception|fatal" || echo "0"
    fi
}

# Extract build progress
extract_build_progress() {
    local log_line="$1"
    
    # Docker build progress: Step X/Y
    if [[ "$log_line" =~ Step\ ([0-9]+)/([0-9]+) ]]; then
        local current="${BASH_REMATCH[1]}"
        local total="${BASH_REMATCH[2]}"
        local percent=$((current * 100 / total))
        echo "$percent|$current/$total"
    fi
}

# Check if service is healthy from logs
check_service_health_from_logs() {
    local service="$1"
    local timeout="${2:-30}"
    
    local start_time=$(date +%s)
    while [ $(($(date +%s) - start_time)) -lt "$timeout" ]; do
        local logs=$(docker-compose logs --tail=20 "$service" 2>&1)
        
        # Check for success indicators
        if echo "$logs" | grep -qiE "ready|started|listening|running|healthy"; then
            return 0
        fi
        
        # Check for fatal errors
        if echo "$logs" | grep -qiE "fatal|cannot start|failed to start|exited"; then
            return 1
        fi
        
        sleep 2
    done
    
    return 1
}

