#!/usr/bin/env python3
"""
Test Trading Operations
Tests all trading-related endpoints with authentication
"""

import os
import requests
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).parent.parent
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TIMEOUT = 10

# Test credentials
TEST_EMAIL = os.getenv("TEST_EMAIL", "test@cmeetrading.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "Test@123456")

def get_auth_token() -> Optional[str]:
    """Get authentication token"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            # Handle nested response structure: {"success":true,"data":{"access_token":"..."}}
            if isinstance(data, dict):
                if "data" in data and isinstance(data["data"], dict):
                    return data["data"].get("access_token") or data["data"].get("token")
                # Fallback to direct access_token
                return data.get("access_token") or data.get("token")
    except Exception as e:
        print(f"Error getting auth token: {e}")
    return None

def test_trading_endpoint(method: str, endpoint: str, token: str, data: Dict = None) -> Dict[str, Any]:
    """Test a trading endpoint with detailed error reporting"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}{endpoint}"
    start_time = time.time()
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=TIMEOUT)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=TIMEOUT)
        else:
            return {"success": False, "error": f"Unsupported method: {method}", "duration_ms": 0}
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Try to parse JSON response
        response_data = None
        response_text = None
        try:
            if response.headers.get("content-type", "").startswith("application/json"):
                response_data = response.json()
            else:
                response_text = response.text[:500]
        except:
            response_text = response.text[:500] if response.text else "No response body"
        
        success = 200 <= response.status_code < 400
        
        # Extract error message from response if available
        error_message = None
        if not success:
            if response_data:
                error_message = response_data.get("detail") or response_data.get("message") or response_data.get("error")
            elif response_text:
                error_message = response_text
        
        result = {
            "success": success,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "response": response_data if response_data else response_text
        }
        
        if error_message:
            result["error_message"] = error_message
        
        return result
        
    except requests.exceptions.Timeout:
        duration_ms = (time.time() - start_time) * 1000
        return {
            "success": False,
            "error": "Request timeout",
            "error_type": "Timeout",
            "duration_ms": round(duration_ms, 2)
        }
    except requests.exceptions.ConnectionError as e:
        duration_ms = (time.time() - start_time) * 1000
        return {
            "success": False,
            "error": f"Connection error: {str(e)}",
            "error_type": "ConnectionError",
            "duration_ms": round(duration_ms, 2)
        }
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "duration_ms": round(duration_ms, 2)
        }

def main():
    """Main test function"""
    print("="*80)
    print("Trading Operations Test")
    print("="*80)
    print(f"Base URL: {BASE_URL}\n")
    
    # Get auth token
    print("Getting authentication token...")
    token = get_auth_token()
    if not token:
        print("❌ Could not get authentication token")
        print("Please ensure:")
        print("1. Backend is running")
        print("2. Test user exists (email: test@example.com)")
        print("3. TEST_EMAIL and TEST_PASSWORD are set correctly")
        sys.exit(1)
    
    print("✅ Authentication token obtained\n")
    
    # Test endpoints
    tests = [
        ("GET", "/api/trading/health", None, "Health check"),
        ("GET", "/api/trading/orders", None, "Get orders"),
        ("GET", "/api/trading/positions", None, "Get positions"),
        ("GET", "/api/trading/statistics", None, "Get statistics"),
        ("GET", "/api/market/symbols", None, "Get symbols"),
        ("GET", "/api/market/orderbook/BTCUSDT?limit=10", None, "Get orderbook"),
        ("GET", "/api/market/trades/BTCUSDT?limit=10", None, "Get trades"),
        ("GET", "/api/market/ticker/BTCUSDT", None, "Get ticker"),
        ("POST", "/api/trading/orders", {
            "symbol": "BTCUSDT",
            "side": "buy",
            "type": "market",
            "quantity": 0.001
        }, "Place order (market)"),
    ]
    
    results = []
    print("Testing trading endpoints...")
    print("-"*80)
    
    for method, endpoint, data, description in tests:
        print(f"[{method:6}] {endpoint[:50]:50} ... ", end="", flush=True)
        result = test_trading_endpoint(method, endpoint, token, data)
        results.append({
            "method": method,
            "endpoint": endpoint,
            "description": description,
            **result
        })
        
        if result["success"]:
            duration = result.get("duration_ms", 0)
            print(f"✅ {result['status_code']} ({duration:.0f}ms)")
        else:
            status_code = result.get('status_code', 'N/A')
            error = result.get("error") or result.get("error_message") or f"HTTP {status_code}"
            error_type = result.get("error_type", "")
            duration = result.get("duration_ms", 0)
            
            error_display = f"{error}"
            if error_type:
                error_display = f"{error_type}: {error}"
            
            print(f"❌ {status_code} - {error_display[:60]}")
            if result.get("response") and isinstance(result["response"], dict):
                detail = result["response"].get("detail") or result["response"].get("message")
                if detail and detail != error:
                    print(f"         Detail: {detail[:60]}")
    
    print("-"*80)
    print("\nSummary:")
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    failed = total - successful
    print(f"Successful: {successful}/{total} ({successful/total*100:.1f}%)")
    print(f"Failed: {failed}/{total} ({failed/total*100:.1f}%)")
    
    # Show failed endpoints details
    if failed > 0:
        print("\nFailed Endpoints:")
        print("-"*80)
        for r in results:
            if not r["success"]:
                error = r.get("error") or r.get("error_message") or f"HTTP {r.get('status_code', 'N/A')}"
                print(f"  ❌ {r['method']} {r['endpoint']}")
                print(f"     {error}")
                if r.get("response") and isinstance(r["response"], dict):
                    detail = r["response"].get("detail") or r["response"].get("message")
                    if detail:
                        print(f"     Detail: {detail}")
    
    # Calculate average response time
    durations = [r.get("duration_ms", 0) for r in results if r.get("duration_ms")]
    if durations:
        avg_duration = sum(durations) / len(durations)
        print(f"\nAverage response time: {avg_duration:.0f}ms")
    
    # Save results
    output_file = BASE_DIR / "scripts" / "trading_operations_test.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "base_url": BASE_URL,
            "results": results,
            "summary": {
                "total": total,
                "successful": successful,
                "failed": total - successful
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Results saved to: {output_file}")

if __name__ == "__main__":
    main()

