#!/usr/bin/env python3
"""
Continuous Testing
Auto-run tests after fixes with incremental and regression testing
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Import framework
sys.path.insert(0, str(Path(__file__).parent.parent))
from acceptance_test_framework import AcceptanceTestFramework


class ContinuousTester:
    """Continuous testing with incremental and regression testing"""
    
    def __init__(self, environment: str = "local"):
        """Initialize continuous tester"""
        self.environment = environment
        self.framework = AcceptanceTestFramework(environment=environment)
        self.test_history = []
        self.history_file = Path(__file__).parent.parent / "test_history.json"
        self._load_history()
    
    def _load_history(self):
        """Load test history"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.test_history = data.get("history", [])
            except:
                self.test_history = []
    
    def _save_history(self):
        """Save test history"""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump({
                "history": self.test_history[-100:],  # Keep last 100 runs
                "last_updated": datetime.now().isoformat()
            }, f, indent=2)
    
    def run_incremental_test(self, changed_modules: List[str] = None) -> Dict:
        """Run incremental test for changed modules only"""
        print("="*60)
        print("Incremental Testing")
        print("="*60)
        
        if changed_modules:
            print(f"Testing changed modules: {', '.join(changed_modules)}")
        else:
            print("No specific modules specified, running all tests")
            changed_modules = None
        
        # Run tests
        start_time = time.time()
        self.framework.test_all_api_endpoints()
        duration = time.time() - start_time
        
        # Get results
        results = self.framework.results
        total = len(results)
        passed = sum(1 for r in results if r.get("success", False))
        pass_rate = passed / total if total > 0 else 0
        
        # Save to history
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "incremental",
            "changed_modules": changed_modules,
            "total": total,
            "passed": passed,
            "pass_rate": pass_rate,
            "duration": duration
        }
        self.test_history.append(history_entry)
        self._save_history()
        
        print(f"\n✅ Incremental test complete: {passed}/{total} passed ({pass_rate*100:.2f}%)")
        
        return history_entry
    
    def run_regression_test(self, baseline_file: Optional[str] = None) -> Dict:
        """Run regression test against baseline"""
        print("="*60)
        print("Regression Testing")
        print("="*60)
        
        # Load baseline if provided
        baseline = None
        if baseline_file:
            with open(baseline_file, 'r') as f:
                baseline_data = json.load(f)
                baseline = {
                    "total": len(baseline_data.get("results", [])),
                    "passed": sum(1 for r in baseline_data.get("results", []) if r.get("success", False))
                }
        
        # Run full test
        start_time = time.time()
        self.framework.test_all_api_endpoints()
        duration = time.time() - start_time
        
        # Get results
        results = self.framework.results
        total = len(results)
        passed = sum(1 for r in results if r.get("success", False))
        pass_rate = passed / total if total > 0 else 0
        
        # Compare with baseline
        regression = None
        if baseline:
            baseline_rate = baseline["passed"] / baseline["total"] if baseline["total"] > 0 else 0
            regression = pass_rate < baseline_rate
            
            if regression:
                print(f"⚠️  REGRESSION DETECTED!")
                print(f"   Baseline: {baseline_rate*100:.2f}%")
                print(f"   Current: {pass_rate*100:.2f}%")
                print(f"   Decline: {(baseline_rate - pass_rate)*100:.2f}%")
            else:
                print(f"✅ No regression detected")
                print(f"   Baseline: {baseline_rate*100:.2f}%")
                print(f"   Current: {pass_rate*100:.2f}%")
                print(f"   Improvement: {(pass_rate - baseline_rate)*100:.2f}%")
        
        # Save to history
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "regression",
            "baseline_file": baseline_file,
            "total": total,
            "passed": passed,
            "pass_rate": pass_rate,
            "duration": duration,
            "regression": regression
        }
        self.test_history.append(history_entry)
        self._save_history()
        
        return history_entry
    
    def get_trends(self) -> Dict:
        """Analyze test trends"""
        if len(self.test_history) < 2:
            return {"message": "Not enough history for trend analysis"}
        
        recent = self.test_history[-10:]  # Last 10 runs
        
        pass_rates = [entry["pass_rate"] for entry in recent if "pass_rate" in entry]
        
        if not pass_rates:
            return {"message": "No pass rate data available"}
        
        trend = "improving" if pass_rates[-1] > pass_rates[0] else "declining" if pass_rates[-1] < pass_rates[0] else "stable"
        
        return {
            "trend": trend,
            "current_rate": pass_rates[-1],
            "previous_rate": pass_rates[0] if len(pass_rates) > 1 else pass_rates[-1],
            "change": pass_rates[-1] - pass_rates[0],
            "runs_analyzed": len(pass_rates)
        }
    
    def save_results(self, output_path: Optional[str] = None):
        """Save test results"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(__file__).parent.parent.parent.parent / "reports" / "acceptance" / "test_results" / f"continuous_test_{timestamp}.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.framework.save_results(str(output_path))
        return str(output_path)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Continuous testing")
    parser.add_argument(
        "-e", "--environment",
        default="local",
        help="Environment"
    )
    parser.add_argument(
        "-t", "--test-type",
        choices=["incremental", "regression", "full"],
        default="full",
        help="Test type"
    )
    parser.add_argument(
        "-m", "--modules",
        nargs="+",
        help="Changed modules for incremental testing"
    )
    parser.add_argument(
        "-b", "--baseline",
        help="Baseline file for regression testing"
    )
    
    args = parser.parse_args()
    
    tester = ContinuousTester(environment=args.environment)
    
    if args.test_type == "incremental":
        result = tester.run_incremental_test(args.modules)
    elif args.test_type == "regression":
        result = tester.run_regression_test(args.baseline)
    else:
        result = tester.run_incremental_test()  # Full test
    
    # Show trends
    trends = tester.get_trends()
    if "trend" in trends:
        print(f"\n📈 Trend: {trends['trend']}")
        print(f"   Change: {trends['change']*100:+.2f}%")
    
    # Save results
    output_path = tester.save_results()
    print(f"\n✅ Results saved to: {output_path}")

