#!/bin/bash

# Weekly Documentation Review Script
# Reviews and updates documentation weekly

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
echo "  Weekly Documentation Review"
echo "=========================================="
echo ""

REPORT_FILE="$PROJECT_ROOT/reports/weekly/documentation_review_$(date +%Y%m%d).md"
mkdir -p "$PROJECT_ROOT/reports/weekly"

log_info "Reviewing documentation files..."

# Check documentation files
DOC_FILES=(
  "$PROJECT_ROOT/DATA_PROCEDURES.md"
  "$PROJECT_ROOT/DATA_OPERATIONS_GUIDE.md"
  "$PROJECT_ROOT/DATA_TROUBLESHOOTING.md"
  "$PROJECT_ROOT/DATA_ALERTING_CONFIG.md"
  "$PROJECT_ROOT/DISASTER_RECOVERY_PLAN.md"
  "$PROJECT_ROOT/DATA_DICTIONARY.md"
)

MISSING_FILES=()
EXISTING_FILES=()

for doc_file in "${DOC_FILES[@]}"; do
  if [ -f "$doc_file" ]; then
    EXISTING_FILES+=("$(basename "$doc_file")")
  else
    MISSING_FILES+=("$(basename "$doc_file")")
  fi
done

# Generate review report
cat > "$REPORT_FILE" << EOF
# Weekly Documentation Review Report

**Date**: $(date)
**Reviewer**: [To be filled]

## Documentation Status

### Existing Documentation Files
$(for file in "${EXISTING_FILES[@]}"; do echo "- ✅ $file"; done)

### Missing Documentation Files
$(if [ ${#MISSING_FILES[@]} -eq 0 ]; then
  echo "- None - All documentation files exist"
else
  for file in "${MISSING_FILES[@]}"; do echo "- ❌ $file"; done
fi)

## Documentation Accuracy Review

### Procedures Documentation
- [ ] DATA_PROCEDURES.md matches actual procedures
- [ ] All procedures are documented
- [ ] Procedures are up to date

### Operations Guide
- [ ] DATA_OPERATIONS_GUIDE.md is accurate
- [ ] All scripts are documented
- [ ] Examples are correct

### Troubleshooting Guide
- [ ] DATA_TROUBLESHOOTING.md covers common issues
- [ ] Solutions are tested and accurate
- [ ] New issues documented

## Lessons Learned This Week

### New Procedures Discovered
1. 
2. 
3. 

### Issues Encountered
1. 
2. 
3. 

### Solutions Applied
1. 
2. 
3. 

## Documentation Updates Needed

### Files to Update
- [ ] DATA_PROCEDURES.md
- [ ] DATA_OPERATIONS_GUIDE.md
- [ ] DATA_TROUBLESHOOTING.md
- [ ] DATA_DICTIONARY.md (if schema changes)

### Update Details
- 
- 
- 

## Recommendations

1. 
2. 
3. 

## Next Steps

- Update documentation based on findings
- Document new procedures discovered
- Review documentation next week

EOF

log_success "Weekly documentation review template generated!"
log_info "Report: $REPORT_FILE"
log_info "Please review and update documentation as needed."

