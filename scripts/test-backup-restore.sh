#!/bin/bash

# Monthly Backup Restore Testing Script
# Tests restore functionality by restoring a random backup to staging

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

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

echo "=========================================="
echo "  Monthly Backup Restore Test"
echo "=========================================="
echo ""

REPORT_FILE="$PROJECT_ROOT/reports/monthly/restore_test_$(date +%Y%m%d).md"
mkdir -p "$PROJECT_ROOT/reports/monthly"

log_info "Selecting a backup from last month for testing..."

# Find backups from last month
BACKUP_DIR="$PROJECT_ROOT/backups"
LAST_MONTH=$(date -d "last month" +%Y%m)
AVAILABLE_BACKUPS=()

for backup_dir in "$BACKUP_DIR"/*/; do
  if [ -d "$backup_dir" ]; then
    backup_name=$(basename "$backup_dir")
    backup_date=$(echo "$backup_name" | cut -d'_' -f1)
    if [[ "$backup_date" == "$LAST_MONTH"* ]]; then
      AVAILABLE_BACKUPS+=("$backup_dir")
    fi
  fi
done

if [ ${#AVAILABLE_BACKUPS[@]} -eq 0 ]; then
  log_warning "No backups found from last month. Skipping restore test."
  cat > "$REPORT_FILE" << EOF
# Monthly Backup Restore Test Report

**Date**: $(date)
**Status**: SKIPPED

## Reason

No backups found from last month to test restore functionality.

## Recommendation

Ensure backups are being created regularly. This test will be attempted again next month.

EOF
  exit 0
fi

# Select random backup
SELECTED_BACKUP="${AVAILABLE_BACKUPS[$RANDOM % ${#AVAILABLE_BACKUPS[@]}]}"
BACKUP_NAME=$(basename "$SELECTED_BACKUP")

log_info "Selected backup: $BACKUP_NAME"
log_warning "Restore test requires manual intervention and staging environment setup."
log_info "This script generates a restore test plan. Actual restore should be done manually."

# Generate restore test plan
cat > "$REPORT_FILE" << EOF
# Monthly Backup Restore Test Report

**Date**: $(date)
**Selected Backup**: $BACKUP_NAME
**Backup Location**: $SELECTED_BACKUP

## Test Plan

### Pre-Restore Steps

1. Verify backup integrity:
   \`\`\`bash
   ./scripts/verify-backup.sh --backup-dir=$SELECTED_BACKUP
   \`\`\`

2. Create safety backup of staging environment before restore

3. Ensure staging environment is available and isolated

### Restore Steps

1. Restore backup to staging:
   \`\`\`bash
   ./scripts/restore-backup.sh --backup-dir=$SELECTED_BACKUP --environment=staging --confirm
   \`\`\`

2. Verify restored data integrity:
   \`\`\`bash
   ./scripts/check-integrity.sh --verbose
   ./scripts/validate-all-data.sh --verbose
   \`\`\`

3. Test application functionality with restored data

### Post-Restore Steps

1. Document restore test results
2. Verify data consistency
3. Test critical workflows
4. Restore staging to original state if needed

## Status

**PENDING MANUAL EXECUTION**

This restore test requires manual execution following the plan above.

## Notes

- Restore should only be done in staging environment
- Always create backup before restore
- Verify data integrity after restore
- Document any issues encountered

EOF

log_success "Restore test plan generated!"
log_info "Report: $REPORT_FILE"
log_warning "Manual execution required. Follow the plan in the report."

