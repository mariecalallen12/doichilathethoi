#!/usr/bin/env python3
"""
Run acceptance tests using existing accounts (skip account creation)
Useful when rate limiting prevents new account creation
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from acceptance_test_framework import AcceptanceTestFramework

def main():
    # Load test accounts
    test_data_path = Path(__file__).parent.parent / "test_data" / "test_accounts.json"
    with open(test_data_path, 'r') as f:
        test_data = json.load(f)
    
    # Get local environment credentials
    local_env = test_data["environments"]["local"]
    client_creds = local_env["client"]
    admin_creds = local_env["admin"]
    
    print("="*80)
    print("Running Acceptance Tests with Existing Accounts")
    print("="*80)
    print("Note: Skipping account creation due to rate limiting")
    print()
    
    # Initialize framework
    framework = AcceptanceTestFramework(environment="local")
    
    # Try to authenticate (accounts should already exist)
    print("Authenticating as client user...")
    if framework.authenticate_client(client_creds["email"], client_creds["password"]):
        print("✓ Client authentication successful")
    else:
        print("✗ Client authentication failed")
        print("  Note: Account may not exist or credentials incorrect")
        print("  You may need to:")
        print("    1. Wait for rate limit to reset (60 minutes)")
        print("    2. Create accounts manually")
        print("    3. Use different test accounts")
        return None
    
    # Authenticate as admin
    print("\nAuthenticating as admin user...")
    if framework.authenticate_admin(admin_creds["email"], admin_creds["password"]):
        print("✓ Admin authentication successful")
    else:
        print("✗ Admin authentication failed")
        print("  Note: Admin account may not exist")
    
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
    if results_file:
        print(f"\nTo generate reports, run:")
        print(f"  python3 generate_acceptance_report.py {results_file}")

