#!/usr/bin/env python3
"""
Acceptance Test Framework
Automated testing framework for comprehensive acceptance testing
"""

import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AcceptanceTestFramework:
    """Main framework for acceptance testing"""
    
    def __init__(self, config_path: Optional[str] = None, environment: str = "local"):
        """Initialize framework with configuration"""
        if config_path is None:
            config_path = Path(__file__).parent / "acceptance_config.json"
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        env_config = self.config.get("environments", {}).get(environment, {})
        self.api_url = env_config.get("api_url", "http://localhost:8000")
        self.client_url = env_config.get("client_url", "http://localhost:3002")
        self.admin_url = env_config.get("admin_url", "http://localhost:3001")
        self.ws_url = env_config.get("ws_url", "ws://localhost:8000/ws")
        
        self.timeouts = self.config.get("test_timeouts", {})
        self.results: List[Dict] = []
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.admin_token: Optional[str] = None
        self.admin_refresh_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.admin_token_expiry: Optional[datetime] = None
        self.current_user_role: Optional[str] = None
        self.endpoint_payloads: Dict = {}
        self._load_endpoint_payloads()
        
    def test_api_endpoint(self, method: str, path: str, expected_status: int = None,
                        data: Dict = None, headers: Dict = None, 
                        description: str = None, requires_auth: bool = False,
                        use_admin_token: bool = False) -> Dict:
        """Test a single API endpoint"""
        url = f"{self.api_url}{path}"
        method_func = getattr(requests, method.lower())
        
        if headers is None:
            headers = {"Content-Type": "application/json"}
        
        # Add authentication if required
        if requires_auth:
            token = self.get_valid_token(use_admin_token)
            if token:
                headers["Authorization"] = f"Bearer {token}"
            else:
                logger.warning(f"No valid token available for {path}")
        
        start_time = time.time()
        max_retries = 3
        retry_count = 0
        response = None
        
        while retry_count < max_retries:
            try:
                if data:
                    response = method_func(
                        url, 
                        json=data, 
                        headers=headers, 
                        timeout=self.timeouts.get("api_request", 10)
                    )
                else:
                    response = method_func(
                        url, 
                        headers=headers, 
                        timeout=self.timeouts.get("api_request", 10)
                    )
                
                # Check for rate limiting
                if response.status_code == 429:
                    if retry_count < max_retries - 1:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        wait_time = min(retry_after, 60)  # Max 60 seconds
                        logger.warning(f"Rate limited, waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        retry_count += 1
                        continue
                
                # Not rate limited, break out of retry loop
                break
                
            except requests.exceptions.Timeout:
                if retry_count < max_retries - 1:
                    wait_time = 2 ** retry_count  # Exponential backoff
                    logger.warning(f"Request timeout, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    retry_count += 1
                    continue
                else:
                    # Final timeout, handle below
                    response = None
                    break
        
        # Handle timeout after all retries
        if response is None:
            response_time = time.time() - start_time
            result = {
                "type": "api",
                "method": method,
                "path": path,
                "url": url,
                "status_code": None,
                "expected_status": expected_status,
                "success": False,
                "description": description or path,
                "response_time": response_time,
                "error": "Request timeout",
                "timestamp": datetime.now().isoformat()
            }
            self.results.append(result)
            return result
        
        # Process successful response
        try:
            response_time = time.time() - start_time
            
            # Determine success
            if expected_status:
                success = response.status_code == expected_status
            else:
                # Default: 2xx is success
                success = 200 <= response.status_code < 300
            
            # Try to parse JSON
            try:
                response_data = response.json()
            except:
                response_data = response.text[:500] if response.text else None
            
            result = {
                "type": "api",
                "method": method,
                "path": path,
                "url": url,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "success": success,
                "description": description or path,
                "response_time": response_time,
                "response_size": len(response.content),
                "has_response": len(response.content) > 0,
                "response_data": response_data,
                "timestamp": datetime.now().isoformat()
            }
            
            if not success:
                result["error"] = f"Expected {expected_status}, got {response.status_code}"
            
            self.results.append(result)
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            result = {
                "type": "api",
                "method": method,
                "path": path,
                "url": url,
                "status_code": None,
                "expected_status": expected_status,
                "success": False,
                "description": description or path,
                "response_time": response_time,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results.append(result)
            return result
    
    def test_page_accessibility(self, url: str, description: str = None,
                               requires_auth: bool = False) -> Dict:
        """Test if a page is accessible"""
        start_time = time.time()
        try:
            headers = {}
            if requires_auth and self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeouts.get("page_load", 30),
                allow_redirects=True
            )
            
            response_time = time.time() - start_time
            success = 200 <= response.status_code < 400
            
            result = {
                "type": "page",
                "url": url,
                "status_code": response.status_code,
                "success": success,
                "description": description or url,
                "response_time": response_time,
                "content_length": len(response.content),
                "timestamp": datetime.now().isoformat()
            }
            
            if not success:
                result["error"] = f"HTTP {response.status_code}"
            
            self.results.append(result)
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            result = {
                "type": "page",
                "url": url,
                "status_code": None,
                "success": False,
                "description": description or url,
                "response_time": response_time,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results.append(result)
            return result
    
    def authenticate_client(self, email: str, password: str) -> bool:
        """Authenticate as client user"""
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/login",
                json={"email": email, "password": password},
                timeout=self.timeouts.get("api_request", 10)
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle different response formats
                if isinstance(data, dict):
                    if "data" in data:
                        token_data = data["data"]
                        self.access_token = token_data.get("access_token") or token_data.get("token")
                        self.refresh_token = token_data.get("refresh_token")
                        self.current_user_role = token_data.get("role", "customer")
                    else:
                        self.access_token = data.get("access_token") or data.get("token")
                        self.refresh_token = data.get("refresh_token")
                        self.current_user_role = data.get("role", "customer")
                    
                    # Calculate token expiry (default 1 hour if not provided)
                    expires_in = data.get("expires_in", 3600)
                    self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                    return True
            return False
        except Exception as e:
            logger.error(f"Client authentication failed: {e}")
            return False
    
    def authenticate_admin(self, email: str, password: str) -> bool:
        """Authenticate as admin user"""
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/login",
                json={"email": email, "password": password},
                timeout=self.timeouts.get("api_request", 10)
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle different response formats
                if isinstance(data, dict):
                    if "data" in data:
                        token_data = data["data"]
                        self.admin_token = token_data.get("access_token") or token_data.get("token")
                        self.admin_refresh_token = token_data.get("refresh_token")
                    else:
                        self.admin_token = data.get("access_token") or data.get("token")
                        self.admin_refresh_token = data.get("refresh_token")
                    
                    # Calculate token expiry
                    expires_in = data.get("expires_in", 3600)
                    self.admin_token_expiry = datetime.now() + timedelta(seconds=expires_in)
                    return True
            return False
        except Exception as e:
            logger.error(f"Admin authentication failed: {e}")
            return False
    
    def refresh_access_token(self, use_admin: bool = False) -> bool:
        """Refresh access token if expired"""
        refresh_token = self.admin_refresh_token if use_admin else self.refresh_token
        if not refresh_token:
            return False
        
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/refresh",
                json={"refresh_token": refresh_token},
                timeout=self.timeouts.get("api_request", 10)
            )
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    if "data" in data:
                        token_data = data["data"]
                        new_token = token_data.get("access_token") or token_data.get("token")
                    else:
                        new_token = data.get("access_token") or data.get("token")
                    
                    if use_admin:
                        self.admin_token = new_token
                    else:
                        self.access_token = new_token
                    return True
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
        return False
    
    def get_valid_token(self, use_admin: bool = False) -> Optional[str]:
        """Get valid access token, refreshing if needed"""
        token = self.admin_token if use_admin else self.access_token
        expiry = self.admin_token_expiry if use_admin else self.token_expiry
        
        # Check if token is expired or about to expire (within 5 minutes)
        if expiry and expiry <= datetime.now() + timedelta(minutes=5):
            if self.refresh_access_token(use_admin):
                token = self.admin_token if use_admin else self.access_token
        
        return token
    
    def _load_endpoint_payloads(self):
        """Load endpoint payloads from test data"""
        try:
            payloads_path = Path(__file__).parent / "test_data" / "endpoint_payloads.json"
            if payloads_path.exists():
                with open(payloads_path, 'r') as f:
                    self.endpoint_payloads = json.load(f)
                logger.info(f"Loaded endpoint payloads from {payloads_path}")
        except Exception as e:
            logger.warning(f"Could not load endpoint payloads: {e}")
            self.endpoint_payloads = {}
    
    def _get_payload_for_endpoint(self, method: str, path: str, module_name: str = None) -> Optional[Dict]:
        """Get payload for an endpoint"""
        if method.upper() not in ["POST", "PUT", "PATCH"]:
            return None
        
        # Try to match by path pattern
        path_lower = path.lower()
        
        # Map common patterns
        payload_key = None
        
        # Auth endpoints
        if "/auth/register" in path:
            payload_key = ("auth", "register", "valid")
        elif "/auth/login" in path:
            payload_key = ("auth", "login", "valid")
        elif "/auth/forgot-password" in path:
            # Use a simple email payload
            return {"email": "test.client@example.com"}
        
        # Client endpoints
        elif "/client/profile" in path and method == "PUT":
            payload_key = ("client", "update_profile", "valid")
        elif "/client/settings" in path and method == "PUT":
            payload_key = ("client", "update_settings", "valid")
        
        # Financial endpoints
        elif "/financial/deposit" in path or "/financial/deposits" in path:
            payload_key = ("financial", "deposit", "valid")
        elif "/financial/withdraw" in path or "/financial/withdrawals" in path:
            payload_key = ("financial", "withdraw", "valid")
        elif "/financial/exchange" in path:
            payload_key = ("financial", "exchange", "valid")
        
        # Trading endpoints
        elif "/trading/orders" in path and method == "POST":
            payload_key = ("trading", "place_order", "market_order")
        
        # Portfolio endpoints
        elif "/portfolio/rebalance" in path or "/portfolio/rebalancing" in path:
            payload_key = ("portfolio", "rebalance", "valid")
        
        # Admin endpoints
        elif "/admin/users" in path and method == "PUT":
            payload_key = ("admin", "update_user", "valid")
        elif "/admin/settings" in path and method == "PUT":
            payload_key = ("admin", "update_settings", "valid")
        
        # Compliance endpoints
        elif "/compliance/kyc" in path and method == "POST":
            payload_key = ("compliance", "submit_kyc", "valid")
        
        # Advanced endpoints
        elif "/advanced/strategies" in path and method == "POST":
            payload_key = ("advanced", "create_strategy", "valid")
        elif "/advanced/backtest" in path and method == "POST":
            payload_key = ("advanced", "backtest", "valid")
        
        # Get payload from loaded data
        if payload_key:
            try:
                payload = self.endpoint_payloads
                for key in payload_key:
                    payload = payload.get(key, {})
                if isinstance(payload, dict) and payload:
                    return payload
            except:
                pass
        
        # Default empty payload for POST/PUT/PATCH
        return {}
    
    def test_all_api_endpoints(self) -> Dict:
        """Test all API endpoints from configuration"""
        logger.info("Testing all API endpoints...")
        api_modules = self.config.get("api_modules", [])
        
        # Load list of not-implemented endpoints to skip
        not_implemented = set()
        not_found_path = Path(__file__).parent.parent.parent.parent / "reports" / "acceptance" / "test_results" / "endpoints_not_found.json"
        if not_found_path.exists():
            try:
                with open(not_found_path, 'r') as f:
                    not_found_data = json.load(f)
                    for ep in not_found_data.get("endpoints", []):
                        if ep.get("note") == "Not found in API":
                            not_implemented.add(ep.get("original", ""))
            except:
                pass
        
        module_results = {}
        
        for module in api_modules:
            module_name = module["name"]
            base_path = module["base_path"]
            endpoints = module.get("endpoints", [])
            
            logger.info(f"Testing module: {module_name}")
            module_results[module_name] = []
            
            for endpoint in endpoints:
                # Skip not-implemented endpoints
                if endpoint in not_implemented:
                    logger.info(f"  Skipping not-implemented: {endpoint}")
                    result = {
                        "type": "api",
                        "method": endpoint.split(" ", 1)[0] if " " in endpoint else "GET",
                        "path": endpoint,
                        "success": None,
                        "description": f"{module_name}: {endpoint}",
                        "skipped": True,
                        "reason": "Not implemented",
                        "timestamp": datetime.now().isoformat()
                    }
                    module_results[module_name].append(result)
                    continue
                
                parts = endpoint.split(" ", 1)
                if len(parts) == 2:
                    method, path = parts
                    full_path = f"{base_path}{path}"
                    
                    # Determine if auth is required (most endpoints require auth)
                    requires_auth = method != "GET" or "profile" in path or "settings" in path
                    
                    # Get payload for POST/PUT/PATCH requests
                    payload = None
                    if method.upper() in ["POST", "PUT", "PATCH"]:
                        payload = self._get_payload_for_endpoint(method, full_path, module_name)
                    
                    result = self.test_api_endpoint(
                        method=method,
                        path=full_path,
                        data=payload,
                        description=f"{module_name}: {endpoint}",
                        requires_auth=requires_auth
                    )
                    
                    # Add suggestions for common errors
                    if not result.get("success"):
                        status_code = result.get("status_code")
                        if status_code == 405:
                            result["suggestion"] = f"Try different HTTP method. Available methods may differ."
                        elif status_code == 404:
                            result["suggestion"] = f"Endpoint may not exist or path is incorrect."
                        elif status_code in [401, 403]:
                            result["suggestion"] = f"Authentication required or insufficient permissions."
                        elif status_code == 422:
                            result["suggestion"] = f"Validation error - check request payload format."
                    
                    module_results[module_name].append(result)
        
        return module_results
    
    def test_all_client_routes(self) -> Dict:
        """Test all client routes from configuration"""
        logger.info("Testing all client routes...")
        routes = self.config.get("client_routes", [])
        
        route_results = {}
        
        for route in routes:
            path = route["path"]
            name = route["name"]
            requires_auth = route.get("requires_auth", False)
            
            url = f"{self.client_url}{path}"
            result = self.test_page_accessibility(
                url=url,
                description=f"Client: {name}",
                requires_auth=requires_auth
            )
            
            if name not in route_results:
                route_results[name] = []
            route_results[name].append(result)
        
        return route_results
    
    def test_all_admin_routes(self) -> Dict:
        """Test all admin routes from configuration"""
        logger.info("Testing all admin routes...")
        routes = self.config.get("admin_routes", [])
        
        route_results = {}
        
        for route in routes:
            path = route["path"]
            name = route["name"]
            requires_auth = route.get("requires_auth", False)
            
            url = f"{self.admin_url}{path}"
            result = self.test_page_accessibility(
                url=url,
                description=f"Admin: {name}",
                requires_auth=requires_auth
            )
            
            if name not in route_results:
                route_results[name] = []
            route_results[name].append(result)
        
        return route_results
    
    def save_results(self, output_path: str):
        """Save test results to JSON file"""
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "environment": {
                "api_url": self.api_url,
                "client_url": self.client_url,
                "admin_url": self.admin_url
            },
            "total_tests": len(self.results),
            "results": self.results
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        logger.info(f"Results saved to: {output_path}")
    
    def get_summary(self) -> Dict:
        """Get summary statistics"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get("success", False))
        failed = total - passed
        
        # Calculate average response time
        api_results = [r for r in self.results if r.get("type") == "api"]
        avg_response_time = 0
        if api_results:
            avg_response_time = sum(r.get("response_time", 0) for r in api_results) / len(api_results)
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total if total > 0 else 0,
            "average_response_time": avg_response_time
        }


if __name__ == "__main__":
    # Example usage
    framework = AcceptanceTestFramework(environment="local")
    
    # Test health endpoint
    framework.test_api_endpoint("GET", "/api/health", expected_status=200, description="Health check")
    
    # Get summary
    summary = framework.get_summary()
    print(f"Tests run: {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    
    # Save results
    framework.save_results("/tmp/acceptance_test_results.json")

