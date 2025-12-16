#!/bin/bash

# Monthly Documentation Audit Script
# Comprehensive documentation audit

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

echo "=========================================="
echo "  Monthly Documentation Audit"
echo "=========================================="
echo ""

REPORT_FILE="$PROJECT_ROOT/reports/monthly/documentation_audit_$(date +%Y%m%d).md"
mkdir -p "$PROJECT_ROOT/reports/monthly"

log_info "Auditing documentation completeness..."

# Count scripts
SCRIPT_COUNT=$(find "$PROJECT_ROOT/scripts" -name "*.sh" -type f 2>/dev/null | wc -l)

# Count documented scripts
DOCUMENTED_SCRIPTS=0
if [ -f "$PROJECT_ROOT/DATA_OPERATIONS_GUIDE.md" ]; then
  DOCUMENTED_SCRIPTS=$(grep -c "\.sh" "$PROJECT_ROOT/DATA_OPERATIONS_GUIDE.md" 2>/dev/null || echo "0")
fi

# Check for schema changes
SCHEMA_CHANGED=false
if [ -f "$PROJECT_ROOT/DATA_DICTIONARY.md" ]; then
  LAST_MODIFIED=$(stat -c %Y "$PROJECT_ROOT/DATA_DICTIONARY.md" 2>/dev/null || echo "0")
  # Check if modified in last 30 days
  if [ $(( $(date +%s) - LAST_MODIFIED )) -lt 2592000 ]; then
    SCHEMA_CHANGED=true
  fi
fi

# Generate audit report
cat > "$REPORT_FILE" << EOF
# Monthly Documentation Audit Report

**Date**: $(date)
**Auditor**: [To be filled]

## Documentation Completeness

### Scripts Documentation
- Total scripts: $SCRIPT_COUNT
- Documented scripts: $DOCUMENTED_SCRIPTS
- Coverage: $(( DOCUMENTED_SCRIPTS * 100 / SCRIPT_COUNT ))% (if > 0)

### Procedures Documentation
- [ ] All daily procedures documented
- [ ] All weekly procedures documented
- [ ] All monthly procedures documented
- [ ] Pre-deployment procedures documented
- [ ] Post-deployment procedures documented
- [ ] Backup procedures documented
- [ ] Recovery procedures documented
- [ ] Maintenance procedures documented

### Reports Documentation
- [ ] All report types documented
- [ ] Report locations documented
- [ ] Report interpretation guide available

## Documentation Accuracy

### Procedures Match Operations
- [ ] Procedures match actual operations
- [ ] Script paths are correct
- [ ] Examples are accurate
- [ ] Troubleshooting solutions tested

### Schema Documentation
- Schema changes detected: $([ "$SCHEMA_CHANGED" = true ] && echo "Yes" || echo "No")
- [ ] DATA_DICTIONARY.md updated if schema changed
- [ ] All tables documented
- [ ] All relationships documented

## Documentation Quality

### Completeness Score
- Procedures: [ ] Complete [ ] Needs updates
- Operations: [ ] Complete [ ] Needs updates
- Troubleshooting: [ ] Complete [ ] Needs updates
- Dictionary: [ ] Complete [ ] Needs updates

### Recommendations
1. 
2. 
3. 

## Action Items

### Immediate Updates Needed
- 
- 
- 

### Future Improvements
- 
- 
- 

## Next Audit

Scheduled for: $(date -d "+1 month" +%Y-%m-%d)

EOF

log_success "Monthly documentation audit completed!"
log_info "Report: $REPORT_FILE"
log_info "Review and update documentation based on audit findings."

