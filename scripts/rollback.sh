#!/bin/bash

# Rollback Script
# Automated rollback to previous deployment version
#
# Usage:
#   ./scripts/rollback.sh [--version=<version>] [--confirm]
#
# Options:
#   --version       Specify version to rollback to (default: latest backup)
#   --confirm       Skip confirmation prompt

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
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
PROD_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.prod.yml"

# Flags
VERSION_TAG=""
SKIP_CONFIRM=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --version=*)
      VERSION_TAG="${1#*=}"
      shift
      ;;
    --confirm)
      SKIP_CONFIRM=true
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
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

confirm_rollback() {
  if [ "$SKIP_CONFIRM" = true ]; then
    return
  fi
  
  echo ""
  echo -e "${YELLOW}⚠️  WARNING: This will rollback the current deployment${NC}"
  echo ""
  
  if [ -n "$VERSION_TAG" ]; then
    echo "Rolling back to version: $VERSION_TAG"
  else
    echo "Rolling back to latest backup"
  fi
  
  echo ""
  read -p "Are you sure you want to continue? (yes/no): " confirm
  
  if [ "$confirm" != "yes" ]; then
    log_info "Rollback cancelled"
    exit 0
  fi
}

list_available_versions() {
  log_info "Available backup versions:"
  docker images | grep "client-app:backup-" | awk '{print $1":"$2}' | sort -r | head -10
}

find_rollback_version() {
  if [ -n "$VERSION_TAG" ]; then
    if docker images | grep -q "client-app:$VERSION_TAG"; then
      echo "$VERSION_TAG"
      return
    else
      log_error "Version $VERSION_TAG not found"
      list_available_versions
      exit 1
    fi
  fi
  
  # Find latest backup
  local latest_backup=$(docker images | grep "client-app:backup-" | head -1 | awk '{print $1":"$2}')
  
  if [ -z "$latest_backup" ]; then
    log_error "No backup versions found"
    exit 1
  fi
  
  echo "$latest_backup" | sed 's/client-app://'
}

perform_rollback() {
  local rollback_version=$(find_rollback_version)
  
  log_info "Rolling back to version: $rollback_version"
  
  # Tag current version as rollback-failed for debugging
  if docker ps | grep -q "digital_utopia_client"; then
    log_info "Tagging current version for debugging..."
    docker tag client-app:latest "client-app:rollback-failed-$(date +%Y%m%d-%H%M%S)" 2>/dev/null || true
  fi
  
  # Stop current containers
  log_info "Stopping current containers..."
  docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" down client-app 2>/dev/null || true
  
  # Tag rollback version as latest
  log_info "Tagging rollback version as latest..."
  docker tag "client-app:$rollback_version" client-app:latest || {
    log_error "Failed to tag rollback version"
    exit 1
  }
  
  # Start containers with rollback version
  log_info "Starting containers with rollback version..."
  docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" up -d client-app || {
    log_error "Failed to start containers"
    exit 1
  }
  
  log_success "Rollback completed"
}

verify_rollback() {
  log_info "Verifying rollback..."
  
  # Wait for container to be ready
  sleep 10
  
  # Check container status
  if docker ps | grep -q "digital_utopia_client"; then
    log_success "Container is running"
  else
    log_error "Container is not running after rollback"
    exit 1
  fi
  
  # Check health endpoint
  local health_url="http://localhost:3002/health"
  if curl -f -s "$health_url" > /dev/null; then
    log_success "Health check passed"
  else
    log_warning "Health check failed, but container is running"
  fi
  
  log_success "Rollback verification completed"
}

main() {
  echo "=========================================="
  echo "  Rollback Script"
  echo "=========================================="
  echo ""
  
  confirm_rollback
  list_available_versions
  perform_rollback
  verify_rollback
  
  echo ""
  echo "=========================================="
  log_success "Rollback completed successfully!"
  echo "=========================================="
  echo ""
  echo "Monitor deployment: docker logs -f digital_utopia_client"
  echo "Health check: curl http://localhost:3002/health"
}

# Run main function
main "$@"

