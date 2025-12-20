#!/usr/bin/env python3
"""
Run Quality Gates
Automated quality checks after fixes
"""

import sys
import json
from pathlib import Path
from typing import Optional

# Import quality gates
sys.path.insert(0, str(Path(__file__).parent.parent))
from quality_gates import QualityGate


def find_latest_test_results() -> Optional[str]:
    """Find latest test results file"""
    results_dir = Path(__file__).parent.parent.parent.parent / "reports" / "acceptance" / "test_results"
    
    if not results_dir.exists():
        return None
    
    # Find latest api_test_results file
    test_files = list(results_dir.glob("api_test_results*.json"))
    if not test_files:
        return None
    
    # Sort by modification time
    test_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return str(test_files[0])


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run quality gates")
    parser.add_argument(
        "test_results_file",
        nargs="?",
        help="Path to test results JSON file (optional, uses latest if not provided)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path"
    )
    
    args = parser.parse_args()
    
    # Get test results file
    if args.test_results_file:
        test_results_file = args.test_results_file
    else:
        test_results_file = find_latest_test_results()
        if not test_results_file:
            print("❌ No test results file found")
            sys.exit(1)
        print(f"Using latest test results: {test_results_file}")
    
    # Load test results
    try:
        with open(test_results_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading test results: {e}")
        sys.exit(1)
    
    test_results = data.get("results", [])
    
    if not test_results:
        print("❌ No test results found in file")
        sys.exit(1)
    
    # Run quality gates
    gate = QualityGate()
    report = gate.run_all_checks(test_results)
    
    gate.print_report(report)
    
    output_path = gate.generate_report(report, args.output)
    print(f"\n✅ Report saved to: {output_path}")
    
    # Exit with appropriate code
    if gate.should_block_deployment(report):
        print("\n🚫 Quality gates failed - deployment blocked")
        sys.exit(1)
    else:
        print("\n✅ Quality gates passed - deployment allowed")
        sys.exit(0)

