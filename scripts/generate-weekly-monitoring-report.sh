#!/bin/bash

# Weekly Monitoring Report Generation Script
# Aggregates monitoring data from the week and generates summary report

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

echo "=========================================="
echo "  Weekly Monitoring Report Generation"
echo "=========================================="
echo ""

REPORT_FILE="$PROJECT_ROOT/reports/weekly/weekly_monitoring_$(date +%Y%m%d).md"
mkdir -p "$PROJECT_ROOT/reports/weekly"

log_info "Aggregating monitoring data from the past week..."

# Collect health reports from the week
HEALTH_REPORTS=$(find "$PROJECT_ROOT" -name "DATA_HEALTH_REPORT_*.md" -mtime -7 2>/dev/null | head -5)
CONSISTENCY_REPORTS=$(find "$PROJECT_ROOT" -name "DATA_CONSISTENCY_REPORT_*.md" -mtime -7 2>/dev/null | head -5)

# Get log file stats
HEALTH_LOG="$PROJECT_ROOT/logs/health-cron.log"
BACKUP_LOG="$PROJECT_ROOT/logs/backup-cron.log"
QUALITY_LOG="$PROJECT_ROOT/logs/quality-cron.log"

# Generate report
cat > "$REPORT_FILE" << EOF
# Weekly Monitoring Summary Report

**Date**: $(date)
**Period**: Past 7 days

## Overview

This report summarizes monitoring activities and metrics from the past week.

## Health Monitoring

### Health Checks
$(if [ -f "$HEALTH_LOG" ]; then
  echo "- Total health checks: $(grep -c "Data health" "$HEALTH_LOG" 2>/dev/null || echo "0")"
  echo "- Successful checks: $(grep -c "passed" "$HEALTH_LOG" 2>/dev/null || echo "0")"
  echo "- Failed checks: $(grep -c "failed\|ERROR" "$HEALTH_LOG" 2>/dev/null || echo "0")"
else
  echo "- Health log not found"
fi)

### Recent Health Reports
$(if [ -n "$HEALTH_REPORTS" ]; then
  for report in $HEALTH_REPORTS; do
    echo "- $(basename "$report")"
  done
else
  echo "- No health reports found"
fi)

## Backup Monitoring

### Backup Status
$(if [ -f "$BACKUP_LOG" ]; then
  echo "- Total backups: $(grep -c "Backup completed" "$BACKUP_LOG" 2>/dev/null || echo "0")"
  echo "- Failed backups: $(grep -c "failed\|ERROR" "$BACKUP_LOG" 2>/dev/null || echo "0")"
else
  echo "- Backup log not found"
fi)

## Quality Monitoring

### Quality Checks
$(if [ -f "$QUALITY_LOG" ]; then
  echo "- Total quality checks: $(grep -c "Data quality" "$QUALITY_LOG" 2>/dev/null || echo "0")"
  echo "- Issues found: $(grep -c "issues\|failed" "$QUALITY_LOG" 2>/dev/null || echo "0")"
else
  echo "- Quality log not found"
fi)

## Consistency Monitoring

### Consistency Reports
$(if [ -n "$CONSISTENCY_REPORTS" ]; then
  for report in $CONSISTENCY_REPORTS; do
    echo "- $(basename "$report")"
  done
else
  echo "- No consistency reports found"
fi)

## Trends and Patterns

### Key Observations
- Review individual reports for detailed analysis
- Check for recurring issues or patterns
- Monitor performance trends

## Recommendations

1. Review any failed checks or issues
2. Investigate patterns in monitoring data
3. Adjust thresholds if needed
4. Update monitoring procedures based on findings

## Next Steps

- Continue daily monitoring
- Address any identified issues
- Review alert thresholds monthly

EOF

log_success "Weekly monitoring report generated!"
log_info "Report: $REPORT_FILE"

