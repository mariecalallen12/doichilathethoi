#!/usr/bin/env python3
"""
Generate comprehensive evaluation report
Combines all test results and verification outputs
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

BASE_DIR = Path(__file__).parent.parent
REPORT_FILE = BASE_DIR / "EVALUATION_REPORT.md"

# Input files
ENDPOINTS_FILE = BASE_DIR / "scripts" / "endpoints_list.json"
API_TEST_RESULTS = BASE_DIR / "scripts" / "api_test_results.json"
API_TEST_REPORT = BASE_DIR / "scripts" / "api_test_report.md"
ADMIN_MAPPING_FILE = BASE_DIR / "scripts" / "admin_features_mapping.json"

def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load JSON file"""
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load {file_path}: {e}")
    return {}

def generate_report():
    """Generate comprehensive evaluation report"""
    
    # Load data
    endpoints_data = load_json_file(ENDPOINTS_FILE)
    api_test_data = load_json_file(API_TEST_RESULTS)
    admin_mapping_data = load_json_file(BASE_DIR / "scripts" / "admin_features_mapping.json")
    
    # Count endpoints
    total_endpoints = endpoints_data.get("total", 0)
    endpoints_by_module = endpoints_data.get("by_module", {})
    
    # API test results
    api_summary = api_test_data.get("summary", {})
    api_by_module = api_test_data.get("by_module", {})
    
    # Admin mapping results
    admin_summary = admin_mapping_data.get("summary", {})
    feature_mapping = admin_mapping_data.get("feature_mapping", {})
    
    # Generate markdown report
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Đánh Giá Dự Án - Evaluation Report\n\n")
        f.write(f"**Ngày tạo:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Executive Summary
        f.write("## 1. Tóm Tắt Tổng Quan (Executive Summary)\n\n")
        f.write(f"- **Tổng số API endpoints:** {total_endpoints}\n")
        f.write(f"- **Số modules:** {len(endpoints_by_module)}\n")
        
        if api_summary:
            f.write(f"- **Endpoints đã test:** {api_summary.get('total', 0)}\n")
            f.write(f"- **Tỷ lệ thành công:** {api_summary.get('success_rate', 0):.1f}%\n")
        
        f.write("\n---\n\n")
        
        # API Endpoints Analysis
        f.write("## 2. Phân Tích API Endpoints\n\n")
        f.write("### 2.1 Danh Sách Endpoints Theo Module\n\n")
        f.write("| Module | Số Endpoints |\n")
        f.write("|--------|-------------|\n")
        
        for module, routes in sorted(endpoints_by_module.items()):
            count = len(routes) if isinstance(routes, list) else 0
            f.write(f"| {module} | {count} |\n")
        
        f.write("\n### 2.2 Kết Quả Test API\n\n")
        
        if api_by_module:
            f.write("| Module | Thành Công | Tổng | Tỷ Lệ |\n")
            f.write("|--------|-----------|------|-------|\n")
            
            for module, stats in sorted(api_by_module.items()):
                total = stats.get("total", 0)
                success = stats.get("success", 0)
                rate = (success / total * 100) if total > 0 else 0
                f.write(f"| {module} | {success} | {total} | {rate:.1f}% |\n")
        else:
            f.write("*Chưa có kết quả test. Chạy `python3 scripts/test_all_apis.py` để test APIs.*\n")
        
        f.write("\n---\n\n")
        
        # Trading Integration
        f.write("## 3. Kiểm Tra Tích Hợp Trading với core-main\n\n")
        f.write("### 3.1 Kết Nối OPEX API\n\n")
        f.write("**Cấu hình:**\n")
        f.write("- OPEX_API_URL được cấu hình trong `backend/app/core/config.py`\n")
        f.write("- OPEX client service: `backend/app/services/opex_client.py`\n")
        f.write("- Trading endpoints: `/api/trading/*`\n")
        f.write("- Market endpoints: `/api/market/*` (OPEX)\n\n")
        
        f.write("**Để kiểm tra chi tiết, chạy:**\n")
        f.write("```bash\n")
        f.write("bash scripts/verify_trading_integration.sh\n")
        f.write("```\n\n")
        
        f.write("### 3.2 Real-time Data\n\n")
        f.write("**WebSocket:**\n")
        f.write("- Client WebSocket: `client-app/src/services/opex_websocket.js`\n")
        f.write("- Backend WebSocket: `backend/app/api/websocket_opex.py`\n")
        f.write("- Path: `/ws/opex`\n\n")
        
        f.write("**Trading Dashboard:**\n")
        f.write("- Component: `client-app/src/views/OpexTradingDashboard.vue`\n")
        f.write("- Components: MarketWatch, OrderBook, TradingChart, PositionList, OrderHistory\n\n")
        
        f.write("### 3.3 Trading Operations\n\n")
        f.write("**Endpoints:**\n")
        f.write("- `POST /api/trading/orders` - Place order\n")
        f.write("- `GET /api/trading/orders` - Get orders\n")
        f.write("- `DELETE /api/trading/orders/{id}` - Cancel order\n")
        f.write("- `GET /api/trading/positions` - Get positions\n")
        f.write("- `POST /api/trading/positions/{id}/close` - Close position\n\n")
        
        f.write("---\n\n")
        
        # Admin-app Evaluation
        f.write("## 4. Đánh Giá Admin-app\n\n")
        f.write("### 4.1 Routes và Views\n\n")
        f.write("**Routes chính:**\n")
        f.write("- Dashboard\n")
        f.write("- UserManagement\n")
        f.write("- OpexTradingManagement\n")
        f.write("- FinancialManagement\n")
        f.write("- AnalyticsReports\n")
        f.write("- SystemSettings\n")
        f.write("- AdminTradingControls\n")
        f.write("- DiagnosticsManagement\n")
        f.write("- AlertManagement\n")
        f.write("- ScenarioBuilder\n")
        f.write("- MarketPreview\n")
        f.write("- EducationalHub\n")
        f.write("- AuditLogViewer\n\n")
        
        f.write("**Để kiểm tra chi tiết, chạy:**\n")
        f.write("```bash\n")
        f.write("bash scripts/verify_admin_app.sh\n")
        f.write("```\n\n")
        
        f.write("### 4.2 Mapping với Backend\n\n")
        
        if feature_mapping:
            f.write("| Admin Feature | Coverage | Found | Total |\n")
            f.write("|---------------|---------|-------|------|\n")
            for feature, mapping in sorted(feature_mapping.items()):
                coverage = mapping.get("coverage", 0)
                found = len(mapping.get("found_endpoints", []))
                total = len(mapping.get("expected_endpoints", []))
                f.write(f"| {feature} | {coverage:.1f}% | {found} | {total} |\n")
            
            f.write("\n**Chi tiết:**\n\n")
            for feature, mapping in sorted(feature_mapping.items()):
                f.write(f"#### {feature}\n\n")
                found = mapping.get("found_endpoints", [])
                missing = mapping.get("missing_endpoints", [])
                
                if found:
                    f.write("✅ Endpoints có sẵn:\n")
                    for ep in found:
                        f.write(f"- `{ep}`\n")
                    f.write("\n")
                
                if missing:
                    f.write("❌ Endpoints thiếu:\n")
                    for ep in missing:
                        f.write(f"- `{ep}`\n")
                    f.write("\n")
        else:
            f.write("*Chưa có dữ liệu mapping. Chạy `python3 scripts/map_admin_features.py` để tạo mapping.*\n\n")
        
        f.write("---\n\n")
        
        # Checklist
        f.write("## 5. Checklist Đánh Giá\n\n")
        f.write("### 5.1 API Endpoints\n\n")
        f.write("- [x] Đã liệt kê tất cả endpoints (357 endpoints)\n")
        f.write("- [ ] Đã test tất cả endpoints\n")
        f.write("- [ ] Tất cả endpoints hoạt động đúng\n\n")
        
        f.write("### 5.2 Trading Integration\n\n")
        f.write("- [ ] OPEX API kết nối được\n")
        f.write("- [ ] WebSocket real-time hoạt động\n")
        f.write("- [ ] Trading dashboard hiển thị dữ liệu\n")
        f.write("- [ ] Trading operations hoạt động (place order, cancel, etc.)\n\n")
        
        f.write("### 5.3 Admin-app\n\n")
        f.write("- [x] Routes đã được định nghĩa (33 routes)\n")
        f.write("- [x] Views đã được tạo (13 views)\n")
        f.write("- [x] Services đã được tạo\n")
        
        if admin_summary:
            total_features = admin_summary.get("total_features", 0)
            full_coverage = admin_summary.get("features_with_full_coverage", 0)
            f.write(f"- [x] Feature mapping đã hoàn thành ({full_coverage}/{total_features} features có coverage 100%)\n")
        else:
            f.write("- [ ] Feature mapping chưa hoàn thành\n")
        
        f.write("- [ ] Tất cả views hoạt động đúng (cần test thủ công)\n")
        f.write("- [ ] API calls từ Admin-app hoạt động (cần test với authentication)\n")
        f.write("- [ ] Permissions và role-based access hoạt động (cần test thủ công)\n\n")
        
        f.write("---\n\n")
        
        # Recommendations
        f.write("## 6. Đề Xuất (Recommendations)\n\n")
        f.write("1. **Chạy test tự động:** `python3 scripts/test_all_apis.py`\n")
        f.write("2. **Kiểm tra OPEX connection:** `bash scripts/verify_trading_integration.sh`\n")
        f.write("3. **Kiểm tra Admin-app:** `bash scripts/verify_admin_app.sh`\n")
        f.write("4. **Test trading operations:** Tạo test user và thực hiện các trading operations\n")
        f.write("5. **Test Admin-app functionality:** Đăng nhập admin và test từng view\n\n")
        
        f.write("---\n\n")
        f.write("**Lưu ý:** Báo cáo này được tạo tự động. Để có đánh giá đầy đủ, cần chạy các script test và verification.\n\n")

    print(f"✅ Evaluation report generated: {REPORT_FILE}")

if __name__ == "__main__":
    generate_report()

