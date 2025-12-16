#!/bin/bash

# Setup Production Cron Jobs for Data Management Framework
# This script sets up all scheduled tasks for production operations

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
echo "  Production Cron Jobs Setup"
echo "=========================================="
echo ""

# Create temporary crontab file
TEMP_CRON=$(mktemp)

# Get existing crontab (if any)
crontab -l > "$TEMP_CRON" 2>/dev/null || true

# Check if production jobs already exist
if grep -q "# Data Management Framework - Production" "$TEMP_CRON" 2>/dev/null; then
  log_warning "Production cron jobs already exist. Removing old entries..."
  # Remove old entries
  sed -i '/# Data Management Framework - Production/,/^$/d' "$TEMP_CRON"
fi

# Add production cron jobs section
echo "" >> "$TEMP_CRON"
echo "# Data Management Framework - Production" >> "$TEMP_CRON"
echo "# Generated: $(date)" >> "$TEMP_CRON"
echo "" >> "$TEMP_CRON"

# Daily validation tasks (6:00 AM)
log_info "Adding daily validation tasks..."
echo "# Daily validation - Health check and freshness" >> "$TEMP_CRON"
echo "0 6 * * * cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/monitor-data-health.sh --environment=production >> $PROJECT_ROOT/logs/daily-health.log 2>&1" >> "$TEMP_CRON"
echo "0 6 * * * cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/monitor-data-freshness.sh --threshold=24 >> $PROJECT_ROOT/logs/daily-freshness.log 2>&1" >> "$TEMP_CRON"

# Daily backup (2:00 AM) - already exists, but ensure it's there
if ! grep -q "backup-scheduled.sh" "$TEMP_CRON" 2>/dev/null; then
  log_info "Adding daily backup..."
  echo "# Daily backup at 2 AM" >> "$TEMP_CRON"
  echo "0 2 * * * cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/backup-scheduled.sh --retention=7 >> $PROJECT_ROOT/logs/backup-cron.log 2>&1" >> "$TEMP_CRON"
fi

# Daily quality check (4:00 AM)
log_info "Adding daily quality check..."
echo "# Daily quality check at 4 AM" >> "$TEMP_CRON"
echo "0 4 * * * cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/data-quality-check.sh >> $PROJECT_ROOT/logs/quality-cron.log 2>&1" >> "$TEMP_CRON"

# Health check every 6 hours
log_info "Adding health check every 6 hours..."
echo "# Health check every 6 hours" >> "$TEMP_CRON"
echo "0 */6 * * * cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/monitor-data-health.sh --environment=production >> $PROJECT_ROOT/logs/health-cron.log 2>&1" >> "$TEMP_CRON"

# Weekly comprehensive validation (Sunday 4:00 AM)
log_info "Adding weekly comprehensive validation..."
echo "# Weekly comprehensive validation - Sunday 4 AM" >> "$TEMP_CRON"
echo "0 4 * * 0 cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/validate-all-data.sh --verbose >> $PROJECT_ROOT/logs/weekly-validation.log 2>&1" >> "$TEMP_CRON"
echo "0 4 * * 0 cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/check-integrity.sh --verbose >> $PROJECT_ROOT/logs/weekly-integrity.log 2>&1" >> "$TEMP_CRON"
echo "0 4 * * 0 cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/validate-business-rules.sh >> $PROJECT_ROOT/logs/weekly-business-rules.log 2>&1" >> "$TEMP_CRON"
echo "0 4 * * 0 cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/data-quality-check.sh --verbose >> $PROJECT_ROOT/logs/weekly-quality.log 2>&1" >> "$TEMP_CRON"
echo "0 4 * * 0 cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/detect-data-anomalies.sh --verbose >> $PROJECT_ROOT/logs/weekly-anomalies.log 2>&1" >> "$TEMP_CRON"

# Weekly backup verification (Sunday 1:00 AM)
log_info "Adding weekly backup verification..."
echo "# Weekly backup verification - Sunday 1 AM" >> "$TEMP_CRON"
echo "0 1 * * 0 cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/verify-weekly-backups.sh >> $PROJECT_ROOT/logs/weekly-backup-verify.log 2>&1" >> "$TEMP_CRON"

# Weekly maintenance (Sunday 3:00 AM)
if ! grep -q "data-maintenance.sh --all" "$TEMP_CRON" 2>/dev/null; then
  log_info "Adding weekly maintenance..."
  echo "# Weekly maintenance - Sunday 3 AM" >> "$TEMP_CRON"
  echo "0 3 * * 0 cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/data-maintenance.sh --all >> $PROJECT_ROOT/logs/maintenance-cron.log 2>&1" >> "$TEMP_CRON"
fi

# Weekly monitoring report (Sunday 9:00 AM)
log_info "Adding weekly monitoring report..."
echo "# Weekly monitoring report - Sunday 9 AM" >> "$TEMP_CRON"
echo "0 9 * * 0 cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/generate-weekly-monitoring-report.sh >> $PROJECT_ROOT/logs/weekly-monitoring.log 2>&1" >> "$TEMP_CRON"

# Monthly deep validation (1st of month 2:00 AM)
log_info "Adding monthly deep validation..."
echo "# Monthly deep validation - 1st of month 2 AM" >> "$TEMP_CRON"
echo "0 2 1 * * cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/data-profiling.sh >> $PROJECT_ROOT/logs/monthly-profiling.log 2>&1" >> "$TEMP_CRON"
echo "0 2 1 * * cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/validate-data-consistency.sh --environment=production >> $PROJECT_ROOT/logs/monthly-consistency.log 2>&1" >> "$TEMP_CRON"

# Monthly backup testing (1st of month 3:00 AM)
log_info "Adding monthly backup testing..."
echo "# Monthly backup testing - 1st of month 3 AM" >> "$TEMP_CRON"
echo "0 3 1 * * cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/test-backup-restore.sh >> $PROJECT_ROOT/logs/monthly-restore-test.log 2>&1" >> "$TEMP_CRON"

# Monthly deep maintenance (1st of month 4:00 AM)
log_info "Adding monthly deep maintenance..."
echo "# Monthly deep maintenance - 1st of month 4 AM" >> "$TEMP_CRON"
echo "0 4 1 * * cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/monthly-maintenance.sh >> $PROJECT_ROOT/logs/monthly-maintenance.log 2>&1" >> "$TEMP_CRON"

# Install crontab
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

log_success "Production cron jobs installed successfully!"
echo ""
echo "Installed schedules:"
echo "  Daily:"
echo "    - Backup: 0 2 * * *"
echo "    - Quality check: 0 4 * * *"
echo "    - Health check: 0 6 * * *"
echo "    - Health check (every 6h): 0 */6 * * *"
echo "  Weekly (Sunday):"
echo "    - Backup verification: 0 1 * * 0"
echo "    - Maintenance: 0 3 * * 0"
echo "    - Comprehensive validation: 0 4 * * 0"
echo "    - Monitoring report: 0 9 * * 0"
echo "  Monthly (1st of month):"
echo "    - Deep validation: 0 2 1 * *"
echo "    - Backup testing: 0 3 1 * *"
echo "    - Deep maintenance: 0 4 1 * *"
echo ""
log_info "View cron jobs with: crontab -l"
log_info "Logs will be written to: $PROJECT_ROOT/logs/"

