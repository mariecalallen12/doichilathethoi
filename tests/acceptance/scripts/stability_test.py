#!/usr/bin/env python3
"""
Stability Testing
Long-running test to check for memory leaks, resource leaks, and stability
"""

import sys
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

# Optional imports
try:
    import psutil
    import os
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  psutil not available, memory metrics will be limited")


class StabilityTester:
    """Stability testing for long-running scenarios"""
    
    def __init__(self, api_url: str = "http://localhost:8000",
                 duration_hours: int = 24,
                 check_interval_minutes: int = 60):
        """Initialize stability tester"""
        self.api_url = api_url
        self.duration_hours = duration_hours
        self.check_interval_minutes = check_interval_minutes
        self.check_interval_seconds = check_interval_minutes * 60
        self.results = []
        self.metrics_history = []
        self.start_time = None
        if PSUTIL_AVAILABLE:
            self.process = psutil.Process(os.getpid())
        else:
            self.process = None
    
    def check_endpoint(self, method: str, path: str) -> Dict:
        """Check endpoint health"""
        url = f"{self.api_url}{path}"
        method_func = getattr(requests, method.lower())
        
        start_time = time.time()
        try:
            response = method_func(url, timeout=10)
            response_time = time.time() - start_time
            
            return {
                "success": 200 <= response.status_code < 300,
                "status_code": response.status_code,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "success": False,
                "status_code": None,
                "response_time": response_time,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def collect_metrics(self) -> Dict:
        """Collect system and application metrics"""
        try:
            metrics = {
                "timestamp": datetime.now().isoformat()
            }
            
            if PSUTIL_AVAILABLE and self.process:
                # System metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Process metrics
                process_memory = self.process.memory_info()
                
                metrics["system"] = {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_mb": memory.available / (1024 * 1024),
                    "disk_percent": disk.percent
                }
                metrics["process"] = {
                    "memory_rss_mb": process_memory.rss / (1024 * 1024),
                    "memory_vms_mb": process_memory.vms / (1024 * 1024)
                }
            else:
                metrics["note"] = "psutil not available, limited metrics"
            
            return metrics
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def run_stability_test(self, endpoints: List[Dict]) -> Dict:
        """Run stability test for specified duration"""
        print("="*60)
        print("Stability Testing")
        print("="*60)
        print(f"Duration: {self.duration_hours} hours")
        print(f"Check Interval: {self.check_interval_minutes} minutes")
        print(f"Endpoints to monitor: {len(endpoints)}")
        print()
        print("Starting stability test...")
        print("Press Ctrl+C to stop early")
        print()
        
        self.start_time = datetime.now()
        end_time = self.start_time + timedelta(hours=self.duration_hours)
        
        check_count = 0
        total_checks = (self.duration_hours * 60) // self.check_interval_minutes
        
        try:
            while datetime.now() < end_time:
                check_count += 1
                elapsed = (datetime.now() - self.start_time).total_seconds() / 3600
                
                print(f"[{check_count}/{total_checks}] Check at {elapsed:.1f}h elapsed...")
                
                # Check endpoints
                check_results = []
                for endpoint in endpoints:
                    method = endpoint.get("method", "GET")
                    path = endpoint.get("path", "/api/health")
                    result = self.check_endpoint(method, path)
                    result["endpoint"] = path
                    check_results.append(result)
                
                # Collect metrics
                metrics = self.collect_metrics()
                self.metrics_history.append(metrics)
                
                # Store results
                self.results.append({
                    "check_number": check_count,
                    "elapsed_hours": elapsed,
                    "endpoints": check_results,
                    "metrics": metrics
                })
                
                # Wait for next check
                if datetime.now() < end_time:
                    time.sleep(self.check_interval_seconds)
        
        except KeyboardInterrupt:
            print("\n⚠️  Test interrupted by user")
        
        # Analyze results
        analysis = self._analyze_results()
        return analysis
    
    def _analyze_results(self) -> Dict:
        """Analyze stability test results"""
        if not self.results:
            return {"error": "No results to analyze"}
        
        total_checks = len(self.results)
        
        # Endpoint success rates
        endpoint_stats = defaultdict(lambda: {"total": 0, "success": 0, "response_times": []})
        
        for check in self.results:
            for endpoint_result in check.get("endpoints", []):
                endpoint = endpoint_result.get("endpoint", "unknown")
                endpoint_stats[endpoint]["total"] += 1
                if endpoint_result.get("success"):
                    endpoint_stats[endpoint]["success"] += 1
                if endpoint_result.get("response_time"):
                    endpoint_stats[endpoint]["response_times"].append(endpoint_result["response_time"])
        
        # Memory trend
        memory_values = []
        for metrics in self.metrics_history:
            if "process" in metrics and "memory_rss_mb" in metrics["process"]:
                memory_values.append(metrics["process"]["memory_rss_mb"])
        
        memory_trend = "stable"
        if len(memory_values) > 10:
            initial_avg = sum(memory_values[:5]) / 5
            final_avg = sum(memory_values[-5:]) / 5
            if final_avg > initial_avg * 1.5:
                memory_trend = "increasing"  # Possible memory leak
            elif final_avg < initial_avg * 0.8:
                memory_trend = "decreasing"
        
        analysis = {
            "test_duration_hours": (datetime.now() - self.start_time).total_seconds() / 3600 if self.start_time else 0,
            "total_checks": total_checks,
            "endpoint_stats": {},
            "memory_trend": memory_trend,
            "memory_initial_mb": memory_values[0] if memory_values else 0,
            "memory_final_mb": memory_values[-1] if memory_values else 0,
            "memory_change_percent": ((memory_values[-1] - memory_values[0]) / memory_values[0] * 100) if len(memory_values) > 1 and memory_values[0] > 0 else 0,
            "stability_issues": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Calculate endpoint stats
        for endpoint, stats in endpoint_stats.items():
            success_rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
            avg_response_time = sum(stats["response_times"]) / len(stats["response_times"]) if stats["response_times"] else 0
            
            analysis["endpoint_stats"][endpoint] = {
                "success_rate": success_rate,
                "total_checks": stats["total"],
                "successful": stats["success"],
                "avg_response_time": avg_response_time
            }
            
            # Check for stability issues
            if success_rate < 0.95:
                analysis["stability_issues"].append({
                    "type": "low_success_rate",
                    "endpoint": endpoint,
                    "success_rate": success_rate
                })
        
        # Check for memory leak
        if memory_trend == "increasing" and analysis["memory_change_percent"] > 50:
            analysis["stability_issues"].append({
                "type": "possible_memory_leak",
                "memory_increase_percent": analysis["memory_change_percent"]
            })
        
        return analysis
    
    def print_analysis(self, analysis: Dict):
        """Print stability test analysis"""
        print("\n" + "="*60)
        print("Stability Test Results")
        print("="*60)
        
        print(f"\n📊 Test Summary:")
        print(f"  Duration: {analysis['test_duration_hours']:.2f} hours")
        print(f"  Total Checks: {analysis['total_checks']}")
        
        print(f"\n💾 Memory Analysis:")
        print(f"  Initial: {analysis['memory_initial_mb']:.2f} MB")
        print(f"  Final: {analysis['memory_final_mb']:.2f} MB")
        print(f"  Change: {analysis['memory_change_percent']:+.2f}%")
        print(f"  Trend: {analysis['memory_trend']}")
        
        if analysis['endpoint_stats']:
            print(f"\n📈 Endpoint Statistics:")
            for endpoint, stats in analysis['endpoint_stats'].items():
                print(f"  {endpoint}:")
                print(f"    Success Rate: {stats['success_rate']*100:.2f}%")
                print(f"    Avg Response Time: {stats['avg_response_time']*1000:.2f}ms")
        
        if analysis['stability_issues']:
            print(f"\n⚠️  Stability Issues:")
            for issue in analysis['stability_issues']:
                print(f"  - {issue.get('type', 'unknown')}: {issue}")
        else:
            print(f"\n✅ No stability issues detected")
    
    def save_results(self, analysis: Dict, output_path: Optional[str] = None) -> str:
        """Save stability test results"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(__file__).parent.parent.parent.parent / "reports" / "acceptance" / "performance" / f"stability_test_{timestamp}.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump({
                "analysis": analysis,
                "metrics_history": self.metrics_history[-100:],  # Last 100 metrics
                "sample_results": self.results[-10:]  # Last 10 checks
            }, f, indent=2)
        
        return str(output_path)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Stability testing")
    parser.add_argument(
        "-u", "--api-url",
        default="http://localhost:8000",
        help="API base URL"
    )
    parser.add_argument(
        "-d", "--duration",
        type=int,
        default=24,
        help="Test duration in hours"
    )
    parser.add_argument(
        "-i", "--interval",
        type=int,
        default=60,
        help="Check interval in minutes"
    )
    parser.add_argument(
        "-e", "--endpoints",
        help="JSON file with endpoints to monitor"
    )
    
    args = parser.parse_args()
    
    # Default endpoints
    if args.endpoints:
        with open(args.endpoints, 'r') as f:
            endpoints = json.load(f)
    else:
        endpoints = [
            {"method": "GET", "path": "/api/health"},
            {"method": "GET", "path": "/api/client/dashboard"}
        ]
    
    tester = StabilityTester(
        api_url=args.api_url,
        duration_hours=args.duration,
        check_interval_minutes=args.interval
    )
    
    analysis = tester.run_stability_test(endpoints)
    tester.print_analysis(analysis)
    
    output_path = tester.save_results(analysis)
    print(f"\n✅ Results saved to: {output_path}")

