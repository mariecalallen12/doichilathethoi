#!/usr/bin/env python3
"""
Server-Side Logic Verification & Formula Sandbox Security Test
Mục tiêu: Verify AC-6 (Security - Server-side logic)

Tests:
1. Verify no pricing logic in client bundle
2. Test formula sandbox security (prevent code injection)
3. Verify RestrictedPython sandbox restrictions
"""

import os
import sys
import re
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any

# Configuration
CLIENT_APP_DIR = Path(__file__).parent.parent.parent / "client-app"
ADMIN_APP_DIR = Path(__file__).parent.parent.parent / "Admin-app"
BACKEND_DIR = Path(__file__).parent.parent.parent / "backend"


class SecurityTest:
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def add_error(self, msg: str):
        self.errors.append(msg)
    
    def add_warning(self, msg: str):
        self.warnings.append(msg)
    
    def set_passed(self):
        self.passed = True
    
    def get_result(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed and len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def test_no_pricing_logic_in_client(test: SecurityTest):
    """Test 1: Verify no pricing logic in client bundle"""
    print(f"\n[TEST 1] {test.name}")
    
    # Dangerous patterns that should NOT be in client code
    dangerous_patterns = [
        r"brownian.*motion",
        r"jump.*diffusion",
        r"drift.*component",
        r"price.*generator",
        r"market.*simulator",
        r"house.*edge",
        r"target.*price.*calculation",
        r"volatility.*calculation",
    ]
    
    # Check client-app build output
    client_build_dir = CLIENT_APP_DIR / "dist"
    if not client_build_dir.exists():
        test.add_warning("Client build directory not found. Run 'npm run build' first.")
        return
    
    # Check JavaScript bundles
    js_files = list(client_build_dir.rglob("*.js"))
    if not js_files:
        test.add_warning("No JavaScript files found in build directory")
        return
    
    found_violations = []
    for js_file in js_files:
        try:
            content = js_file.read_text(encoding='utf-8', errors='ignore')
            for pattern in dangerous_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    found_violations.append(f"{js_file.name}: Found '{pattern}' pattern")
        except Exception as e:
            test.add_warning(f"Could not read {js_file.name}: {e}")
    
    if found_violations:
        for violation in found_violations:
            test.add_error(violation)
    else:
        test.set_passed()
        print("  ✅ No pricing logic found in client bundle")


def test_formula_sandbox_security(test: SecurityTest):
    """Test 2: Test formula sandbox prevents code injection"""
    print(f"\n[TEST 2] {test.name}")
    
    # Malicious formula attempts
    malicious_formulas = [
        "__import__('os').system('rm -rf /')",
        "eval('__import__(\"os\").system(\"ls\")')",
        "exec('import os; os.system(\"pwd\")')",
        "open('/etc/passwd').read()",
        "__builtins__.__import__('os')",
        "globals()['__builtins__']['__import__']('os')",
        "compile('import os', '<string>', 'exec')",
        "vars(__builtins__)['__import__']('os')",
        "getattr(__builtins__, '__import__')('os')",
        "import os",
        "from os import system",
        "require('fs')",
        "process.exit()",
        "child_process.exec('ls')",
    ]
    
    # Import the sandbox function
    sys.path.insert(0, str(BACKEND_DIR))
    
    try:
        from app.services.trading_data_simulator import TradingDataSimulator
        
        simulator = TradingDataSimulator()
        safe_context = {
            "price": 100.0,
            "dt": 1.0,
            "trend": "SIDEWAY",
            "target": None,
            "drift": 0.0005,
            "volatility": 0.002,
        }
        
        blocked_count = 0
        for formula in malicious_formulas:
            try:
                result = simulator._safe_eval_formula(formula, safe_context)
                if result is not None:
                    test.add_error(f"Formula was not blocked: {formula}")
                else:
                    blocked_count += 1
            except Exception as e:
                # Expected - formula should be blocked
                blocked_count += 1
        
        if blocked_count == len(malicious_formulas):
            test.set_passed()
            print(f"  ✅ All {len(malicious_formulas)} malicious formulas were blocked")
        else:
            test.add_error(f"Only {blocked_count}/{len(malicious_formulas)} formulas were blocked")
            
    except ImportError as e:
        test.add_error(f"Could not import TradingDataSimulator: {e}")
    except Exception as e:
        test.add_error(f"Unexpected error: {e}")


def test_allowed_formula_functions(test: SecurityTest):
    """Test 3: Verify allowed functions work correctly"""
    print(f"\n[TEST 3] {test.name}")
    
    # Safe formulas that should work
    safe_formulas = [
        "price * (1 + drift * dt)",
        "price + (random.random() - 0.5) * volatility",
        "math.sqrt(price) * drift",
        "abs(price - target) if target else price",
        "max(price, target) if target else price",
        "min(price, target) if target else price",
        "round(price, 2)",
        "price * math.sin(time.time())",
    ]
    
    sys.path.insert(0, str(BACKEND_DIR))
    
    try:
        from app.services.trading_data_simulator import TradingDataSimulator
        
        simulator = TradingDataSimulator()
        safe_context = {
            "price": 100.0,
            "dt": 1.0,
            "trend": "SIDEWAY",
            "target": 105.0,
            "drift": 0.0005,
            "volatility": 0.002,
        }
        
        success_count = 0
        for formula in safe_formulas:
            try:
                result = simulator._safe_eval_formula(formula, safe_context)
                if result is not None and isinstance(result, (int, float)):
                    success_count += 1
                else:
                    test.add_warning(f"Formula returned None or invalid type: {formula}")
            except Exception as e:
                test.add_warning(f"Formula failed (may be expected): {formula} - {e}")
        
        if success_count >= len(safe_formulas) * 0.7:  # 70% success rate
            test.set_passed()
            print(f"  ✅ {success_count}/{len(safe_formulas)} safe formulas executed successfully")
        else:
            test.add_warning(f"Only {success_count}/{len(safe_formulas)} safe formulas worked")
            
    except ImportError as e:
        test.add_error(f"Could not import TradingDataSimulator: {e}")
    except Exception as e:
        test.add_error(f"Unexpected error: {e}")


def test_ast_whitelist(test: SecurityTest):
    """Test 4: Verify AST whitelist validation"""
    print(f"\n[TEST 4] {test.name}")
    
    # Formulas with disallowed AST nodes
    disallowed_formulas = [
        "lambda x: x + 1",  # Lambda
        "def func(): pass",  # FunctionDef
        "for i in range(10): pass",  # For
        "while True: pass",  # While
        "class A: pass",  # ClassDef
        "import os",  # Import
        "from os import system",  # ImportFrom
    ]
    
    sys.path.insert(0, str(BACKEND_DIR))
    
    try:
        from app.services.trading_data_simulator import TradingDataSimulator
        
        simulator = TradingDataSimulator()
        safe_context = {
            "price": 100.0,
            "dt": 1.0,
            "trend": "SIDEWAY",
            "target": None,
            "drift": 0.0005,
            "volatility": 0.002,
        }
        
        blocked_count = 0
        for formula in disallowed_formulas:
            try:
                result = simulator._safe_eval_formula(formula, safe_context)
                if result is None:
                    blocked_count += 1
                else:
                    test.add_error(f"Disallowed AST node was not blocked: {formula}")
            except (ValueError, SyntaxError):
                # Expected - should be blocked
                blocked_count += 1
            except Exception as e:
                test.add_warning(f"Unexpected error for {formula}: {e}")
        
        if blocked_count == len(disallowed_formulas):
            test.set_passed()
            print(f"  ✅ All {len(disallowed_formulas)} disallowed AST nodes were blocked")
        else:
            test.add_error(f"Only {blocked_count}/{len(disallowed_formulas)} disallowed nodes were blocked")
            
    except ImportError as e:
        test.add_error(f"Could not import TradingDataSimulator: {e}")
    except Exception as e:
        test.add_error(f"Unexpected error: {e}")


def main():
    """Run all security tests"""
    print("="*60)
    print("SERVER-SIDE LOGIC & FORMULA SANDBOX SECURITY TEST")
    print("="*60)
    print(f"Timestamp: {Path(__file__).stat().st_mtime}")
    print("")
    
    tests = [
        SecurityTest("No Pricing Logic in Client Bundle"),
        SecurityTest("Formula Sandbox Blocks Code Injection"),
        SecurityTest("Allowed Formula Functions Work"),
        SecurityTest("AST Whitelist Validation"),
    ]
    
    # Run tests
    test_no_pricing_logic_in_client(tests[0])
    test_formula_sandbox_security(tests[1])
    test_allowed_formula_functions(tests[2])
    test_ast_whitelist(tests[3])
    
    # Generate report
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    
    timestamp = Path(__file__).stat().st_mtime
    report_file = results_dir / f"server_side_logic_test_{timestamp}.json"
    
    results = {
        "timestamp": str(timestamp),
        "tests": [test.get_result() for test in tests],
        "summary": {
            "total": len(tests),
            "passed": sum(1 for t in tests if t.get_result()["passed"]),
            "failed": sum(1 for t in tests if not t.get_result()["passed"]),
        }
    }
    
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test in tests:
        result = test.get_result()
        status = "✅ PASSED" if result["passed"] else "❌ FAILED"
        print(f"{status}: {result['name']}")
        if result["errors"]:
            for error in result["errors"]:
                print(f"  ERROR: {error}")
        if result["warnings"]:
            for warning in result["warnings"]:
                print(f"  WARNING: {warning}")
    
    print(f"\nResults saved to: {report_file}")
    
    # Overall result
    all_passed = all(t.get_result()["passed"] for t in tests)
    if all_passed:
        print("\n✅ ALL SECURITY TESTS PASSED")
        return 0
    else:
        print("\n❌ SOME SECURITY TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
