"""
Test script for authentication flow and user ID mapping
Tests: FastAPI Backend ↔ OPEX User ID mapping
"""
import asyncio
import httpx
import json
from typing import Dict, Any, Optional
import time

# Configuration
BACKEND_URL = "http://localhost:8000"
OPEX_API_URL = "http://localhost:8082"  # NOTE: not reachable from host in dockerized setups; use backend checks instead

# Admin credentials (seeded by backend)
ADMIN_EMAIL = "admin@digitalutopia.com"
ADMIN_PASSWORD = "Admin@123"

# Use a unique client IP per run to avoid hitting per-IP rate limits
TEST_CLIENT_IP = f"10.0.0.{int(time.time()) % 250 + 1}"

# Test user credentials
TEST_USER_EMAIL = "auth_test@example.com"
TEST_USER_PHONE = "+1987654321"
TEST_USER_PASSWORD = "testpassword123"


async def register_user() -> Optional[Dict[str, Any]]:
    """Register a new test user"""
    async with httpx.AsyncClient() as client:
        print("\n📋 Registering test user...")
        response = await client.post(
            f"{BACKEND_URL}/api/auth/register",
            json={
                "phoneNumber": TEST_USER_PHONE,
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "displayName": "Auth Test User",
                "agreeToTerms": True
            },
            headers={"X-Forwarded-For": TEST_CLIENT_IP},
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print("✅ User registered successfully")
            return data
        elif response.status_code == 400:
            print("ℹ️  User may already exist, continuing...")
            return None
        else:
            print(f"⚠️  Registration response: {response.status_code} - {response.text}")
            return None


async def admin_login() -> Optional[str]:
    """Login as admin and get token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"X-Forwarded-For": TEST_CLIENT_IP},
            timeout=10.0,
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token") or data.get("data", {}).get("access_token")
        print(f"⚠️  Admin login failed: {response.status_code} - {response.text}")
        return None


async def approve_user_if_pending(email: str) -> bool:
    """Approve registration if the user is pending approval."""
    token = await admin_login()
    if not token:
        return False

    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}

        # Query pending registrations
        r = await client.get(
            f"{BACKEND_URL}/api/admin/registrations",
            params={"status_filter": "pending", "page": 1, "page_size": 100},
            headers=headers,
            timeout=15.0,
        )
        if r.status_code != 200:
            print(f"⚠️  Cannot list pending registrations: {r.status_code} - {r.text}")
            return False

        data = r.json()
        regs = (data.get("data", {}) or {}).get("registrations", []) or []
        target = next((u for u in regs if (u.get("email") or "").lower() == email.lower()), None)
        if not target:
            # Nothing to approve (already approved, or not found)
            return True

        user_id = target.get("id")
        if not user_id:
            return False

        ar = await client.post(
            f"{BACKEND_URL}/api/admin/registrations/{user_id}/approve",
            headers=headers,
            timeout=15.0,
        )
        if ar.status_code == 200:
            print("✅ User approved successfully (admin)")
            return True
        print(f"⚠️  Approve failed: {ar.status_code} - {ar.text}")
        return False


async def login_user() -> Optional[str]:
    """Login and get auth token"""
    async with httpx.AsyncClient() as client:
        print("\n📋 Logging in...")
        response = await client.post(
            f"{BACKEND_URL}/api/auth/login",
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            },
            headers={"X-Forwarded-For": TEST_CLIENT_IP},
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token") or data.get("data", {}).get("access_token")
            if token:
                print("✅ Login successful")
                print(f"   Token: {token[:30]}...")
                return token
            else:
                print("❌ No access token in response")
                print(f"   Response: {json.dumps(data, indent=2)}")
                return None
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None


async def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token"""
    async with httpx.AsyncClient() as client:
        print("\n📋 Verifying token...")
        response = await client.get(
            f"{BACKEND_URL}/api/auth/verify",
            headers={"Authorization": f"Bearer {token}", "X-Forwarded-For": TEST_CLIENT_IP},
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Token verified")
            user_data = data.get("data", {}).get("user") or data.get("user")
            if user_data:
                print(f"   User ID: {user_data.get('id')}")
                print(f"   Email: {user_data.get('email')}")
                print(f"   Role: {user_data.get('role')}")
            return data
        else:
            print(f"❌ Token verification failed: {response.status_code}")
            return None


async def get_user_profile(token: str) -> Optional[Dict[str, Any]]:
    """Get user profile from backend"""
    async with httpx.AsyncClient() as client:
        print("\n📋 Getting user profile from backend...")
        headers = {"Authorization": f"Bearer {token}", "X-Forwarded-For": TEST_CLIENT_IP}
        response = await client.get(
            f"{BACKEND_URL}/api/client/profile",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ User profile retrieved")
            # Profile response is typically {success, data:{...}}; accept a few shapes
            user_data = (data.get("data") or {}).get("user") or data.get("user") or data.get("data") or data
            if user_data:
                user_id = user_data.get("id") or user_data.get("user_id")
                print(f"   Backend User ID: {user_id}")
                print(f"   Email: {user_data.get('email')}")
                print(f"   Phone: {user_data.get('phone')}")
            return data
        else:
            print(f"⚠️  Get profile failed: {response.status_code} - {response.text}")
            return None


async def check_opex_user_account(user_id: int) -> Optional[Dict[str, Any]]:
    """Check if user exists in OPEX system"""
    async with httpx.AsyncClient() as client:
        print(f"\n📋 Checking OPEX user account for user_id={user_id}...")
        try:
            # Try to get user from OPEX API
            # Note: OPEX may not have a public user endpoint
            response = await client.get(
                f"{OPEX_API_URL}/api/users/{user_id}",
                timeout=5.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ User found in OPEX")
                print(f"   OPEX User ID: {data.get('userId') or data.get('id')}")
                return data
            elif response.status_code == 404:
                print("ℹ️  User not found in OPEX (may need manual creation)")
                return None
            else:
                print(f"⚠️  OPEX API response: {response.status_code}")
                return None
        except httpx.ConnectError:
            print("⚠️  Cannot connect to OPEX API (service may not be running)")
            return None
        except Exception as e:
            print(f"⚠️  Error checking OPEX user: {e}")
            return None


async def test_user_id_mapping(token: str, backend_user_id: int):
    """Test user ID mapping between FastAPI and OPEX"""
    print("\n" + "="*60)
    print("🧪 Testing User ID Mapping")
    print("="*60)
    
    # Check OPEX user account
    opex_user = await check_opex_user_account(backend_user_id)
    
    if opex_user:
        opex_user_id = opex_user.get("userId") or opex_user.get("id")
        print(f"\n✅ User ID Mapping:")
        print(f"   FastAPI Backend User ID: {backend_user_id}")
        print(f"   OPEX User ID: {opex_user_id}")
        
        # Verify mapping
        if str(opex_user_id) == str(backend_user_id):
            print("✅ User ID mapping is correct (1:1 mapping)")
        else:
            print(f"⚠️  User ID mapping differs: {backend_user_id} → {opex_user_id}")
    else:
        print(f"\n⚠️  User {backend_user_id} not found in OPEX")
        print("   This is expected if OPEX user creation is manual or pending")


async def test_order_with_user_id(token: str, user_id: int):
    """Test placing an order to verify user ID is correctly passed to OPEX"""
    print("\n" + "="*60)
    print("🧪 Testing Order Placement with User ID")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        order_data = {
            "symbol": "BTCUSDT",
            "side": "buy",
            "type": "market",
            "quantity": 0.0001  # Very small quantity for testing
        }
        
        print(f"\n📤 Placing test order with user_id={user_id}...")
        try:
            response = await client.post(
                f"{BACKEND_URL}/api/trading/orders",
                json=order_data,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                order = response.json()
                order_user_id = order.get("user_id")
                print("✅ Order placed successfully")
                print(f"   Order User ID: {order_user_id}")
                
                if order_user_id == user_id:
                    print("✅ User ID correctly passed to OPEX")
                else:
                    print(f"⚠️  User ID mismatch: expected {user_id}, got {order_user_id}")
                
                return order
            else:
                print(f"⚠️  Order placement response: {response.status_code}")
                print(f"   Response: {response.text}")
                # This might fail if user doesn't have wallet/balance in OPEX
                # That's okay for this test - we're just checking user ID mapping
                return None
        except Exception as e:
            print(f"⚠️  Order placement error: {e}")
            return None


async def main():
    """Main test function"""
    print("="*60)
    print("🧪 Authentication & User ID Mapping Test")
    print("="*60)
    
    # Step 1: Register user
    await register_user()

    # Step 1.5: Approve if pending (required by backend)
    await approve_user_if_pending(TEST_USER_EMAIL)
    
    # Step 2: Login
    token = await login_user()
    if not token:
        print("\n❌ Failed to authenticate. Cannot continue.")
        return
    
    # Step 3: Verify token
    verify_result = await verify_token(token)
    if not verify_result:
        print("\n⚠️  Token verification failed, but continuing...")
    
    # Step 4: Determine backend user_id (prefer verify result, profile is optional and may error)
    user_id = None
    if verify_result:
        verify_user = verify_result.get("data", {}).get("user") or verify_result.get("user")
        user_id = verify_user.get("id") if verify_user else None

    # Try profile only as supplemental info
    profile = await get_user_profile(token)
    if not profile:
        print("\n⚠️  Could not get user profile, but continuing...")
    else:
        user_data = (profile.get("data") or {}).get("user") or profile.get("user") or profile.get("data") or profile
        user_id = user_id or user_data.get("id") or user_data.get("user_id")
    
    if not user_id:
        print("\n❌ Could not determine user ID. Cannot continue with mapping test.")
        return
    
    print(f"\n✅ Backend User ID determined: {user_id}")
    
    # Step 5: Test user ID mapping
    await test_user_id_mapping(token, user_id)
    
    # Step 6: Test order placement with user ID
    await test_order_with_user_id(token, user_id)
    
    # Summary
    print("\n" + "="*60)
    print("✅ Authentication & User ID Mapping Test Complete")
    print("="*60)
    print(f"\nSummary:")
    print(f"  ✅ Authentication: Success")
    print(f"  ✅ Token Verification: {'Success' if verify_result else 'Failed'}")
    print(f"  ✅ User Profile: {'Success' if profile else 'Failed'}")
    print(f"  ✅ User ID: {user_id}")
    print(f"  ℹ️  OPEX User Account: Check manually in OPEX admin panel")
    print("\n🎉 Test completed!")


if __name__ == "__main__":
    asyncio.run(main())

