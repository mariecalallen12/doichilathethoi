#!/bin/bash

# Alert Configuration Update Script
# Updates alert thresholds and configuration

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

EMAIL="${1:-ops@digitalutopia.com}"

echo "=========================================="
echo "  Alert Configuration Update"
echo "=========================================="
echo ""

log_info "Updating alert configuration..."
log_info "Email: $EMAIL"

# Update alert configuration
if [ -f "$PROJECT_ROOT/scripts/setup-data-alerts.sh" ]; then
  "$PROJECT_ROOT/scripts/setup-data-alerts.sh" --email="$EMAIL" 2>&1 | tail -10
fi

log_info "Reviewing current alert configuration..."

# Display current config
if [ -f "$PROJECT_ROOT/DATA_ALERTING_CONFIG.md" ]; then
  log_info "Current alert configuration:"
  echo ""
  cat "$PROJECT_ROOT/DATA_ALERTING_CONFIG.md" | head -50
  echo ""
fi

log_success "Alert configuration update completed!"
log_info "Review DATA_ALERTING_CONFIG.md for details"
log_info "Test alerts to ensure they are working correctly"

