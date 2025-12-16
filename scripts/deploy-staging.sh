#!/bin/bash

# Staging Deployment Script
# Automated deployment to staging environment
#
# Usage:
#   ./scripts/deploy-staging.sh [--skip-build] [--skip-tests]
#
# Options:
#   --skip-build    Skip Docker build step
#   --skip-tests    Skip pre-deployment tests

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
ENV_FILE="$PROJECT_ROOT/.env.staging"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
STAGING_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.staging.yml"

# Flags
SKIP_BUILD=false
SKIP_TESTS=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --skip-build)
      SKIP_BUILD=true
      shift
      ;;
    --skip-tests)
      SKIP_TESTS=true
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

check_prerequisites() {
  log_info "Checking prerequisites..."
  
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
    log_warning ".env.staging file not found. Creating from template..."
    if [ -f "$PROJECT_ROOT/client-app/.env.staging.example" ]; then
      cp "$PROJECT_ROOT/client-app/.env.staging.example" "$ENV_FILE"
      log_warning "Please update .env.staging with your staging configuration"
      exit 1
    else
      log_error ".env.staging.example not found"
      exit 1
    fi
  fi
  
  log_success "Prerequisites check passed"
}

load_environment() {
  log_info "Loading environment variables..."
  
  if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
    log_success "Environment variables loaded"
  else
    log_error "Environment file not found: $ENV_FILE"
    exit 1
  fi
}

run_pre_deployment_tests() {
  if [ "$SKIP_TESTS" = true ]; then
    log_warning "Skipping pre-deployment tests"
    return
  fi
  
  log_info "Running pre-deployment tests..."
  
  cd "$PROJECT_ROOT/client-app"
  
  # Run local tests if backend is available
  if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    log_info "Running local API tests..."
    node scripts/test-local.mjs || {
      log_warning "Some tests failed, but continuing deployment"
    }
  else
    log_warning "Backend not available locally, skipping local tests"
  fi
  
  cd "$PROJECT_ROOT"
  log_success "Pre-deployment tests completed"
}

build_staging_image() {
  if [ "$SKIP_BUILD" = true ]; then
    log_warning "Skipping Docker build"
    return
  fi
  
  log_info "Building staging Docker image..."
  
  cd "$PROJECT_ROOT"
  
  docker-compose -f "$COMPOSE_FILE" -f "$STAGING_COMPOSE_FILE" build client-app || {
    log_error "Docker build failed"
    exit 1
  }
  
  log_success "Docker image built successfully"
}

deploy_to_staging() {
  log_info "Deploying to staging..."
  
  cd "$PROJECT_ROOT"
  
  # Stop existing containers
  log_info "Stopping existing containers..."
  docker-compose -f "$COMPOSE_FILE" -f "$STAGING_COMPOSE_FILE" down client-app 2>/dev/null || true
  
  # Start new containers
  log_info "Starting staging containers..."
  docker-compose -f "$COMPOSE_FILE" -f "$STAGING_COMPOSE_FILE" up -d client-app || {
    log_error "Deployment failed"
    exit 1
  }
  
  log_success "Deployment completed"
}

verify_deployment() {
  log_info "Verifying deployment..."
  
  # Wait for container to be ready
  sleep 5
  
  # Check container status
  if docker ps | grep -q "digital_utopia_client_staging"; then
    log_success "Container is running"
  else
    log_error "Container is not running"
    exit 1
  fi
  
  # Check health endpoint
  local health_url="http://localhost:${STAGING_CLIENT_PORT:-3003}/health"
  if curl -f -s "$health_url" > /dev/null; then
    log_success "Health check passed"
  else
    log_warning "Health check failed, but container is running"
  fi
  
  # Show container logs
  log_info "Recent container logs:"
  docker logs --tail 20 digital_utopia_client_staging
}

main() {
  echo "=========================================="
  echo "  Staging Deployment Script"
  echo "=========================================="
  echo ""
  
  check_prerequisites
  load_environment
  run_pre_deployment_tests
  build_staging_image
  deploy_to_staging
  verify_deployment
  
  echo ""
  echo "=========================================="
  log_success "Staging deployment completed successfully!"
  echo "=========================================="
  echo ""
  echo "Access staging at: http://localhost:${STAGING_CLIENT_PORT:-3003}"
  echo "View logs: docker logs -f digital_utopia_client_staging"
}

# Run main function
main "$@"

