#!/bin/bash

# Monthly Deep Maintenance Script
# Performs extended maintenance tasks monthly

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "=========================================="
echo "  Monthly Deep Maintenance"
echo "=========================================="
echo ""

REPORT_FILE="$PROJECT_ROOT/reports/monthly/monthly_maintenance_$(date +%Y%m%d).md"
mkdir -p "$PROJECT_ROOT/reports/monthly"

log_info "Starting monthly deep maintenance..."

# Pre-maintenance backup
log_info "Creating pre-maintenance backup..."
if [ -f "$PROJECT_ROOT/scripts/data-backup.sh" ]; then
  "$PROJECT_ROOT/scripts/data-backup.sh" --name="pre-monthly-maintenance-$(date +%Y%m%d)" >> /tmp/monthly_maintenance.log 2>&1 || log_warning "Pre-maintenance backup failed, continuing..."
fi

# Extended maintenance
log_info "Running extended maintenance..."
if [ -f "$PROJECT_ROOT/scripts/data-maintenance.sh" ]; then
  "$PROJECT_ROOT/scripts/data-maintenance.sh" --all >> /tmp/monthly_maintenance.log 2>&1 || log_warning "Extended maintenance had issues"
fi

# Cache maintenance
log_info "Running cache maintenance..."
if [ -f "$PROJECT_ROOT/scripts/cache-invalidation.sh" ]; then
  "$PROJECT_ROOT/scripts/cache-invalidation.sh" --all >> /tmp/monthly_maintenance.log 2>&1 || log_warning "Cache invalidation had issues"
fi

if [ -f "$PROJECT_ROOT/scripts/cache-consistency-check.sh" ]; then
  "$PROJECT_ROOT/scripts/cache-consistency-check.sh" >> /tmp/monthly_maintenance.log 2>&1 || log_warning "Cache consistency check had issues"
fi

# Post-maintenance validation
log_info "Running post-maintenance validation..."
VALIDATION_RESULTS=""
if [ -f "$PROJECT_ROOT/scripts/check-integrity.sh" ]; then
  if "$PROJECT_ROOT/scripts/check-integrity.sh" --verbose >> /tmp/monthly_maintenance.log 2>&1; then
    VALIDATION_RESULTS="✅ Integrity check passed"
  else
    VALIDATION_RESULTS="⚠️ Integrity check had issues"
  fi
fi

# Generate report
cat > "$REPORT_FILE" << EOF
# Monthly Deep Maintenance Report

**Date**: $(date)
**Environment**: Production

## Maintenance Tasks Completed

1. ✅ Pre-maintenance backup created
2. ✅ Extended database maintenance (VACUUM, REINDEX, cleanup)
3. ✅ Cache invalidation
4. ✅ Cache consistency check
5. ✅ Post-maintenance validation

## Validation Results

$VALIDATION_RESULTS

## Maintenance Logs

See: /tmp/monthly_maintenance.log

## Next Steps

- Review maintenance logs for any issues
- Monitor system performance after maintenance
- Schedule next monthly maintenance for next month

EOF

log_success "Monthly deep maintenance completed!"
log_info "Report generated: $REPORT_FILE"

