"""
Performance Monitoring Utilities
For measuring latency and performance metrics
"""
import time
from typing import Dict, Optional
from datetime import datetime
from collections import deque
import statistics

class PerformanceMonitor:
    """Monitor performance metrics like latency, throughput, etc."""
    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.latency_samples: deque = deque(maxlen=max_samples)
        self.broadcast_times: deque = deque(maxlen=max_samples)
        self.message_sizes: deque = deque(maxlen=max_samples)
        
    def record_latency(self, latency_ms: float):
        """Record a latency measurement in milliseconds"""
        self.latency_samples.append(latency_ms)
    
    def record_broadcast_time(self, time_ms: float):
        """Record broadcast time in milliseconds"""
        self.broadcast_times.append(time_ms)
    
    def record_message_size(self, size_bytes: int):
        """Record message size in bytes"""
        self.message_sizes.append(size_bytes)
    
    def get_latency_stats(self) -> Dict[str, float]:
        """Get latency statistics"""
        if not self.latency_samples:
            return {
                "mean": 0.0,
                "median": 0.0,
                "min": 0.0,
                "max": 0.0,
                "p95": 0.0,
                "p99": 0.0,
                "count": 0,
            }
        
        samples = list(self.latency_samples)
        sorted_samples = sorted(samples)
        
        return {
            "mean": statistics.mean(samples),
            "median": statistics.median(samples),
            "min": min(samples),
            "max": max(samples),
            "p95": sorted_samples[int(len(sorted_samples) * 0.95)] if len(sorted_samples) > 0 else 0.0,
            "p99": sorted_samples[int(len(sorted_samples) * 0.99)] if len(sorted_samples) > 0 else 0.0,
            "count": len(samples),
        }
    
    def get_broadcast_stats(self) -> Dict[str, float]:
        """Get broadcast time statistics"""
        if not self.broadcast_times:
            return {
                "mean": 0.0,
                "max": 0.0,
                "count": 0,
            }
        
        samples = list(self.broadcast_times)
        return {
            "mean": statistics.mean(samples),
            "max": max(samples),
            "count": len(samples),
        }
    
    def get_message_size_stats(self) -> Dict[str, float]:
        """Get message size statistics"""
        if not self.message_sizes:
            return {
                "mean": 0.0,
                "max": 0.0,
                "count": 0,
            }
        
        samples = list(self.message_sizes)
        return {
            "mean": statistics.mean(samples),
            "max": max(samples),
            "count": len(samples),
        }
    
    def get_summary(self) -> Dict:
        """Get summary of all metrics"""
        return {
            "latency": self.get_latency_stats(),
            "broadcast": self.get_broadcast_stats(),
            "message_size": self.get_message_size_stats(),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def reset(self):
        """Reset all metrics"""
        self.latency_samples.clear()
        self.broadcast_times.clear()
        self.message_sizes.clear()


# Global performance monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


class LatencyTimer:
    """Context manager for measuring latency"""
    
    def __init__(self, monitor: Optional[PerformanceMonitor] = None):
        self.monitor = monitor or get_performance_monitor()
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            elapsed_ms = (time.perf_counter() - self.start_time) * 1000
            self.monitor.record_latency(elapsed_ms)
        return False

