#!/usr/bin/env python3
"""
Customization API Test Suite (Python)
======================================

Comprehensive tests for customization functionality
"""

import requests
import json
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class TestConfig:
    """Test configuration"""
    base_url: str = "http://localhost:8000"
    admin_email: str = "admin@cmeetrading.com"
    admin_password: str = "admin123"
    token: Optional[str] = None


class CustomizationTester:
    """Test suite for customization API"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.session = requests.Session()
        self.created_rules = []
        self.created_sessions = []
    
    def print_header(self, text: str):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}\n")
    
    def print_success(self, text: str):
        """Print success message"""
        print(f"✅ {text}")
    
    def print_error(self, text: str):
        """Print error message"""
        print(f"❌ {text}")
    
    def print_info(self, text: str):
        """Print info message"""
        print(f"ℹ️  {text}")
    
    def login(self) -> bool:
        """Login and get JWT token"""
        self.print_header("Step 1: Admin Login")
        
        try:
            response = self.session.post(
                f"{self.config.base_url}/api/auth/login",
                json={
                    "email": self.config.admin_email,
                    "password": self.config.admin_password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.config.token = data.get('access_token') or data.get('token')
                
                if self.config.token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.config.token}'
                    })
                    self.print_success("Login successful")
                    return True
            
            self.print_error(f"Login failed: {response.status_code}")
            print(response.text)
            return False
            
        except Exception as e:
            self.print_error(f"Login error: {e}")
            return False
    
    def create_rules(self):
        """Create test customization rules"""
        self.print_header("Step 2: Create Customization Rules")
        
        rules = [
            {
                "name": "BTC_BULLISH",
                "symbol": "BTC",
                "price_adjustment": 5.0,
                "change_adjustment": 3.0,
                "force_signal": "STRONG_BUY",
                "confidence_boost": 20.0,
                "enabled": True
            },
            {
                "name": "ETH_MODERATE",
                "symbol": "ETH",
                "price_adjustment": 2.5,
                "change_adjustment": 1.5,
                "force_signal": "BUY",
                "confidence_boost": 10.0,
                "enabled": True
            },
            {
                "name": "GLOBAL_BOOST",
                "symbol": "*",
                "confidence_boost": 5.0,
                "enabled": False
            }
        ]
        
        for rule in rules:
            try:
                response = self.session.post(
                    f"{self.config.base_url}/api/admin/customizations/rules",
                    json=rule
                )
                
                if response.status_code in [200, 201]:
                    self.created_rules.append(rule['name'])
                    self.print_success(f"Created rule: {rule['name']}")
                else:
                    self.print_error(f"Failed to create rule {rule['name']}: {response.status_code}")
                    
            except Exception as e:
                self.print_error(f"Error creating rule {rule['name']}: {e}")
    
    def list_rules(self):
        """List all customization rules"""
        self.print_header("Step 3: List All Rules")
        
        try:
            response = self.session.get(
                f"{self.config.base_url}/api/admin/customizations/rules"
            )
            
            if response.status_code == 200:
                rules = response.json()
                self.print_success(f"Total rules: {len(rules)}")
                
                for rule in rules:
                    print(f"  - {rule['name']}: symbol={rule['symbol']}, "
                          f"price_adj={rule.get('price_adjustment', 'N/A')}, "
                          f"enabled={rule['enabled']}")
                
                return rules
            else:
                self.print_error(f"Failed to list rules: {response.status_code}")
                
        except Exception as e:
            self.print_error(f"Error listing rules: {e}")
        
        return []
    
    def create_sessions(self) -> Dict[str, str]:
        """Create test sessions"""
        self.print_header("Step 4: Create Sessions")
        
        sessions = {}
        session_configs = [
            {"name": "Marketing Campaign Q1"},
            {"name": "VIP Demo Session"}
        ]
        
        for config in session_configs:
            try:
                response = self.session.post(
                    f"{self.config.base_url}/api/admin/customizations/sessions",
                    json=config
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    session_id = data['session_id']
                    sessions[config['name']] = session_id
                    self.created_sessions.append(session_id)
                    self.print_success(f"Created session: {config['name']}")
                    self.print_info(f"  Session ID: {session_id}")
                else:
                    self.print_error(f"Failed to create session: {response.status_code}")
                    
            except Exception as e:
                self.print_error(f"Error creating session: {e}")
        
        return sessions
    
    def bind_rules_to_session(self, session_id: str, rule_names: list):
        """Bind rules to a session"""
        self.print_info(f"Binding rules to session {session_id[:8]}...")
        
        for rule_name in rule_names:
            try:
                response = self.session.post(
                    f"{self.config.base_url}/api/admin/customizations/sessions/{session_id}/bind",
                    json={"rule_name": rule_name}
                )
                
                if response.status_code == 200:
                    self.print_success(f"  Bound {rule_name}")
                else:
                    self.print_error(f"  Failed to bind {rule_name}")
                    
            except Exception as e:
                self.print_error(f"  Error binding {rule_name}: {e}")
    
    def activate_session(self, session_id: str):
        """Activate a session"""
        try:
            response = self.session.post(
                f"{self.config.base_url}/api/admin/customizations/sessions/{session_id}/activate"
            )
            
            if response.status_code == 200:
                self.print_success(f"Activated session {session_id[:8]}...")
                return True
            else:
                self.print_error(f"Failed to activate session: {response.status_code}")
                
        except Exception as e:
            self.print_error(f"Error activating session: {e}")
        
        return False
    
    def test_market_data(self, symbol: str = "BTC", session_id: Optional[str] = None):
        """Test market data endpoint"""
        headers = {}
        if session_id:
            headers['X-Session-Id'] = session_id
        
        try:
            response = requests.get(
                f"{self.config.base_url}/api/market/prices?symbol={symbol}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if symbol in data.get('prices', {}):
                    price_data = data['prices'][symbol]
                    price = price_data.get('price', 0)
                    change = price_data.get('change_24h', 0)
                    
                    session_info = f" (Session: {session_id[:8]}...)" if session_id else " (No session)"
                    self.print_success(f"{symbol} data{session_info}")
                    print(f"  Price: ${price:.2f}")
                    print(f"  Change 24h: {change:.2f}%")
                    
                    return price_data
            else:
                self.print_error(f"Failed to fetch {symbol} price: {response.status_code}")
                
        except Exception as e:
            self.print_error(f"Error fetching market data: {e}")
        
        return None
    
    def test_manual_override(self, symbol: str = "BTC"):
        """Test manual override"""
        self.print_header("Step 9: Test Manual Override")
        
        try:
            response = self.session.post(
                f"{self.config.base_url}/api/admin/customizations/manual-override",
                json={
                    "symbol": symbol,
                    "price": 50000.0,
                    "signal": "STRONG_BUY",
                    "confidence": 95.0
                }
            )
            
            if response.status_code == 200:
                self.print_success(f"Manual override set for {symbol}")
                
                # Test the override
                self.print_info("Testing override...")
                time.sleep(0.5)
                
                override_data = self.test_market_data(symbol)
                if override_data and override_data['price'] == 50000.0:
                    self.print_success("Override working correctly! Price = $50,000")
                else:
                    self.print_error("Override not applied correctly")
                    
            else:
                self.print_error(f"Failed to set override: {response.status_code}")
                
        except Exception as e:
            self.print_error(f"Error setting override: {e}")
    
    def get_system_status(self):
        """Get customization system status"""
        self.print_header("Step 10: System Status")
        
        try:
            response = self.session.get(
                f"{self.config.base_url}/api/admin/customizations/status"
            )
            
            if response.status_code == 200:
                status = response.json()
                self.print_success("System Status:")
                print(json.dumps(status, indent=2))
                return status
            else:
                self.print_error(f"Failed to get status: {response.status_code}")
                
        except Exception as e:
            self.print_error(f"Error getting status: {e}")
        
        return None
    
    def cleanup(self):
        """Cleanup test data"""
        self.print_header("Cleanup")
        
        try:
            # Clear manual overrides
            response = self.session.delete(
                f"{self.config.base_url}/api/admin/customizations/manual-override"
            )
            if response.status_code == 200:
                self.print_success("Manual overrides cleared")
            
            # Deactivate sessions
            for session_id in self.created_sessions:
                self.session.post(
                    f"{self.config.base_url}/api/admin/customizations/sessions/{session_id}/deactivate"
                )
            
            self.print_success("Sessions deactivated")
            self.print_info("Test data preserved (delete manually if needed)")
            
        except Exception as e:
            self.print_error(f"Cleanup error: {e}")
    
    def run_all_tests(self):
        """Run complete test suite"""
        self.print_header("CUSTOMIZATION API TEST SUITE")
        
        # Login
        if not self.login():
            return
        
        # Create rules
        self.create_rules()
        time.sleep(0.5)
        
        # List rules
        self.list_rules()
        time.sleep(0.5)
        
        # Create sessions
        sessions = self.create_sessions()
        time.sleep(0.5)
        
        if not sessions:
            self.print_error("No sessions created, aborting tests")
            return
        
        # Bind rules
        self.print_header("Step 5: Bind Rules to Sessions")
        
        marketing_session = sessions.get("Marketing Campaign Q1")
        if marketing_session:
            self.bind_rules_to_session(marketing_session, ["BTC_BULLISH", "ETH_MODERATE"])
        
        vip_session = sessions.get("VIP Demo Session")
        if vip_session:
            self.bind_rules_to_session(vip_session, ["BTC_BULLISH", "GLOBAL_BOOST"])
        
        time.sleep(0.5)
        
        # Activate session
        self.print_header("Step 6: Activate Session")
        if marketing_session:
            self.activate_session(marketing_session)
        
        time.sleep(0.5)
        
        # Test without session
        self.print_header("Step 7: Test Without Customization")
        original_data = self.test_market_data("BTC")
        
        time.sleep(0.5)
        
        # Test with session
        self.print_header("Step 8: Test With Customization")
        if marketing_session:
            customized_data = self.test_market_data("BTC", marketing_session)
            
            # Compare
            if original_data and customized_data:
                original_price = original_data.get('price', 0)
                customized_price = customized_data.get('price', 0)
                
                if customized_price > original_price:
                    diff = ((customized_price - original_price) / original_price) * 100
                    self.print_success(f"Customization applied! Price increased by {diff:.2f}%")
                else:
                    self.print_error("Customization may not be working")
        
        time.sleep(0.5)
        
        # Test manual override
        self.test_manual_override()
        
        time.sleep(0.5)
        
        # Get status
        self.get_system_status()
        
        # Cleanup
        print("\n")
        cleanup_choice = input("Clean up test data? (y/N): ").lower()
        if cleanup_choice == 'y':
            self.cleanup()
        
        # Summary
        self.print_header("TEST SUMMARY")
        print(f"✅ Created {len(self.created_rules)} rules")
        print(f"✅ Created {len(self.created_sessions)} sessions")
        print(f"✅ All tests completed!")
        print(f"\nSession IDs for reference:")
        for name, sid in sessions.items():
            print(f"  - {name}: {sid}")


if __name__ == "__main__":
    print("🚀 Starting Customization API Tests...\n")
    
    config = TestConfig()
    tester = CustomizationTester(config)
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Tests failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✨ Test suite completed!\n")
