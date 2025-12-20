#!/bin/bash
# Execute Complete Acceptance Testing Workflow
# Automated workflow to achieve ≥ 90% completion rate

set -e

WORKFLOW_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="$WORKFLOW_DIR/scripts"
REPORTS_DIR="$WORKFLOW_DIR/../reports/acceptance"

echo "=================================================================================="
echo "ACCEPTANCE TESTING WORKFLOW - Automated Execution"
echo "=================================================================================="
echo ""

# Step 1: Setup Test Accounts
echo "STEP 1: Setting up test accounts..."
cd "$SCRIPTS_DIR"
python3 create_test_accounts.py -e local || echo "⚠️  Account creation had issues, continuing..."
python3 approve_test_accounts.py -e local || echo "⚠️  Account approval had issues, continuing..."
echo "✅ Step 1 completed"
echo ""

# Step 2: Run Acceptance Tests
echo "STEP 2: Running acceptance tests..."
cd "$WORKFLOW_DIR"
python3 run_tests_with_auth.py

# Find latest results file
LATEST_RESULTS=$(ls -t "$REPORTS_DIR/test_results/api_test_results_"*.json 2>/dev/null | head -1)

if [ -z "$LATEST_RESULTS" ]; then
    echo "❌ No test results found!"
    exit 1
fi

echo "✅ Step 2 completed - Results: $LATEST_RESULTS"
echo ""

# Step 3: Analyze Issues
echo "STEP 3: Analyzing issues..."
cd "$WORKFLOW_DIR"
python3 scripts/analyze_issues.py "$LATEST_RESULTS" || echo "⚠️  Issue analysis had problems"

if [ -f "$REPORTS_DIR/issues/issue_report.json" ]; then
    python3 scripts/prioritize_issues.py "$REPORTS_DIR/issues/issue_report.json" || echo "⚠️  Issue prioritization had problems"
fi

echo "✅ Step 3 completed"
echo ""

# Step 4: Fix Issues
echo "STEP 4: Fixing issues..."
cd "$SCRIPTS_DIR"
python3 fix_auth_issues.py -e local || echo "⚠️  Auth fixes had issues"
python3 fix_missing_endpoints.py || echo "⚠️  Endpoint fixes had issues"
echo "✅ Step 4 completed"
echo ""

# Step 5: Re-run Tests
echo "STEP 5: Re-running tests after fixes..."
cd "$WORKFLOW_DIR"
python3 run_tests_with_auth.py

# Find new latest results
NEW_LATEST_RESULTS=$(ls -t "$REPORTS_DIR/test_results/api_test_results_"*.json 2>/dev/null | head -1)
echo "✅ Step 5 completed - New Results: $NEW_LATEST_RESULTS"
echo ""

# Step 6: Quality Gates
echo "STEP 6: Running quality gates..."
cd "$WORKFLOW_DIR"
if [ -n "$NEW_LATEST_RESULTS" ]; then
    python3 scripts/run_quality_gates.py "$NEW_LATEST_RESULTS" || echo "⚠️  Quality gates check had issues"
fi
echo "✅ Step 6 completed"
echo ""

# Step 7: Generate Report
echo "STEP 7: Generating acceptance report..."
cd "$WORKFLOW_DIR"
if [ -n "$NEW_LATEST_RESULTS" ]; then
    python3 generate_acceptance_report.py "$NEW_LATEST_RESULTS" || echo "⚠️  Report generation had issues"
fi
echo "✅ Step 7 completed"
echo ""

echo "=================================================================================="
echo "WORKFLOW COMPLETED"
echo "=================================================================================="
echo ""
echo "📊 Results Summary:"
echo "  Latest results: $NEW_LATEST_RESULTS"
echo "  Reports: $REPORTS_DIR/"
echo ""
echo "Next steps:"
echo "  1. Review acceptance report"
echo "  2. Check quality gate results"
echo "  3. Address any remaining issues"
echo "  4. Run production readiness checks if quality gates pass"
echo ""

