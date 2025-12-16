#!/bin/bash

# Production Build Script
# Build Docker images for production environment with validation and optimization
#
# Usage:
#   ./scripts/build-production.sh [--version=<version>] [--service=<service>] [--no-cache]
#
# Options:
#   --version=<version>  Specify version tag for the build
#   --service=<service>  Build specific service (backend|client-app|admin-app|all)
#   --no-cache          Build without using cache

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env.production"

VERSION_TAG=""
SERVICE="all"
NO_CACHE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --version=*)
      VERSION_TAG="${1#*=}"
      shift
      ;;
    --service=*)
      SERVICE="${1#*=}"
      shift
      ;;
    --no-cache)
      NO_CACHE="--no-cache"
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

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Validate environment
validate_environment() {
  log_info "Validating environment..."
  
  # Check Docker
  if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed"
    exit 1
  fi
  
  # Check Docker Compose
  if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose is not installed"
    exit 1
  fi
  
  # Check environment file
  if [ ! -f "$ENV_FILE" ]; then
    log_error ".env.production file not found at $ENV_FILE"
    log_info "Please create .env.production with production configuration"
    exit 1
  fi
  
  # Load and validate environment variables
  # Use a safer method to load env file that handles special characters
  set -a
  # Filter out comments and empty lines, then source
  while IFS= read -r line || [ -n "$line" ]; do
    # Skip comments and empty lines
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${line// }" ]] && continue
    # Export the variable
    eval "export $line" 2>/dev/null || true
  done < "$ENV_FILE"
  set +a
  
  # Validate required variables for client-app
  if [[ "$SERVICE" == "client-app" || "$SERVICE" == "all" ]]; then
    if [ -z "$CLIENT_API_BASE_URL" ] || [ -z "$CLIENT_WS_URL" ]; then
      log_error "Required environment variables not set: CLIENT_API_BASE_URL, CLIENT_WS_URL"
      exit 1
    fi
  fi
  
  # Validate required variables for admin-app
  if [[ "$SERVICE" == "admin-app" || "$SERVICE" == "all" ]]; then
    if [ -z "$ADMIN_API_BASE_URL" ]; then
      log_warning "ADMIN_API_BASE_URL not set, using default /api"
      export ADMIN_API_BASE_URL="/api"
    fi
  fi
  
  # Validate required variables for backend
  if [[ "$SERVICE" == "backend" || "$SERVICE" == "all" ]]; then
    if [ -z "$POSTGRES_PASSWORD" ] || [ -z "$SECRET_KEY" ]; then
      log_warning "POSTGRES_PASSWORD or SECRET_KEY not set in .env.production"
      log_warning "Using defaults - NOT RECOMMENDED FOR PRODUCTION"
    fi
  fi
  
  log_success "Environment validation passed"
}

# Build backend
build_backend() {
  log_info "Building backend service..."
  
  cd "$PROJECT_ROOT/backend"
  
  TAGS="-t digital_utopia_backend:latest"
  if [ -n "$VERSION_TAG" ]; then
    TAGS="$TAGS -t digital_utopia_backend:$VERSION_TAG"
  fi
  TAGS="$TAGS -t digital_utopia_backend:production-$(date +%Y%m%d-%H%M%S)"
  
  # Use BuildKit for better caching and performance (if available)
  export DOCKER_BUILDKIT=1
  export COMPOSE_DOCKER_CLI_BUILD=1
  # Fallback if BuildKit not available
  if ! docker buildx version &>/dev/null; then
    export DOCKER_BUILDKIT=0
    log_warning "BuildKit not available, using standard build"
  fi
  
  docker build \
    $NO_CACHE \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    $TAGS \
    -f Dockerfile \
    . || {
    log_error "Backend build failed"
    exit 1
  }
  
  log_success "Backend build completed"
}

# Build client-app
build_client_app() {
  log_info "Building client-app service..."
  log_info "API URL: ${CLIENT_API_BASE_URL}"
  log_info "WebSocket URL: ${CLIENT_WS_URL}"
  
  cd "$PROJECT_ROOT/client-app"
  
  TAGS="-t digital_utopia_client:latest"
  if [ -n "$VERSION_TAG" ]; then
    TAGS="$TAGS -t digital_utopia_client:$VERSION_TAG"
  fi
  TAGS="$TAGS -t digital_utopia_client:production-$(date +%Y%m%d-%H%M%S)"
  
  # Use BuildKit for better caching and performance (if available)
  export DOCKER_BUILDKIT=1
  export COMPOSE_DOCKER_CLI_BUILD=1
  # Fallback if BuildKit not available
  if ! docker buildx version &>/dev/null; then
    export DOCKER_BUILDKIT=0
    log_warning "BuildKit not available, using standard build"
  fi
  
  docker build \
    $NO_CACHE \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --build-arg VITE_API_BASE_URL="${CLIENT_API_BASE_URL}" \
    --build-arg VITE_WS_URL="${CLIENT_WS_URL}" \
    $TAGS \
    -f Dockerfile \
    . || {
    log_error "Client-app build failed"
    exit 1
  }
  
  log_success "Client-app build completed"
}

# Build admin-app
build_admin_app() {
  log_info "Building admin-app service..."
  log_info "API URL: ${ADMIN_API_BASE_URL:-/api}"
  
  cd "$PROJECT_ROOT/Admin-app"
  
  TAGS="-t digital_utopia_admin:latest"
  if [ -n "$VERSION_TAG" ]; then
    TAGS="$TAGS -t digital_utopia_admin:$VERSION_TAG"
  fi
  TAGS="$TAGS -t digital_utopia_admin:production-$(date +%Y%m%d-%H%M%S)"
  
  # Use BuildKit for better caching and performance (if available)
  export DOCKER_BUILDKIT=1
  export COMPOSE_DOCKER_CLI_BUILD=1
  # Fallback if BuildKit not available
  if ! docker buildx version &>/dev/null; then
    export DOCKER_BUILDKIT=0
    log_warning "BuildKit not available, using standard build"
  fi
  
  docker build \
    $NO_CACHE \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --build-arg VITE_API_BASE_URL="${ADMIN_API_BASE_URL:-/api}" \
    $TAGS \
    -f Dockerfile \
    . || {
    log_error "Admin-app build failed"
    exit 1
  }
  
  log_success "Admin-app build completed"
}

# Verify build
verify_build() {
  log_info "Verifying builds..."
  
  local services=()
  
  if [[ "$SERVICE" == "backend" || "$SERVICE" == "all" ]]; then
    services+=("digital_utopia_backend:latest")
  fi
  
  if [[ "$SERVICE" == "client-app" || "$SERVICE" == "all" ]]; then
    services+=("digital_utopia_client:latest")
  fi
  
  if [[ "$SERVICE" == "admin-app" || "$SERVICE" == "all" ]]; then
    services+=("digital_utopia_admin:latest")
  fi
  
  for image in "${services[@]}"; do
    if docker image inspect "$image" &> /dev/null; then
      local size=$(docker image inspect "$image" --format='{{.Size}}' | numfmt --to=iec-i --suffix=B 2>/dev/null || echo "unknown")
      log_success "Image $image verified (Size: $size)"
    else
      log_error "Image $image not found"
      exit 1
    fi
  done
}

# Main execution
main() {
  echo "=========================================="
  echo "  Production Build Script"
  echo "=========================================="
  echo ""
  
  validate_environment
  
  if [ -n "$VERSION_TAG" ]; then
    log_info "Building version: $VERSION_TAG"
  fi
  
  if [ "$NO_CACHE" == "--no-cache" ]; then
    log_warning "Building without cache - this will take longer"
  fi
  
  case "$SERVICE" in
    backend)
      build_backend
      ;;
    client-app)
      build_client_app
      ;;
    admin-app)
      build_admin_app
      ;;
    all)
      build_backend
      build_client_app
      build_admin_app
      ;;
    *)
      log_error "Unknown service: $SERVICE"
      log_info "Available services: backend, client-app, admin-app, all"
      exit 1
      ;;
  esac
  
  verify_build
  
  echo ""
  echo "=========================================="
  log_success "Production build completed successfully!"
  echo "=========================================="
  echo ""
  log_info "Built images:"
  docker images | grep -E "digital_utopia_(backend|client|admin)" | head -10
}

# Run main function
main "$@"
