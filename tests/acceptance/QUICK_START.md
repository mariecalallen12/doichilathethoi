# Quick Start Guide - Acceptance Testing với Debug Mode

## Bước 1: Setup Test Accounts

```bash
cd tests/acceptance/scripts
python3 create_test_accounts.py -e local
python3 approve_test_accounts.py -e local
```

## Bước 2: Chạy Tests với Debug

```bash
cd tests/acceptance
python3 run_tests_with_auth.py --debug-level normal
```

## Bước 3: Phân tích Issues

```bash
# Tìm file results mới nhất
LATEST=$(ls -t reports/acceptance/test_results/api_test_results_*.json | head -1)

# Phân tích
python3 scripts/analyze_issues.py "$LATEST"
python3 scripts/prioritize_issues.py reports/acceptance/issues/issue_report.json
```

## Bước 4: Fix Issues

```bash
# Fix authentication
python3 scripts/fix_auth_issues.py -e local

# Fix missing endpoints
python3 scripts/fix_missing_endpoints.py
```

## Bước 5: Quality Gates

```bash
LATEST=$(ls -t reports/acceptance/test_results/api_test_results_*.json | head -1)
python3 scripts/run_quality_gates.py "$LATEST"
```

## Bước 6: Production Readiness

```bash
# Load test
python3 scripts/load_test.py -c 50 -r 5

# Generate report
LATEST=$(ls -t reports/acceptance/test_results/api_test_results_*.json | head -1)
python3 scripts/generate_production_readiness_report.py "$LATEST"
```

## Debug Commands

```bash
# Debug specific endpoint
python3 run_tests_with_auth.py --debug-level detailed --debug-endpoint /api/client/dashboard

# Interactive debugging
python3 run_tests_with_auth.py --debug-level full --interactive
```

Xem thêm:
- `DEBUG_GUIDE.md` - Hướng dẫn debug mode chi tiết
- `WORKFLOW_GUIDE.md` - Quy trình làm việc đầy đủ
