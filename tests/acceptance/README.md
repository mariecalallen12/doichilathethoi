# Acceptance Testing Framework

Hệ thống nghiệm thu tổng thể để đánh giá mức độ hoàn thiện của dự án.

## Cấu Trúc Thư Mục

```
tests/acceptance/
├── README.md                          # File này
├── ACCEPTANCE_TESTING_GUIDE.md        # Hướng dẫn chi tiết
├── acceptance_config.json             # Cấu hình môi trường và scoring
├── acceptance_test_framework.py      # Framework testing tự động
├── api_validator.py                   # API validation utilities
├── scoring_calculator.py              # Tính toán completion percentage
├── generate_acceptance_report.py     # Generate reports
├── checklists/                        # Manual testing checklists
│   ├── client_checklist.md
│   ├── admin_checklist.md
│   └── api_checklist.md
├── report_templates/                  # Report templates
│   ├── report_template.md
│   ├── report_template.html
│   └── report_schema.json
├── test_data/                         # Test data và accounts
│   └── test_accounts.json
└── utils/                             # Utilities (nếu cần)
```

## Quick Start

### 1. Chạy Automated Tests

```bash
# Sử dụng script tự động (khuyến nghị)
./scripts/run_acceptance_tests.sh

# Hoặc chỉ định môi trường
./scripts/run_acceptance_tests.sh -e staging
```

### 2. Manual Testing

Sử dụng các checklists trong thư mục `checklists/`:
- `client_checklist.md` - Kiểm tra giao diện client
- `admin_checklist.md` - Kiểm tra giao diện admin
- `api_checklist.md` - Kiểm tra API endpoints

### 3. Generate Reports

```bash
cd tests/acceptance
python3 generate_acceptance_report.py <results_file> [output_prefix]
```

Reports sẽ được tạo trong `reports/acceptance/`:
- Markdown (`.md`)
- HTML (`.html`) - Mở trực tiếp trong browser
- JSON (`.json`) - Machine-readable

## Tài Liệu

- **Hướng dẫn chi tiết**: Xem `ACCEPTANCE_TESTING_GUIDE.md`
- **Configuration**: Xem `acceptance_config.json`
- **Checklists**: Xem thư mục `checklists/`

## Scoring System

**Weighted Scoring:**
- Client Interface: 35%
- Admin Interface: 25%
- API Functionality: 25%
- Data Integrity: 15%

**Pass Criteria:**
- Individual module: ≥80% pass rate
- Overall completion: ≥85% for production readiness

## Output

Sau khi chạy nghiệm thu, reports được lưu tại:
- `reports/acceptance/` - Main reports
- `reports/acceptance/test_results/` - Detailed test results
- `reports/acceptance/screenshots/` - Screenshots (nếu có)

## Hỗ Trợ

Xem `ACCEPTANCE_TESTING_GUIDE.md` để biết thêm chi tiết và troubleshooting.

