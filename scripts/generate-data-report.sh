#!/bin/bash

# Data Report Generation Script
# Generate comprehensive data reports
#
# Usage:
#   ./scripts/generate-data-report.sh [--type=<type>] [--output=<file>]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

REPORT_TYPE="comprehensive"
OUTPUT_FILE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --type=*)
      REPORT_TYPE="${1#*=}"
      shift
      ;;
    --output=*)
      OUTPUT_FILE="${1#*=}"
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

generate_comprehensive_report() {
  log_info "Generating comprehensive data report..."
  
  if [ -z "$OUTPUT_FILE" ]; then
    OUTPUT_FILE="$PROJECT_ROOT/DATA_REPORT_$(date +%Y%m%d_%H%M%S).md"
  fi
  
  cat > "$OUTPUT_FILE" <<EOF
# Comprehensive Data Report

**Date**: $(date)
**Type**: $REPORT_TYPE

## Database Statistics

### Table Counts
$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
  SELECT table_name, 
         (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
  FROM information_schema.tables t
  WHERE table_schema = 'public'
  ORDER BY table_name;
" 2>/dev/null | sed 's/^/- /' || echo "Unable to retrieve")

### Database Size
$(docker exec digital_utopia_postgres psql -U postgres -d digital_utopia -t -c "
  SELECT pg_size_pretty(pg_database_size('digital_utopia'));
" 2>/dev/null | tr -d ' ' || echo "Unknown")

## Data Quality

- Validation: Run \`./scripts/validate-all-data.sh\`
- Integrity: Run \`./scripts/check-integrity.sh\`
- Quality: Run \`./scripts/data-quality-check.sh\`

## Summary

Comprehensive data report generated.

EOF
  
  log_success "Report generated: $OUTPUT_FILE"
}

main() {
  echo "=========================================="
  echo "  Data Report Generation"
  echo "=========================================="
  echo ""
  
  case "$REPORT_TYPE" in
    comprehensive)
      generate_comprehensive_report
      ;;
    *)
      log_error "Unknown report type: $REPORT_TYPE"
      exit 1
      ;;
  esac
  
  echo ""
  echo "=========================================="
  log_success "Report generation completed!"
  echo "=========================================="
}

main "$@"

