"""
Performance Tests for API Endpoints
Tests response times, throughput, and performance baselines
"""

import pytest
import requests
import time
import statistics
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
BASE_URL = "http://localhost:8000"
HEALTH_ENDPOINT = f"{BASE_URL}/api/health"
CONCURRENT_REQUESTS = 10
TOTAL_REQUESTS = 100
TARGET_P95_RESPONSE_TIME = 0.5  # 500ms
TARGET_P99_RESPONSE_TIME = 1.0  # 1s


class TestAPIPerformance:
    """API performance tests"""
    
    def test_health_endpoint_response_time(self):
        """Test health endpoint response time"""
        response_times = []
        
        for i in range(10):
            start_time = time.time()
            response = requests.get(HEALTH_ENDPOINT, timeout=10)
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            response_times.append(response_time)
        
        avg_time = statistics.mean(response_times)
        p95_time = self._calculate_percentile(response_times, 95)
        
        print(f"Average response time: {avg_time:.3f}s")
        print(f"P95 response time: {p95_time:.3f}s")
        
        assert avg_time < 0.2, f"Average response time too high: {avg_time}s"
        assert p95_time < TARGET_P95_RESPONSE_TIME, f"P95 response time too high: {p95_time}s"
    
    def test_concurrent_requests(self):
        """Test API under concurrent load"""
        def make_request():
            start_time = time.time()
            try:
                response = requests.get(HEALTH_ENDPOINT, timeout=10)
                response_time = time.time() - start_time
                return {
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "success": response.status_code == 200
                }
            except Exception as e:
                return {
                    "status_code": 0,
                    "response_time": time.time() - start_time,
                    "success": False,
                    "error": str(e)
                }
        
        with ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
            futures = [executor.submit(make_request) for _ in range(TOTAL_REQUESTS)]
            results = [future.result() for future in as_completed(futures)]
        
        # Analyze results
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        success_rate = len(successful) / len(results) * 100
        response_times = [r["response_time"] for r in successful]
        
        if response_times:
            avg_time = statistics.mean(response_times)
            p95_time = self._calculate_percentile(response_times, 95)
            p99_time = self._calculate_percentile(response_times, 99)
            
            print(f"Total requests: {TOTAL_REQUESTS}")
            print(f"Successful: {len(successful)} ({success_rate:.1f}%)")
            print(f"Failed: {len(failed)}")
            print(f"Average response time: {avg_time:.3f}s")
            print(f"P95 response time: {p95_time:.3f}s")
            print(f"P99 response time: {p99_time:.3f}s")
            
            assert success_rate >= 95, f"Success rate too low: {success_rate}%"
            assert p95_time < TARGET_P95_RESPONSE_TIME, f"P95 response time too high: {p95_time}s"
            assert p99_time < TARGET_P99_RESPONSE_TIME, f"P99 response time too high: {p99_time}s"
        else:
            pytest.fail("All requests failed")
    
    def test_throughput(self):
        """Test API throughput (requests per second)"""
        start_time = time.time()
        request_count = 0
        
        # Run for 10 seconds
        while time.time() - start_time < 10:
            response = requests.get(HEALTH_ENDPOINT, timeout=10)
            assert response.status_code == 200
            request_count += 1
        
        elapsed_time = time.time() - start_time
        throughput = request_count / elapsed_time
        
        print(f"Requests processed: {request_count}")
        print(f"Time elapsed: {elapsed_time:.2f}s")
        print(f"Throughput: {throughput:.2f} requests/second")
        
        assert throughput > 10, f"Throughput too low: {throughput} req/s"
    
    def test_response_time_consistency(self):
        """Test that response times are consistent"""
        response_times = []
        
        for i in range(50):
            start_time = time.time()
            response = requests.get(HEALTH_ENDPOINT, timeout=10)
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            response_times.append(response_time)
        
        # Calculate coefficient of variation
        mean_time = statistics.mean(response_times)
        std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
        cv = (std_dev / mean_time) * 100 if mean_time > 0 else 0
        
        print(f"Mean response time: {mean_time:.3f}s")
        print(f"Standard deviation: {std_dev:.3f}s")
        print(f"Coefficient of variation: {cv:.2f}%")
        
        # CV should be less than 50% for consistent performance
        assert cv < 50, f"Response times too inconsistent: CV={cv}%"
    
    @staticmethod
    def _calculate_percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile of a list"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        if index >= len(sorted_data):
            index = len(sorted_data) - 1
        return sorted_data[index]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
