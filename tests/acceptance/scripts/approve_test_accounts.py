#!/usr/bin/env python3
"""
Script to approve test accounts for acceptance testing
Approves accounts using admin API or direct database update
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, Optional


def approve_test_accounts(environment="local", api_url="http://localhost:8000", 
                         admin_email: Optional[str] = None, 
                         admin_password: Optional[str] = None):
    """Approve test accounts for acceptance testing"""
    
    try:
        # Load test accounts configuration
        test_data_path = Path(__file__).parent.parent / "test_data" / "test_accounts.json"
        with open(test_data_path, 'r') as f:
            test_data = json.load(f)
        
        env_data = test_data["environments"].get(environment)
        if not env_data:
            print(f"❌ Environment '{environment}' not found in test_accounts.json")
            return False
        
        # Get admin credentials
        if not admin_email or not admin_password:
            admin_data = env_data["admin"]
            admin_email = admin_data["email"]
            admin_password = admin_data["password"]
        
        print("="*60)
        print("Approving Test Accounts")
        print("="*60)
        print()
        
        # Step 1: Login as admin
        print("Step 1: Authenticating as admin...")
        login_response = requests.post(
            f"{api_url}/api/auth/login",
            json={
                "email": admin_email,
                "password": admin_password
            },
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Admin login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text[:200]}")
            return False
        
        admin_data = login_response.json()
        # Extract token
        if isinstance(admin_data, dict):
            if "data" in admin_data:
                admin_token = admin_data["data"].get("access_token") or admin_data["data"].get("token")
            else:
                admin_token = admin_data.get("access_token") or admin_data.get("token")
        else:
            admin_token = None
        
        if not admin_token:
            print("❌ Could not extract admin token from login response")
            return False
        
        print("✅ Admin authenticated successfully")
        print()
        
        # Step 2: Get pending registrations
        print("Step 2: Fetching pending registrations...")
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
        
        registrations_response = requests.get(
            f"{api_url}/api/admin/registrations?status=pending",
            headers=headers,
            timeout=10
        )
        
        pending_registrations = []
        if registrations_response.status_code == 200:
            reg_data = registrations_response.json()
            if isinstance(reg_data, dict):
                if "data" in reg_data:
                    pending_registrations = reg_data["data"].get("registrations", [])
                elif "registrations" in reg_data:
                    pending_registrations = reg_data["registrations"]
            print(f"✅ Found {len(pending_registrations)} pending registrations")
        else:
            print(f"⚠️  Could not fetch registrations: {registrations_response.status_code}")
            print("   Will try to approve by email/phone instead")
        
        # Step 3: Approve client account
        client_data = env_data["client"]
        print()
        print("Step 3: Approving client account...")
        print(f"   Email: {client_data['email']}")
        
        # Try to approve via registration ID first
        client_approved = False
        for reg in pending_registrations:
            if reg.get("email") == client_data["email"] or reg.get("phone") == client_data["phone"]:
                reg_id = reg.get("id") or reg.get("registration_id")
                if reg_id:
                    approve_response = requests.post(
                        f"{api_url}/api/admin/registrations/{reg_id}/approve",
                        headers=headers,
                        json={"notes": "Auto-approved for acceptance testing"},
                        timeout=10
                    )
                    if approve_response.status_code in [200, 201]:
                        print(f"✅ Client account approved via registration ID: {reg_id}")
                        client_approved = True
                        break
        
        # If not found in registrations, try to get user by email and approve directly
        if not client_approved:
            # Try to get user and update directly
            users_response = requests.get(
                f"{api_url}/api/admin/users?email={client_data['email']}",
                headers=headers,
                timeout=10
            )
            if users_response.status_code == 200:
                users_data = users_response.json()
                users = []
                if isinstance(users_data, dict):
                    if "data" in users_data:
                        users = users_data["data"].get("users", [])
                    elif "users" in users_data:
                        users = users_data["users"]
                
                for user in users:
                    if user.get("email") == client_data["email"]:
                        user_id = user.get("id") or user.get("user_id")
                        if user_id:
                            # Update user to approved
                            update_response = requests.put(
                                f"{api_url}/api/admin/users/{user_id}",
                                headers=headers,
                                json={
                                    "status": "active",
                                    "is_approved": True,
                                    "kyc_status": "verified",
                                    "email_verified": True,
                                    "phone_verified": True
                                },
                                timeout=10
                            )
                            if update_response.status_code in [200, 201]:
                                print(f"✅ Client account approved via user update: {user_id}")
                                client_approved = True
                                break
        
        if not client_approved:
            print("⚠️  Could not approve client account automatically")
            print("   Account may need manual approval")
        
        # Step 4: Approve admin account
        admin_data = env_data["admin"]
        print()
        print("Step 4: Approving admin account...")
        print(f"   Email: {admin_data['email']}")
        
        admin_approved = False
        for reg in pending_registrations:
            if reg.get("email") == admin_data["email"] or reg.get("phone") == admin_data["phone"]:
                reg_id = reg.get("id") or reg.get("registration_id")
                if reg_id:
                    approve_response = requests.post(
                        f"{api_url}/api/admin/registrations/{reg_id}/approve",
                        headers=headers,
                        json={"notes": "Auto-approved for acceptance testing"},
                        timeout=10
                    )
                    if approve_response.status_code in [200, 201]:
                        print(f"✅ Admin account approved via registration ID: {reg_id}")
                        admin_approved = True
                        break
        
        if not admin_approved:
            users_response = requests.get(
                f"{api_url}/api/admin/users?email={admin_data['email']}",
                headers=headers,
                timeout=10
            )
            if users_response.status_code == 200:
                users_data = users_response.json()
                users = []
                if isinstance(users_data, dict):
                    if "data" in users_data:
                        users = users_data["data"].get("users", [])
                    elif "users" in users_data:
                        users = users_data["users"]
                
                for user in users:
                    if user.get("email") == admin_data["email"]:
                        user_id = user.get("id") or user.get("user_id")
                        if user_id:
                            # Update user to approved and set admin role
                            update_response = requests.put(
                                f"{api_url}/api/admin/users/{user_id}",
                                headers=headers,
                                json={
                                    "status": "active",
                                    "is_approved": True,
                                    "kyc_status": "verified",
                                    "email_verified": True,
                                    "phone_verified": True,
                                    "role": "admin"
                                },
                                timeout=10
                            )
                            if update_response.status_code in [200, 201]:
                                print(f"✅ Admin account approved via user update: {user_id}")
                                admin_approved = True
                                break
        
        if not admin_approved:
            print("⚠️  Could not approve admin account automatically")
            print("   Account may need manual approval")
        
        # Step 5: Verify accounts can login
        print()
        print("Step 5: Verifying accounts can login...")
        
        # Test client login
        client_login = requests.post(
            f"{api_url}/api/auth/login",
            json={
                "email": client_data["email"],
                "password": client_data["password"]
            },
            timeout=10
        )
        if client_login.status_code == 200:
            print("✅ Client account can login")
        else:
            print(f"⚠️  Client login failed: {client_login.status_code}")
        
        # Test admin login
        admin_login = requests.post(
            f"{api_url}/api/auth/login",
            json={
                "email": admin_data["email"],
                "password": admin_data["password"]
            },
            timeout=10
        )
        if admin_login.status_code == 200:
            print("✅ Admin account can login")
        else:
            print(f"⚠️  Admin login failed: {admin_login.status_code}")
        
        print()
        print("="*60)
        print("Summary")
        print("="*60)
        print(f"Client account: {'✅ Approved' if client_approved else '⚠️  Needs manual approval'}")
        print(f"Admin account: {'✅ Approved' if admin_approved else '⚠️  Needs manual approval'}")
        
        return client_approved and admin_approved
        
    except Exception as e:
        print(f"❌ Error approving test accounts: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Approve test accounts for acceptance testing")
    parser.add_argument(
        "-e", "--environment",
        default="local",
        choices=["local", "staging", "production"],
        help="Environment to approve accounts for"
    )
    parser.add_argument(
        "-u", "--api-url",
        default="http://localhost:8000",
        help="API base URL"
    )
    parser.add_argument(
        "--admin-email",
        help="Admin email (optional, uses test_accounts.json if not provided)"
    )
    parser.add_argument(
        "--admin-password",
        help="Admin password (optional, uses test_accounts.json if not provided)"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("Test Accounts Approval Script")
    print("="*60)
    print(f"Environment: {args.environment}")
    print(f"API URL: {args.api_url}")
    print()
    
    success = approve_test_accounts(
        environment=args.environment,
        api_url=args.api_url,
        admin_email=args.admin_email,
        admin_password=args.admin_password
    )
    
    if success:
        print("\n✅ All test accounts approved successfully!")
        sys.exit(0)
    else:
        print("\n⚠️  Some accounts may need manual approval")
        sys.exit(1)

