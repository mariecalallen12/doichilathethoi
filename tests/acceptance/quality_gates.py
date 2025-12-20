#!/usr/bin/env python3
"""
Quality Gates
Automated quality checks with blocking mechanism
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import statistics


class QualityGate:
    """Quality gate checker"""
    
    def __init__(self, criteria_path: Optional[str] = None):
        """Initialize quality gate"""
        if criteria_path is None:
            criteria_path = Path(__file__).parent / "quality_criteria.json"
        
        with open(criteria_path, 'r') as f:
            self.criteria = json.load(f)
        
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
    
    def check_completion_rate(self, test_results: List[Dict]) -> Tuple[bool, Dict]:
        """Check completion rate"""
        total = len(test_results)
        passed = sum(1 for r in test_results if r.get("success", False))
        completion_rate = passed / total if total > 0 else 0
        
        minimum = self.criteria["completion_rate"]["minimum"]
        passed_check = completion_rate >= minimum
        
        result = {
            "check": "completion_rate",
            "passed": passed_check,
            "value": completion_rate,
            "minimum": minimum,
            "total_tests": total,
            "passed_tests": passed,
            "message": f"Completion rate: {completion_rate*100:.2f}% (minimum: {minimum*100:.0f}%)"
        }
        
        return passed_check, result
    
    def check_critical_issues(self, test_results: List[Dict]) -> Tuple[bool, Dict]:
        """Check for critical issues"""
        critical_issues = []
        
        for result in test_results:
            if not result.get("success", False):
                status_code = result.get("status_code")
                # Server errors are critical
                if status_code and status_code >= 500:
                    critical_issues.append(result)
                # Auth errors in critical modules
                elif status_code in [401, 403]:
                    path = result.get("path", "")
                    if any(module in path for module in ["/auth", "/client", "/financial"]):
                        critical_issues.append(result)
        
        maximum = self.criteria["critical_issues"]["maximum"]
        passed_check = len(critical_issues) <= maximum
        
        result = {
            "check": "critical_issues",
            "passed": passed_check,
            "value": len(critical_issues),
            "maximum": maximum,
            "issues": critical_issues[:10],  # Top 10
            "message": f"Critical issues: {len(critical_issues)} (maximum: {maximum})"
        }
        
        return passed_check, result
    
    def check_high_issues(self, test_results: List[Dict]) -> Tuple[bool, Dict]:
        """Check high priority issues"""
        high_issues = []
        
        for result in test_results:
            if not result.get("success", False):
                status_code = result.get("status_code")
                # High priority: 404 in important modules, 422 validation errors
                if status_code == 404:
                    path = result.get("path", "")
                    if any(module in path for module in ["/admin", "/portfolio", "/compliance"]):
                        high_issues.append(result)
                elif status_code == 422:
                    high_issues.append(result)
        
        maximum = self.criteria["high_issues"]["maximum"]
        passed_check = len(high_issues) <= maximum
        
        result = {
            "check": "high_issues",
            "passed": passed_check,
            "value": len(high_issues),
            "maximum": maximum,
            "issues": high_issues[:10],
            "message": f"High priority issues: {len(high_issues)} (maximum: {maximum})"
        }
        
        return passed_check, result
    
    def check_response_time(self, test_results: List[Dict]) -> Tuple[bool, Dict]:
        """Check API response times"""
        response_times = [
            r.get("response_time", 0) for r in test_results
            if r.get("response_time") and r.get("success", False)
        ]
        
        if not response_times:
            return True, {
                "check": "response_time",
                "passed": True,
                "message": "No response time data available"
            }
        
        p95 = self._percentile(response_times, 95)
        p99 = self._percentile(response_times, 99)
        
        p95_max = self.criteria["api_response_time"]["p95_maximum_seconds"]
        p99_max = self.criteria["api_response_time"]["p99_maximum_seconds"]
        
        passed_check = p95 <= p95_max and p99 <= p99_max
        
        result = {
            "check": "response_time",
            "passed": passed_check,
            "p95": p95,
            "p99": p99,
            "p95_maximum": p95_max,
            "p99_maximum": p99_max,
            "message": f"P95: {p95:.2f}s (max: {p95_max}s), P99: {p99:.2f}s (max: {p99_max}s)"
        }
        
        return passed_check, result
    
    def check_error_rate(self, test_results: List[Dict]) -> Tuple[bool, Dict]:
        """Check error rate"""
        total = len(test_results)
        errors = sum(1 for r in test_results if not r.get("success", False))
        error_rate = errors / total if total > 0 else 0
        
        maximum = self.criteria["error_rate"]["maximum"]
        passed_check = error_rate <= maximum
        
        result = {
            "check": "error_rate",
            "passed": passed_check,
            "value": error_rate,
            "maximum": maximum,
            "total": total,
            "errors": errors,
            "message": f"Error rate: {error_rate*100:.2f}% (maximum: {maximum*100:.0f}%)"
        }
        
        return passed_check, result
    
    def check_module_pass_rates(self, test_results: List[Dict]) -> Tuple[bool, Dict]:
        """Check pass rates per module"""
        module_results = {}
        
        for result in test_results:
            description = result.get("description", "")
            if ":" in description:
                module = description.split(":")[0].strip()
                if module not in module_results:
                    module_results[module] = {"total": 0, "passed": 0}
                module_results[module]["total"] += 1
                if result.get("success", False):
                    module_results[module]["passed"] += 1
        
        minimum = self.criteria["module_pass_rates"]["minimum"]
        critical_modules = self.criteria["module_pass_rates"].get("critical_modules", {})
        
        failed_modules = []
        for module, stats in module_results.items():
            pass_rate = stats["passed"] / stats["total"] if stats["total"] > 0 else 0
            required_rate = critical_modules.get(module, minimum)
            
            if pass_rate < required_rate:
                failed_modules.append({
                    "module": module,
                    "pass_rate": pass_rate,
                    "required": required_rate,
                    "passed": stats["passed"],
                    "total": stats["total"]
                })
        
        passed_check = len(failed_modules) == 0
        
        result = {
            "check": "module_pass_rates",
            "passed": passed_check,
            "minimum": minimum,
            "failed_modules": failed_modules,
            "message": f"Module pass rates: {len(failed_modules)} modules below threshold"
        }
        
        return passed_check, result
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        if index >= len(sorted_data):
            index = len(sorted_data) - 1
        return sorted_data[index]
    
    def run_all_checks(self, test_results: List[Dict]) -> Dict:
        """Run all quality gate checks"""
        checks = [
            self.check_completion_rate,
            self.check_critical_issues,
            self.check_high_issues,
            self.check_response_time,
            self.check_error_rate,
            self.check_module_pass_rates
        ]
        
        results = []
        all_passed = True
        
        for check_func in checks:
            passed, result = check_func(test_results)
            results.append(result)
            
            if not passed:
                all_passed = False
                self.results["failed"].append(result)
            else:
                self.results["passed"].append(result)
        
        return {
            "all_passed": all_passed,
            "checks": results,
            "summary": {
                "total_checks": len(results),
                "passed": len(self.results["passed"]),
                "failed": len(self.results["failed"])
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def should_block_deployment(self, quality_report: Dict) -> bool:
        """Determine if deployment should be blocked"""
        if not quality_report.get("all_passed", False):
            return True
        
        # Check critical checks
        for check in quality_report.get("checks", []):
            check_name = check.get("check", "")
            if check_name in ["completion_rate", "critical_issues"]:
                if not check.get("passed", False):
                    return True
        
        return False
    
    def generate_report(self, quality_report: Dict, output_path: Optional[str] = None) -> str:
        """Generate quality gate report"""
        if output_path is None:
            output_path = Path(__file__).parent.parent.parent.parent / "reports" / "acceptance" / "quality" / "quality_gate_report.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(quality_report, f, indent=2)
        
        return str(output_path)
    
    def print_report(self, quality_report: Dict):
        """Print quality gate report"""
        print("\n" + "="*60)
        print("QUALITY GATE REPORT")
        print("="*60)
        
        summary = quality_report.get("summary", {})
        print(f"\n📊 Summary:")
        print(f"  Total Checks: {summary.get('total_checks', 0)}")
        print(f"  Passed: {summary.get('passed', 0)}")
        print(f"  Failed: {summary.get('failed', 0)}")
        
        all_passed = quality_report.get("all_passed", False)
        status = "✅ PASSED" if all_passed else "❌ FAILED"
        print(f"\n🎯 Overall Status: {status}")
        
        if not all_passed:
            print(f"\n❌ Failed Checks:")
            for check in quality_report.get("checks", []):
                if not check.get("passed", False):
                    print(f"  - {check.get('check', 'unknown')}: {check.get('message', '')}")
        
        # Deployment blocking
        should_block = self.should_block_deployment(quality_report)
        if should_block:
            print(f"\n🚫 DEPLOYMENT BLOCKED")
            print("   Quality gates not passed. Fix issues before deployment.")
        else:
            print(f"\n✅ DEPLOYMENT ALLOWED")
            print("   All quality gates passed.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run quality gates")
    parser.add_argument(
        "test_results_file",
        help="Path to test results JSON file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path"
    )
    
    args = parser.parse_args()
    
    # Load test results
    with open(args.test_results_file, 'r') as f:
        data = json.load(f)
    
    test_results = data.get("results", [])
    
    # Run quality gates
    gate = QualityGate()
    report = gate.run_all_checks(test_results)
    
    gate.print_report(report)
    
    output_path = gate.generate_report(report, args.output)
    print(f"\n✅ Report saved to: {output_path}")
    
    # Exit with appropriate code
    if gate.should_block_deployment(report):
        sys.exit(1)
    else:
        sys.exit(0)

