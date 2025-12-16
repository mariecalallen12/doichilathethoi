#!/bin/bash

# Disaster Recovery Script
# Automated disaster recovery procedures
#
# Usage:
#   ./scripts/disaster-recovery.sh [--scenario=<scenario>] [--backup-dir=<dir>] [--confirm]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SCENARIO=""
BACKUP_DIR=""
SKIP_CONFIRM=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --scenario=*)
      SCENARIO="${1#*=}"
      shift
      ;;
    --backup-dir=*)
      BACKUP_DIR="${1#*=}"
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

confirm_recovery() {
  if [ "$SKIP_CONFIRM" = true ]; then
    return
  fi
  
  echo ""
  log_warning "⚠️  WARNING: DISASTER RECOVERY PROCEDURE"
  echo ""
  echo "This will:"
  echo "  - Stop all services"
  echo "  - Restore from backup"
  echo "  - Restart services"
  echo ""
  read -p "Are you sure you want to continue? (yes/no): " confirm
  
  if [ "$confirm" != "yes" ]; then
    log_info "Recovery cancelled"
    exit 0
  fi
}

stop_services() {
  log_info "Stopping all services..."
  
  cd "$PROJECT_ROOT"
  docker-compose down || {
    log_warning "Some services may not have stopped cleanly"
  }
  
  log_success "Services stopped"
}

restore_data() {
  log_info "Restoring data from backup..."
  
  if [ -z "$BACKUP_DIR" ]; then
    BACKUP_DIR=$(ls -td "$PROJECT_ROOT/backups"/*/ 2>/dev/null | head -1)
    if [ -z "$BACKUP_DIR" ]; then
      log_error "No backup directory found"
      exit 1
    fi
  fi
  
  log_info "Using backup: $BACKUP_DIR"
  
  if [ -f "$PROJECT_ROOT/scripts/restore-backup.sh" ]; then
    "$PROJECT_ROOT/scripts/restore-backup.sh" --backup-dir="$BACKUP_DIR" --confirm || {
      log_error "Data restoration failed"
      exit 1
    }
  else
    log_error "Restore script not found"
    exit 1
  fi
}

restart_services() {
  log_info "Restarting services..."
  
  cd "$PROJECT_ROOT"
  docker-compose up -d || {
    log_error "Service restart failed"
    exit 1
  }
  
  log_success "Services restarted"
}

verify_recovery() {
  log_info "Verifying recovery..."
  
  # Wait for services to be ready
  sleep 10
  
  if [ -f "$PROJECT_ROOT/scripts/health-check.sh" ]; then
    "$PROJECT_ROOT/scripts/health-check.sh" || {
      log_error "Health check failed"
      return 1
    }
  fi
  
  if [ -f "$PROJECT_ROOT/scripts/verify-deployment.sh" ]; then
    "$PROJECT_ROOT/scripts/verify-deployment.sh" || {
      log_error "Deployment verification failed"
      return 1
    }
  fi
  
  log_success "Recovery verification passed"
}

main() {
  echo "=========================================="
  echo "  Disaster Recovery"
  echo "=========================================="
  echo ""
  
  if [ -n "$SCENARIO" ]; then
    log_info "Recovery scenario: $SCENARIO"
  fi
  
  confirm_recovery
  stop_services
  restore_data
  restart_services
  verify_recovery
  
  echo ""
  echo "=========================================="
  log_success "Disaster recovery completed!"
  echo "=========================================="
  echo ""
  log_info "Please verify all services are functioning correctly"
}

main "$@"

