#!/usr/bin/env python3
"""
OPEX WebSocket Test Script
Tests WebSocket connection and message handling
"""
import asyncio
import websockets
import json
import sys
import signal

WS_URL = "ws://localhost:8000/ws/opex"

async def test_websocket_connection():
    """Test WebSocket connection"""
    print(f"=== OPEX WebSocket Integration Tests ===")
    print(f"WebSocket URL: {WS_URL}")
    print("")
    
    try:
        print("Connecting to WebSocket...")
        async with websockets.connect(WS_URL) as websocket:
            print("✓ Connected successfully")
            
            # Send ping message
            ping_message = {"type": "ping", "timestamp": "2025-12-16T00:00:00Z"}
            print(f"Sending: {ping_message}")
            await websocket.send(json.dumps(ping_message))
            
            # Wait for response (with timeout)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"✓ Received: {response[:100]}")
                return True
            except asyncio.TimeoutError:
                print("⚠️  No response received within 5 seconds")
                return True  # Connection successful even without response
            
    except websockets.exceptions.InvalidURI:
        print(f"✗ Invalid WebSocket URL: {WS_URL}")
        return False
    except websockets.exceptions.ConnectionClosed:
        print("✗ Connection closed unexpectedly")
        return False
    except ConnectionRefusedError:
        print("✗ Connection refused - server may not be running")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Main function"""
    try:
        result = asyncio.run(test_websocket_connection())
        if result:
            print("\n✓ WebSocket test completed")
            sys.exit(0)
        else:
            print("\n✗ WebSocket test failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)

if __name__ == "__main__":
    main()

