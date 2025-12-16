#!/bin/bash

# Cache Invalidation Script
# Invalidate Redis cache
#
# Usage:
#   ./scripts/cache-invalidation.sh [--pattern=<pattern>] [--all] [--confirm]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PATTERN=""
INVALIDATE_ALL=false
SKIP_CONFIRM=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --pattern=*)
      PATTERN="${1#*=}"
      shift
      ;;
    --all)
      INVALIDATE_ALL=true
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

log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

confirm_invalidation() {
  if [ "$SKIP_CONFIRM" = true ]; then
    return
  fi
  
  echo ""
  log_warning "⚠️  WARNING: This will invalidate cache"
  echo ""
  read -p "Are you sure you want to continue? (yes/no): " confirm
  
  if [ "$confirm" != "yes" ]; then
    log_info "Invalidation cancelled"
    exit 0
  fi
}

invalidate_all() {
  log_info "Invalidating all cache..."
  
  docker exec digital_utopia_redis redis-cli FLUSHDB > /dev/null 2>&1 || {
    log_error "Cache invalidation failed"
    exit 1
  }
  
  log_success "All cache invalidated"
}

invalidate_pattern() {
  log_info "Invalidating cache with pattern: $PATTERN"
  
  # Get keys matching pattern
  local keys=$(docker exec digital_utopia_redis redis-cli KEYS "$PATTERN" 2>/dev/null | tr -d '\r' || echo "")
  
  if [ -n "$keys" ]; then
    echo "$keys" | while read key; do
      if [ -n "$key" ]; then
        docker exec digital_utopia_redis redis-cli DEL "$key" > /dev/null 2>&1 || true
      fi
    done
    log_success "Cache keys matching pattern invalidated"
  else
    log_info "No keys found matching pattern"
  fi
}

main() {
  echo "=========================================="
  echo "  Cache Invalidation"
  echo "=========================================="
  echo ""
  
  confirm_invalidation
  
  if [ "$INVALIDATE_ALL" = true ]; then
    invalidate_all
  elif [ -n "$PATTERN" ]; then
    invalidate_pattern
  else
    log_warning "No invalidation specified. Use --all or --pattern"
    exit 1
  fi
  
  echo ""
  echo "=========================================="
  log_success "Cache invalidation completed!"
  echo "=========================================="
}

main "$@"

