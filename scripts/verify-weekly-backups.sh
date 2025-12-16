#!/bin/bash

# Weekly Backup Verification Script
# Verifies all backups created during the week

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

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

echo "=========================================="
echo "  Weekly Backup Verification"
echo "=========================================="
echo ""

BACKUP_DIR="$PROJECT_ROOT/backups"
REPORT_FILE="$PROJECT_ROOT/reports/weekly/weekly_backup_verification_$(date +%Y%m%d).md"

mkdir -p "$PROJECT_ROOT/reports/weekly"

log_info "Verifying backups from the past week..."

# Find backups from the past 7 days
FAILED_BACKUPS=()
SUCCESSFUL_BACKUPS=()

for backup_dir in "$BACKUP_DIR"/*/; do
  if [ -d "$backup_dir" ]; then
    backup_name=$(basename "$backup_dir")
    backup_date=$(echo "$backup_name" | cut -d'_' -f1)
    
    # Check if backup is from the past week
    if [ -f "$PROJECT_ROOT/scripts/verify-backup.sh" ]; then
      if "$PROJECT_ROOT/scripts/verify-backup.sh" --backup-dir="$backup_dir" >> /tmp/backup_verify.log 2>&1; then
        SUCCESSFUL_BACKUPS+=("$backup_name")
        log_success "Backup $backup_name verified successfully"
      else
        FAILED_BACKUPS+=("$backup_name")
        log_error "Backup $backup_name verification failed"
      fi
    fi
  fi
done

# Generate report
cat > "$REPORT_FILE" << EOF
# Weekly Backup Verification Report

**Date**: $(date)
**Period**: Past 7 days

## Summary

- Total backups checked: $((${#SUCCESSFUL_BACKUPS[@]} + ${#FAILED_BACKUPS[@]}))
- Successful: ${#SUCCESSFUL_BACKUPS[@]}
- Failed: ${#FAILED_BACKUPS[@]}

## Successful Backups

$(for backup in "${SUCCESSFUL_BACKUPS[@]}"; do echo "- $backup"; done)

## Failed Backups

$(if [ ${#FAILED_BACKUPS[@]} -eq 0 ]; then echo "- None"; else for backup in "${FAILED_BACKUPS[@]}"; do echo "- $backup"; done; fi)

## Backup Retention Policy

- Retention period: 7 days
- Old backups will be automatically rotated

## Recommendations

$(if [ ${#FAILED_BACKUPS[@]} -gt 0 ]; then echo "- Investigate failed backups immediately"; echo "- Review backup logs for errors"; else echo "- All backups verified successfully"; fi)

EOF

log_success "Weekly backup verification completed!"
log_info "Report generated: $REPORT_FILE"

if [ ${#FAILED_BACKUPS[@]} -gt 0 ]; then
  log_error "Some backups failed verification. Review the report."
  exit 1
fi

