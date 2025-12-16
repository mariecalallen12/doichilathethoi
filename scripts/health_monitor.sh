#!/bin/bash
# Health monitoring script for CMEETRADING

LOG_FILE="/var/log/cmeetrading_health.log"

log_message() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_backend() {
  if curl -f -s http://localhost:8000/api/health > /dev/null 2>&1; then
    log_message "✅ Backend health check: OK"
    return 0
  else
    log_message "❌ Backend health check: FAILED"
    return 1
  fi
}

check_database() {
  if docker exec digital_utopia_postgres pg_isready -U postgres > /dev/null 2>&1; then
    log_message "✅ Database health check: OK"
    return 0
  else
    log_message "❌ Database health check: FAILED"
    return 1
  fi
}

check_redis() {
  if docker exec digital_utopia_redis redis-cli ping > /dev/null 2>&1; then
    log_message "✅ Redis health check: OK"
    return 0
  else
    log_message "❌ Redis health check: FAILED"
    return 1
  fi
}

# Main monitoring loop
while true; do
  check_backend
  check_database
  check_redis
  sleep 60
done
