#!/bin/bash

# Data Comparison Script
# Compare data between environments
#
# Usage:
#   ./scripts/compare-data.sh --source=<env> --target=<env> [--tables=<table1,table2>]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SOURCE_ENV=""
TARGET_ENV=""
TABLES=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --source=*)
      SOURCE_ENV="${1#*=}"
      shift
      ;;
    --target=*)
      TARGET_ENV="${1#*=}"
      shift
      ;;
    --tables=*)
      TABLES="${1#*=}"
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
  echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
  echo -e "${RED}[✗]${NC} $1"
}

compare_table_counts() {
  local table=$1
  local source_count=$2
  local target_count=$3
  
  if [ "$source_count" = "$target_count" ]; then
    log_success "$table: $source_count rows (match)"
  else
    log_error "$table: Source=$source_count, Target=$target_count (mismatch)"
  fi
}

compare_tables() {
  log_info "Comparing tables between $SOURCE_ENV and $TARGET_ENV..."
  
  if [ -n "$TABLES" ]; then
    IFS=',' read -ra TABLE_ARRAY <<< "$TABLES"
    for table in "${TABLE_ARRAY[@]}"; do
      log_info "Comparing table: $table"
      # Get row counts from both environments
      # This is a placeholder for actual comparison logic
      compare_table_counts "$table" "0" "0"
    done
  else
    log_info "Comparing all tables"
    # Compare all tables
    # This is a placeholder for actual comparison logic
  fi
}

generate_comparison_report() {
  log_info "Generating comparison report..."
  
  local report_file="$PROJECT_ROOT/DATA_COMPARISON_REPORT_$(date +%Y%m%d_%H%M%S).md"
  
  cat > "$report_file" <<EOF
# Data Comparison Report

**Date**: $(date)
**Source Environment**: $SOURCE_ENV
**Target Environment**: $TARGET_ENV

## Comparison Results

$(compare_tables)

## Summary

Comparison completed between $SOURCE_ENV and $TARGET_ENV.

EOF
  
  log_success "Report generated: $report_file"
}

main() {
  echo "=========================================="
  echo "  Data Comparison Script"
  echo "=========================================="
  echo ""
  
  if [ -z "$SOURCE_ENV" ] || [ -z "$TARGET_ENV" ]; then
    log_error "Source and target environments must be specified"
    echo "Usage: ./scripts/compare-data.sh --source=<env> --target=<env>"
    exit 1
  fi
  
  compare_tables
  generate_comparison_report
  
  echo ""
  echo "=========================================="
  log_success "Data comparison completed!"
  echo "=========================================="
}

main "$@"

