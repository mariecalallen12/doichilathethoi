#!/usr/bin/env python3
"""
Map Admin-app features to backend API endpoints
Analyzes Admin-app routes and maps them to corresponding backend endpoints
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).parent.parent
ADMIN_APP_DIR = BASE_DIR / "Admin-app"
ENDPOINTS_FILE = BASE_DIR / "scripts" / "endpoints_list.json"
OUTPUT_FILE = BASE_DIR / "scripts" / "admin_features_mapping.json"

# Feature to endpoint mapping
FEATURE_MAPPING = {
    "Dashboard": [
        "/api/admin/dashboard",
        "/api/admin/platform-stats",
        "/api/admin/analytics"
    ],
    "UserManagement": [
        "/api/admin/users",
        "/api/users",
        "/api/admin/users/{user_id}/performance",
        "/api/admin/users/bulk-update",
        "/api/admin/registrations",
        "/api/admin/registrations/{registration_id}/approve"
    ],
    "OpexTradingManagement": [
        "/api/admin/trading",
        "/api/admin/trading/adjustments",
        "/api/admin/trades",
        "/api/admin/trades/{trade_id}/approve",
        "/api/admin/trades/{trade_id}/reject"
    ],
    "FinancialManagement": [
        "/api/admin/deposits",
        "/api/admin/deposits/{deposit_id}",
        "/api/admin/deposits/{deposit_id}/approve",
        "/api/admin/deposits/{deposit_id}/reject",
        "/api/admin/withdrawals",
        "/api/admin/withdrawals/{withdrawal_id}",
        "/api/admin/withdrawals/{withdrawal_id}/approve",
        "/api/admin/withdrawals/{withdrawal_id}/reject",
        "/api/admin/invoices",
        "/api/admin/invoices/{invoice_id}",
        "/api/admin/payments",
        "/api/admin/payments/{payment_id}"
    ],
    "AnalyticsReports": [
        "/api/admin/analytics",
        "/api/admin/analytics/performance",
        "/api/admin/reports",
        "/api/admin/reports/scheduled",
        "/api/admin/platform-stats"
    ],
    "SystemSettings": [
        "/api/admin/settings",
        "/api/admin/settings/market-display",
        "/api/admin/settings/chart-display",
        "/api/admin/settings/market-scenarios",
        "/api/admin/settings/registration-fields",
        "/api/admin/settings/cors-origins",
        "/api/admin/settings/auto-approve-registration"
    ],
    "AdminTradingControls": [
        "/api/admin/trading/orders/{order_id}",
        "/api/admin/trading/orders/{order_id}/force",
        "/api/admin/trading/positions/{position_id}",
        "/api/admin/trading/positions/{position_id}/force-close",
        "/api/admin/trading/prices/{symbol}",
        "/api/admin/trading/balances/{user_id}",
        "/api/admin/trading-adjustments/win-rate",
        "/api/admin/trading-adjustments/position-override"
    ],
    "DiagnosticsManagement": [
        "/api/diagnostics/trading-report",
        "/api/diagnostics/trading-reports",
        "/api/diagnostics/trading-reports/{report_id}"
    ],
    "AlertManagement": [
        "/api/alert-rules",
        "/api/alert-rules/{rule_id}",
        "/api/alert-history",
        "/api/alert-history/{alert_id}/acknowledge",
        "/api/alert-history/{alert_id}/resolve"
    ],
    "ScenarioBuilder": [
        "/api/admin/simulator/sessions",
        "/api/admin/simulator/sessions/start",
        "/api/admin/simulator/sessions/stop",
        "/api/admin/simulator/sessions/reset",
        "/api/admin/simulator/sessions/replay",
        "/api/admin/simulator/monitoring"
    ],
    "MarketPreview": [
        "/api/admin/market-preview",
        "/api/admin/market-preview/{symbol}"
    ],
    "EducationalHub": [
        "/api/education/videos",
        "/api/education/ebooks",
        "/api/education/calendar",
        "/api/education/reports"
    ],
    "AuditLogViewer": [
        "/api/logs",
        "/api/logs/stats",
        "/api/logs/{log_id}",
        "/api/compliance/audit"
    ]
}

def load_endpoints() -> Dict[str, Any]:
    """Load endpoints from JSON"""
    try:
        with open(ENDPOINTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load endpoints: {e}")
        return {}

def check_endpoint_exists(endpoint_path: str, endpoints_data: Dict) -> bool:
    """Check if endpoint exists in backend"""
    endpoints = endpoints_data.get("endpoints", [])
    for ep in endpoints:
        full_path = ep.get("full_path", ep.get("path", ""))
        # Match exact
        if full_path == endpoint_path:
            return True
        # Match without leading/trailing slashes
        if full_path.rstrip('/') == endpoint_path.rstrip('/'):
            return True
        # Check if it matches with parameter replacement
        # Convert {param} to regex pattern
        pattern = endpoint_path.replace("{", "\\{").replace("}", "\\}")
        if re.match(pattern, full_path):
            return True
        # Also check reverse - if endpoint_path has params, check if full_path matches
        # e.g., /api/users matches /api/users/{id} pattern
        if "{" in full_path:
            base_path = full_path.split("{")[0].rstrip("/")
            if endpoint_path.rstrip("/") == base_path:
                return True
    return False

def analyze_admin_services() -> Dict[str, List[str]]:
    """Analyze Admin-app services to find API calls"""
    services_dir = ADMIN_APP_DIR / "src" / "services"
    api_calls = {}
    
    if not services_dir.exists():
        return api_calls
    
    for service_file in services_dir.glob("*.js"):
        try:
            with open(service_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find API calls
                api_pattern = r"['\"](/api/[^'\"]+)['\"]"
                matches = re.findall(api_pattern, content)
                if matches:
                    api_calls[service_file.name] = list(set(matches))
        except Exception as e:
            print(f"Warning: Could not read {service_file}: {e}")
    
    return api_calls

def main():
    """Main function"""
    print("="*80)
    print("Admin-app Features to Backend Endpoints Mapping")
    print("="*80)
    print()
    
    # Load endpoints
    endpoints_data = load_endpoints()
    
    # Analyze admin services
    print("Analyzing Admin-app services...")
    service_api_calls = analyze_admin_services()
    print(f"Found {len(service_api_calls)} service files with API calls\n")
    
    # Map features
    print("Mapping features to backend endpoints...")
    print("-"*80)
    
    mapping_results = {}
    all_backend_endpoints = {ep.get("full_path", ep.get("path", "")) for ep in endpoints_data.get("endpoints", [])}
    
    for feature, expected_endpoints in FEATURE_MAPPING.items():
        print(f"\n{feature}:")
        feature_results = {
            "expected_endpoints": expected_endpoints,
            "found_endpoints": [],
            "missing_endpoints": [],
            "coverage": 0
        }
        
        for endpoint in expected_endpoints:
            if check_endpoint_exists(endpoint, endpoints_data):
                feature_results["found_endpoints"].append(endpoint)
                print(f"  ✅ {endpoint}")
            else:
                feature_results["missing_endpoints"].append(endpoint)
                print(f"  ❌ {endpoint} (not found)")
        
        total = len(expected_endpoints)
        found = len(feature_results["found_endpoints"])
        feature_results["coverage"] = (found / total * 100) if total > 0 else 0
        
        print(f"  Coverage: {found}/{total} ({feature_results['coverage']:.1f}%)")
        mapping_results[feature] = feature_results
    
    # Check for additional endpoints used in services
    print("\n" + "-"*80)
    print("API calls found in Admin-app services:")
    print("-"*80)
    
    all_service_endpoints = set()
    for service, endpoints in service_api_calls.items():
        print(f"\n{service}:")
        for endpoint in endpoints:
            print(f"  - {endpoint}")
            all_service_endpoints.add(endpoint)
    
    # Check if service endpoints exist in backend
    print("\n" + "-"*80)
    print("Verifying service endpoints exist in backend:")
    print("-"*80)
    
    service_endpoint_status = {}
    for endpoint in sorted(all_service_endpoints):
        exists = check_endpoint_exists(endpoint, endpoints_data)
        service_endpoint_status[endpoint] = exists
        status = "✅" if exists else "❌"
        print(f"{status} {endpoint}")
    
    # Generate summary
    print("\n" + "="*80)
    print("Summary")
    print("="*80)
    
    total_features = len(FEATURE_MAPPING)
    features_with_full_coverage = sum(1 for r in mapping_results.values() if r["coverage"] == 100)
    
    print(f"Total features: {total_features}")
    print(f"Features with full coverage: {features_with_full_coverage}/{total_features}")
    print(f"Service files analyzed: {len(service_api_calls)}")
    print(f"Unique API endpoints in services: {len(all_service_endpoints)}")
    
    # Save results
    output_data = {
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "feature_mapping": mapping_results,
        "service_api_calls": service_api_calls,
        "service_endpoint_status": service_endpoint_status,
        "summary": {
            "total_features": total_features,
            "features_with_full_coverage": features_with_full_coverage,
            "service_files": len(service_api_calls),
            "unique_service_endpoints": len(all_service_endpoints)
        }
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Mapping results saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

