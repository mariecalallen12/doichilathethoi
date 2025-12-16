#!/bin/bash
set -e

echo "📊 Production Monitoring"
echo "======================="
echo ""

# Configuration
ALERT_EMAIL="${ALERT_EMAIL:-admin@cmeetrading.com}"
LOG_FILE="${LOG_FILE:-/var/log/production-monitor.log}"
ALERT_THRESHOLD_CPU=80
ALERT_THRESHOLD_MEM=85
ALERT_THRESHOLD_DISK=90

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check service health
check_service_health() {
    local service=$1
    local url=$2
    
    if curl -s -f --max-time 5 "$url" >/dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
        return 0
    else
        echo -e "${RED}❌${NC}"
        log "ALERT: $service is down!"
        return 1
    fi
}

# Function to get container stats
get_container_stats() {
    local container=$1
    docker stats --no-stream --format "{{.CPUPerc}} {{.MemUsage}} {{.MemPerc}}" "$container" 2>/dev/null || echo "0 0/0 0%"
}

# Check services
echo "🌐 Service Health:"
echo "-----------------"
echo -n "Backend API:    "
check_service_health "Backend" "http://localhost:8000/api/health"

echo -n "Client App:     "
check_service_health "Client" "http://localhost:3002/health"

echo -n "Admin App:      "
check_service_health "Admin" "http://localhost:3001/health"
echo ""

# Container resource usage
echo "📦 Container Resources:"
echo "---------------------"
containers=("digital_utopia_backend" "digital_utopia_client" "digital_utopia_admin" "digital_utopia_postgres" "digital_utopia_redis")

for container in "${containers[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        stats=($(get_container_stats "$container"))
        cpu=${stats[0]%\%}
        mem_usage=${stats[1]}
        mem_perc=${stats[2]%\%}
        
        cpu_int=${cpu%.*}
        mem_int=${mem_perc%.*}
        
        cpu_status="${GREEN}✅${NC}"
        mem_status="${GREEN}✅${NC}"
        
        if [ "$cpu_int" -gt "$ALERT_THRESHOLD_CPU" ]; then
            cpu_status="${RED}⚠️${NC}"
            log "ALERT: $container CPU usage is ${cpu}% (threshold: ${ALERT_THRESHOLD_CPU}%)"
        fi
        
        if [ "$mem_int" -gt "$ALERT_THRESHOLD_MEM" ]; then
            mem_status="${RED}⚠️${NC}"
            log "ALERT: $container Memory usage is ${mem_perc}% (threshold: ${ALERT_THRESHOLD_MEM}%)"
        fi
        
        printf "%-25s CPU: %-6s %s  MEM: %-6s %s\n" "$container" "$cpu" "$cpu_status" "$mem_perc" "$mem_status"
    fi
done
echo ""

# Disk usage
echo "💾 Disk Usage:"
echo "-------------"
disk_usage=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$disk_usage" -gt "$ALERT_THRESHOLD_DISK" ]; then
    echo -e "${RED}⚠️  Disk usage: ${disk_usage}% (threshold: ${ALERT_THRESHOLD_DISK}%)${NC}"
    log "ALERT: Disk usage is ${disk_usage}% (threshold: ${ALERT_THRESHOLD_DISK}%)"
else
    echo -e "${GREEN}✅ Disk usage: ${disk_usage}%${NC}"
fi
echo ""

# Database connections
echo "🗄️  Database:"
echo "------------"
if docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "SELECT count(*) FROM pg_stat_activity;" >/dev/null 2>&1; then
    conn_count=$(docker exec digital_utopia_postgres psql -U postgres -t -d digital_utopia -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null | tr -d ' ')
    echo -e "${GREEN}✅ Active connections: $conn_count${NC}"
else
    echo -e "${RED}❌ Cannot check database connections${NC}"
fi
echo ""

# Recent errors in logs
echo "📋 Recent Errors (last 5 minutes):"
echo "----------------------------------"
error_count=$(docker logs --since 5m digital_utopia_backend 2>&1 | grep -i "error\|exception\|failed" | wc -l)
if [ "$error_count" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Found $error_count error(s) in backend logs${NC}"
    docker logs --since 5m digital_utopia_backend 2>&1 | grep -i "error\|exception\|failed" | tail -5
else
    echo -e "${GREEN}✅ No recent errors${NC}"
fi
echo ""

log "Monitoring check completed"

