#!/bin/bash

# Database Migration Script
# Automated database migration using Alembic
#
# Usage:
#   ./scripts/migrate-database.sh [--environment=<env>] [--revision=<rev>] [--dry-run]
#
# Options:
#   --environment    Target environment (development, staging, production)
#   --revision       Specific revision to migrate to
#   --dry-run        Show what would be done without executing

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

ENVIRONMENT="development"
REVISION="head"
DRY_RUN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --environment=*)
      ENVIRONMENT="${1#*=}"
      shift
      ;;
    --revision=*)
      REVISION="${1#*=}"
      shift
      ;;
    --dry-run)
      DRY_RUN=true
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

check_prerequisites() {
  log_info "Checking prerequisites..."
  
  # Check if backend container is running
  if ! docker ps | grep -q "digital_utopia_backend"; then
    log_error "Backend container is not running"
    exit 1
  fi
  
  # Check if database is accessible
  if ! docker exec digital_utopia_postgres pg_isready -U postgres > /dev/null 2>&1; then
    log_error "Database is not accessible"
    exit 1
  fi
  
  log_success "Prerequisites check passed"
}

get_current_revision() {
  log_info "Getting current database revision..."
  
  docker exec digital_utopia_backend alembic current 2>/dev/null | head -1 || echo "unknown"
}

get_head_revision() {
  log_info "Getting head revision..."
  
  docker exec digital_utopia_backend alembic heads 2>/dev/null | head -1 || echo "unknown"
}

backup_before_migration() {
  log_info "Creating backup before migration..."
  
  if [ -f "$PROJECT_ROOT/scripts/data-backup.sh" ]; then
    "$PROJECT_ROOT/scripts/data-backup.sh" --name="pre-migration-$(date +%Y%m%d-%H%M%S)" || {
      log_warning "Backup failed, but continuing..."
    }
  else
    log_warning "Backup script not found, skipping backup"
  fi
}

run_migration() {
  log_info "Running database migration..."
  log_info "Environment: $ENVIRONMENT"
  log_info "Target revision: $REVISION"
  
  if [ "$DRY_RUN" = true ]; then
    log_warning "DRY RUN MODE - No changes will be made"
    docker exec digital_utopia_backend alembic upgrade --sql "$REVISION" || {
      log_error "Migration dry run failed"
      exit 1
    }
  else
    # Confirm for production
    if [ "$ENVIRONMENT" = "production" ]; then
      echo ""
      log_warning "⚠️  WARNING: This will migrate PRODUCTION database"
      read -p "Are you sure? (yes/no): " confirm
      if [ "$confirm" != "yes" ]; then
        log_info "Migration cancelled"
        exit 0
      fi
    fi
    
    docker exec digital_utopia_backend alembic upgrade "$REVISION" || {
      log_error "Migration failed"
      exit 1
    }
  fi
  
  log_success "Migration completed"
}

verify_migration() {
  log_info "Verifying migration..."
  
  local current_rev=$(get_current_revision)
  log_info "Current revision: $current_rev"
  
  if [ "$REVISION" = "head" ]; then
    local head_rev=$(get_head_revision)
    if [ "$current_rev" = "$head_rev" ]; then
      log_success "Database is at head revision"
    else
      log_warning "Database revision mismatch"
    fi
  fi
  
  # Run schema verification
  if [ -f "$PROJECT_ROOT/scripts/verify-schema.sh" ]; then
    "$PROJECT_ROOT/scripts/verify-schema.sh" || {
      log_warning "Schema verification found issues"
    }
  fi
}

main() {
  echo "=========================================="
  echo "  Database Migration Script"
  echo "=========================================="
  echo ""
  
  check_prerequisites
  
  local current_rev=$(get_current_revision)
  log_info "Current database revision: $current_rev"
  
  if [ "$DRY_RUN" = false ]; then
    backup_before_migration
  fi
  
  run_migration
  verify_migration
  
  echo ""
  echo "=========================================="
  log_success "Database migration completed successfully!"
  echo "=========================================="
}

main "$@"

