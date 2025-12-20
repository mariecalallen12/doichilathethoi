#!/usr/bin/env python3
"""
Run Complete Acceptance Testing Workflow with Debug Mode
Executes all phases with comprehensive debug logging
"""

import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

# Debug logging configuration
DEBUG_LOG_PATH = Path("/root/forexxx/.cursor/debug.log")

def debug_log(location: str, message: str, data: Dict = None, hypothesis_id: str = None, run_id: str = "workflow"):
    """Write debug log entry"""
    log_entry = {
        "sessionId": "debug-session",
        "runId": run_id,
        "hypothesisId": hypothesis_id or "N/A",
        "location": location,
        "message": message,
        "data": data or {},
        "timestamp": int(time.time() * 1000)
    }
    
    try:
        with open(DEBUG_LOG_PATH, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"⚠️  Debug log write failed: {e}")

def run_step(step_name: str, command: list, description: str, hypothesis_id: str = None):
    """Run a workflow step with debug logging"""
    location = f"run_workflow_with_debug.py:{step_name}"
    
    # #region agent log
    debug_log(location, f"Starting step: {step_name}", {
        "command": command,
        "description": description
    }, hypothesis_id, "workflow")
    # #endregion
    
    print(f"\n{'='*80}")
    print(f"STEP: {step_name}")
    print(f"{'='*80}")
    print(f"{description}\n")
    
    start_time = time.time()
    success = False
    output = ""
    error = None
    
    try:
        # #region agent log
        debug_log(location, f"Executing command", {
            "command": " ".join(command),
            "step": step_name
        }, hypothesis_id, "workflow")
        # #endregion
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        output = result.stdout
        error_output = result.stderr
        
        # #region agent log
        debug_log(location, f"Command completed", {
            "returncode": result.returncode,
            "stdout_length": len(output),
            "stderr_length": len(error_output),
            "step": step_name
        }, hypothesis_id, "workflow")
        # #endregion
        
        if result.returncode == 0:
            success = True
            print(f"✅ {step_name} completed successfully")
        else:
            error = error_output or "Unknown error"
            print(f"❌ {step_name} failed with return code {result.returncode}")
            if error_output:
                print(f"Error output: {error_output[:500]}")
        
    except subprocess.TimeoutExpired:
        error = "Command timed out after 5 minutes"
        print(f"⏱️  {step_name} timed out")
        # #region agent log
        debug_log(location, f"Command timed out", {
            "step": step_name,
            "timeout": 300
        }, hypothesis_id, "workflow")
        # #endregion
        
    except Exception as e:
        error = str(e)
        print(f"❌ {step_name} raised exception: {e}")
        # #region agent log
        debug_log(location, f"Command exception", {
            "step": step_name,
            "exception": str(e),
            "exception_type": type(e).__name__
        }, hypothesis_id, "workflow")
        # #endregion
    
    elapsed = time.time() - start_time
    
    # #region agent log
    debug_log(location, f"Step completed", {
        "step": step_name,
        "success": success,
        "elapsed_seconds": elapsed,
        "error": error
    }, hypothesis_id, "workflow")
    # #endregion
    
    return {
        "step": step_name,
        "success": success,
        "elapsed": elapsed,
        "output": output,
        "error": error
    }

def main():
    """Run complete workflow with debug mode"""
    
    # Clear previous debug log
    if DEBUG_LOG_PATH.exists():
        DEBUG_LOG_PATH.unlink()
    
    # #region agent log
    debug_log("run_workflow_with_debug.py:main", "Workflow started", {
        "workflow_version": "1.0",
        "timestamp": datetime.now().isoformat()
    }, "H1", "workflow")
    # #endregion
    
    print("="*80)
    print("ACCEPTANCE TESTING WORKFLOW - DEBUG MODE")
    print("="*80)
    print(f"Debug logs: {DEBUG_LOG_PATH}")
    print()
    
    workflow_dir = Path(__file__).parent.parent
    scripts_dir = Path(__file__).parent
    
    results = []
    
    # Step 1: Setup test accounts
    # #region agent log
    debug_log("run_workflow_with_debug.py:main", "Starting Step 1: Setup", {}, "H1", "workflow")
    # #endregion
    
    step1 = run_step(
        "1. Create Test Accounts",
        ["python3", str(scripts_dir / "create_test_accounts.py"), "-e", "local"],
        "Creating test accounts for client and admin users",
        "H1"
    )
    results.append(step1)
    
    if not step1["success"]:
        print("⚠️  Warning: Account creation failed, continuing anyway...")
    
    step1b = run_step(
        "1b. Approve Test Accounts",
        ["python3", str(scripts_dir / "approve_test_accounts.py"), "-e", "local"],
        "Approving test accounts to enable login",
        "H1"
    )
    results.append(step1b)
    
    # Step 2: Run acceptance tests
    # #region agent log
    debug_log("run_workflow_with_debug.py:main", "Starting Step 2: Run Tests", {}, "H2", "workflow")
    # #endregion
    
    step2 = run_step(
        "2. Run Acceptance Tests",
        ["python3", str(workflow_dir / "run_tests_with_auth.py")],
        "Running comprehensive acceptance tests with authentication",
        "H2"
    )
    results.append(step2)
    
    if not step2["success"]:
        print("❌ Tests failed - cannot continue")
        return results
    
    # Extract results file from output
    results_file = None
    if "Results saved to:" in step2["output"]:
        for line in step2["output"].split('\n'):
            if "Results saved to:" in line:
                results_file = line.split("Results saved to:")[-1].strip()
                break
    
    # #region agent log
    debug_log("run_workflow_with_debug.py:main", "Test results file identified", {
        "results_file": results_file
    }, "H2", "workflow")
    # #endregion
    
    if not results_file or not Path(results_file).exists():
        # Try to find latest results file
        results_dir = workflow_dir.parent.parent / "reports" / "acceptance" / "test_results"
        if results_dir.exists():
            test_files = sorted(results_dir.glob("api_test_results_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
            if test_files:
                results_file = str(test_files[0])
                # #region agent log
                debug_log("run_workflow_with_debug.py:main", "Using latest results file", {
                    "results_file": results_file
                }, "H2", "workflow")
                # #endregion
    
    # Step 3: Analyze issues
    # #region agent log
    debug_log("run_workflow_with_debug.py:main", "Starting Step 3: Analyze Issues", {}, "H3", "workflow")
    # #endregion
    
    if results_file:
        step3 = run_step(
            "3. Analyze Issues",
            ["python3", str(scripts_dir / "analyze_issues.py"), results_file],
            "Analyzing test results and categorizing issues",
            "H3"
        )
        results.append(step3)
        
        step3b = run_step(
            "3b. Prioritize Issues",
            ["python3", str(scripts_dir / "prioritize_issues.py"), 
             str(workflow_dir.parent.parent / "reports" / "acceptance" / "issues" / "issue_report.json")],
            "Prioritizing issues by severity and impact",
            "H3"
        )
        results.append(step3b)
    else:
        print("⚠️  No results file found, skipping issue analysis")
    
    # Step 4: Fix issues
    # #region agent log
    debug_log("run_workflow_with_debug.py:main", "Starting Step 4: Fix Issues", {}, "H4", "workflow")
    # #endregion
    
    step4 = run_step(
        "4. Fix Authentication Issues",
        ["python3", str(scripts_dir / "fix_auth_issues.py"), "-e", "local"],
        "Fixing authentication and authorization issues",
        "H4"
    )
    results.append(step4)
    
    step4b = run_step(
        "4b. Fix Missing Endpoints",
        ["python3", str(scripts_dir / "fix_missing_endpoints.py")],
        "Reviewing and fixing missing endpoint issues",
        "H4"
    )
    results.append(step4b)
    
    # Step 5: Quality Gates
    # #region agent log
    debug_log("run_workflow_with_debug.py:main", "Starting Step 5: Quality Gates", {}, "H5", "workflow")
    # #endregion
    
    if results_file:
        step5 = run_step(
            "5. Run Quality Gates",
            ["python3", str(scripts_dir / "run_quality_gates.py"), results_file],
            "Running quality gate checks",
            "H5"
        )
        results.append(step5)
    else:
        print("⚠️  No results file found, skipping quality gates")
    
    # Step 6: Generate Report
    # #region agent log
    debug_log("run_workflow_with_debug.py:main", "Starting Step 6: Generate Report", {}, "H6", "workflow")
    # #endregion
    
    if results_file:
        step6 = run_step(
            "6. Generate Acceptance Report",
            ["python3", str(workflow_dir / "generate_acceptance_report.py"), results_file],
            "Generating comprehensive acceptance test report",
            "H6"
        )
        results.append(step6)
    
    # Summary
    # #region agent log
    debug_log("run_workflow_with_debug.py:main", "Workflow completed", {
        "total_steps": len(results),
        "successful_steps": sum(1 for r in results if r["success"]),
        "failed_steps": sum(1 for r in results if not r["success"])
    }, "H_SUMMARY", "workflow")
    # #endregion
    
    print("\n" + "="*80)
    print("WORKFLOW SUMMARY")
    print("="*80)
    
    total_time = sum(r["elapsed"] for r in results)
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    
    print(f"Total Steps: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total Time: {total_time:.2f}s")
    print()
    print("Step Details:")
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"  {status} {r['step']}: {r['elapsed']:.2f}s")
        if r["error"]:
            print(f"     Error: {r['error'][:100]}")
    
    print()
    print(f"Debug logs saved to: {DEBUG_LOG_PATH}")
    print("="*80)
    
    return results

if __name__ == "__main__":
    results = main()
    sys.exit(0 if all(r["success"] for r in results) else 1)

