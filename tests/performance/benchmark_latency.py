#!/usr/bin/env python3
"""
Performance Benchmark Script for CMEETRADING
Measures API latency and WebSocket performance

Requirements:
- pip install aiohttp websockets

Targets:
- AC-1: Real-time latency < 30ms
- AC-7: 10k concurrent WebSocket connections (scaled test)
"""

import asyncio
import aiohttp
import websockets
import time
import statistics
import json
from datetime import datetime
from typing import List, Dict, Any
import os
import sys

# Configuration
API_BASE = os.environ.get("API_BASE", "http://localhost:8000/api")
WS_URL = os.environ.get("WS_URL", "ws://localhost:8000/ws")
NUM_REQUESTS = int(os.environ.get("NUM_REQUESTS", "100"))
CONCURRENT_REQUESTS = int(os.environ.get("CONCURRENT_REQUESTS", "10"))
WS_CONNECTIONS = int(os.environ.get("WS_CONNECTIONS", "100"))  # Scaled down for local testing


class BenchmarkResults:
    def __init__(self, name: str):
        self.name = name
        self.latencies: List[float] = []
        self.errors: int = 0
        self.success: int = 0
        self.start_time: float = 0
        self.end_time: float = 0
    
    def add_latency(self, latency_ms: float):
        self.latencies.append(latency_ms)
        self.success += 1
    
    def add_error(self):
        self.errors += 1
    
    def get_stats(self) -> Dict[str, Any]:
        if not self.latencies:
            return {
                "name": self.name,
                "error": "No successful requests"
            }
        
        sorted_latencies = sorted(self.latencies)
        p50_idx = int(len(sorted_latencies) * 0.50)
        p90_idx = int(len(sorted_latencies) * 0.90)
        p95_idx = int(len(sorted_latencies) * 0.95)
        p99_idx = int(len(sorted_latencies) * 0.99)
        
        return {
            "name": self.name,
            "total_requests": self.success + self.errors,
            "successful": self.success,
            "errors": self.errors,
            "error_rate": f"{(self.errors / (self.success + self.errors) * 100):.2f}%",
            "latency_avg_ms": f"{statistics.mean(self.latencies):.2f}",
            "latency_min_ms": f"{min(self.latencies):.2f}",
            "latency_max_ms": f"{max(self.latencies):.2f}",
            "latency_p50_ms": f"{sorted_latencies[p50_idx]:.2f}",
            "latency_p90_ms": f"{sorted_latencies[p90_idx]:.2f}",
            "latency_p95_ms": f"{sorted_latencies[p95_idx]:.2f}",
            "latency_p99_ms": f"{sorted_latencies[p99_idx]:.2f}",
            "duration_seconds": f"{self.end_time - self.start_time:.2f}",
            "requests_per_second": f"{self.success / (self.end_time - self.start_time):.2f}",
        }
    
    def passed_ac1(self) -> bool:
        """Check if AC-1 is passed (p95 latency < 30ms)"""
        if not self.latencies:
            return False
        sorted_latencies = sorted(self.latencies)
        p95_idx = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[p95_idx] < 30


async def benchmark_rest_api():
    """Benchmark REST API endpoints"""
    print("\n" + "="*60)
    print("REST API BENCHMARK (AC-1: Latency < 30ms)")
    print("="*60)
    
    results = BenchmarkResults("REST API")
    
    endpoints = [
        "/market/prices",
        "/market/instruments",
    ]
    
    async def make_request(session: aiohttp.ClientSession, url: str):
        start = time.perf_counter()
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                await response.read()
                latency_ms = (time.perf_counter() - start) * 1000
                if response.status == 200:
                    results.add_latency(latency_ms)
                else:
                    results.add_error()
        except Exception as e:
            results.add_error()
    
    results.start_time = time.perf_counter()
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(NUM_REQUESTS):
            endpoint = endpoints[i % len(endpoints)]
            url = f"{API_BASE}{endpoint}"
            tasks.append(make_request(session, url))
            
            # Limit concurrent requests
            if len(tasks) >= CONCURRENT_REQUESTS:
                await asyncio.gather(*tasks)
                tasks = []
        
        # Complete remaining tasks
        if tasks:
            await asyncio.gather(*tasks)
    
    results.end_time = time.perf_counter()
    
    stats = results.get_stats()
    print(f"\nResults:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    if results.passed_ac1():
        print(f"\n✅ AC-1 PASSED: p95 latency < 30ms")
    else:
        print(f"\n❌ AC-1 FAILED: p95 latency >= 30ms")
    
    return results


async def benchmark_websocket():
    """Benchmark WebSocket connections"""
    print("\n" + "="*60)
    print(f"WEBSOCKET BENCHMARK (AC-7: {WS_CONNECTIONS} connections)")
    print("="*60)
    
    results = BenchmarkResults("WebSocket")
    connected = 0
    messages_received = 0
    
    async def connect_and_receive(ws_id: int):
        nonlocal connected, messages_received
        start = time.perf_counter()
        try:
            async with websockets.connect(
                WS_URL, 
                ping_interval=30,
                ping_timeout=10,
                close_timeout=5
            ) as ws:
                latency_ms = (time.perf_counter() - start) * 1000
                results.add_latency(latency_ms)
                connected += 1
                
                # Subscribe to prices
                await ws.send(json.dumps({
                    "type": "subscribe",
                    "channel": "prices",
                    "symbol": "BTCUSDT"
                }))
                
                # Wait for a message or timeout
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    messages_received += 1
                except asyncio.TimeoutError:
                    pass
                
        except Exception as e:
            results.add_error()
    
    results.start_time = time.perf_counter()
    
    # Create connections in batches
    batch_size = min(50, WS_CONNECTIONS)
    for i in range(0, WS_CONNECTIONS, batch_size):
        batch = range(i, min(i + batch_size, WS_CONNECTIONS))
        tasks = [connect_and_receive(j) for j in batch]
        await asyncio.gather(*tasks, return_exceptions=True)
        print(f"  Progress: {min(i + batch_size, WS_CONNECTIONS)}/{WS_CONNECTIONS} connections")
    
    results.end_time = time.perf_counter()
    
    stats = results.get_stats()
    print(f"\nResults:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print(f"  peak_connections: {connected}")
    print(f"  messages_received: {messages_received}")
    
    success_rate = connected / WS_CONNECTIONS
    if success_rate >= 0.95:  # 95% success rate
        print(f"\n✅ WebSocket test PASSED: {connected}/{WS_CONNECTIONS} connections")
    else:
        print(f"\n❌ WebSocket test FAILED: Only {connected}/{WS_CONNECTIONS} connections")
    
    return results


async def run_benchmarks():
    """Run all benchmarks"""
    print("\n" + "="*60)
    print("CMEETRADING PERFORMANCE BENCHMARK")
    print("="*60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"API_BASE: {API_BASE}")
    print(f"WS_URL: {WS_URL}")
    print(f"REST requests: {NUM_REQUESTS}")
    print(f"WS connections: {WS_CONNECTIONS}")
    
    rest_results = await benchmark_rest_api()
    ws_results = await benchmark_websocket()
    
    # Generate summary
    print("\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)
    
    ac1_passed = rest_results.passed_ac1()
    ac7_passed = ws_results.success >= WS_CONNECTIONS * 0.95
    
    print(f"\nAcceptance Criteria Results:")
    print(f"  AC-1 (Latency < 30ms): {'✅ PASSED' if ac1_passed else '❌ FAILED'}")
    print(f"  AC-7 (Scalability):    {'✅ PASSED' if ac7_passed else '❌ NEEDS FULL TEST'}")
    
    # Save results
    results_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(results_dir, f"benchmark_results_{timestamp}.json")
    
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "api_base": API_BASE,
            "ws_url": WS_URL,
            "num_requests": NUM_REQUESTS,
            "ws_connections": WS_CONNECTIONS,
        },
        "rest_api": rest_results.get_stats(),
        "websocket": ws_results.get_stats(),
        "acceptance_criteria": {
            "ac1_latency": "PASSED" if ac1_passed else "FAILED",
            "ac7_scalability": "PASSED" if ac7_passed else "NEEDS_FULL_TEST",
        }
    }
    
    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\nResults saved to: {results_file}")
    
    return ac1_passed and ac7_passed


if __name__ == "__main__":
    try:
        success = asyncio.run(run_benchmarks())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nBenchmark interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\nBenchmark error: {e}")
        sys.exit(1)
