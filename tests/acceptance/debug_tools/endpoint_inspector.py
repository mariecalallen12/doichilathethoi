#!/usr/bin/env python3
"""
Endpoint Inspector
Detailed inspection of API endpoints including request/response analysis
"""

import json
import requests
from typing import Dict, Optional, Any
from datetime import datetime
from pathlib import Path


class EndpointInspector:
    """Inspect API endpoints in detail"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        """Initialize inspector"""
        self.api_url = api_url
        self.inspection_history = []
    
    def inspect(self, method: str, path: str, headers: Optional[Dict] = None,
                data: Optional[Dict] = None, timeout: int = 10) -> Dict:
        """Inspect an endpoint in detail"""
        url = f"{self.api_url}{path}"
        method_func = getattr(requests, method.lower())
        
        inspection = {
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "path": path,
            "url": url,
            "request": {
                "headers": headers or {},
                "body": data
            },
            "response": None,
            "analysis": {}
        }
        
        try:
            start_time = datetime.now()
            response = method_func(url, json=data, headers=headers, timeout=timeout)
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Parse response
            try:
                response_data = response.json()
            except:
                response_data = response.text[:1000]
            
            inspection["response"] = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response_data,
                "response_time": response_time,
                "size": len(response.content)
            }
            
            # Analyze response
            inspection["analysis"] = self._analyze_response(response, response_data)
            
        except Exception as e:
            inspection["response"] = {
                "error": str(e),
                "status_code": None
            }
            inspection["analysis"] = {
                "error": True,
                "error_message": str(e)
            }
        
        self.inspection_history.append(inspection)
        return inspection
    
    def _analyze_response(self, response: requests.Response, data: Any) -> Dict:
        """Analyze response for issues"""
        analysis = {
            "status": "unknown",
            "issues": [],
            "suggestions": []
        }
        
        status_code = response.status_code
        
        # Status analysis
        if 200 <= status_code < 300:
            analysis["status"] = "success"
        elif status_code == 401:
            analysis["status"] = "unauthorized"
            analysis["issues"].append("Authentication required")
            analysis["suggestions"].append("Check if auth token is valid and included in headers")
        elif status_code == 403:
            analysis["status"] = "forbidden"
            analysis["issues"].append("Insufficient permissions")
            analysis["suggestions"].append("Check user role and permissions")
        elif status_code == 404:
            analysis["status"] = "not_found"
            analysis["issues"].append("Endpoint not found")
            analysis["suggestions"].append("Verify endpoint path and method")
        elif status_code == 422:
            analysis["status"] = "validation_error"
            analysis["issues"].append("Request validation failed")
            if isinstance(data, dict) and "detail" in data:
                analysis["suggestions"].append(f"Check validation errors: {data['detail']}")
        elif status_code == 429:
            analysis["status"] = "rate_limited"
            analysis["issues"].append("Rate limit exceeded")
            analysis["suggestions"].append("Wait before retrying or check rate limit settings")
        elif status_code >= 500:
            analysis["status"] = "server_error"
            analysis["issues"].append("Server error")
            analysis["suggestions"].append("Check server logs and backend implementation")
        
        # Response time analysis
        if response:
            response_time = getattr(response, 'elapsed', None)
            if response_time:
                response_time_seconds = response_time.total_seconds()
                if response_time_seconds > 2:
                    analysis["issues"].append(f"Slow response time: {response_time_seconds:.2f}s")
                    analysis["suggestions"].append("Check backend performance and database queries")
        
        # Response format analysis
        if isinstance(data, dict):
            if "error" in data and data.get("error"):
                analysis["issues"].append("Response indicates error")
            if "message" in data:
                analysis["message"] = data["message"]
        
        return analysis
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """Generate inspection report"""
        if output_path is None:
            output_path = Path(__file__).parent.parent.parent.parent / "reports" / "acceptance" / "debug" / "endpoint_inspections.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "total_inspections": len(self.inspection_history),
            "inspections": self.inspection_history
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return str(output_path)
    
    def print_inspection(self, inspection: Dict):
        """Print inspection details"""
        print("\n" + "="*60)
        print(f"Inspection: {inspection['method']} {inspection['path']}")
        print("="*60)
        
        print("\n📤 Request:")
        print(f"  URL: {inspection['url']}")
        print(f"  Headers: {json.dumps(inspection['request']['headers'], indent=2)}")
        if inspection['request']['body']:
            print(f"  Body: {json.dumps(inspection['request']['body'], indent=2)}")
        
        if inspection['response']:
            print("\n📥 Response:")
            print(f"  Status: {inspection['response'].get('status_code', 'N/A')}")
            if 'response_time' in inspection['response']:
                print(f"  Time: {inspection['response']['response_time']*1000:.2f}ms")
            if 'body' in inspection['response']:
                body = inspection['response']['body']
                if isinstance(body, dict):
                    print(f"  Body: {json.dumps(body, indent=2)[:500]}")
                else:
                    print(f"  Body: {str(body)[:500]}")
        
        if inspection['analysis']:
            print("\n🔍 Analysis:")
            analysis = inspection['analysis']
            print(f"  Status: {analysis.get('status', 'unknown')}")
            if analysis.get('issues'):
                print("  Issues:")
                for issue in analysis['issues']:
                    print(f"    - {issue}")
            if analysis.get('suggestions'):
                print("  Suggestions:")
                for suggestion in analysis['suggestions']:
                    print(f"    - {suggestion}")


if __name__ == "__main__":
    inspector = EndpointInspector()
    result = inspector.inspect("GET", "/api/health")
    inspector.print_inspection(result)

