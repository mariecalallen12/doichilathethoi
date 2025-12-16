#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Script
Tests all endpoints in the Digital Utopia Platform
"""

import requests
import json
from typing import Dict, List, Tuple
from datetime import datetime

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results: List[Dict] = []
        self.access_token = None
        
    def test_endpoint(self, method: str, path: str, expected_status: int = None, 
                     data: dict = None, headers: dict = None, description: str = None) -> Dict:
        """Test a single endpoint"""
        url = f"{self.base_url}{path}"
        method_func = getattr(requests, method.lower())
        
        if headers is None:
            headers = {}
        if self.access_token:
            headers.setdefault("Authorization", f"Bearer {self.access_token}")
        
        try:
            if data:
                response = method_func(url, json=data, headers=headers, timeout=10)
            else:
                response = method_func(url, headers=headers, timeout=10)
            
            result = {
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "success": expected_status is None or response.status_code == expected_status,
                "description": description or path,
                "response_time": response.elapsed.total_seconds(),
                "has_response": len(response.content) > 0
            }
            
            # Try to parse JSON response
            try:
                result["response_data"] = response.json()
            except:
                result["response_data"] = response.text[:200] if response.text else None
            
            self.results.append(result)
            return result
            
        except Exception as e:
            result = {
                "method": method,
                "path": path,
                "status_code": None,
                "expected_status": expected_status,
                "success": False,
                "description": description or path,
                "error": str(e),
                "response_time": 0
            }
            self.results.append(result)
            return result
    
    def print_result(self, result: Dict):
        """Print test result with color coding"""
        status_icon = f"{Colors.GREEN}✓{Colors.NC}" if result.get("success", False) else f"{Colors.RED}✗{Colors.NC}"
        status_code = result.get("status_code", "N/A")
        desc = result.get("description", result.get("path", ""))
        time_ms = result.get("response_time", 0) * 1000
        
        print(f"{status_icon} {result.get('method', 'GET'):<6} {desc:<50} [{status_code}] ({time_ms:.0f}ms)")
        
        if not result.get("success", False) and result.get("error"):
            print(f"   {Colors.RED}Error: {result['error']}{Colors.NC}")
    
    def test_all(self):
        """Test all endpoints"""
        print(f"\n{Colors.BLUE}{'='*80}{Colors.NC}")
        print(f"{Colors.BLUE}Digital Utopia Platform - Comprehensive API Testing{Colors.NC}")
        print(f"{Colors.BLUE}{'='*80}{Colors.NC}\n")
        
        # Phase 1: Health and System Endpoints
        print(f"\n{Colors.YELLOW}[Phase 1] Health and System Endpoints{Colors.NC}")
        print("-" * 80)
        self.test_endpoint("GET", "/api/health", 200, description="Health check")
        self.test_endpoint("GET", "/", 200, description="Root endpoint")
        self.test_endpoint("GET", "/docs", 200, description="Swagger UI")
        self.test_endpoint("GET", "/openapi.json", 200, description="OpenAPI schema")
        
        # Phase 2: Authentication Endpoints (without auth)
        print(f"\n{Colors.YELLOW}[Phase 2] Authentication Endpoints{Colors.NC}")
        print("-" * 80)
        self.test_endpoint("POST", "/api/auth/register", None, 
                          data={"email": "test@example.com", "password": "test123"}, 
                          description="Register (validation test)")
        self.test_endpoint("POST", "/api/auth/login", None,
                          data={"email": "test@example.com", "password": "test123"},
                          description="Login (validation test)")
        self.test_endpoint("POST", "/api/auth/refresh", None, description="Refresh token")
        self.test_endpoint("POST", "/api/auth/logout", None, description="Logout")
        self.test_endpoint("POST", "/api/auth/verify", None, description="Verify token")
        self.test_endpoint("POST", "/api/auth/forgot-password", None,
                          data={"email": "test@example.com"},
                          description="Forgot password")
        
        # Phase 3: Client Endpoints (should require auth - expect 401)
        print(f"\n{Colors.YELLOW}[Phase 3] Client Endpoints (Auth Required){Colors.NC}")
        print("-" * 80)
        self.test_endpoint("GET", "/api/client/profile", 401, description="Get profile")
        self.test_endpoint("PUT", "/api/client/profile", 401, description="Update profile")
        self.test_endpoint("GET", "/api/client/settings", 401, description="Get settings")
        self.test_endpoint("PUT", "/api/client/settings", 401, description="Update settings")
        self.test_endpoint("GET", "/api/client/preferences", 401, description="Get preferences")
        self.test_endpoint("PUT", "/api/client/preferences", 401, description="Update preferences")
        self.test_endpoint("GET", "/api/client/onboarding/status", 401, description="Onboarding status")
        self.test_endpoint("POST", "/api/client/onboarding/complete", 401, description="Complete onboarding")
        
        # Phase 4: Admin Endpoints (should require auth - expect 401)
        print(f"\n{Colors.YELLOW}[Phase 4] Admin Endpoints (Auth Required){Colors.NC}")
        print("-" * 80)
        self.test_endpoint("GET", "/api/admin/dashboard", 401, description="Admin dashboard")
        self.test_endpoint("GET", "/api/admin/users", 401, description="List users")
        self.test_endpoint("GET", "/api/admin/platform-stats", 401, description="Platform stats")
        self.test_endpoint("GET", "/api/admin/analytics", 401, description="Analytics")
        
        # Phase 5: Financial Endpoints (should require auth - expect 401)
        print(f"\n{Colors.YELLOW}[Phase 5] Financial Endpoints (Auth Required){Colors.NC}")
        print("-" * 80)
        self.test_endpoint("GET", "/api/financial/balance", 401, description="Get balance")
        self.test_endpoint("GET", "/api/financial/transactions", 401, description="Get transactions")
        self.test_endpoint("POST", "/api/financial/deposit", 401, description="Deposit")
        self.test_endpoint("POST", "/api/financial/withdraw", 401, description="Withdraw")
        self.test_endpoint("GET", "/api/financial/reports", 401, description="Financial reports")
        
        # Phase 6: Trading Endpoints (should require auth - expect 401)
        print(f"\n{Colors.YELLOW}[Phase 6] Trading Endpoints (Auth Required){Colors.NC}")
        print("-" * 80)
        self.test_endpoint("GET", "/api/trading/orders", 401, description="Get orders")
        self.test_endpoint("POST", "/api/trading/orders", 401, description="Place order")
        self.test_endpoint("GET", "/api/trading/positions", 401, description="Get positions")
        self.test_endpoint("GET", "/api/trading/statistics", 401, description="Trading statistics")
        
        # Phase 7: Market Data Endpoints (may or may not require auth)
        print(f"\n{Colors.YELLOW}[Phase 7] Market Data Endpoints{Colors.NC}")
        print("-" * 80)
        self.test_endpoint("GET", "/api/market/prices", None, description="Get prices")
        self.test_endpoint("GET", "/api/market/summary", None, description="Market summary")
        
        # Phase 8: Portfolio Endpoints (should require auth - expect 401)
        print(f"\n{Colors.YELLOW}[Phase 8] Portfolio Endpoints (Auth Required){Colors.NC}")
        print("-" * 80)
        self.test_endpoint("GET", "/api/portfolio/analytics", 401, description="Portfolio analytics")
        self.test_endpoint("GET", "/api/portfolio/metrics", 401, description="Portfolio metrics")
        
        # Phase 9: Compliance Endpoints (should require auth - expect 401)
        print(f"\n{Colors.YELLOW}[Phase 9] Compliance Endpoints (Auth Required){Colors.NC}")
        print("-" * 80)
        self.test_endpoint("GET", "/api/compliance/kyc", 401, description="KYC status")
        self.test_endpoint("GET", "/api/compliance/aml", 401, description="AML status")
        
        # Phase 10: Risk Management Endpoints (should require auth - expect 401)
        print(f"\n{Colors.YELLOW}[Phase 10] Risk Management Endpoints (Auth Required){Colors.NC}")
        print("-" * 80)
        self.test_endpoint("GET", "/api/risk-management/assessment", 401, description="Risk assessment")
        self.test_endpoint("GET", "/api/risk-management/limits", 401, description="Risk limits")
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{Colors.BLUE}{'='*80}{Colors.NC}")
        print(f"{Colors.BLUE}Test Summary{Colors.NC}")
        print(f"{Colors.BLUE}{'='*80}{Colors.NC}\n")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get("success", False))
        failed = total - passed
        
        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.NC}")
        print(f"{Colors.RED}Failed: {failed}{Colors.NC}")
        
        if failed > 0:
            print(f"\n{Colors.YELLOW}Failed Tests:{Colors.NC}")
            for result in self.results:
                if not result.get("success", False):
                    print(f"  {Colors.RED}✗{Colors.NC} {result.get('method')} {result.get('path')} - Status: {result.get('status_code', 'N/A')}")
        
        # Calculate average response time
        avg_time = sum(r.get("response_time", 0) for r in self.results) / total if total > 0 else 0
        print(f"\nAverage Response Time: {avg_time*1000:.2f}ms")
        
        # Save results to file
        with open("/tmp/api_test_results.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total": total,
                "passed": passed,
                "failed": failed,
                "results": self.results
            }, f, indent=2)
        
        print(f"\n{Colors.BLUE}Detailed results saved to: /tmp/api_test_results.json{Colors.NC}")

if __name__ == "__main__":
    tester = APITester()
    tester.test_all()

