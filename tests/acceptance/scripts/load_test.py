#!/usr/bin/env python3
"""
Load Testing
Test API performance under load
"""

import sys
import json
import time
import concurrent.futures
import requests
from pathlib import Path
from typing import Dict, List, Optional, Optional
from datetime import datetime
from collections import defaultdict
import statistics


class LoadTester:
    """Load testing for API endpoints"""
    
    def __init__(self, api_url: str = "http://localhost:8000", 
                 concurrent_users: int = 100,
                 requests_per_user: int = 10):
        """Initialize load tester"""
        self.api_url = api_url
        self.concurrent_users = concurrent_users
        self.requests_per_user = requests_per_user
        self.results = []
    
    def test_endpoint(self, method: str, path: str, headers: Dict = None, 
                     data: Dict = None) -> Dict:
        """Test a single endpoint"""
        url = f"{self.api_url}{path}"
        method_func = getattr(requests, method.lower())
        
        start_time = time.time()
        try:
            if data:
                response = method_func(url, json=data, headers=headers, timeout=10)
            else:
                response = method_func(url, headers=headers, timeout=10)
            
            response_time = time.time() - start_time
            
            return {
                "success": 200 <= response.status_code < 300,
                "status_code": response.status_code,
                "response_time": response_time,
                "error": None
            }
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "success": False,
                "status_code": None,
                "response_time": response_time,
                "error": str(e)
            }
    
    def user_simulation(self, user_id: int, endpoints: List[Dict]) -> List[Dict]:
        """Simulate a user making requests"""
        user_results = []
        
        for i in range(self.requests_per_user):
            # Select endpoint (round-robin)
            endpoint = endpoints[i % len(endpoints)]
            method = endpoint.get("method", "GET")
            path = endpoint.get("path", "/api/health")
            headers = endpoint.get("headers", {})
            data = endpoint.get("data")
            
            result = self.test_endpoint(method, path, headers, data)
            result["user_id"] = user_id
            result["request_number"] = i + 1
            user_results.append(result)
            
            # Small delay between requests
            time.sleep(0.1)
        
        return user_results
    
    def run_load_test(self, endpoints: List[Dict]) -> Dict:
        """Run load test with concurrent users"""
        print("="*60)
        print("Load Testing")
        print("="*60)
        print(f"Concurrent Users: {self.concurrent_users}")
        print(f"Requests per User: {self.requests_per_user}")
        print(f"Total Requests: {self.concurrent_users * self.requests_per_user}")
        print()
        
        start_time = time.time()
        
        # Run concurrent users
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.concurrent_users) as executor:
            futures = [
                executor.submit(self.user_simulation, user_id, endpoints)
                for user_id in range(self.concurrent_users)
            ]
            
            all_results = []
            for future in concurrent.futures.as_completed(futures):
                user_results = future.result()
                all_results.extend(user_results)
        
        total_time = time.time() - start_time
        
        # Analyze results
        total_requests = len(all_results)
        successful = sum(1 for r in all_results if r.get("success", False))
        failed = total_requests - successful
        
        response_times = [r["response_time"] for r in all_results if r.get("response_time")]
        
        analysis = {
            "total_requests": total_requests,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total_requests if total_requests > 0 else 0,
            "total_time": total_time,
            "requests_per_second": total_requests / total_time if total_time > 0 else 0,
            "response_times": {
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "mean": statistics.mean(response_times) if response_times else 0,
                "median": statistics.median(response_times) if response_times else 0,
                "p95": self._percentile(response_times, 95) if response_times else 0,
                "p99": self._percentile(response_times, 99) if response_times else 0
            },
            "errors_by_status": defaultdict(int),
            "timestamp": datetime.now().isoformat()
        }
        
        # Count errors by status
        for result in all_results:
            if not result.get("success"):
                status = result.get("status_code", "error")
                analysis["errors_by_status"][status] += 1
        
        self.results = all_results
        
        return analysis
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        if index >= len(sorted_data):
            index = len(sorted_data) - 1
        return sorted_data[index]
    
    def print_analysis(self, analysis: Dict):
        """Print load test analysis"""
        print("\n" + "="*60)
        print("Load Test Results")
        print("="*60)
        
        print(f"\n📊 Summary:")
        print(f"  Total Requests: {analysis['total_requests']}")
        print(f"  Successful: {analysis['successful']}")
        print(f"  Failed: {analysis['failed']}")
        print(f"  Success Rate: {analysis['success_rate']*100:.2f}%")
        print(f"  Total Time: {analysis['total_time']:.2f}s")
        print(f"  Requests/Second: {analysis['requests_per_second']:.2f}")
        
        rt = analysis['response_times']
        print(f"\n⏱️  Response Times:")
        print(f"  Min: {rt['min']*1000:.2f}ms")
        print(f"  Max: {rt['max']*1000:.2f}ms")
        print(f"  Mean: {rt['mean']*1000:.2f}ms")
        print(f"  Median: {rt['median']*1000:.2f}ms")
        print(f"  P95: {rt['p95']*1000:.2f}ms")
        print(f"  P99: {rt['p99']*1000:.2f}ms")
        
        if analysis['errors_by_status']:
            print(f"\n❌ Errors by Status:")
            for status, count in sorted(analysis['errors_by_status'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {status}: {count}")
    
    def save_results(self, analysis: Dict, output_path: Optional[str] = None) -> str:
        """Save load test results"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(__file__).parent.parent.parent.parent / "reports" / "acceptance" / "performance" / f"load_test_{timestamp}.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump({
                "analysis": analysis,
                "sample_results": self.results[:100]  # Sample of results
            }, f, indent=2)
        
        return str(output_path)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load testing")
    parser.add_argument(
        "-u", "--api-url",
        default="http://localhost:8000",
        help="API base URL"
    )
    parser.add_argument(
        "-c", "--concurrent",
        type=int,
        default=100,
        help="Number of concurrent users"
    )
    parser.add_argument(
        "-r", "--requests",
        type=int,
        default=10,
        help="Requests per user"
    )
    parser.add_argument(
        "-e", "--endpoints",
        help="JSON file with endpoints to test"
    )
    
    args = parser.parse_args()
    
    # Default endpoints to test
    if args.endpoints:
        with open(args.endpoints, 'r') as f:
            endpoints = json.load(f)
    else:
        endpoints = [
            {"method": "GET", "path": "/api/health"},
            {"method": "GET", "path": "/api/client/dashboard"},
            {"method": "GET", "path": "/api/market/prices"}
        ]
    
    tester = LoadTester(
        api_url=args.api_url,
        concurrent_users=args.concurrent,
        requests_per_user=args.requests
    )
    
    analysis = tester.run_load_test(endpoints)
    tester.print_analysis(analysis)
    
    output_path = tester.save_results(analysis)
    print(f"\n✅ Results saved to: {output_path}")

