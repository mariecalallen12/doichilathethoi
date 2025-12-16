#!/bin/bash
# Backend Health Monitoring Script
# Usage: ./scripts/monitor-backend.sh

set -e

BACKEND_URL="${BACKEND_URL:-https://cmeetrading.com}"
HEALTH_ENDPOINT="${BACKEND_URL}/api/health"
ALERT_EMAIL="${ALERT_EMAIL:-}"
LOG_FILE="${LOG_FILE:-/var/log/backend-monitor.log}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check backend health
check_backend_health() {
    local response
    local status_code
    local status
    
    response=$(curl -s -w "\n%{http_code}" "$HEALTH_ENDPOINT" 2>&1) || {
        log "ERROR: Failed to connect to backend"
        return 1
    }
    
    status_code=$(echo "$response" | tail -n1)
    status=$(echo "$response" | head -n-1)
    
    if [ "$status_code" = "200" ]; then
        # Parse JSON response
        db_status=$(echo "$status" | grep -o '"database":"[^"]*"' | cut -d'"' -f4)
        redis_status=$(echo "$status" | grep -o '"redis":"[^"]*"' | cut -d'"' -f4)
        
        if [ "$db_status" = "connected" ]; then
            log "✅ Backend is healthy - Database: $db_status, Redis: $redis_status"
            return 0
        else
            log "⚠️  Backend responded but database is not connected"
            return 1
        fi
    else
        log "❌ Backend health check failed - HTTP $status_code"
        return 1
    fi
}

# Function to send alert (if email is configured)
send_alert() {
    local message="$1"
    if [ -n "$ALERT_EMAIL" ]; then
        echo "$message" | mail -s "Backend Health Alert" "$ALERT_EMAIL" 2>/dev/null || true
    fi
    log "ALERT: $message"
}

# Main monitoring loop
main() {
    log "Starting backend health monitoring..."
    log "Monitoring endpoint: $HEALTH_ENDPOINT"
    
    while true; do
        if ! check_backend_health; then
            send_alert "Backend health check failed at $(date)"
        fi
        
        # Wait 30 seconds before next check
        sleep 30
    done
}

# Run once if --once flag is provided
if [ "$1" = "--once" ]; then
    check_backend_health
    exit $?
fi

# Run continuously
main

