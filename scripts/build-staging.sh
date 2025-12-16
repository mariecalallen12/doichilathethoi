#!/bin/bash

# Staging Build Script
# Build Docker image for staging environment
#
# Usage:
#   ./scripts/build-staging.sh

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env.staging"

log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Load environment
if [ -f "$ENV_FILE" ]; then
  source "$ENV_FILE"
else
  log_info "Using default staging URLs"
  export STAGING_API_BASE_URL="${STAGING_API_BASE_URL:-https://staging-api.yourdomain.com}"
  export STAGING_WS_URL="${STAGING_WS_URL:-wss://staging-api.yourdomain.com/ws}"
fi

log_info "Building staging image..."
log_info "API URL: ${STAGING_API_BASE_URL}"
log_info "WebSocket URL: ${STAGING_WS_URL}"

cd "$PROJECT_ROOT/client-app"

docker build \
  --build-arg VITE_API_BASE_URL="${STAGING_API_BASE_URL}" \
  --build-arg VITE_WS_URL="${STAGING_WS_URL}" \
  -t client-app:staging \
  -t client-app:staging-$(date +%Y%m%d-%H%M%S) \
  . || {
  echo "Build failed"
  exit 1
}

log_success "Staging build completed"

