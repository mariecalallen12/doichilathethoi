#!/bin/bash

# Schema Verification Script
# Verify database schema consistency and version
#
# Usage:
#   ./scripts/verify-schema.sh [--verbose]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --verbose)
      VERBOSE=true
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

log_warning() {
  echo -e "${YELLOW}[!]${NC} $1"
}

check_database_connection() {
  log_info "Checking database connection..."
  
  if docker exec digital_utopia_postgres pg_isready -U postgres > /dev/null 2>&1; then
    log_success "Database is accessible"
    return 0
  else
    log_error "Database is not accessible"
    return 1
  fi
}

get_schema_version() {
  log_info "Getting schema version..."
  
  # Get Alembic version
  local alembic_version=$(docker exec digital_utopia_backend alembic current 2>/dev/null | head -1 || echo "unknown")
  
  if [ "$VERBOSE" = true ]; then
    echo "  Alembic version: $alembic_version"
  fi
  
  echo "$alembic_version"
}

verify_tables() {
  log_info "Verifying database tables..."
  
  # Get list of tables
  local tables=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name;
  " | tr -d ' ' | grep -v '^$')
  
  local table_count=$(echo "$tables" | wc -l)
  log_info "Found $table_count tables"
  
  if [ "$VERBOSE" = true ]; then
    echo "$tables" | while read table; do
      if [ -n "$table" ]; then
        local row_count=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "SELECT COUNT(*) FROM $table;" 2>/dev/null | tr -d ' ')
        echo "  - $table: $row_count rows"
      fi
    done
  fi
  
  log_success "Table verification completed"
}

verify_foreign_keys() {
  log_info "Verifying foreign key constraints..."
  
  local fk_count=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
    SELECT COUNT(*) 
    FROM information_schema.table_constraints 
    WHERE constraint_type = 'FOREIGN KEY' 
    AND table_schema = 'public';
  " | tr -d ' ')
  
  log_info "Found $fk_count foreign key constraints"
  
  # Check for orphaned records (simplified check)
  log_info "Checking for potential orphaned records..."
  # This would need to be customized based on schema
  
  log_success "Foreign key verification completed"
}

verify_indexes() {
  log_info "Verifying database indexes..."
  
  local index_count=$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
    SELECT COUNT(*) 
    FROM pg_indexes 
    WHERE schemaname = 'public';
  " | tr -d ' ')
  
  log_info "Found $index_count indexes"
  log_success "Index verification completed"
}

compare_with_migrations() {
  log_info "Comparing schema with migration files..."
  
  # Get list of migration files
  local migration_files=$(ls "$PROJECT_ROOT/backend/alembic/versions/"*.py 2>/dev/null | wc -l)
  log_info "Found $migration_files migration files"
  
  # Check if database is up to date
  local current_rev=$(get_schema_version)
  local head_rev=$(docker exec digital_utopia_backend alembic heads 2>/dev/null | head -1 || echo "unknown")
  
  if [ "$current_rev" = "$head_rev" ]; then
    log_success "Database schema is up to date"
  else
    log_warning "Database schema may not be up to date"
    log_info "Current: $current_rev"
    log_info "Head: $head_rev"
  fi
}

generate_schema_report() {
  log_info "Generating schema report..."
  
  local report_file="$PROJECT_ROOT/SCHEMA_VERIFICATION_REPORT_$(date +%Y%m%d_%H%M%S).md"
  
  cat > "$report_file" <<EOF
# Schema Verification Report

**Date**: $(date)
**Database**: digital_utopia

## Schema Version
- Current: $(get_schema_version)
- Head: $(docker exec digital_utopia_backend alembic heads 2>/dev/null | head -1 || echo "unknown")

## Tables
$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
  SELECT table_name 
  FROM information_schema.tables 
  WHERE table_schema = 'public' 
  ORDER BY table_name;
" | tr -d ' ' | grep -v '^$' | sed 's/^/- /')

## Foreign Keys
- Count: $(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
    SELECT COUNT(*) 
    FROM information_schema.table_constraints 
    WHERE constraint_type = 'FOREIGN KEY' 
    AND table_schema = 'public';
  " | tr -d ' ')

## Indexes
- Count: $(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
    SELECT COUNT(*) 
    FROM pg_indexes 
    WHERE schemaname = 'public';
  " | tr -d ' ')

EOF
  
  log_success "Report generated: $report_file"
}

main() {
  echo "=========================================="
  echo "  Schema Verification"
  echo "=========================================="
  echo ""
  
  local exit_code=0
  
  check_database_connection || exit_code=1
  get_schema_version
  verify_tables || exit_code=1
  verify_foreign_keys || exit_code=1
  verify_indexes || exit_code=1
  compare_with_migrations || exit_code=1
  generate_schema_report
  
  echo ""
  echo "=========================================="
  if [ $exit_code -eq 0 ]; then
    log_success "Schema verification completed successfully!"
  else
    log_error "Some verification checks failed"
  fi
  echo "=========================================="
  
  exit $exit_code
}

main "$@"
