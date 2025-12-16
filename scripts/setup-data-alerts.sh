#!/bin/bash

# Data Alerting Setup Script
# Setup data consistency and quality alerts
#
# Usage:
#   ./scripts/setup-data-alerts.sh [--email=<email>]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

EMAIL=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --email=*)
      EMAIL="${1#*=}"
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

create_alert_config() {
  log_info "Creating alert configuration..."
  
  cat > "$PROJECT_ROOT/data-alerting-config.json" <<EOF
{
  "alerts": [
    {
      "name": "Data Consistency Failure",
      "condition": "data_consistency_check_failed",
      "severity": "critical",
      "notification": {
        "email": "${EMAIL:-admin@example.com}",
        "enabled": true
      }
    },
    {
      "name": "Data Quality Degradation",
      "condition": "data_quality_score < 0.9",
      "severity": "warning",
      "notification": {
        "email": "${EMAIL:-admin@example.com}",
        "enabled": true
      }
    },
    {
      "name": "Backup Failure",
      "condition": "backup_failed",
      "severity": "critical",
      "notification": {
        "email": "${EMAIL:-admin@example.com}",
        "enabled": true
      }
    },
    {
      "name": "Data Integrity Issues",
      "condition": "integrity_issues_detected",
      "severity": "warning",
      "notification": {
        "email": "${EMAIL:-admin@example.com}",
        "enabled": true
      }
    }
  ]
}
EOF
  
  log_success "Alert configuration created"
}

setup_cron_alerts() {
  log_info "Setting up cron-based alert checks..."
  
  local cron_job="*/30 * * * * cd $PROJECT_ROOT && ./scripts/monitor-data-health.sh >> /var/log/data-health.log 2>&1"
  
  if crontab -l 2>/dev/null | grep -q "monitor-data-health.sh"; then
    log_info "Data health monitoring cron already exists"
  else
    (crontab -l 2>/dev/null; echo "$cron_job") | crontab -
    log_success "Data health monitoring cron added"
  fi
}

main() {
  echo "=========================================="
  echo "  Data Alerting Setup"
  echo "=========================================="
  echo ""
  
  create_alert_config
  setup_cron_alerts
  
  echo ""
  echo "=========================================="
  log_success "Data alerting setup completed!"
  echo "=========================================="
  echo ""
  echo "Next steps:"
  echo "1. Review data-alerting-config.json"
  echo "2. Configure email notifications"
  echo "3. Test alert system"
}

main "$@"

