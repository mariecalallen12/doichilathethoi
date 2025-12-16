#!/bin/bash

# Production Deployment Script
# Automated deployment to production environment with safety checks, rollback, and migration validation
#
# Usage:
#   ./scripts/deploy-production.sh [--dry-run] [--skip-tests] [--version=<version>] [--service=<service>]
#
# Options:
#   --dry-run       Perform a dry run without actual deployment
#   --skip-tests    Skip pre-deployment tests
#   --version       Specify version tag for the deployment
#   --service       Deploy specific service (backend|client-app|admin-app|all)

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
ENV_FILE="$PROJECT_ROOT/.env.production"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
PROD_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.prod.yml"
BACKUP_DIR="$PROJECT_ROOT/deployment_backups"

# Flags
DRY_RUN=false
SKIP_TESTS=false
VERSION_TAG=""
SERVICE="all"
ROLLBACK_TAG=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --skip-tests)
      SKIP_TESTS=true
      shift
      ;;
    --version=*)
      VERSION_TAG="${1#*=}"
      shift
      ;;
    --service=*)
      SERVICE="${1#*=}"
      shift
      ;;
    --rollback=*)
      ROLLBACK_TAG="${1#*=}"
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

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Rollback function
rollback_deployment() {
  local service=$1
  log_error "Deployment failed for $service. Initiating rollback..."
  
  # Find the most recent backup
  local backup_tag=$(docker images --format "{{.Tag}}" | grep "backup-" | sort -r | head -1)
  
  if [ -z "$backup_tag" ]; then
    log_error "No backup found for rollback"
    return 1
  fi
  
  log_info "Rolling back to: $backup_tag"
  
  case "$service" in
    backend)
      docker tag "digital_utopia_backend:$backup_tag" "digital_utopia_backend:latest" || true
      docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" up -d backend || true
      ;;
    client-app)
      docker tag "digital_utopia_client:$backup_tag" "digital_utopia_client:latest" || true
      docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" up -d client-app || true
      ;;
    admin-app)
      docker tag "digital_utopia_admin:$backup_tag" "digital_utopia_admin:latest" || true
      docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" up -d admin-app || true
      ;;
    all)
      rollback_deployment "backend"
      rollback_deployment "client-app"
      rollback_deployment "admin-app"
      ;;
  esac
  
  log_warning "Rollback completed. Please verify the system."
}

confirm_deployment() {
  if [ "$DRY_RUN" = true ]; then
    log_warning "DRY RUN MODE - No changes will be made"
    return
  fi
  
  if [ -n "$ROLLBACK_TAG" ]; then
    log_warning "ROLLBACK MODE - Rolling back to: $ROLLBACK_TAG"
    return
  fi
  
  echo ""
  echo -e "${YELLOW}⚠️  WARNING: This will deploy to PRODUCTION${NC}"
  echo ""
  read -p "Are you sure you want to continue? (yes/no): " confirm
  
  if [ "$confirm" != "yes" ]; then
    log_info "Deployment cancelled"
    exit 0
  fi
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
    log_error ".env.production file not found"
    log_info "Please create .env.production with production configuration"
    exit 1
  fi
  
  log_success "Prerequisites check passed"
}

load_environment() {
  log_info "Loading environment variables..."
  
  if [ -f "$ENV_FILE" ]; then
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
    log_success "Environment variables loaded"
  else
    log_error "Environment file not found: $ENV_FILE"
    exit 1
  fi
}

check_database_migrations() {
  log_info "Checking database migrations..."
  
  if [ "$DRY_RUN" = true ]; then
    log_warning "Skipping migration check in dry-run mode"
    return
  fi
  
  # Check if backend container is running
  if ! docker ps | grep -q "digital_utopia_backend"; then
    log_warning "Backend container not running, skipping migration check"
    return
  fi
  
  # Run migration check
  log_info "Running alembic check..."
  docker exec digital_utopia_backend alembic check || {
    log_warning "Migration check failed or alembic not available"
    log_info "You may need to run migrations manually after deployment"
  }
  
  log_success "Database migration check completed"
}

run_pre_deployment_checks() {
  log_info "Running pre-deployment checks..."
  
  # Check if production API is accessible
  if [ -n "$CLIENT_API_BASE_URL" ]; then
    log_info "Checking production API connectivity..."
    if curl -f -s "${CLIENT_API_BASE_URL}/api/health" > /dev/null 2>&1; then
      log_success "Production API is accessible"
    else
      log_warning "Production API health check failed (may be normal if first deployment)"
    fi
  fi
  
  # Check disk space
  log_info "Checking disk space..."
  available_space=$(df -BG "$PROJECT_ROOT" 2>/dev/null | tail -1 | awk '{print $4}' | sed 's/G//' || echo "0")
  if [ "$available_space" -lt 10 ] && [ "$available_space" != "0" ]; then
    log_warning "Low disk space: ${available_space}G available"
  else
    log_success "Sufficient disk space available"
  fi
  
  # Check Docker images exist
  log_info "Checking Docker images..."
  case "$SERVICE" in
    backend)
      if ! docker images | grep -q "digital_utopia_backend"; then
        log_error "Backend image not found. Please build first."
        exit 1
      fi
      ;;
    client-app)
      if ! docker images | grep -q "digital_utopia_client"; then
        log_error "Client-app image not found. Please build first."
        exit 1
      fi
      ;;
    admin-app)
      if ! docker images | grep -q "digital_utopia_admin"; then
        log_error "Admin-app image not found. Please build first."
        exit 1
      fi
      ;;
    all)
      for img in "digital_utopia_backend" "digital_utopia_client" "digital_utopia_admin"; do
        if ! docker images | grep -q "$img"; then
          log_error "$img image not found. Please build first."
          exit 1
        fi
      done
      ;;
  esac
  
  log_success "Pre-deployment checks completed"
}

run_pre_deployment_tests() {
  if [ "$SKIP_TESTS" = true ]; then
    log_warning "Skipping pre-deployment tests"
    return
  fi
  
  log_info "Running pre-deployment tests..."
  
  # Test backend health
  if [[ "$SERVICE" == "backend" || "$SERVICE" == "all" ]]; then
    log_info "Testing backend health..."
    if docker ps | grep -q "digital_utopia_backend"; then
      if curl -f -s "http://localhost:${BACKEND_PORT:-8000}/api/health" > /dev/null 2>&1; then
        log_success "Backend health check passed"
      else
        log_warning "Backend health check failed"
      fi
    fi
  fi
  
  # Test client-app
  if [[ "$SERVICE" == "client-app" || "$SERVICE" == "all" ]]; then
    if [ -n "$CLIENT_API_BASE_URL" ] && [ -n "$CLIENT_WS_URL" ]; then
      log_info "Running production API tests..."
      cd "$PROJECT_ROOT/client-app"
      if [ -f "scripts/test-production-api.mjs" ]; then
        node scripts/test-production-api.mjs \
          --api-url="$CLIENT_API_BASE_URL" \
          --ws-url="$CLIENT_WS_URL" || {
          log_warning "Pre-deployment API tests failed (non-blocking)"
        }
      fi
      cd "$PROJECT_ROOT"
    fi
  fi
  
  log_success "Pre-deployment tests completed"
}

create_backup() {
  local service=$1
  local backup_tag="backup-$(date +%Y%m%d-%H%M%S)"
  
  log_info "Creating backup for $service..."
  
  case "$service" in
    backend)
      if docker images | grep -q "digital_utopia_backend:latest"; then
        docker tag "digital_utopia_backend:latest" "digital_utopia_backend:$backup_tag"
        log_success "Backend backup created: $backup_tag"
      fi
      ;;
    client-app)
      if docker images | grep -q "digital_utopia_client:latest"; then
        docker tag "digital_utopia_client:latest" "digital_utopia_client:$backup_tag"
        log_success "Client-app backup created: $backup_tag"
      fi
      ;;
    admin-app)
      if docker images | grep -q "digital_utopia_admin:latest"; then
        docker tag "digital_utopia_admin:latest" "digital_utopia_admin:$backup_tag"
        log_success "Admin-app backup created: $backup_tag"
      fi
      ;;
  esac
}

deploy_service() {
  local service=$1
  
  if [ "$DRY_RUN" = true ]; then
    log_info "DRY RUN: Would deploy $service"
    return 0
  fi
  
  log_info "Deploying $service..."
  
  # Create backup
  create_backup "$service"
  
  # Stop existing container
  log_info "Stopping existing $service container..."
  docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" stop "$service" 2>/dev/null || true
  
  # Start new container
  log_info "Starting new $service container..."
  if docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" up -d "$service"; then
    log_success "$service deployed successfully"
    return 0
  else
    log_error "$service deployment failed"
    return 1
  fi
}

deploy_to_production() {
  if [ -n "$ROLLBACK_TAG" ]; then
    rollback_deployment "$SERVICE"
    return
  fi
  
  log_info "Deploying to production..."
  
  cd "$PROJECT_ROOT"
  
  case "$SERVICE" in
    backend)
      if ! deploy_service "backend"; then
        rollback_deployment "backend"
        exit 1
      fi
      ;;
    client-app)
      if ! deploy_service "client-app"; then
        rollback_deployment "client-app"
        exit 1
      fi
      ;;
    admin-app)
      if ! deploy_service "admin-app"; then
        rollback_deployment "admin-app"
        exit 1
      fi
      ;;
    all)
      local failed=false
      for svc in "backend" "client-app" "admin-app"; do
        if ! deploy_service "$svc"; then
          failed=true
        fi
      done
      if [ "$failed" = true ]; then
        log_error "Some services failed to deploy"
        rollback_deployment "all"
        exit 1
      fi
      ;;
    *)
      log_error "Unknown service: $SERVICE"
      exit 1
      ;;
  esac
  
  log_success "Deployment completed"
}

verify_deployment() {
  log_info "Verifying deployment..."
  
  # Wait for containers to be ready
  sleep 15
  
  local failed=false
  
  case "$SERVICE" in
    backend)
      if ! docker ps | grep -q "digital_utopia_backend"; then
        log_error "Backend container is not running"
        failed=true
      else
        log_info "Checking backend health..."
        for i in {1..5}; do
          if curl -f -s "http://localhost:${BACKEND_PORT:-8000}/api/health" > /dev/null 2>&1; then
            log_success "Backend health check passed"
            break
          fi
          if [ $i -eq 5 ]; then
            log_error "Backend health check failed after 5 attempts"
            failed=true
          else
            sleep 3
          fi
        done
      fi
      ;;
    client-app)
      if ! docker ps | grep -q "digital_utopia_client"; then
        log_error "Client-app container is not running"
        failed=true
      else
        log_info "Checking client-app health..."
        for i in {1..5}; do
          if curl -f -s "http://localhost:${CLIENT_PORT:-3002}/health" > /dev/null 2>&1; then
            log_success "Client-app health check passed"
            break
          fi
          if [ $i -eq 5 ]; then
            log_error "Client-app health check failed after 5 attempts"
            failed=true
          else
            sleep 3
          fi
        done
      fi
      ;;
    admin-app)
      if ! docker ps | grep -q "digital_utopia_admin"; then
        log_error "Admin-app container is not running"
        failed=true
      else
        log_info "Checking admin-app health..."
        for i in {1..5}; do
          if curl -f -s "http://localhost:${ADMIN_PORT:-3001}/health" > /dev/null 2>&1; then
            log_success "Admin-app health check passed"
            break
          fi
          if [ $i -eq 5 ]; then
            log_error "Admin-app health check failed after 5 attempts"
            failed=true
          else
            sleep 3
          fi
        done
      fi
      ;;
    all)
      verify_deployment "backend"
      verify_deployment "client-app"
      verify_deployment "admin-app"
      ;;
  esac
  
  if [ "$failed" = true ]; then
    log_error "Deployment verification failed"
    if [ "$DRY_RUN" != true ]; then
      log_info "Initiating automatic rollback..."
      rollback_deployment "$SERVICE"
    fi
    exit 1
  fi
  
  log_success "Deployment verification completed"
}

main() {
  echo "=========================================="
  echo "  Production Deployment Script"
  echo "=========================================="
  echo ""
  
  confirm_deployment
  check_prerequisites
  load_environment
  run_pre_deployment_checks
  check_database_migrations
  run_pre_deployment_tests
  deploy_to_production
  verify_deployment
  
  echo ""
  echo "=========================================="
  log_success "Production deployment completed successfully!"
  echo "=========================================="
  echo ""
  log_info "Deployed services: $SERVICE"
  log_info "Monitor deployment:"
  case "$SERVICE" in
    backend)
      echo "  docker logs -f digital_utopia_backend"
      echo "  curl http://localhost:${BACKEND_PORT:-8000}/api/health"
      ;;
    client-app)
      echo "  docker logs -f digital_utopia_client"
      echo "  curl http://localhost:${CLIENT_PORT:-3002}/health"
      ;;
    admin-app)
      echo "  docker logs -f digital_utopia_admin"
      echo "  curl http://localhost:${ADMIN_PORT:-3001}/health"
      ;;
    all)
      echo "  docker logs -f digital_utopia_backend"
      echo "  docker logs -f digital_utopia_client"
      echo "  docker logs -f digital_utopia_admin"
      ;;
  esac
}

# Run main function
main "$@"
