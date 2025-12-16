#!/bin/bash

# Data Maintenance Script
# Automated data maintenance tasks
#
# Usage:
#   ./scripts/data-maintenance.sh [--tasks=<task1,task2>] [--all]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

TASKS=""
RUN_ALL=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --tasks=*)
      TASKS="${1#*=}"
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

vacuum_database() {
  log_info "Running VACUUM on database..."
  
  docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "VACUUM ANALYZE;" > /dev/null 2>&1 || {
    log_warning "VACUUM had issues"
    return 1
  }
  
  log_success "VACUUM completed"
}

reindex_database() {
  log_info "Reindexing database..."
  
  docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "REINDEX DATABASE digital_utopia;" > /dev/null 2>&1 || {
    log_warning "Reindex had issues"
    return 1
  }
  
  log_success "Reindex completed"
}

cleanup_old_data() {
  log_info "Cleaning up old data..."
  
  # Cleanup old audit logs (older than 90 days)
  docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -c "
    DELETE FROM audit_logs 
    WHERE created_at < NOW() - INTERVAL '90 days';
  " > /dev/null 2>&1 || log_warning "Cleanup had issues"
  
  log_success "Cleanup completed"
}

run_all_tasks() {
  log_info "Running all maintenance tasks..."
  
  vacuum_database
  reindex_database
  cleanup_old_data
  
  log_success "All maintenance tasks completed"
}

main() {
  echo "=========================================="
  echo "  Data Maintenance"
  echo "=========================================="
  echo ""
  
  if [ "$RUN_ALL" = true ]; then
    run_all_tasks
  elif [ -n "$TASKS" ]; then
    IFS=',' read -ra TASK_ARRAY <<< "$TASKS"
    for task in "${TASK_ARRAY[@]}"; do
      case "$task" in
        vacuum)
          vacuum_database
          ;;
        reindex)
          reindex_database
          ;;
        cleanup)
          cleanup_old_data
          ;;
        *)
          log_warning "Unknown task: $task"
          ;;
      esac
    done
  else
    echo "Available tasks:"
    echo "  --tasks=vacuum,reindex,cleanup"
    echo "  --all (run all tasks)"
  fi
  
  echo ""
  echo "=========================================="
  log_success "Data maintenance completed!"
  echo "=========================================="
}

main "$@"

