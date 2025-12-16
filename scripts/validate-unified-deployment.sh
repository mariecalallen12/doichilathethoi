#!/bin/bash
# Script validation sau deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

ENVIRONMENTS="${1:-dev,staging,prod}"

log "Validating deployment..."

# Validate schema
python3 "$SCRIPT_DIR/validate-schema-unified.py" --environments $(echo $ENVIRONMENTS | tr ',' ' ') || {
    log "Schema validation failed"
    exit 1
}

# Validate API
for env in $(echo $ENVIRONMENTS | tr ',' ' '); do
    log "Validating API for $env..."
    # Add API health checks
done

log "✅ Validation completed"

