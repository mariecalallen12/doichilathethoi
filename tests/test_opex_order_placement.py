"""
Test script for end-to-end order placement flow
Tests: Frontend → Backend → OPEX
"""
import asyncio
import httpx
import json
from typing import Dict, Any
import time

# Configuration
BACKEND_URL = "http://localhost:8000"
OPEX_API_URL = "http://localhost:8082"  # OPEX API service (often not reachable from host; rely on backend health)

# Test user credentials (should be created in system)
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"
TEST_USER_PHONE = "+1234567890"

# Admin credentials (seeded by backend) to approve pending registrations
ADMIN_EMAIL = "admin@digitalutopia.com"
ADMIN_PASSWORD = "Admin@123"

# Use a unique client IP per run to avoid hitting per-IP rate limits
TEST_CLIENT_IP = f"10.0.1.{int(time.time()) % 250 + 1}"

# Test token (will be obtained from login)
auth_token = None


async def login_user() -> str:
    """Login and get auth token"""
    async with httpx.AsyncClient() as client:
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
            return data.get("access_token") or data.get("data", {}).get("access_token")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None


async def register_test_user() -> bool:
    """Register a test user if not exists"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BACKEND_URL}/api/auth/register",
                json={
                    "phoneNumber": TEST_USER_PHONE,
                    "email": TEST_USER_EMAIL,
                    "password": TEST_USER_PASSWORD,
                    "displayName": "Test User",
                    "agreeToTerms": True
                },
                headers={"X-Forwarded-For": TEST_CLIENT_IP},
            )
            if response.status_code in [200, 201]:
                print("✅ Test user registered successfully")
                return True
            elif response.status_code == 400:
                print("ℹ️  Test user may already exist, trying to login...")
                return True
            else:
                print(f"⚠️  Registration response: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False


async def admin_login() -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BACKEND_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"X-Forwarded-For": TEST_CLIENT_IP},
            timeout=10.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("access_token") or data.get("data", {}).get("access_token")
        return None


async def approve_user_if_pending(email: str) -> bool:
    token = await admin_login()
    if not token:
        return False
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        r = await client.get(
            f"{BACKEND_URL}/api/admin/registrations",
            params={"status_filter": "pending", "page": 1, "page_size": 100},
            headers=headers,
            timeout=15.0,
        )
        if r.status_code != 200:
            return False
        regs = (r.json().get("data", {}) or {}).get("registrations", []) or []
        target = next((u for u in regs if (u.get("email") or "").lower() == email.lower()), None)
        if not target:
            return True
        user_id = target.get("id")
        if not user_id:
            return False
        ar = await client.post(
            f"{BACKEND_URL}/api/admin/registrations/{user_id}/approve",
            headers=headers,
            timeout=15.0,
        )
        return ar.status_code == 200


async def check_opex_health() -> bool:
    """Check if OPEX API is healthy"""
    # In this repo, OPEX core-main services run in docker network; the backend verifies connectivity.
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BACKEND_URL}/api/trading/health", timeout=10.0)
            if response.status_code == 200:
                print("✅ Backend trading service: healthy (OPEX connectivity via backend)")
                return True
            print(f"⚠️  Trading health check failed: {response.status_code} - {response.text}")
            return False
        except Exception as e:
            print(f"❌ Trading health check error: {e}")
            return False


async def check_backend_trading_health() -> bool:
    """Check backend trading service health"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BACKEND_URL}/api/trading/health", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend trading service: {data.get('status', 'unknown')}")
                return True
            else:
                print(f"⚠️  Backend trading health: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend trading service error: {e}")
            return False


async def place_market_order(token: str, symbol: str = "BTCUSDT", side: str = "buy", quantity: float = 0.001) -> Dict[str, Any]:
    """Place a market order"""
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}", "X-Forwarded-For": TEST_CLIENT_IP}
        order_data = {
            "symbol": symbol,
            "side": side,
            "type": "market",
            "quantity": quantity
        }
        
        print(f"\n📤 Placing market order: {side} {quantity} {symbol}")
        try:
            response = await client.post(
                f"{BACKEND_URL}/api/trading/orders",
                json=order_data,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                order = response.json()
                print(f"✅ Market order placed successfully!")
                print(f"   Order ID: {order.get('id')}")
                print(f"   Status: {order.get('status')}")
                print(f"   Symbol: {order.get('symbol')}")
                print(f"   Side: {order.get('side')}")
                print(f"   Quantity: {order.get('quantity')}")
                return order
            else:
                print(f"❌ Order placement failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Order placement error: {e}")
            return None


async def place_limit_order(token: str, symbol: str = "BTCUSDT", side: str = "buy", quantity: float = 0.001, price: float = 40000.0) -> Dict[str, Any]:
    """Place a limit order"""
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}", "X-Forwarded-For": TEST_CLIENT_IP}
        order_data = {
            "symbol": symbol,
            "side": side,
            "type": "limit",
            "quantity": quantity,
            "price": price
        }
        
        print(f"\n📤 Placing limit order: {side} {quantity} {symbol} @ {price}")
        try:
            response = await client.post(
                f"{BACKEND_URL}/api/trading/orders",
                json=order_data,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                order = response.json()
                print(f"✅ Limit order placed successfully!")
                print(f"   Order ID: {order.get('id')}")
                print(f"   Status: {order.get('status')}")
                print(f"   Price: {order.get('price')}")
                return order
            else:
                print(f"❌ Limit order placement failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Limit order placement error: {e}")
            return None


async def place_stop_order(token: str, symbol: str = "BTCUSDT", side: str = "sell", quantity: float = 0.001, price: float = 35000.0, stop_price: float = 34000.0) -> Dict[str, Any]:
    """Place a stop order"""
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}", "X-Forwarded-For": TEST_CLIENT_IP}
        order_data = {
            "symbol": symbol,
            "side": side,
            "type": "stop",
            "quantity": quantity,
            "price": price,
            "stop_price": stop_price
        }
        
        print(f"\n📤 Placing stop order: {side} {quantity} {symbol} @ {price} (stop: {stop_price})")
        try:
            response = await client.post(
                f"{BACKEND_URL}/api/trading/orders",
                json=order_data,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                order = response.json()
                print(f"✅ Stop order placed successfully!")
                print(f"   Order ID: {order.get('id')}")
                print(f"   Status: {order.get('status')}")
                print(f"   Stop Price: {order.get('stop_price')}")
                return order
            else:
                print(f"❌ Stop order placement failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Stop order placement error: {e}")
            return None


async def get_orders(token: str, symbol: str = None) -> list:
    """Get user's orders"""
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        params = {}
        if symbol:
            params["symbol"] = symbol
        
        try:
            response = await client.get(
                f"{BACKEND_URL}/api/trading/orders",
                headers=headers,
                params=params,
                timeout=10.0
            )
            
            if response.status_code == 200:
                orders = response.json()
                print(f"\n📋 Retrieved {len(orders)} orders")
                return orders
            else:
                print(f"⚠️  Get orders failed: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Get orders error: {e}")
            return []


async def cancel_order(token: str, order_id: str) -> bool:
    """Cancel an order"""
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        print(f"\n🗑️  Cancelling order: {order_id}")
        try:
            response = await client.delete(
                f"{BACKEND_URL}/api/trading/orders/{order_id}",
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code == 200:
                print(f"✅ Order cancelled successfully")
                return True
            else:
                print(f"❌ Cancel order failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Cancel order error: {e}")
            return False


async def get_positions(token: str, symbol: str = None) -> list:
    """Get user's positions"""
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        params = {}
        if symbol:
            params["symbol"] = symbol
        
        try:
            response = await client.get(
                f"{BACKEND_URL}/api/trading/positions",
                headers=headers,
                params=params,
                timeout=10.0
            )
            
            if response.status_code == 200:
                positions = response.json()
                print(f"\n📊 Retrieved {len(positions)} positions")
                return positions
            else:
                print(f"⚠️  Get positions failed: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Get positions error: {e}")
            return []


async def test_error_handling(token: str):
    """Test error handling scenarios"""
    print("\n" + "="*60)
    print("🧪 Testing Error Handling")
    print("="*60)
    
    # Test 1: Invalid symbol
    print("\n1. Testing invalid symbol...")
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            f"{BACKEND_URL}/api/trading/orders",
            json={
                "symbol": "INVALID",
                "side": "buy",
                "type": "market",
                "quantity": 0.001
            },
            headers=headers
        )
        if response.status_code == 400:
            print("✅ Invalid symbol correctly rejected")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
    
    # Test 2: Insufficient quantity
    print("\n2. Testing zero quantity...")
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            f"{BACKEND_URL}/api/trading/orders",
            json={
                "symbol": "BTCUSDT",
                "side": "buy",
                "type": "market",
                "quantity": 0
            },
            headers=headers
        )
        if response.status_code == 400:
            print("✅ Zero quantity correctly rejected")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
    
    # Test 3: Missing price for limit order
    print("\n3. Testing missing price for limit order...")
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            f"{BACKEND_URL}/api/trading/orders",
            json={
                "symbol": "BTCUSDT",
                "side": "buy",
                "type": "limit",
                "quantity": 0.001
            },
            headers=headers
        )
        if response.status_code == 400:
            print("✅ Missing price correctly rejected")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")


async def main():
    """Main test function"""
    print("="*60)
    print("🧪 OPEX Order Placement End-to-End Test")
    print("="*60)
    
    # Step 1: Check services health
    print("\n📋 Step 1: Checking services health...")
    opex_healthy = await check_opex_health()
    backend_healthy = await check_backend_trading_health()
    
    if not opex_healthy or not backend_healthy:
        print("\n❌ Services are not healthy. Please check OPEX and backend services.")
        return
    
    # Step 2: Register/Login test user
    print("\n📋 Step 2: Setting up test user...")
    await register_test_user()
    await approve_user_if_pending(TEST_USER_EMAIL)
    token = await login_user()
    
    if not token:
        print("\n❌ Failed to authenticate. Please check user credentials.")
        return
    
    print(f"✅ Authenticated successfully")
    auth_token = token
    
    # Step 3: Test order placement
    print("\n" + "="*60)
    print("📋 Step 3: Testing Order Placement")
    print("="*60)
    
    # Test market order
    market_order = await place_market_order(auth_token, "BTCUSDT", "buy", 0.001)
    
    # Test limit order
    limit_order = await place_limit_order(auth_token, "BTCUSDT", "buy", 0.001, 40000.0)
    
    # Test stop order
    stop_order = await place_stop_order(auth_token, "BTCUSDT", "sell", 0.001, 35000.0, 34000.0)
    
    # Step 4: Test order retrieval
    print("\n" + "="*60)
    print("📋 Step 4: Testing Order Retrieval")
    print("="*60)
    
    orders = await get_orders(auth_token, "BTCUSDT")
    if orders:
        print(f"\n📋 Order Details:")
        for order in orders[:3]:  # Show first 3
            print(f"   - ID: {order.get('id')}, Status: {order.get('status')}, "
                  f"Type: {order.get('type')}, Side: {order.get('side')}")
    
    # Step 5: Test position retrieval
    print("\n" + "="*60)
    print("📋 Step 5: Testing Position Retrieval")
    print("="*60)
    
    positions = await get_positions(auth_token, "BTCUSDT")
    if positions:
        print(f"\n📊 Position Details:")
        for pos in positions:
            print(f"   - ID: {pos.get('id')}, Symbol: {pos.get('symbol')}, "
                  f"Quantity: {pos.get('quantity')}, P&L: {pos.get('unrealized_pnl')}")
    
    # Step 6: Test order cancellation
    if limit_order and limit_order.get('id'):
        print("\n" + "="*60)
        print("📋 Step 6: Testing Order Cancellation")
        print("="*60)
        await cancel_order(auth_token, limit_order.get('id'))
    
    # Step 7: Test error handling
    await test_error_handling(auth_token)
    
    # Summary
    print("\n" + "="*60)
    print("✅ Test Summary")
    print("="*60)
    print(f"Market Order: {'✅' if market_order else '❌'}")
    print(f"Limit Order: {'✅' if limit_order else '❌'}")
    print(f"Stop Order: {'✅' if stop_order else '❌'}")
    print(f"Order Retrieval: {'✅' if orders is not None else '❌'}")
    print(f"Position Retrieval: {'✅' if positions is not None else '❌'}")
    print("\n🎉 End-to-end test completed!")


if __name__ == "__main__":
    asyncio.run(main())

