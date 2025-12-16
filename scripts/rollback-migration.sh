#!/bin/bash

# Migration Rollback Script
# Rollback database migration to a previous revision
#
# Usage:
#   ./scripts/rollback-migration.sh [--revision=<rev>] [--steps=<n>] [--confirm]
#
# Options:
#   --revision    Specific revision to rollback to
#   --steps       Number of steps to rollback
#   --confirm     Skip confirmation prompt

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

REVISION=""
STEPS=""
SKIP_CONFIRM=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --revision=*)
      REVISION="${1#*=}"
      shift
      ;;
    --steps=*)
      STEPS="${1#*=}"
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

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

confirm_rollback() {
  if [ "$SKIP_CONFIRM" = true ]; then
    return
  fi
  
  echo ""
  log_warning "⚠️  WARNING: This will rollback database migration"
  echo ""
  
  if [ -n "$REVISION" ]; then
    echo "Rolling back to revision: $REVISION"
  elif [ -n "$STEPS" ]; then
    echo "Rolling back $STEPS steps"
  else
    echo "Rolling back one step"
  fi
  
  echo ""
  read -p "Are you sure you want to continue? (yes/no): " confirm
  
  if [ "$confirm" != "yes" ]; then
    log_info "Rollback cancelled"
    exit 0
  fi
}

backup_before_rollback() {
  log_info "Creating backup before rollback..."
  
  if [ -f "$PROJECT_ROOT/scripts/data-backup.sh" ]; then
    "$PROJECT_ROOT/scripts/data-backup.sh" --name="pre-rollback-$(date +%Y%m%d-%H%M%S)" || {
      log_error "Backup failed"
      exit 1
    }
  else
    log_error "Backup script not found"
    exit 1
  fi
}

get_current_revision() {
  docker exec digital_utopia_backend alembic current 2>/dev/null | head -1 || echo "unknown"
}

perform_rollback() {
  log_info "Performing migration rollback..."
  
  local current_rev=$(get_current_revision)
  log_info "Current revision: $current_rev"
  
  if [ -n "$REVISION" ]; then
    log_info "Rolling back to revision: $REVISION"
    docker exec digital_utopia_backend alembic downgrade "$REVISION" || {
      log_error "Rollback failed"
      exit 1
    }
  elif [ -n "$STEPS" ]; then
    log_info "Rolling back $STEPS steps"
    docker exec digital_utopia_backend alembic downgrade "-$STEPS" || {
      log_error "Rollback failed"
      exit 1
    }
  else
    log_info "Rolling back one step"
    docker exec digital_utopia_backend alembic downgrade -1 || {
      log_error "Rollback failed"
      exit 1
    }
  fi
  
  log_success "Rollback completed"
}

verify_rollback() {
  log_info "Verifying rollback..."
  
  local new_rev=$(get_current_revision)
  log_info "New revision: $new_rev"
  
  # Run schema verification
  if [ -f "$PROJECT_ROOT/scripts/verify-schema.sh" ]; then
    "$PROJECT_ROOT/scripts/verify-schema.sh" || {
      log_warning "Schema verification found issues"
    }
  fi
}

main() {
  echo "=========================================="
  echo "  Migration Rollback Script"
  echo "=========================================="
  echo ""
  
  confirm_rollback
  backup_before_rollback
  perform_rollback
  verify_rollback
  
  echo ""
  echo "=========================================="
  log_success "Migration rollback completed successfully!"
  echo "=========================================="
}

main "$@"

