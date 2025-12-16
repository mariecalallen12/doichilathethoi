#!/bin/bash

# Data Operations Master Script
# Master script for all data operations
#
# Usage:
#   ./scripts/data-operations-master.sh [--operation=<op>] [--all]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

OPERATION=""
RUN_ALL=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --operation=*)
      OPERATION="${1#*=}"
      shift
      ;;
    --all)
      RUN_ALL=true
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

run_validation() {
  log_info "Running data validation..."
  
  if [ -f "$SCRIPT_DIR/validate-all-data.sh" ]; then
    "$SCRIPT_DIR/validate-all-data.sh" || return 1
  fi
  
  if [ -f "$SCRIPT_DIR/check-integrity.sh" ]; then
    "$SCRIPT_DIR/check-integrity.sh" || return 1
  fi
  
  log_success "Validation completed"
}

run_backup() {
  log_info "Running backup..."
  
  if [ -f "$SCRIPT_DIR/data-backup.sh" ]; then
    "$SCRIPT_DIR/data-backup.sh" || return 1
  fi
  
  log_success "Backup completed"
}

run_monitoring() {
  log_info "Running monitoring..."
  
  if [ -f "$SCRIPT_DIR/monitor-data-health.sh" ]; then
    "$SCRIPT_DIR/monitor-data-health.sh" || return 1
  fi
  
  log_success "Monitoring completed"
}

run_all_operations() {
  log_info "Running all data operations..."
  
  run_validation
  run_backup
  run_monitoring
  
  log_success "All operations completed"
}

main() {
  echo "=========================================="
  echo "  Data Operations Master"
  echo "=========================================="
  echo ""
  
  if [ "$RUN_ALL" = true ]; then
    run_all_operations
  elif [ -n "$OPERATION" ]; then
    case "$OPERATION" in
      validation)
        run_validation
        ;;
      backup)
        run_backup
        ;;
      monitoring)
        run_monitoring
        ;;
      *)
        log_error "Unknown operation: $OPERATION"
        exit 1
        ;;
    esac
  else
    echo "Available operations:"
    echo "  --operation=validation"
    echo "  --operation=backup"
    echo "  --operation=monitoring"
    echo "  --all (run all operations)"
  fi
  
  echo ""
  echo "=========================================="
  log_success "Data operations completed!"
  echo "=========================================="
}

main "$@"

