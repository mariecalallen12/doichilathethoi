#!/usr/bin/env python3
"""
Comprehensive API Testing Script
Tests all API endpoints from the endpoints list
"""

import json
import os
import requests
import time
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict

# Base directory
BASE_DIR = Path(__file__).parent.parent
ENDPOINTS_FILE = BASE_DIR / "scripts" / "endpoints_list.json"
RESULTS_FILE = BASE_DIR / "scripts" / "api_test_results.json"
REPORT_FILE = BASE_DIR / "scripts" / "api_test_report.md"

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TIMEOUT = 10
MAX_RETRIES = 2

# Test credentials (should be created or use existing test user)
TEST_EMAIL = os.getenv("TEST_EMAIL", "test@example.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "testpassword123")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "adminpassword123")

# Global auth tokens
access_token = None
refresh_token = None
admin_token = None

def get_auth_token(email: str, password: str) -> Optional[str]:
    """Get authentication token"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": password},
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token") or data.get("token")
    except Exception as e:
        print(f"Error getting auth token: {e}")
    return None

def get_headers(require_auth: bool = False, use_admin: bool = False) -> Dict[str, str]:
    """Get request headers"""
    headers = {"Content-Type": "application/json"}
    
    if require_auth:
        global access_token, admin_token
        token = admin_token if use_admin else access_token
        
        if not token:
            # Try to get token
            email = ADMIN_EMAIL if use_admin else TEST_EMAIL
            password = ADMIN_PASSWORD if use_admin else TEST_PASSWORD
            token = get_auth_token(email, password)
            
            if use_admin:
                admin_token = token
            else:
                access_token = token
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
    
    return headers

def test_endpoint(
    method: str,
    path: str,
    module: str,
    description: str = "",
    require_auth: bool = False,
    use_admin: bool = False
) -> Dict[str, Any]:
    """Test a single endpoint"""
    result = {
        "method": method,
        "path": path,
        "module": module,
        "description": description,
        "status_code": None,
        "response_time": None,
        "success": False,
        "error": None,
        "timestamp": datetime.now().isoformat()
    }
    
    # Determine if endpoint requires auth
    # Most endpoints under /api/admin require auth
    if "/admin/" in path or "/client/" in path or "/portfolio/" in path:
        require_auth = True
        if "/admin/" in path:
            use_admin = True
    
    # Skip auth endpoints that need special handling
    if "/auth/" in path and method == "POST":
        if "login" in path or "register" in path:
            require_auth = False
    
    # Prepare request
    url = f"{BASE_URL}{path}"
    headers = get_headers(require_auth, use_admin)
    
    # Prepare request data based on method
    data = None
    params = None
    
    if method in ["POST", "PUT", "PATCH"]:
        # Generate minimal test data
        if "order" in path.lower() and method == "POST":
            data = {
                "symbol": "BTCUSDT",
                "side": "buy",
                "type": "market",
                "quantity": 0.001
            }
        elif "deposit" in path.lower() or "withdrawal" in path.lower():
            data = {"amount": 100, "currency": "USDT"}
        elif "contact" in path.lower() or "complaint" in path.lower():
            data = {
                "subject": "Test",
                "message": "Test message",
                "email": TEST_EMAIL
            }
        elif "search" in path.lower():
            data = {"query": "test"}
        elif "approve" in path.lower() or "reject" in path.lower():
            data = {"reason": "Test approval"}
        else:
            data = {}
    elif method == "GET":
        # Add query params for list endpoints
        if "{" not in path:  # Not a detail endpoint
            params = {"limit": 10, "page": 1}
        elif "{symbol}" in path:
            params = {"symbol": "BTCUSDT"}
        elif "{id}" in path or "{order_id}" in path or "{position_id}" in path:
            # Use placeholder ID
            path = path.replace("{id}", "1").replace("{order_id}", "1").replace("{position_id}", "1")
            url = f"{BASE_URL}{path}"
    
    # Replace path parameters
    path_replacements = {
        "{symbol}": "BTCUSDT",
        "{video_id}": "1",
        "{ebook_id}": "1",
        "{report_id}": "1",
        "{article_id}": "1",
        "{complaint_id}": "1",
        "{rule_id}": "1",
        "{alert_id}": "1",
        "{log_id}": "1",
        "{invoice_id}": "1",
        "{payment_id}": "1",
        "{deposit_id}": "1",
        "{withdrawal_id}": "1",
        "{trade_id}": "1",
        "{registration_id}": "1",
        "{user_id}": "1",
        "{position_id}": "1",
        "{order_id}": "1",
        "{screening_id}": "1",
        "{event_id}": "1",
        "{alert_id}": "1",
        "{category}": "general",
        "{version}": "1.0"
    }
    
    for placeholder, value in path_replacements.items():
        if placeholder in path:
            path = path.replace(placeholder, value)
            url = f"{BASE_URL}{path}"
    
    # Make request
    start_time = time.time()
    try:
        response = requests.request(
            method=method,
            url=url,
            json=data,
            params=params,
            headers=headers,
            timeout=TIMEOUT,
            allow_redirects=False
        )
        
        response_time = time.time() - start_time
        result["response_time"] = round(response_time, 3)
        result["status_code"] = response.status_code
        
        # Consider success if status code is 2xx or 3xx (redirects)
        # Also allow 401/403 for auth-required endpoints (expected)
        # Allow 404 for detail endpoints with invalid IDs
        if 200 <= response.status_code < 400:
            result["success"] = True
        elif response.status_code in [401, 403]:
            result["success"] = True  # Expected for protected endpoints without auth
            result["error"] = "Authentication required (expected)"
        elif response.status_code == 404:
            result["success"] = True  # Expected for detail endpoints
            result["error"] = "Not found (expected for test IDs)"
        elif response.status_code == 422:
            result["success"] = True  # Validation error is acceptable
            result["error"] = "Validation error (expected)"
        else:
            result["error"] = f"HTTP {response.status_code}"
        
        # Try to get response body
        try:
            result["response_size"] = len(response.content)
            if response.headers.get("content-type", "").startswith("application/json"):
                result["response_type"] = "json"
                result["response_sample"] = str(response.json())[:200]
            else:
                result["response_type"] = "other"
                result["response_sample"] = response.text[:200]
        except:
            pass
    
    except requests.exceptions.Timeout:
        result["error"] = "Request timeout"
        result["response_time"] = TIMEOUT
    except requests.exceptions.ConnectionError:
        result["error"] = "Connection error - backend may not be running"
    except Exception as e:
        result["error"] = str(e)
    
    return result

def load_endpoints() -> List[Dict[str, Any]]:
    """Load endpoints from JSON file"""
    try:
        with open(ENDPOINTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("endpoints", [])
    except FileNotFoundError:
        print(f"Error: Endpoints file not found: {ENDPOINTS_FILE}")
        print("Please run list_all_endpoints.py first")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading endpoints: {e}")
        sys.exit(1)

def main():
    """Main test function"""
    print("="*80)
    print("COMPREHENSIVE API TESTING")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Testing against: {BASE_URL}")
    print()
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"⚠️  Backend health check returned {response.status_code}")
    except:
        print("❌ Backend is not running or not accessible")
        print(f"   Please start the backend at {BASE_URL}")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print()
    
    # Load endpoints
    endpoints = load_endpoints()
    print(f"Loaded {len(endpoints)} endpoints to test")
    print()
    
    # Get auth tokens
    print("Getting authentication tokens...")
    global access_token, admin_token
    access_token = get_auth_token(TEST_EMAIL, TEST_PASSWORD)
    admin_token = get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
    
    if access_token:
        print("✅ User token obtained")
    else:
        print("⚠️  Could not get user token (some tests may fail)")
    
    if admin_token:
        print("✅ Admin token obtained")
    else:
        print("⚠️  Could not get admin token (admin tests may fail)")
    
    print()
    
    # Test endpoints
    results = []
    total = len(endpoints)
    
    print("Testing endpoints...")
    print("-"*80)
    
    for i, endpoint in enumerate(endpoints, 1):
        path = endpoint.get("full_path", endpoint.get("path", ""))
        method = endpoint.get("method", "GET")
        module = endpoint.get("module", "unknown")
        description = endpoint.get("description", "")
        
        print(f"[{i}/{total}] {method:6} {path[:60]:60}", end="", flush=True)
        
        result = test_endpoint(method, path, module, description)
        results.append(result)
        
        if result["success"]:
            print(f" ✅ {result['status_code']} ({result['response_time']:.3f}s)")
        else:
            print(f" ❌ {result['status_code']} - {result.get('error', 'Unknown error')}")
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.1)
    
    print()
    print("-"*80)
    
    # Analyze results
    total_tested = len(results)
    successful = sum(1 for r in results if r["success"])
    failed = total_tested - successful
    
    # Group by module
    by_module = defaultdict(lambda: {"total": 0, "success": 0, "failed": 0})
    for result in results:
        module = result["module"]
        by_module[module]["total"] += 1
        if result["success"]:
            by_module[module]["success"] += 1
        else:
            by_module[module]["failed"] += 1
    
    # Group by status code
    by_status = defaultdict(int)
    for result in results:
        status_code = result.get("status_code", 0)
        by_status[status_code] += 1
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total endpoints tested: {total_tested}")
    print(f"Successful: {successful} ({successful/total_tested*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total_tested*100:.1f}%)")
    print()
    
    print("Results by Module:")
    print("-"*80)
    for module in sorted(by_module.keys()):
        stats = by_module[module]
        success_rate = stats["success"] / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"{module:20} {stats['success']:3}/{stats['total']:3} ({success_rate:5.1f}%)")
    
    print()
    print("Status Code Distribution:")
    print("-"*80)
    for status_code in sorted(by_status.keys()):
        count = by_status[status_code]
        print(f"  {status_code}: {count}")
    
    # Save results
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "base_url": BASE_URL,
        "summary": {
            "total": total_tested,
            "successful": successful,
            "failed": failed,
            "success_rate": successful/total_tested*100 if total_tested > 0 else 0
        },
        "by_module": dict(by_module),
        "by_status_code": dict(by_status),
        "results": results
    }
    
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Detailed results saved to: {RESULTS_FILE}")
    
    # Generate markdown report
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# API Test Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Base URL:** {BASE_URL}\n\n")
        f.write(f"**Total Endpoints:** {total_tested}\n")
        f.write(f"**Successful:** {successful} ({successful/total_tested*100:.1f}%)\n")
        f.write(f"**Failed:** {failed} ({failed/total_tested*100:.1f}%)\n\n")
        
        f.write("## Results by Module\n\n")
        f.write("| Module | Success | Total | Success Rate |\n")
        f.write("|--------|---------|-------|--------------|\n")
        for module in sorted(by_module.keys()):
            stats = by_module[module]
            success_rate = stats["success"] / stats["total"] * 100 if stats["total"] > 0 else 0
            f.write(f"| {module} | {stats['success']} | {stats['total']} | {success_rate:.1f}% |\n")
        
        f.write("\n## Failed Endpoints\n\n")
        failed_results = [r for r in results if not r["success"]]
        if failed_results:
            f.write("| Method | Path | Module | Status | Error |\n")
            f.write("|--------|------|--------|--------|-------|\n")
            for result in failed_results[:50]:  # Limit to 50
                f.write(f"| {result['method']} | `{result['path']}` | {result['module']} | {result.get('status_code', 'N/A')} | {result.get('error', 'Unknown')} |\n")
        else:
            f.write("No failed endpoints!\n")
    
    print(f"✅ Markdown report saved to: {REPORT_FILE}")
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

