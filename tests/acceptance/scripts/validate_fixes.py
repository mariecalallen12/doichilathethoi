#!/usr/bin/env python3
"""
Validate Fixes
Pre-fix baseline, post-fix verification, regression check
"""

import sys
import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

# Import framework
sys.path.insert(0, str(Path(__file__).parent.parent))
from acceptance_test_framework import AcceptanceTestFramework


class FixValidator:
    """Validate fixes with baseline comparison"""
    
    def __init__(self, environment: str = "local"):
        """Initialize validator"""
        self.environment = environment
        self.framework = AcceptanceTestFramework(environment=environment)
    
    def create_baseline(self, output_path: Optional[str] = None) -> str:
        """Create baseline before fixes"""
        print("="*60)
        print("Creating Baseline")
        print("="*60)
        
        # Run tests
        print("Running tests to create baseline...")
        self.framework.test_all_api_endpoints()
        
        # Save baseline
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(__file__).parent.parent.parent.parent / "reports" / "acceptance" / "baselines" / f"baseline_{timestamp}.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.framework.save_results(str(output_path))
        
        # Calculate baseline metrics
        results = self.framework.results
        total = len(results)
        passed = sum(1 for r in results if r.get("success", False))
        pass_rate = passed / total if total > 0 else 0
        
        baseline_metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total,
            "passed": passed,
            "pass_rate": pass_rate,
            "results_file": str(output_path)
        }
        
        metrics_file = output_path.parent / f"baseline_{timestamp}_metrics.json"
        with open(metrics_file, 'w') as f:
            json.dump(baseline_metrics, f, indent=2)
        
        print(f"\n✅ Baseline created:")
        print(f"   Total: {total}")
        print(f"   Passed: {passed}")
        print(f"   Pass Rate: {pass_rate*100:.2f}%")
        print(f"   Baseline file: {output_path}")
        print(f"   Metrics file: {metrics_file}")
        
        return str(output_path)
    
    def verify_fixes(self, baseline_file: str, fix_description: str = "") -> Dict:
        """Verify fixes against baseline"""
        print("="*60)
        print("Verifying Fixes")
        print("="*60)
        
        if fix_description:
            print(f"Fix: {fix_description}")
        
        # Load baseline
        with open(baseline_file, 'r') as f:
            baseline_data = json.load(f)
        
        baseline_results = baseline_data.get("results", [])
        baseline_total = len(baseline_results)
        baseline_passed = sum(1 for r in baseline_results if r.get("success", False))
        baseline_rate = baseline_passed / baseline_total if baseline_total > 0 else 0
        
        print(f"\n📊 Baseline:")
        print(f"   Total: {baseline_total}")
        print(f"   Passed: {baseline_passed}")
        print(f"   Pass Rate: {baseline_rate*100:.2f}%")
        
        # Run current tests
        print(f"\n🔄 Running current tests...")
        self.framework.results = []  # Reset
        self.framework.test_all_api_endpoints()
        
        current_results = self.framework.results
        current_total = len(current_results)
        current_passed = sum(1 for r in current_results if r.get("success", False))
        current_rate = current_passed / current_total if current_total > 0 else 0
        
        print(f"\n📊 Current:")
        print(f"   Total: {current_total}")
        print(f"   Passed: {current_passed}")
        print(f"   Pass Rate: {current_rate*100:.2f}%")
        
        # Compare
        improvement = current_rate - baseline_rate
        regression = improvement < 0
        
        print(f"\n📈 Comparison:")
        print(f"   Change: {improvement*100:+.2f}%")
        
        if regression:
            print(f"   ⚠️  REGRESSION: Pass rate decreased!")
        elif improvement > 0:
            print(f"   ✅ IMPROVEMENT: Pass rate increased!")
        else:
            print(f"   ➡️  NO CHANGE: Pass rate unchanged")
        
        # Detailed comparison
        baseline_by_status = {}
        current_by_status = {}
        
        for r in baseline_results:
            status = r.get("status_code", "unknown")
            baseline_by_status[status] = baseline_by_status.get(status, 0) + 1
        
        for r in current_results:
            status = r.get("status_code", "unknown")
            current_by_status[status] = current_by_status.get(status, 0) + 1
        
        # Find improvements and regressions
        improvements = []
        regressions = []
        
        for status in set(list(baseline_by_status.keys()) + list(current_by_status.keys())):
            baseline_count = baseline_by_status.get(status, 0)
            current_count = current_by_status.get(status, 0)
            
            if current_count < baseline_count:
                improvements.append({
                    "status": status,
                    "baseline": baseline_count,
                    "current": current_count,
                    "improvement": baseline_count - current_count
                })
            elif current_count > baseline_count:
                regressions.append({
                    "status": status,
                    "baseline": baseline_count,
                    "current": current_count,
                    "regression": current_count - baseline_count
                })
        
        verification = {
            "baseline": {
                "file": baseline_file,
                "total": baseline_total,
                "passed": baseline_passed,
                "pass_rate": baseline_rate
            },
            "current": {
                "total": current_total,
                "passed": current_passed,
                "pass_rate": current_rate
            },
            "comparison": {
                "improvement": improvement,
                "regression": regression,
                "improvements": improvements,
                "regressions": regressions
            },
            "fix_description": fix_description,
            "timestamp": datetime.now().isoformat()
        }
        
        return verification
    
    def check_regression(self, verification: Dict) -> bool:
        """Check if there's a regression"""
        return verification.get("comparison", {}).get("regression", False)
    
    def generate_report(self, verification: Dict, output_path: Optional[str] = None) -> str:
        """Generate verification report"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(__file__).parent.parent.parent.parent / "reports" / "acceptance" / "fix_validation" / f"fix_validation_{timestamp}.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(verification, f, indent=2)
        
        return str(output_path)
    
    def print_verification(self, verification: Dict):
        """Print verification results"""
        comparison = verification.get("comparison", {})
        
        print("\n" + "="*60)
        print("FIX VERIFICATION REPORT")
        print("="*60)
        
        baseline = verification.get("baseline", {})
        current = verification.get("current", {})
        
        print(f"\nBaseline Pass Rate: {baseline.get('pass_rate', 0)*100:.2f}%")
        print(f"Current Pass Rate: {current.get('pass_rate', 0)*100:.2f}%")
        print(f"Change: {comparison.get('improvement', 0)*100:+.2f}%")
        
        if comparison.get("improvements"):
            print(f"\n✅ Improvements:")
            for imp in comparison["improvements"]:
                print(f"   Status {imp['status']}: {imp['baseline']} → {imp['current']} "
                      f"({imp['improvement']} fewer errors)")
        
        if comparison.get("regressions"):
            print(f"\n⚠️  Regressions:")
            for reg in comparison["regressions"]:
                print(f"   Status {reg['status']}: {reg['baseline']} → {reg['current']} "
                      f"({reg['regression']} more errors)")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate fixes")
    parser.add_argument(
        "baseline_file",
        help="Path to baseline test results file"
    )
    parser.add_argument(
        "-e", "--environment",
        default="local",
        help="Environment"
    )
    parser.add_argument(
        "-d", "--description",
        default="",
        help="Description of fixes applied"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path"
    )
    
    args = parser.parse_args()
    
    validator = FixValidator(environment=args.environment)
    verification = validator.verify_fixes(args.baseline_file, args.description)
    
    validator.print_verification(verification)
    
    output_path = validator.generate_report(verification, args.output)
    print(f"\n✅ Report saved to: {output_path}")
    
    if validator.check_regression(verification):
        print("\n⚠️  Regression detected - review fixes")
        sys.exit(1)
    else:
        print("\n✅ No regression - fixes validated")
        sys.exit(0)

