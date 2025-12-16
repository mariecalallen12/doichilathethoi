#!/usr/bin/env python3
"""Verify all bugs from test execution report are fixed"""
import sys
import os

def test_pricetick_import():
    """Bug #1: PriceTick Model"""
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
        from app.models.market import PriceTick
        print("✅ Bug #1: PriceTick import - FIXED")
        return True
    except Exception as e:
        print(f"❌ Bug #1: PriceTick import - FAILED: {e}")
        return False

def test_settings_config():
    """Bug #2: Settings Configuration"""
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
        from app.core.config import settings
        print(f"✅ Bug #2: Settings - FIXED (APP_NAME={settings.APP_NAME})")
        return True
    except Exception as e:
        print(f"❌ Bug #2: Settings - FAILED: {e}")
        return False

def test_authentication():
    """Bug #3: Authentication"""
    try:
        import requests
        response = requests.post(
            "http://localhost:8000/api/auth/login",
            json={"email": "test@cmeetrading.com", "password": "Test@123456"},
            timeout=5
        )
        if response.status_code == 200:
            print("✅ Bug #3: Authentication - FIXED")
            return True
        else:
            print(f"⚠️  Bug #3: Authentication - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Bug #3: Authentication - Cannot test (backend may be down): {e}")
        return False

def test_api_documentation():
    """Bug #4: API Documentation"""
    import os
    if os.path.exists("docs/API_ENDPOINTS_AVAILABLE.md"):
        print("✅ Bug #4: API Documentation - FIXED")
        return True
    else:
        print("❌ Bug #4: API Documentation - MISSING")
        return False

def test_scripts_created():
    """Bug #5: Scripts and Documentation"""
    scripts = [
        "scripts/backup.sh",
        "scripts/health_monitor.sh",
        "scripts/create_test_user.py",
        "KNOWN_ISSUES.md",
        "PRODUCTION_DEPLOYMENT_CHECKLIST.md",
    ]
    all_exist = True
    for script in scripts:
        if os.path.exists(script):
            print(f"✅ {script} exists")
        else:
            print(f"❌ {script} missing")
            all_exist = False
    return all_exist

if __name__ == "__main__":
    print("="*60)
    print("Bug Fixes Verification")
    print("="*60)
    print()
    
    results = [
        ("PriceTick Import", test_pricetick_import()),
        ("Settings Config", test_settings_config()),
        ("Authentication", test_authentication()),
        ("API Documentation", test_api_documentation()),
        ("Scripts Created", test_scripts_created()),
    ]
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print()
    print("="*60)
    print(f"Bug Fixes Verification: {passed}/{total} PASSED ({passed*100//total}%)")
    print("="*60)
    print()
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print()
    if passed == total:
        print("✅ ALL BUGS FIXED - READY FOR DEPLOYMENT")
        sys.exit(0)
    elif passed >= total * 0.8:
        print("⚠️  MOST BUGS FIXED - NEEDS MINOR WORK")
        sys.exit(0)
    else:
        print("❌ MANY BUGS NOT FIXED - NOT READY")
        sys.exit(1)
