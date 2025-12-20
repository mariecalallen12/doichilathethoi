# Workflow Guide - Hoàn thiện nghiệm thu với chế độ debug

**Version**: 1.0.0  
**Last Updated**: 2025-12-16

---

## Overview

Quy trình làm việc có hệ thống để đạt ≥ 90% completion rate và đảm bảo production readiness.

---

## Workflow Steps

### Step 1: Setup và Preparation

```bash
# 1. Tạo test accounts
cd tests/acceptance/scripts
python3 create_test_accounts.py -e local

# 2. Approve test accounts
python3 approve_test_accounts.py -e local

# 3. Verify accounts can login
python3 fix_auth_issues.py -e local
```

**Expected Output**: Test accounts created and approved

---

### Step 2: Run Initial Tests với Debug Mode

```bash
# Run tests with detailed debug
cd tests/acceptance
python3 run_tests_with_auth.py --debug-level detailed

# Results saved to: reports/acceptance/test_results/
```

**Expected Output**: Test results with detailed debugging information

---

### Step 3: Analyze Issues

```bash
# 1. Analyze issues from test results
python3 scripts/analyze_issues.py \
  reports/acceptance/test_results/api_test_results_*.json

# 2. Prioritize issues
python3 scripts/prioritize_issues.py \
  reports/acceptance/issues/issue_report.json

# Output: reports/acceptance/issues/fix_plan.json
```

**Expected Output**: 
- Issue report with categorized issues
- Priority matrix
- Fix plan with estimated effort

---

### Step 4: Fix Issues Systematically

#### 4.1 Fix Authentication Issues

```bash
python3 scripts/fix_auth_issues.py -e local
```

#### 4.2 Fix Missing Endpoints

```bash
# Review and fix missing endpoints
python3 scripts/fix_missing_endpoints.py -u http://localhost:8000

# This will:
# - Identify endpoints that exist with different paths
# - Mark endpoints as not-implemented if needed
# - Update acceptance_config.json
```

#### 4.3 Fix Backend Errors

```bash
# Document backend errors
# Check: reports/acceptance/issues/backend_errors.md
```

---

### Step 5: Validate Fixes

```bash
# 1. Create baseline before fixes
python3 scripts/validate_fixes.py --create-baseline

# 2. Apply fixes
# ... make your fixes ...

# 3. Verify fixes
python3 scripts/validate_fixes.py \
  reports/acceptance/baselines/baseline_*.json \
  -d "Fixed authentication issues"

# 4. Check for regression
# Script will report if pass rate decreased
```

---

### Step 6: Run Quality Gates

```bash
# Run quality gates
python3 scripts/run_quality_gates.py \
  reports/acceptance/test_results/latest.json

# This checks:
# - Completion rate ≥ 90%
# - Critical issues = 0
# - High issues ≤ 5
# - Response times
# - Error rates
```

**Expected Output**: Quality gate report with pass/fail status

---

### Step 7: Continuous Testing

```bash
# Run incremental test (only changed modules)
python3 scripts/continuous_testing.py \
  -t incremental -m auth client

# Run regression test
python3 scripts/continuous_testing.py \
  -t regression -b reports/acceptance/baselines/baseline_*.json
```

---

### Step 8: Production Readiness Validation

```bash
# 1. Load testing
python3 scripts/load_test.py \
  -c 100 -r 10 \
  -e endpoints.json

# 2. Stability testing (24 hours)
python3 scripts/stability_test.py \
  -d 24 -i 60

# 3. Generate production readiness report
python3 scripts/generate_production_readiness_report.py \
  reports/acceptance/test_results/latest.json \
  -q reports/acceptance/quality/quality_gate_report.json \
  -l reports/acceptance/performance/load_test_*.json \
  -s reports/acceptance/performance/stability_test_*.json
```

---

## Complete Workflow Example

```bash
#!/bin/bash
# Complete workflow script

set -e

echo "=== Step 1: Setup ==="
cd tests/acceptance/scripts
python3 create_test_accounts.py -e local
python3 approve_test_accounts.py -e local

echo "=== Step 2: Initial Test ==="
cd ..
python3 run_tests_with_auth.py --debug-level normal

echo "=== Step 3: Analyze Issues ==="
LATEST_RESULTS=$(ls -t reports/acceptance/test_results/api_test_results_*.json | head -1)
python3 scripts/analyze_issues.py "$LATEST_RESULTS"
python3 scripts/prioritize_issues.py reports/acceptance/issues/issue_report.json

echo "=== Step 4: Fix Issues ==="
python3 scripts/fix_auth_issues.py -e local
python3 scripts/fix_missing_endpoints.py

echo "=== Step 5: Re-test ==="
python3 run_tests_with_auth.py --debug-level normal

echo "=== Step 6: Quality Gates ==="
LATEST_RESULTS=$(ls -t reports/acceptance/test_results/api_test_results_*.json | head -1)
python3 scripts/run_quality_gates.py "$LATEST_RESULTS"

echo "=== Step 7: Production Readiness ==="
python3 scripts/generate_production_readiness_report.py \
  "$LATEST_RESULTS" \
  -q reports/acceptance/quality/quality_gate_report.json

echo "=== Complete ==="
```

---

## Debug Mode trong Workflow

### Khi nào dùng Debug Mode?

1. **Initial Testing**: Normal level để xem tổng quan
2. **Issue Investigation**: Detailed level để xem chi tiết
3. **Complex Issues**: Full level với interactive mode
4. **Specific Endpoints**: Dùng `--debug-endpoint` cho endpoint cụ thể

### Debug Commands trong Workflow

```bash
# Debug specific failing endpoint
python3 run_tests_with_auth.py \
  --debug-level full \
  --debug-endpoint /api/financial/deposit

# Debug entire module
python3 run_tests_with_auth.py \
  --debug-level detailed \
  --debug-module auth

# Interactive debugging
python3 run_tests_with_auth.py \
  --debug-level full \
  --interactive \
  --breakpoint /api/auth/login
```

---

## Quality Gates Workflow

```
Test Run
  ↓
Quality Gates Check
  ↓
{Pass?} → Yes → Continue
  ↓ No
Analyze Failures
  ↓
Fix Issues (Debug Mode)
  ↓
Re-test
  ↓
Quality Gates Check
  ↓
{Pass?} → Yes → Continue
  ↓ No
Repeat...
```

---

## Production Readiness Workflow

```
All Fixes Applied
  ↓
Quality Gates Passed
  ↓
Load Testing
  ↓
Stability Testing
  ↓
Generate Readiness Report
  ↓
Risk Assessment
  ↓
{Ready?} → Yes → Deploy
  ↓ No
Address Gaps
  ↓
Re-validate
```

---

## Best Practices

1. **Always Create Baseline**: Before making fixes, create baseline
2. **Fix Systematically**: Follow priority order from fix plan
3. **Validate After Each Fix**: Don't accumulate fixes without validation
4. **Use Debug Mode**: Use appropriate debug level for each step
5. **Document Issues**: Keep track of what was fixed and how
6. **Run Quality Gates**: Always run quality gates before proceeding
7. **Check for Regression**: Ensure fixes don't break existing functionality

---

## Troubleshooting Workflow

### Issue: Tests keep failing

```bash
# 1. Run with full debug
python3 run_tests_with_auth.py --debug-level full

# 2. Analyze errors
python3 scripts/analyze_issues.py <results_file>

# 3. Use error analyzer
python3 -m debug_tools.error_analyzer <results_file>
```

### Issue: Can't reach 90% completion

```bash
# 1. Check what's blocking
python3 scripts/prioritize_issues.py <issue_report>

# 2. Focus on critical issues first
# 3. Fix missing endpoints
python3 scripts/fix_missing_endpoints.py

# 4. Re-run and check progress
```

### Issue: Quality gates failing

```bash
# 1. Check which gates failed
python3 scripts/run_quality_gates.py <results_file>

# 2. Address specific failures
# 3. Re-run quality gates
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Create accounts | `python3 scripts/create_test_accounts.py -e local` |
| Approve accounts | `python3 scripts/approve_test_accounts.py -e local` |
| Run tests | `python3 run_tests_with_auth.py --debug-level normal` |
| Analyze issues | `python3 scripts/analyze_issues.py <results_file>` |
| Prioritize | `python3 scripts/prioritize_issues.py <issue_report>` |
| Fix auth | `python3 scripts/fix_auth_issues.py -e local` |
| Fix endpoints | `python3 scripts/fix_missing_endpoints.py` |
| Quality gates | `python3 scripts/run_quality_gates.py <results_file>` |
| Validate fixes | `python3 scripts/validate_fixes.py <baseline>` |
| Load test | `python3 scripts/load_test.py -c 100` |
| Stability test | `python3 scripts/stability_test.py -d 24` |
| Readiness report | `python3 scripts/generate_production_readiness_report.py <results>` |

---

## Next Steps

Sau khi hoàn thành workflow:

1. Review production readiness report
2. Address any remaining risks
3. Get stakeholder approval
4. Schedule production deployment
5. Execute deployment with monitoring

---

## Support

For issues or questions:
- Check `DEBUG_GUIDE.md` for debug mode details
- Review test results in `reports/acceptance/`
- Check logs in `reports/acceptance/debug/`

