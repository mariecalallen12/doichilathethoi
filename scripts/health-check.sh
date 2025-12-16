#!/bin/bash

# Health Check Script
# Comprehensive health check for all services
#
# Usage:
#   ./scripts/health-check.sh [--service=<service>] [--verbose]
#
# Options:
#   --service       Check specific service (client-app, backend, postgres, redis)
#   --verbose       Show detailed information

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Flags
SERVICE=""
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --service=*)
      SERVICE="${1#*=}"
      shift
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

# Functions
log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
  echo -e "${RED}[✗]${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}[!]${NC} $1"
}

check_docker() {
  if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed"
    return 1
  fi
  return 0
}

check_container_health() {
  local container_name=$1
  local health_url=$2
  
  if docker ps | grep -q "$container_name"; then
    log_success "$container_name container is running"
    
    if [ -n "$health_url" ]; then
      if curl -f -s "$health_url" > /dev/null 2>&1; then
        log_success "$container_name health endpoint is accessible"
        
        if [ "$VERBOSE" = true ]; then
          local response=$(curl -s "$health_url")
          echo "  Response: $response"
        fi
      else
        log_error "$container_name health endpoint is not accessible"
        return 1
      fi
    fi
    
    # Check container health status
    local health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "none")
    if [ "$health_status" != "none" ]; then
      if [ "$health_status" = "healthy" ]; then
        log_success "$container_name health status: $health_status"
      else
        log_warning "$container_name health status: $health_status"
      fi
    fi
    
    return 0
  else
    log_error "$container_name container is not running"
    return 1
  fi
}

check_client_app() {
  log_info "Checking Client App..."
  
  check_container_health "digital_utopia_client" "http://localhost:3002/health"
  
  # Check API connectivity
  if [ "$VERBOSE" = true ]; then
    log_info "Checking API connectivity..."
    # This would check if the app can connect to backend API
  fi
}

check_backend() {
  log_info "Checking Backend API..."
  
  check_container_health "digital_utopia_backend" "http://localhost:8000/api/health"
  
  if [ "$VERBOSE" = true ]; then
    local response=$(curl -s http://localhost:8000/api/health)
    echo "  Backend health: $response"
  fi
}

check_database() {
  log_info "Checking Database..."
  
  if docker ps | grep -q "digital_utopia_postgres"; then
    log_success "PostgreSQL container is running"
    
    # Check database connectivity
    if docker exec digital_utopia_postgres pg_isready -U postgres > /dev/null 2>&1; then
      log_success "PostgreSQL is ready to accept connections"
    else
      log_error "PostgreSQL is not ready"
      return 1
    fi
  else
    log_error "PostgreSQL container is not running"
    return 1
  fi
}

check_redis() {
  log_info "Checking Redis..."
  
  if docker ps | grep -q "digital_utopia_redis"; then
    log_success "Redis container is running"
    
    # Check Redis connectivity
    if docker exec digital_utopia_redis redis-cli ping > /dev/null 2>&1; then
      log_success "Redis is responding to ping"
    else
      log_error "Redis is not responding"
      return 1
    fi
  else
    log_error "Redis container is not running"
    return 1
  fi
}

check_network() {
  log_info "Checking Docker network..."
  
  if docker network ls | grep -q "digital_utopia_network"; then
    log_success "Docker network exists"
  else
    log_error "Docker network not found"
    return 1
  fi
}

check_all_services() {
  local exit_code=0
  
  check_network || exit_code=1
  check_database || exit_code=1
  check_redis || exit_code=1
  check_backend || exit_code=1
  check_client_app || exit_code=1
  
  return $exit_code
}

main() {
  echo "=========================================="
  echo "  Health Check Script"
  echo "=========================================="
  echo ""
  
  if ! check_docker; then
    exit 1
  fi
  
  case "$SERVICE" in
    client-app)
      check_client_app
      ;;
    backend)
      check_backend
      ;;
    postgres)
      check_database
      ;;
    redis)
      check_redis
      ;;
    "")
      check_all_services
      ;;
    *)
      log_error "Unknown service: $SERVICE"
      exit 1
      ;;
  esac
  
  local result=$?
  
  echo ""
  echo "=========================================="
  if [ $result -eq 0 ]; then
    log_success "All health checks passed!"
  else
    log_error "Some health checks failed"
  fi
  echo "=========================================="
  
  exit $result
}

# Run main function
main "$@"
