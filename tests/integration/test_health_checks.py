"""
Integration Tests for Health Checks
Automated health check tests for all services
"""

import pytest
import requests
import time
import subprocess
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
BACKEND_HEALTH_URL = f"{BASE_URL}/api/health"
CLIENT_HEALTH_URL = "http://localhost:3002/health"
ADMIN_HEALTH_URL = "http://localhost:3001/health"
TIMEOUT = 10
RETRY_INTERVAL = 5
MAX_RETRIES = 12  # 1 minute total


class TestHealthChecks:
    """Health check integration tests"""
    
    def test_backend_health_endpoint(self):
        """Test backend health endpoint"""
        response = requests.get(BACKEND_HEALTH_URL, timeout=TIMEOUT)
        assert response.status_code == 200, f"Backend health check failed: {response.status_code}"
        
        data = response.json()
        assert data.get("status") in ["ok", "degraded"], f"Unexpected status: {data.get('status')}"
        print(f"✓ Backend health: {data.get('status')}")
    
    def test_backend_database_connection(self):
        """Test backend database connection"""
        response = requests.get(BACKEND_HEALTH_URL, timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("database") == "connected", f"Database not connected: {data.get('database')}"
        print(f"✓ Database connection: {data.get('database')}")
    
    def test_backend_redis_connection(self):
        """Test backend Redis connection"""
        response = requests.get(BACKEND_HEALTH_URL, timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("redis") == "connected", f"Redis not connected: {data.get('redis')}"
        print(f"✓ Redis connection: {data.get('redis')}")
    
    def test_client_app_health(self):
        """Test client app health endpoint"""
        response = requests.get(CLIENT_HEALTH_URL, timeout=TIMEOUT, allow_redirects=True)
        assert response.status_code in [200, 301, 302], f"Client app health check failed: {response.status_code}"
        print(f"✓ Client app health: HTTP {response.status_code}")
    
    def test_admin_app_health(self):
        """Test admin app health endpoint"""
        response = requests.get(ADMIN_HEALTH_URL, timeout=TIMEOUT, allow_redirects=True)
        assert response.status_code in [200, 301, 302], f"Admin app health check failed: {response.status_code}"
        print(f"✓ Admin app health: HTTP {response.status_code}")
    
    def test_database_connectivity(self):
        """Test PostgreSQL database connectivity"""
        result = subprocess.run(
            ["docker", "exec", "digital_utopia_postgres", "pg_isready", "-U", "postgres"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0, f"Database connectivity test failed: {result.stderr}"
        print("✓ PostgreSQL database is accessible")
    
    def test_redis_connectivity(self):
        """Test Redis connectivity"""
        result = subprocess.run(
            ["docker", "exec", "digital_utopia_redis", "redis-cli", "ping"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0, f"Redis connectivity test failed: {result.stderr}"
        assert "PONG" in result.stdout, "Redis did not respond with PONG"
        print("✓ Redis is accessible")
    
    def test_container_status(self):
        """Test all containers are running"""
        containers = [
            "digital_utopia_postgres",
            "digital_utopia_redis",
            "digital_utopia_backend",
            "digital_utopia_client",
            "digital_utopia_admin",
            "digital_utopia_nginx_proxy"
        ]
        
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        running_containers = result.stdout.strip().split('\n')
        
        for container in containers:
            assert container in running_containers, f"Container {container} is not running"
            print(f"✓ Container {container} is running")
    
    def test_backend_response_time(self):
        """Test backend response time"""
        start_time = time.time()
        response = requests.get(BACKEND_HEALTH_URL, timeout=TIMEOUT)
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0, f"Response time too slow: {response_time}s"
        print(f"✓ Backend response time: {response_time:.3f}s")


class TestHealthCheckAutomation:
    """Automated health check that runs periodically"""
    
    @pytest.mark.parametrize("iteration", range(12))  # Run 12 times (1 hour at 5min intervals)
    def test_periodic_health_check(self, iteration):
        """Periodic health check (runs every 5 minutes)"""
        print(f"\n=== Health Check Iteration {iteration + 1} ===")
        
        # Test backend
        response = requests.get(BACKEND_HEALTH_URL, timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        print(f"Backend Status: {data.get('status')}")
        print(f"Database: {data.get('database')}")
        print(f"Redis: {data.get('redis')}")
        
        # Wait 5 minutes before next check (except last iteration)
        if iteration < 11:
            print(f"Waiting 5 minutes before next check...")
            time.sleep(300)  # 5 minutes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
