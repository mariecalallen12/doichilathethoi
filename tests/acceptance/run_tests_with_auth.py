#!/usr/bin/env python3
"""
Run acceptance tests with authentication
"""

import sys
import json
from pathlib import Path
from acceptance_test_framework import AcceptanceTestFramework

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    # Load test accounts
    test_data_path = Path(__file__).parent / "test_data" / "test_accounts.json"
    with open(test_data_path, 'r') as f:
        test_data = json.load(f)
    
    # Get local environment credentials
    local_env = test_data["environments"]["local"]
    client_creds = local_env["client"]
    admin_creds = local_env["admin"]
    
    print("="*80)
    print("Running Acceptance Tests with Authentication")
    print("="*80)
    print()
    
    # Initialize framework
    framework = AcceptanceTestFramework(environment="local")
    
    # Authenticate as client
    print("Authenticating as client user...")
    if framework.authenticate_client(client_creds["email"], client_creds["password"]):
        print("✓ Client authentication successful")
    else:
        print("✗ Client authentication failed - trying to create test user...")
        # Try to register first
        register_response = framework.test_api_endpoint(
            "POST", 
            "/api/auth/register",
            data={
                "phoneNumber": client_creds["phone"],
                "email": client_creds["email"],
                "password": client_creds["password"],
                "displayName": client_creds["full_name"],
                "agreeToTerms": True
            },
            description="Register test client user"
        )
        if register_response.get("success"):
            print("✓ Test client user registered")
            if framework.authenticate_client(client_creds["email"], client_creds["password"]):
                print("✓ Client authentication successful after registration")
        else:
            print("⚠ Warning: Could not register/authenticate client user")
            print(f"  Response: {register_response.get('status_code')}")
    
    # Authenticate as admin
    print("\nAuthenticating as admin user...")
    if framework.authenticate_admin(admin_creds["email"], admin_creds["password"]):
        print("✓ Admin authentication successful")
    else:
        print("✗ Admin authentication failed")
        print("  Note: Admin user may need to be created manually")
    
    print("\n" + "="*80)
    print("Testing API Endpoints with Authentication")
    print("="*80)
    print()
    
    # Test all API endpoints
    framework.test_all_api_endpoints()
    
    # Test client routes
    print("\n" + "="*80)
    print("Testing Client Routes")
    print("="*80)
    print()
    framework.test_all_client_routes()
    
    # Test admin routes
    print("\n" + "="*80)
    print("Testing Admin Routes")
    print("="*80)
    print()
    framework.test_all_admin_routes()
    
    # Save results
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"/root/forexxx/reports/acceptance/test_results/api_test_results_auth_{timestamp}.json"
    framework.save_results(results_file)
    
    # Print summary
    summary = framework.get_summary()
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Pass Rate: {summary['pass_rate']*100:.2f}%")
    print(f"Average Response Time: {summary['average_response_time']*1000:.2f}ms")
    print()
    print(f"Results saved to: {results_file}")
    print("="*80)
    
    return results_file

if __name__ == "__main__":
    results_file = main()
    print(f"\nTo generate reports, run:")
    print(f"  python3 generate_acceptance_report.py {results_file}")

