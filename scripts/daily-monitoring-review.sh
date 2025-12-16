#!/bin/bash

# Daily Monitoring Review Script
# Manual review script for daily monitoring dashboard

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
echo "  Daily Monitoring Review"
echo "=========================================="
echo ""

REPORT_FILE="$PROJECT_ROOT/reports/daily/daily_monitoring_$(date +%Y%m%d).md"
mkdir -p "$PROJECT_ROOT/reports/daily"

log_info "Reviewing monitoring dashboard and alerts..."

# Check monitoring dashboard config
DASHBOARD_CONFIG="$PROJECT_ROOT/monitoring-dashboard.json"
ALERT_CONFIG="$PROJECT_ROOT/DATA_ALERTING_CONFIG.md"

# Get recent alerts from logs
HEALTH_LOG="$PROJECT_ROOT/logs/health-cron.log"
BACKUP_LOG="$PROJECT_ROOT/logs/backup-cron.log"
QUALITY_LOG="$PROJECT_ROOT/logs/quality-cron.log"

# Generate daily review report
cat > "$REPORT_FILE" << EOF
# Daily Monitoring Review Report

**Date**: $(date)
**Reviewer**: [To be filled]

## Monitoring Dashboard Review

### Dashboard Status
- Dashboard config: $([ -f "$DASHBOARD_CONFIG" ] && echo "✅ Available" || echo "❌ Not found")
- Alert config: $([ -f "$ALERT_CONFIG" ] && echo "✅ Available" || echo "❌ Not found")

### Alert Notifications Review

#### Health Check Alerts
$(if [ -f "$HEALTH_LOG" ]; then
  echo "- Recent health check issues:"
  grep -i "error\|failed\|warning" "$HEALTH_LOG" 2>/dev/null | tail -5 | sed 's/^/  - /' || echo "  - No issues found"
else
  echo "- Health log not available"
fi)

#### Backup Alerts
$(if [ -f "$BACKUP_LOG" ]; then
  echo "- Recent backup issues:"
  grep -i "error\|failed\|warning" "$BACKUP_LOG" 2>/dev/null | tail -5 | sed 's/^/  - /' || echo "  - No issues found"
else
  echo "- Backup log not available"
fi)

#### Quality Alerts
$(if [ -f "$QUALITY_LOG" ]; then
  echo "- Recent quality issues:"
  grep -i "error\|failed\|warning\|issues" "$QUALITY_LOG" 2>/dev/null | tail -5 | sed 's/^/  - /' || echo "  - No issues found"
else
  echo "- Quality log not available"
fi)

## Data Health Metrics

### Current Status
- Review latest health report: \`DATA_HEALTH_REPORT_*.md\`
- Check data freshness metrics
- Review consistency reports

## Performance Metrics

### Key Metrics to Review
- Database performance
- Query response times
- Cache hit rates
- System resource usage

## Anomalies Detected

### Issues Found
- [ ] No anomalies
- [ ] Issues detected (document below)

### Action Items
1. 
2. 
3. 

## Notes

- Review monitoring dashboard: \`monitoring-dashboard.json\`
- Check alert thresholds: \`DATA_ALERTING_CONFIG.md\`
- Follow escalation procedures if critical issues found

## Next Steps

- Address any identified issues
- Update monitoring thresholds if needed
- Document lessons learned

EOF

log_success "Daily monitoring review template generated!"
log_info "Report: $REPORT_FILE"
log_info "Please review and fill in the details manually."

