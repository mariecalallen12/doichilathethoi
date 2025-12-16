#!/bin/bash

# Setup Cron Jobs for Data Management Framework
# This script sets up scheduled tasks for backup, maintenance, and monitoring

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
echo "  Cron Jobs Setup for Data Management"
echo "=========================================="
echo ""

# Create temporary crontab file
TEMP_CRON=$(mktemp)

# Get existing crontab (if any)
crontab -l > "$TEMP_CRON" 2>/dev/null || true

# Check if jobs already exist
if grep -q "backup-scheduled.sh" "$TEMP_CRON" 2>/dev/null; then
  log_warning "Cron jobs already exist. Skipping setup."
  rm "$TEMP_CRON"
  exit 0
fi

# Add cron jobs
log_info "Adding cron jobs..."

# Daily backup at 2 AM
echo "# Daily backup at 2 AM" >> "$TEMP_CRON"
echo "0 2 * * * cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/backup-scheduled.sh >> $PROJECT_ROOT/logs/backup-cron.log 2>&1" >> "$TEMP_CRON"

# Weekly maintenance on Sunday at 3 AM
echo "# Weekly maintenance on Sunday at 3 AM" >> "$TEMP_CRON"
echo "0 3 * * 0 cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/data-maintenance.sh --all >> $PROJECT_ROOT/logs/maintenance-cron.log 2>&1" >> "$TEMP_CRON"

# Daily health check every 6 hours
echo "# Daily health check every 6 hours" >> "$TEMP_CRON"
echo "0 */6 * * * cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/monitor-data-health.sh --environment=production >> $PROJECT_ROOT/logs/health-cron.log 2>&1" >> "$TEMP_CRON"

# Daily quality check at 4 AM
echo "# Daily quality check at 4 AM" >> "$TEMP_CRON"
echo "0 4 * * * cd $PROJECT_ROOT && $PROJECT_ROOT/scripts/data-quality-check.sh >> $PROJECT_ROOT/logs/quality-cron.log 2>&1" >> "$TEMP_CRON"

# Install crontab
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

log_success "Cron jobs installed successfully!"
echo ""
echo "Installed jobs:"
echo "  - Daily backup: 0 2 * * *"
echo "  - Weekly maintenance: 0 3 * * 0"
echo "  - Health check: 0 */6 * * *"
echo "  - Quality check: 0 4 * * *"
echo ""
log_info "View cron jobs with: crontab -l"
log_info "Logs will be written to: $PROJECT_ROOT/logs/"

