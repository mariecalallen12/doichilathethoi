#!/usr/bin/env python3
"""
Script to create test accounts for acceptance testing
Creates client and admin test accounts using API registration endpoint
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, Optional


def create_test_accounts(environment="local", api_url="http://localhost:8000"):
    """Create test accounts for acceptance testing using API"""
    
    try:
        # Load test accounts configuration
        test_data_path = Path(__file__).parent.parent / "test_data" / "test_accounts.json"
        with open(test_data_path, 'r') as f:
            test_data = json.load(f)
        
        env_data = test_data["environments"].get(environment)
        if not env_data:
            print(f"❌ Environment '{environment}' not found in test_accounts.json")
            return False
        
        results = {
            "client": False,
            "admin": False
        }
        
        # Create client account
        client_data = env_data["client"]
        print(f"\n{'='*60}")
        print("Creating Client Test Account")
        print(f"{'='*60}")
        
        # Try to register client
        try:
            register_response = requests.post(
                f"{api_url}/api/auth/register",
                json={
                    "phoneNumber": client_data["phone"],
                    "email": client_data["email"],
                    "password": client_data["password"],
                    "displayName": client_data["full_name"],
                    "agreeToTerms": True
                },
                timeout=10
            )
            
            if register_response.status_code in [200, 201]:
                print(f"✅ Client account registered successfully")
                print(f"   Email: {client_data['email']}")
                print(f"   Phone: {client_data['phone']}")
                results["client"] = True
            elif register_response.status_code == 422:
                # User might already exist, try to login
                print("⚠️  Registration returned 422, checking if user exists...")
                login_response = requests.post(
                    f"{api_url}/api/auth/login",
                    json={
                        "email": client_data["email"],
                        "password": client_data["password"]
                    },
                    timeout=10
                )
                if login_response.status_code == 200:
                    print(f"✅ Client account already exists and can login")
                    results["client"] = True
                else:
                    print(f"⚠️  Could not register or login client")
                    print(f"   Register response: {register_response.status_code}")
                    print(f"   Login response: {login_response.status_code}")
                    if register_response.status_code == 422:
                        print(f"   Register details: {register_response.text[:300]}")
            else:
                print(f"⚠️  Registration failed: {register_response.status_code}")
                print(f"   Response: {register_response.text[:200]}")
        except Exception as e:
            print(f"⚠️  Error creating client account: {e}")
        
        # Create admin account
        admin_data = env_data["admin"]
        print(f"\n{'='*60}")
        print("Creating Admin Test Account")
        print(f"{'='*60}")
        
        # Try to register admin
        try:
            register_response = requests.post(
                f"{api_url}/api/auth/register",
                json={
                    "phoneNumber": admin_data["phone"],
                    "email": admin_data["email"],
                    "password": admin_data["password"],
                    "displayName": admin_data["full_name"],
                    "agreeToTerms": True
                },
                timeout=10
            )
            
            if register_response.status_code in [200, 201]:
                print(f"✅ Admin account registered successfully")
                print(f"   Email: {admin_data['email']}")
                print(f"   Phone: {admin_data['phone']}")
                print("   Note: Admin role may need to be assigned manually")
                results["admin"] = True
            elif register_response.status_code == 422:
                # User might already exist, try to login
                print("⚠️  Registration returned 422, checking if user exists...")
                login_response = requests.post(
                    f"{api_url}/api/auth/login",
                    json={
                        "email": admin_data["email"],
                        "password": admin_data["password"]
                    },
                    timeout=10
                )
                if login_response.status_code == 200:
                    print(f"✅ Admin account already exists and can login")
                    results["admin"] = True
                else:
                    print(f"⚠️  Could not register or login admin")
                    print(f"   Register response: {register_response.status_code}")
                    print(f"   Login response: {login_response.status_code}")
                    if register_response.status_code == 422:
                        print(f"   Register details: {register_response.text[:300]}")
            else:
                print(f"⚠️  Registration failed: {register_response.status_code}")
                print(f"   Response: {register_response.text[:200]}")
        except Exception as e:
            print(f"⚠️  Error creating admin account: {e}")
        
        # Verify accounts can authenticate
        print(f"\n{'='*60}")
        print("Verifying Accounts")
        print(f"{'='*60}")
        
        # Test client login
        try:
            response = requests.post(
                f"{api_url}/api/auth/login",
                json={
                    "email": client_data["email"],
                    "password": client_data["password"]
                },
                timeout=10
            )
            if response.status_code == 200:
                token_data = response.json()
                print("✅ Client authentication verified")
                print(f"   Token received: {len(token_data.get('access_token', ''))} chars")
            else:
                print(f"⚠️  Client authentication failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"⚠️  Could not verify client authentication: {e}")
        
        # Test admin login
        try:
            response = requests.post(
                f"{api_url}/api/auth/login",
                json={
                    "email": admin_data["email"],
                    "password": admin_data["password"]
                },
                timeout=10
            )
            if response.status_code == 200:
                token_data = response.json()
                print("✅ Admin authentication verified")
                print(f"   Token received: {len(token_data.get('access_token', ''))} chars")
            else:
                print(f"⚠️  Admin authentication failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"⚠️  Could not verify admin authentication: {e}")
        
        # Step 6: Try to auto-approve accounts
        print(f"\n{'='*60}")
        print("Auto-approving Accounts")
        print(f"{'='*60}")
        
        # Try to run approve script if accounts were created
        if results["client"] or results["admin"]:
            try:
                import subprocess
                approve_result = subprocess.run(
                    [sys.executable, str(Path(__file__).parent / "approve_test_accounts.py"), 
                     "-e", environment],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if approve_result.returncode == 0:
                    print("✅ Accounts approved successfully")
                else:
                    print("⚠️  Auto-approval failed (may need existing admin account)")
                    print("   Run manually: python3 approve_test_accounts.py -e local")
            except Exception as e:
                print(f"⚠️  Could not auto-approve: {e}")
                print("   Run manually: python3 approve_test_accounts.py -e local")
        else:
            print("⚠️  No accounts to approve (creation failed)")
        
        print(f"\n{'='*60}")
        print("Summary")
        print(f"{'='*60}")
        print(f"Client account: {'✅ Created/Verified' if results['client'] else '❌ Failed'}")
        print(f"Admin account: {'✅ Created/Verified' if results['admin'] else '❌ Failed'}")
        
        return all(results.values())
        
    except Exception as e:
        print(f"❌ Error creating test accounts: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create test accounts for acceptance testing")
    parser.add_argument(
        "-e", "--environment",
        default="local",
        choices=["local", "staging", "production"],
        help="Environment to create accounts for"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("Test Accounts Creation Script")
    print("="*60)
    print(f"Environment: {args.environment}")
    print()
    
    success = create_test_accounts(args.environment)
    
    if success:
        print("\n✅ All test accounts created successfully!")
        sys.exit(0)
    else:
        print("\n❌ Failed to create some test accounts")
        sys.exit(1)

