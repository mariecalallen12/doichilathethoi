# Hướng Dẫn Nghiệm Thu Tổng Thể

**Phiên bản**: 1.0  
**Ngày cập nhật**: 2025-01-XX

---

## Mục Lục

1. [Giới Thiệu](#giới-thiệu)
2. [Tổng Quan Quy Trình](#tổng-quan-quy-trình)
3. [Chuẩn Bị](#chuẩn-bị)
4. [Chạy Nghiệm Thu Tự Động](#chạy-nghiệm-thu-tự-động)
5. [Nghiệm Thu Thủ Công](#nghiệm-thu-thủ-công)
6. [Tạo Báo Cáo](#tạo-báo-cáo)
7. [Đánh Giá Kết Quả](#đánh-giá-kết-quả)
8. [Xử Lý Vấn Đề](#xử-lý-vấn-đề)
9. [FAQ](#faq)

---

## Giới Thiệu

Quy trình nghiệm thu tổng thể được thiết kế để đánh giá toàn diện mức độ hoàn thiện của dự án thông qua:

- **Kiểm tra giao diện Client**: Tất cả các trang và chức năng cho người dùng cuối
- **Kiểm tra giao diện Admin**: Tất cả các trang và chức năng quản trị
- **Kiểm tra API**: Xác thực 72 endpoints và tính toàn vẹn dữ liệu
- **Báo cáo tự động**: Tạo báo cáo ở nhiều định dạng (Markdown, HTML, JSON)

---

## Tổng Quan Quy Trình

### Quy Trình Nghiệm Thu

```
1. Chuẩn Bị
   ├── Cấu hình môi trường
   ├── Chuẩn bị test data
   └── Verify services đang chạy

2. API Testing (Tự động)
   ├── Test tất cả endpoints
   ├── Validate response schemas
   └── Performance testing

3. Client Interface Testing (Thủ công + Tự động)
   ├── Navigate tất cả routes
   ├── Test authentication flows
   └── Validate UI/UX

4. Admin Interface Testing (Thủ công + Tự động)
   ├── Navigate tất cả routes
   ├── Test admin features
   └── Validate permissions

5. Data Validation
   ├── Cross-reference frontend-backend
   └── Verify data accuracy

6. Report Generation
   ├── Aggregate results
   ├── Calculate scores
   └── Generate reports
```

### Scoring System

**Weighted Scoring:**
- Client Interface: 35%
- Admin Interface: 25%
- API Functionality: 25%
- Data Integrity: 15%

**Pass Criteria:**
- Individual module: ≥80% pass rate
- Overall completion: ≥85% for production readiness

---

## Chuẩn Bị

### 1. Kiểm Tra Môi Trường

Đảm bảo các services đang chạy:

```bash
# Check backend API
curl http://localhost:8000/api/health

# Check client app
curl http://localhost:3002

# Check admin app
curl http://localhost:3001
```

### 2. Cấu Hình Môi Trường

Chỉnh sửa `tests/acceptance/acceptance_config.json` nếu cần:

```json
{
  "environments": {
    "local": {
      "client_url": "http://localhost:3002",
      "admin_url": "http://localhost:3001",
      "api_url": "http://localhost:8000"
    }
  }
}
```

### 3. Chuẩn Bị Test Accounts

Test accounts được lưu trong `tests/acceptance/test_data/test_accounts.json`.

**Lưu ý**: Đảm bảo các test accounts đã được tạo trong database trước khi chạy tests.

---

## Chạy Nghiệm Thu Tự Động

### Cách 1: Sử Dụng Script Tự Động (Khuyến Nghị)

```bash
# Chạy toàn bộ quy trình
./scripts/run_acceptance_tests.sh

# Chỉ định môi trường
./scripts/run_acceptance_tests.sh -e staging

# Chỉ định output prefix
./scripts/run_acceptance_tests.sh -o my_report

# Bỏ qua API tests (chỉ manual)
./scripts/run_acceptance_tests.sh --skip-api
```

### Cách 2: Chạy Từng Bước Thủ Công

#### Bước 1: Chạy API Tests

```bash
cd tests/acceptance
python3 acceptance_test_framework.py
```

Hoặc sử dụng framework trực tiếp:

```python
from acceptance_test_framework import AcceptanceTestFramework

framework = AcceptanceTestFramework(environment="local")
framework.test_all_api_endpoints()
framework.save_results("results.json")
```

#### Bước 2: Generate Reports

```bash
python3 generate_acceptance_report.py results.json
```

---

## Nghiệm Thu Thủ Công

### Sử Dụng Checklists

1. **Client Checklist**: `tests/acceptance/checklists/client_checklist.md`
   - Đánh dấu từng test case: ✅ Pass, ❌ Fail, hoặc ⚪ N/A
   - Ghi chú các vấn đề phát hiện
   - Chụp screenshot cho các lỗi critical

2. **Admin Checklist**: `tests/acceptance/checklists/admin_checklist.md`
   - Tương tự như client checklist
   - Tập trung vào các chức năng quản trị

3. **API Checklist**: `tests/acceptance/checklists/api_checklist.md`
   - Kiểm tra từng endpoint
   - Verify response structure
   - Check error handling

### Quy Trình Kiểm Tra

1. **Mở checklist** tương ứng
2. **Truy cập từng route/page** theo thứ tự
3. **Thực hiện các test cases** được liệt kê
4. **Đánh dấu kết quả** trong checklist
5. **Ghi chú** các vấn đề phát hiện
6. **Chụp screenshot** cho các lỗi quan trọng

### Ví Dụ: Kiểm Tra Client Login

1. Truy cập `http://localhost:3002/login`
2. Kiểm tra form hiển thị đúng
3. Thử login với credentials hợp lệ
4. Verify redirect sau khi login
5. Kiểm tra token được lưu trong localStorage
6. Đánh dấu kết quả trong checklist

---

## Tạo Báo Cáo

### Tự Động Generate Reports

Sau khi có test results:

```bash
cd tests/acceptance
python3 generate_acceptance_report.py <results_file> [output_prefix]
```

Reports sẽ được tạo trong `reports/acceptance/`:
- `{prefix}.md` - Markdown report
- `{prefix}.html` - HTML report (có thể mở trực tiếp trong browser)
- `{prefix}.json` - JSON report (machine-readable)

### Cấu Trúc Báo Cáo

Báo cáo bao gồm:

1. **Tóm Tắt Điều Hành**
   - Overall completion percentage
   - Tổng số tests, passed, failed
   - Phân loại lỗi theo severity

2. **Kết Quả Chi Tiết**
   - Client Interface results
   - Admin Interface results
   - API Functionality results
   - Data Integrity results

3. **Phân Tích**
   - Critical issues
   - High priority issues
   - Medium/Low priority issues

4. **Đề Xuất**
   - Các vấn đề cần khắc phục ngay
   - Cải tiến đề xuất
   - Hướng dẫn khắc phục

5. **Kết Luận**
   - Đánh giá tổng thể
   - Quyết định nghiệm thu
   - Next steps

---

## Đánh Giá Kết Quả

### Tiêu Chí Đánh Giá

**PASS (Sẵn sàng cho Production):**
- Overall completion ≥ 85%
- Không có critical issues
- High priority issues ≤ 5
- Tất cả modules ≥ 80% pass rate

**FAIL (Cần khắc phục):**
- Overall completion < 85%
- Có critical issues
- Nhiều high priority issues

**WARNING (Có thể release với giới hạn):**
- Overall completion 70-85%
- Không có critical issues
- Một số high priority issues

### Phân Loại Lỗi

**Critical:**
- Application crashes
- Data loss
- Security vulnerabilities
- Không thể hoàn thành core workflows

**High:**
- Major feature không hoạt động
- Performance issues nghiêm trọng
- Data display errors
- Có workaround nhưng bất tiện

**Medium:**
- Minor feature issues
- UI/UX problems
- Non-critical errors
- Có workaround dễ dàng

**Low:**
- Cosmetic issues
- Minor text errors
- Enhancement suggestions

---

## Xử Lý Vấn Đề

### Vấn Đề Thường Gặp

#### 1. API Không Accessible

**Triệu chứng**: API tests fail với connection errors

**Giải pháp**:
```bash
# Check backend service
docker-compose ps backend

# Check logs
docker-compose logs backend

# Restart service
docker-compose restart backend
```

#### 2. Authentication Failures

**Triệu chứng**: Tests fail với 401 errors

**Giải pháp**:
- Verify test accounts exist in database
- Check credentials in `test_data/test_accounts.json`
- Ensure JWT tokens are valid

#### 3. Frontend Không Load

**Triệu chứng**: Page tests fail

**Giải pháp**:
```bash
# Check client app
docker-compose ps client-app

# Check logs
docker-compose logs client-app

# Verify environment variables
cat client-app/.env
```

#### 4. Report Generation Fails

**Triệu chứng**: Error khi generate reports

**Giải pháp**:
- Verify test results file exists and is valid JSON
- Check Python dependencies installed
- Ensure report templates exist

---

## FAQ

### Q: Tôi có thể chạy tests cho một môi trường cụ thể không?

A: Có, sử dụng option `-e`:
```bash
./scripts/run_acceptance_tests.sh -e staging
```

### Q: Làm thế nào để chỉ test một module cụ thể?

A: Hiện tại framework test tất cả modules. Để test một module, bạn có thể:
1. Sửa `acceptance_config.json` để chỉ include module cần test
2. Hoặc chạy framework trực tiếp và chỉ gọi methods cho module đó

### Q: Tôi có thể tùy chỉnh scoring weights không?

A: Có, chỉnh sửa `acceptance_config.json`:
```json
{
  "scoring_weights": {
    "client_interface": 0.40,
    "admin_interface": 0.30,
    "api_functionality": 0.20,
    "data_integrity": 0.10
  }
}
```

### Q: Làm thế nào để thêm test cases mới?

A: 
1. Thêm vào checklist tương ứng trong `checklists/`
2. Nếu là API endpoint, thêm vào `acceptance_config.json` trong `api_modules`
3. Nếu là route, thêm vào `client_routes` hoặc `admin_routes`

### Q: Reports được lưu ở đâu?

A: Reports được lưu trong `reports/acceptance/`:
- `{prefix}.md` - Markdown
- `{prefix}.html` - HTML
- `{prefix}.json` - JSON
- `test_results/{prefix}_detailed.json` - Detailed results

### Q: Tôi có thể tích hợp với CI/CD không?

A: Có, script có thể chạy trong CI/CD pipeline:
```yaml
# Example GitHub Actions
- name: Run Acceptance Tests
  run: |
    ./scripts/run_acceptance_tests.sh -e staging
    # Upload reports as artifacts
```

---

## Tài Liệu Tham Khảo

- **Checklists**: `tests/acceptance/checklists/`
- **Configuration**: `tests/acceptance/acceptance_config.json`
- **Test Data**: `tests/acceptance/test_data/`
- **Report Templates**: `tests/acceptance/report_templates/`

---

## Hỗ Trợ

Nếu gặp vấn đề hoặc có câu hỏi:
1. Kiểm tra logs trong `reports/acceptance/test_results/`
2. Review error messages trong reports
3. Tham khảo troubleshooting section trong guide này

---

**Chúc bạn nghiệm thu thành công!** 🎉

