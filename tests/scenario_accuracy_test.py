#!/usr/bin/env python3
"""
Scenario Accuracy Test (AC-3)
Mục tiêu: Verify scenario accuracy ±0.5%

Test: Scenario +5% trong 1h phải đạt ±0.5%
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any
import json

# Add backend to path
BACKEND_DIR = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.services.trading_data_simulator import TradingDataSimulator, TradingSimScenario
from app.schemas.trading_simulator import TradingSimScenario as ScenarioSchema


class ScenarioAccuracyTest:
    """Test scenario accuracy against target price"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {
            "tests": [],
            "summary": {},
        }
    
    async def test_scenario_accuracy(
        self,
        scenario_name: str,
        initial_price: float,
        target_percent: float,
        duration_seconds: float,
        tolerance_percent: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Test scenario accuracy
        
        Args:
            scenario_name: Name of the test scenario
            initial_price: Starting price
            target_percent: Target price change percentage (e.g., 5.0 for +5%)
            duration_seconds: Test duration in seconds (accelerated)
            tolerance_percent: Allowed deviation from target (default 0.5%)
        
        Returns:
            Test result dictionary
        """
        print(f"\n[TEST] {scenario_name}")
        print(f"  Initial Price: ${initial_price:.2f}")
        print(f"  Target: {target_percent:+.2f}%")
        print(f"  Duration: {duration_seconds}s (accelerated)")
        print(f"  Tolerance: ±{tolerance_percent}%")
        
        # Calculate target price
        target_price = initial_price * (1 + target_percent / 100)
        
        # Create scenario
        scenario = TradingSimScenario(
            symbol="BTCUSDT",
            name=scenario_name,
            trend="UPTREND" if target_percent > 0 else "DOWNTREND",
            drift=abs(target_percent / 100) / duration_seconds * 0.1,  # Adjust drift to reach target
            volatility=0.002,
            spread_bps=8,
            depth=10,
            target_price=target_price,
            house_edge=0.0,
            anti_ta=False,
            formula="",
            notes=f"Accuracy test: {target_percent}% in {duration_seconds}s",
        )
        
        # Create simulator
        simulator = TradingDataSimulator(symbols=["BTCUSDT"])
        simulator.scenarios["BTCUSDT"] = scenario
        simulator.state["BTCUSDT"] = {
            "price": initial_price,
            "last_price": initial_price,
            "high": initial_price,
            "low": initial_price,
            "volume": 0.0,
            "ts": datetime.utcnow(),
            "last_update_id": 0,
        }
        
        # Run simulator for specified duration
        tick_interval = 0.1  # 100ms per tick
        num_ticks = int(duration_seconds / tick_interval)
        
        print(f"  Running {num_ticks} ticks...")
        
        start_time = datetime.utcnow()
        for i in range(num_ticks):
            await simulator._update_symbol("BTCUSDT", tick_interval)
            if (i + 1) % (num_ticks // 10) == 0:
                progress = ((i + 1) / num_ticks) * 100
                current_price = simulator.state["BTCUSDT"]["price"]
                print(f"    Progress: {progress:.0f}% - Current: ${current_price:.2f}")
        
        end_time = datetime.utcnow()
        actual_price = simulator.state["BTCUSDT"]["price"]
        
        # Calculate accuracy
        price_change = actual_price - initial_price
        actual_percent = (price_change / initial_price) * 100
        deviation = abs(actual_percent - target_percent)
        deviation_percent = (deviation / abs(target_percent)) * 100 if target_percent != 0 else deviation
        
        # Check if within tolerance
        passed = deviation <= tolerance_percent
        
        result = {
            "scenario_name": scenario_name,
            "initial_price": initial_price,
            "target_price": target_price,
            "actual_price": actual_price,
            "target_percent": target_percent,
            "actual_percent": actual_percent,
            "deviation": deviation,
            "deviation_percent": deviation_percent,
            "tolerance_percent": tolerance_percent,
            "passed": passed,
            "duration_seconds": (end_time - start_time).total_seconds(),
            "num_ticks": num_ticks,
        }
        
        # Print result
        print(f"\n  Results:")
        print(f"    Target Price: ${target_price:.2f}")
        print(f"    Actual Price: ${actual_price:.2f}")
        print(f"    Target %: {target_percent:+.2f}%")
        print(f"    Actual %: {actual_percent:+.2f}%")
        print(f"    Deviation: {deviation:.2f}%")
        print(f"    Status: {'✅ PASSED' if passed else '❌ FAILED'}")
        
        return result
    
    async def run_all_tests(self):
        """Run all scenario accuracy tests"""
        print("="*60)
        print("SCENARIO ACCURACY TEST (AC-3)")
        print("="*60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("")
        
        # Test cases
        test_cases = [
            {
                "name": "Uptrend +5% in 1 hour",
                "initial_price": 45000.0,
                "target_percent": 5.0,
                "duration_seconds": 60.0,  # Accelerated: 1 hour = 60 seconds
            },
            {
                "name": "Downtrend -3% in 30 minutes",
                "initial_price": 45000.0,
                "target_percent": -3.0,
                "duration_seconds": 30.0,  # Accelerated: 30 min = 30 seconds
            },
            {
                "name": "Uptrend +10% in 2 hours",
                "initial_price": 45000.0,
                "target_percent": 10.0,
                "duration_seconds": 120.0,  # Accelerated: 2 hours = 120 seconds
            },
            {
                "name": "Small movement +1% in 15 minutes",
                "initial_price": 45000.0,
                "target_percent": 1.0,
                "duration_seconds": 15.0,  # Accelerated: 15 min = 15 seconds
            },
        ]
        
        # Run tests
        for test_case in test_cases:
            result = await self.test_scenario_accuracy(
                scenario_name=test_case["name"],
                initial_price=test_case["initial_price"],
                target_percent=test_case["target_percent"],
                duration_seconds=test_case["duration_seconds"],
                tolerance_percent=0.5,  # AC-3 requirement: ±0.5%
            )
            self.results["tests"].append(result)
        
        # Calculate summary
        passed_count = sum(1 for t in self.results["tests"] if t["passed"])
        total_count = len(self.results["tests"])
        
        avg_deviation = sum(t["deviation"] for t in self.results["tests"]) / total_count
        max_deviation = max(t["deviation"] for t in self.results["tests"])
        
        self.results["summary"] = {
            "total_tests": total_count,
            "passed": passed_count,
            "failed": total_count - passed_count,
            "pass_rate": (passed_count / total_count) * 100,
            "avg_deviation_percent": avg_deviation,
            "max_deviation_percent": max_deviation,
            "ac3_requirement": "±0.5%",
            "ac3_passed": max_deviation <= 0.5,
        }
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_count}")
        print(f"Passed: {passed_count}")
        print(f"Failed: {total_count - passed_count}")
        print(f"Pass Rate: {self.results['summary']['pass_rate']:.1f}%")
        print(f"Average Deviation: {avg_deviation:.3f}%")
        print(f"Max Deviation: {max_deviation:.3f}%")
        print(f"AC-3 Requirement: ±0.5%")
        print(f"AC-3 Status: {'✅ PASSED' if self.results['summary']['ac3_passed'] else '❌ FAILED'}")
        
        # Save results
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"scenario_accuracy_{timestamp}.json"
        
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\nResults saved to: {results_file}")
        
        return self.results["summary"]["ac3_passed"]


async def main():
    """Main entry point"""
    try:
        tester = ScenarioAccuracyTest()
        passed = await tester.run_all_tests()
        
        if passed:
            print("\n✅ ALL SCENARIO ACCURACY TESTS PASSED (AC-3)")
            return 0
        else:
            print("\n❌ SOME SCENARIO ACCURACY TESTS FAILED (AC-3)")
            return 1
            
    except KeyboardInterrupt:
        print("\nTest interrupted")
        return 1
    except Exception as e:
        print(f"\nTest error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
