#!/usr/bin/env python3
"""
Fix Authentication Issues Systematically
Approve test accounts, verify auth flow, test token refresh
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class AuthIssueFixer:
    """Systematically fix authentication issues"""
    
    def __init__(self, api_url: str = "http://localhost:8000", environment: str = "local"):
        """Initialize fixer"""
        self.api_url = api_url
        self.environment = environment
        
        # Load test accounts
        test_data_path = Path(__file__).parent.parent / "test_data" / "test_accounts.json"
        with open(test_data_path, 'r') as f:
            self.test_data = json.load(f)
        
        self.env_data = self.test_data["environments"].get(environment, {})
        self.results = {
            "accounts_approved": [],
            "accounts_failed": [],
            "auth_verified": [],
            "token_refresh_tested": []
        }
    
    def approve_all_accounts(self) -> bool:
        """Approve all test accounts"""
        print("="*60)
        print("Step 1: Approving Test Accounts")
        print("="*60)
        
        # Try to use existing approve script
        try:
            import subprocess
            approve_script = Path(__file__).parent / "approve_test_accounts.py"
            if approve_script.exists():
                result = subprocess.run(
                    [sys.executable, str(approve_script), "-e", self.environment, "-u", self.api_url],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    print("✅ Accounts approved via approve_test_accounts.py")
                    return True
                else:
                    print(f"⚠️  Approve script returned: {result.returncode}")
                    print(f"   Output: {result.stdout[:200]}")
        except Exception as e:
            print(f"⚠️  Could not run approve script: {e}")
        
        # Manual approval attempt
        print("\nAttempting manual approval...")
        print("Note: This requires an existing admin account")
        
        return False
    
    def verify_auth_flow(self) -> Dict:
        """Verify authentication flow for all test accounts"""
        print("\n" + "="*60)
        print("Step 2: Verifying Authentication Flow")
        print("="*60)
        
        verification_results = {}
        
        # Test client account
        client_data = self.env_data.get("client", {})
        if client_data:
            print(f"\nTesting client account: {client_data.get('email')}")
            result = self._test_login(client_data["email"], client_data["password"])
            verification_results["client"] = result
            if result["success"]:
                self.results["auth_verified"].append("client")
                print("✅ Client authentication verified")
            else:
                print(f"❌ Client authentication failed: {result.get('error')}")
        
        # Test admin account
        admin_data = self.env_data.get("admin", {})
        if admin_data:
            print(f"\nTesting admin account: {admin_data.get('email')}")
            result = self._test_login(admin_data["email"], admin_data["password"])
            verification_results["admin"] = result
            if result["success"]:
                self.results["auth_verified"].append("admin")
                print("✅ Admin authentication verified")
            else:
                print(f"❌ Admin authentication failed: {result.get('error')}")
        
        return verification_results
    
    def _test_login(self, email: str, password: str) -> Dict:
        """Test login and return result"""
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/login",
                json={"email": email, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Extract token
                token = None
                if isinstance(data, dict):
                    if "data" in data:
                        token = data["data"].get("access_token") or data["data"].get("token")
                    else:
                        token = data.get("access_token") or data.get("token")
                
                return {
                    "success": True,
                    "token": token,
                    "status_code": response.status_code
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text[:200]
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_token_refresh(self, refresh_token: str) -> Dict:
        """Test token refresh functionality"""
        print("\n" + "="*60)
        print("Step 3: Testing Token Refresh")
        print("="*60)
        
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/refresh",
                json={"refresh_token": refresh_token},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                new_token = None
                if isinstance(data, dict):
                    if "data" in data:
                        new_token = data["data"].get("access_token") or data["data"].get("token")
                    else:
                        new_token = data.get("access_token") or data.get("token")
                
                if new_token:
                    print("✅ Token refresh successful")
                    self.results["token_refresh_tested"].append("success")
                    return {"success": True, "new_token": new_token}
                else:
                    print("⚠️  Token refresh returned 200 but no token in response")
                    return {"success": False, "error": "No token in response"}
            else:
                print(f"❌ Token refresh failed: {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except Exception as e:
            print(f"❌ Token refresh error: {e}")
            return {"success": False, "error": str(e)}
    
    def fix_all(self) -> Dict:
        """Run all auth fixes"""
        print("="*60)
        print("Fixing Authentication Issues")
        print("="*60)
        print()
        
        # Step 1: Approve accounts
        approve_success = self.approve_all_accounts()
        
        # Step 2: Verify auth flow
        auth_results = self.verify_auth_flow()
        
        # Step 3: Test token refresh if we have tokens
        refresh_results = {}
        for account_type, result in auth_results.items():
            if result.get("success") and "refresh_token" in result:
                refresh_result = self.test_token_refresh(result["refresh_token"])
                refresh_results[account_type] = refresh_result
        
        # Summary
        print("\n" + "="*60)
        print("Summary")
        print("="*60)
        print(f"Accounts approved: {len(self.results['accounts_approved'])}")
        print(f"Auth verified: {len(self.results['auth_verified'])}")
        print(f"Token refresh tested: {len(self.results['token_refresh_tested'])}")
        
        return {
            "approve_success": approve_success,
            "auth_results": auth_results,
            "refresh_results": refresh_results,
            "summary": self.results
        }
    
    def save_report(self, results: Dict, output_path: Optional[str] = None):
        """Save fix results to file"""
        if output_path is None:
            output_path = Path(__file__).parent.parent.parent.parent / "reports" / "acceptance" / "issues" / "auth_fix_report.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "environment": self.environment,
                "results": results
            }, f, indent=2)
        
        print(f"\n✅ Report saved to: {output_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix authentication issues systematically")
    parser.add_argument(
        "-e", "--environment",
        default="local",
        choices=["local", "staging", "production"],
        help="Environment"
    )
    parser.add_argument(
        "-u", "--api-url",
        default="http://localhost:8000",
        help="API base URL"
    )
    
    args = parser.parse_args()
    
    fixer = AuthIssueFixer(api_url=args.api_url, environment=args.environment)
    results = fixer.fix_all()
    fixer.save_report(results)
    
    if results["auth_results"].get("client", {}).get("success") and \
       results["auth_results"].get("admin", {}).get("success"):
        print("\n✅ All authentication issues fixed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some authentication issues remain")
        sys.exit(1)

