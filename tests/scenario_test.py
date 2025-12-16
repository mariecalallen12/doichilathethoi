#!/usr/bin/env python3
"""
Scenario Testing Script
Test various scenarios to verify accuracy
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.trading_data_simulator import TradingDataSimulator, get_trading_data_simulator
from app.schemas.trading_simulator import TradingSimScenario, TradingSimScenarioUpdate


class ScenarioTester:
    def __init__(self):
        self.sim = None
        self.results = []

    async def setup(self):
        """Initialize simulator"""
        self.sim = get_trading_data_simulator()
        await self.sim.start(interval_seconds=1.0)
        print("✅ Simulator started")

    async def teardown(self):
        """Cleanup"""
        if self.sim:
            await self.sim.stop()
        print("✅ Simulator stopped")

    async def test_drift(self):
        """Test Case 1: Drift Test"""
        print("\n" + "="*50)
        print("Test Case 1: Drift Test")
        print("="*50)
        
        scenario = TradingSimScenario(
            symbol="BTCUSDT",
            drift=0.001,
            volatility=0.002,
            trend="SIDEWAY",
            target_price=None,
            house_edge=0,
            anti_ta=False,
            formula=None,
        )
        
        await self.sim.update_scenarios(TradingSimScenarioUpdate(scenarios=[scenario]))
        await self.sim.reset_state(["BTCUSDT"])
        
        # Get initial price
        initial_price = self.sim.state["BTCUSDT"]["price"]
        print(f"Initial price: {initial_price:.2f}")
        
        # Wait 60 seconds
        print("Waiting 60 seconds...")
        await asyncio.sleep(60)
        
        # Get final price
        final_price = self.sim.state["BTCUSDT"]["price"]
        print(f"Final price: {final_price:.2f}")
        
        # Calculate actual drift
        actual_drift = (final_price - initial_price) / initial_price / 60
        expected_drift = 0.001
        error = abs(actual_drift - expected_drift) / expected_drift
        
        print(f"Expected drift: {expected_drift}")
        print(f"Actual drift: {actual_drift:.6f}")
        print(f"Error: {error*100:.2f}%")
        
        result = {
            "test": "Drift Test",
            "expected_drift": expected_drift,
            "actual_drift": actual_drift,
            "error_percent": error * 100,
            "passed": error < 0.2,  # Allow 20% error
        }
        
        self.results.append(result)
        return result

    async def test_target_price(self):
        """Test Case 2: Target Price (Mean Reversion)"""
        print("\n" + "="*50)
        print("Test Case 2: Target Price (Mean Reversion)")
        print("="*50)
        
        target_price = 50000.0
        
        scenario = TradingSimScenario(
            symbol="BTCUSDT",
            drift=0,
            volatility=0.002,
            trend="SIDEWAY",
            target_price=target_price,
            house_edge=0,
            anti_ta=False,
            formula=None,
        )
        
        await self.sim.update_scenarios(TradingSimScenarioUpdate(scenarios=[scenario]))
        
        # Set initial price lower than target
        self.sim.state["BTCUSDT"]["price"] = 45000.0
        initial_price = self.sim.state["BTCUSDT"]["price"]
        print(f"Initial price: {initial_price:.2f}")
        print(f"Target price: {target_price:.2f}")
        
        # Wait 5 minutes
        print("Waiting 5 minutes...")
        await asyncio.sleep(300)
        
        # Get final price
        final_price = self.sim.state["BTCUSDT"]["price"]
        print(f"Final price: {final_price:.2f}")
        
        # Check if price moved towards target
        initial_diff = abs(initial_price - target_price)
        final_diff = abs(final_price - target_price)
        convergence = (initial_diff - final_diff) / initial_diff
        
        print(f"Initial difference: {initial_diff:.2f}")
        print(f"Final difference: {final_diff:.2f}")
        print(f"Convergence: {convergence*100:.2f}%")
        
        result = {
            "test": "Target Price",
            "target": target_price,
            "initial_price": initial_price,
            "final_price": final_price,
            "convergence_percent": convergence * 100,
            "passed": convergence > 0.1,  # At least 10% convergence
        }
        
        self.results.append(result)
        return result

    async def test_volatility(self):
        """Test Case 3: Volatility Test"""
        print("\n" + "="*50)
        print("Test Case 3: Volatility Test")
        print("="*50)
        
        # Test with low volatility
        scenario_low = TradingSimScenario(
            symbol="BTCUSDT",
            drift=0,
            volatility=0.001,
            trend="SIDEWAY",
        )
        
        await self.sim.update_scenarios(TradingSimScenarioUpdate(scenarios=[scenario_low]))
        await self.sim.reset_state(["BTCUSDT"])
        
        initial_price = self.sim.state["BTCUSDT"]["price"]
        prices_low = [initial_price]
        
        print("Testing low volatility (0.001)...")
        for _ in range(60):
            await asyncio.sleep(1)
            prices_low.append(self.sim.state["BTCUSDT"]["price"])
        
        # Test with high volatility
        scenario_high = TradingSimScenario(
            symbol="BTCUSDT",
            drift=0,
            volatility=0.01,
            trend="SIDEWAY",
        )
        
        await self.sim.update_scenarios(TradingSimScenarioUpdate(scenarios=[scenario_high]))
        await self.sim.reset_state(["BTCUSDT"])
        
        initial_price = self.sim.state["BTCUSDT"]["price"]
        prices_high = [initial_price]
        
        print("Testing high volatility (0.01)...")
        for _ in range(60):
            await asyncio.sleep(1)
            prices_high.append(self.sim.state["BTCUSDT"]["price"])
        
        # Calculate standard deviation
        import statistics
        std_low = statistics.stdev(prices_low)
        std_high = statistics.stdev(prices_high)
        
        print(f"Low volatility std: {std_low:.2f}")
        print(f"High volatility std: {std_high:.2f}")
        print(f"Ratio: {std_high/std_low:.2f}x")
        
        result = {
            "test": "Volatility Test",
            "low_volatility_std": std_low,
            "high_volatility_std": std_high,
            "ratio": std_high / std_low,
            "passed": std_high > std_low * 2,  # High should be at least 2x
        }
        
        self.results.append(result)
        return result

    async def test_trend(self):
        """Test Case 4: Trend Test"""
        print("\n" + "="*50)
        print("Test Case 4: Trend Test (UPTREND)")
        print("="*50)
        
        scenario = TradingSimScenario(
            symbol="BTCUSDT",
            drift=0.0005,
            volatility=0.002,
            trend="UPTREND",
        )
        
        await self.sim.update_scenarios(TradingSimScenarioUpdate(scenarios=[scenario]))
        await self.sim.reset_state(["BTCUSDT"])
        
        initial_price = self.sim.state["BTCUSDT"]["price"]
        print(f"Initial price: {initial_price:.2f}")
        
        # Wait 5 minutes
        print("Waiting 5 minutes...")
        await asyncio.sleep(300)
        
        final_price = self.sim.state["BTCUSDT"]["price"]
        print(f"Final price: {final_price:.2f}")
        
        price_change = (final_price - initial_price) / initial_price
        print(f"Price change: {price_change*100:.2f}%")
        
        result = {
            "test": "Trend Test (UPTREND)",
            "initial_price": initial_price,
            "final_price": final_price,
            "price_change_percent": price_change * 100,
            "passed": price_change > 0,  # Should increase
        }
        
        self.results.append(result)
        return result

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print("Test Summary")
        print("="*50)
        
        passed = sum(1 for r in self.results if r["passed"])
        total = len(self.results)
        
        print(f"Passed: {passed}/{total}")
        print("")
        
        for result in self.results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"{status} - {result['test']}")
            if "error_percent" in result:
                print(f"  Error: {result['error_percent']:.2f}%")
            if "convergence_percent" in result:
                print(f"  Convergence: {result['convergence_percent']:.2f}%")
            if "ratio" in result:
                print(f"  Ratio: {result['ratio']:.2f}x")
            if "price_change_percent" in result:
                print(f"  Price Change: {result['price_change_percent']:.2f}%")
            print("")


async def main():
    tester = ScenarioTester()
    
    try:
        await tester.setup()
        
        # Run tests
        await tester.test_drift()
        await tester.test_target_price()
        await tester.test_volatility()
        await tester.test_trend()
        
        tester.print_summary()
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await tester.teardown()


if __name__ == "__main__":
    asyncio.run(main())

