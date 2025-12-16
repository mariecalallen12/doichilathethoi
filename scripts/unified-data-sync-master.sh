#!/bin/bash
# Master script để chạy toàn bộ quy trình đồng bộ hóa dữ liệu tự động

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPORT_DIR="$PROJECT_ROOT/reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$REPORT_DIR/unified_sync_${TIMESTAMP}.log"

mkdir -p "$REPORT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Parse arguments
ENVIRONMENTS="${1:-dev,staging,prod}"
MASTER_ENV="${2:-}"
CONFLICT_STRATEGY="${3:-master_wins}"

log "=========================================="
log "UNIFIED DATA SYNC MASTER SCRIPT"
log "=========================================="
log "Environments: $ENVIRONMENTS"
log "Master: $MASTER_ENV"
log "Strategy: $CONFLICT_STRATEGY"
log ""

# Step 1: Audit data
log "Step 1: Auditing data..."
"$SCRIPT_DIR/data-audit-comprehensive.sh" || {
    error "Data audit failed"
    exit 1
}

# Step 2: Compare schemas
log "Step 2: Comparing schemas..."
python3 "$SCRIPT_DIR/schema-comparison.py" --environments $(echo $ENVIRONMENTS | tr ',' ' ') --compare-all || {
    error "Schema comparison failed"
    exit 1
}

# Step 3: Analyze data
log "Step 3: Analyzing data..."
python3 "$SCRIPT_DIR/data-analysis-comprehensive.py" --environments $(echo $ENVIRONMENTS | tr ',' ' ') --compare || {
    error "Data analysis failed"
    exit 1
}

# Step 4: Determine master
if [ -z "$MASTER_ENV" ]; then
    log "Step 4: Determining master database..."
    "$SCRIPT_DIR/determine-master-db.sh" || {
        error "Master determination failed"
        exit 1
    }
    
    if [ -f "$REPORT_DIR/master_env.txt" ]; then
        MASTER_ENV=$(cat "$REPORT_DIR/master_env.txt")
        log "Master environment determined: $MASTER_ENV"
    else
        error "Could not determine master environment"
        exit 1
    fi
else
    log "Step 4: Using provided master: $MASTER_ENV"
fi

# Step 5: Run migration
log "Step 5: Running schema unification migration..."
cd "$PROJECT_ROOT/backend"
alembic upgrade head || {
    error "Migration failed"
    exit 1
}
cd "$PROJECT_ROOT"

# Step 6: Validate schema
log "Step 6: Validating schema..."
python3 "$SCRIPT_DIR/validate-schema-unified.py" --environments $(echo $ENVIRONMENTS | tr ',' ' ') || {
    error "Schema validation failed"
    exit 1
}

# Step 7: Sync data
log "Step 7: Syncing data..."
TARGET_ENVS=$(echo $ENVIRONMENTS | tr ',' '\n' | grep -v "^$MASTER_ENV$" | tr '\n' ' ')
if [ -n "$TARGET_ENVS" ]; then
    python3 "$SCRIPT_DIR/data-sync-unified.py" \
        --master "$MASTER_ENV" \
        --targets $TARGET_ENVS \
        --strategy "$CONFLICT_STRATEGY" || {
        error "Data sync failed"
        exit 1
    }
else
    warning "No target environments to sync"
fi

# Step 8: Cleanup
log "Step 8: Cleaning up data..."
"$SCRIPT_DIR/data-cleanup-unified.sh" || {
    warning "Cleanup had issues (non-critical)"
}

# Step 9: Final validation
log "Step 9: Final validation..."
python3 "$SCRIPT_DIR/validate-schema-unified.py" --environments $(echo $ENVIRONMENTS | tr ',' ' ') || {
    error "Final validation failed"
    exit 1
}

log ""
log "=========================================="
log "✅ UNIFIED DATA SYNC COMPLETED SUCCESSFULLY"
log "=========================================="
log "Log file: $LOG_FILE"
log "Reports: $REPORT_DIR"

