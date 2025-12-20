#!/usr/bin/env python3
"""
Endpoint Verifier
Verifies all endpoints in acceptance_config.json exist in the API
Compares with Swagger/OpenAPI documentation
"""

import json
import requests
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EndpointVerifier:
    """Verify endpoints exist and match API documentation"""
    
    def __init__(self, config_path: str = None, api_url: str = "http://localhost:8000"):
        """Initialize verifier"""
        if config_path is None:
            config_path = Path(__file__).parent / "acceptance_config.json"
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.api_url = api_url
        self.openapi_spec = None
        self.verified_endpoints = []
        self.missing_endpoints = []
        self.invalid_paths = []
    
    def fetch_openapi_spec(self) -> Dict:
        """Fetch OpenAPI specification from API"""
        try:
            response = requests.get(f"{self.api_url}/openapi.json", timeout=10)
            if response.status_code == 200:
                self.openapi_spec = response.json()
                logger.info("✅ OpenAPI spec fetched successfully")
                return self.openapi_spec
            else:
                logger.warning(f"⚠️  Could not fetch OpenAPI spec: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"❌ Error fetching OpenAPI spec: {e}")
            return {}
    
    def get_api_paths(self) -> Dict[str, List[str]]:
        """Extract all paths and methods from OpenAPI spec"""
        if not self.openapi_spec:
            return {}
        
        paths = {}
        for path, methods in self.openapi_spec.get("paths", {}).items():
            paths[path] = list(methods.keys())
        
        return paths
    
    def verify_endpoint(self, method: str, path: str) -> Tuple[bool, str]:
        """
        Verify if an endpoint exists in API
        
        Returns:
            (exists, status_message)
        """
        # Normalize path
        if not path.startswith("/"):
            path = "/" + path
        
        # Check in OpenAPI spec
        api_paths = self.get_api_paths()
        
        # Try exact match first
        if path in api_paths:
            methods = api_paths[path]
            method_lower = method.lower()
            if method_lower in methods:
                return (True, "Found in OpenAPI spec")
            else:
                return (False, f"Path exists but method {method} not found. Available: {methods}")
        
        # Try to find similar paths
        similar_paths = [p for p in api_paths.keys() if path.split("/")[-1] in p or p.split("/")[-1] in path]
        if similar_paths:
            return (False, f"Path not found. Similar paths: {similar_paths[:3]}")
        
        # Try actual API call (lightweight check)
        try:
            test_response = requests.request(
                method,
                f"{self.api_url}{path}",
                timeout=5,
                headers={"Content-Type": "application/json"}
            )
            # If we get anything other than 404, the endpoint exists
            if test_response.status_code != 404:
                return (True, f"Endpoint responds (status: {test_response.status_code})")
            else:
                return (False, "Endpoint returns 404")
        except Exception as e:
            return (False, f"Error testing endpoint: {str(e)[:100]}")
    
    def verify_all_endpoints(self) -> Dict:
        """Verify all endpoints in config"""
        logger.info("Fetching OpenAPI specification...")
        self.fetch_openapi_spec()
        
        logger.info("Verifying endpoints from config...")
        api_modules = self.config.get("api_modules", [])
        
        results = {
            "total": 0,
            "verified": 0,
            "missing": 0,
            "invalid_paths": 0,
            "details": []
        }
        
        for module in api_modules:
            module_name = module["name"]
            base_path = module["base_path"]
            endpoints = module.get("endpoints", [])
            
            logger.info(f"Verifying module: {module_name} ({len(endpoints)} endpoints)")
            
            for endpoint in endpoints:
                parts = endpoint.split(" ", 1)
                if len(parts) == 2:
                    method, path = parts
                    full_path = f"{base_path}{path}"
                    
                    results["total"] += 1
                    exists, message = self.verify_endpoint(method, full_path)
                    
                    result_entry = {
                        "module": module_name,
                        "method": method,
                        "path": full_path,
                        "exists": exists,
                        "message": message
                    }
                    
                    if exists:
                        results["verified"] += 1
                        self.verified_endpoints.append(result_entry)
                    else:
                        results["missing"] += 1
                        self.missing_endpoints.append(result_entry)
                        # Check if path format might be wrong
                        if "404" in message or "not found" in message.lower():
                            results["invalid_paths"] += 1
                            self.invalid_paths.append(result_entry)
                    
                    results["details"].append(result_entry)
        
        return results
    
    def generate_report(self) -> str:
        """Generate verification report"""
        lines = []
        lines.append("="*80)
        lines.append("ENDPOINT VERIFICATION REPORT")
        lines.append("="*80)
        lines.append("")
        
        total = len(self.verified_endpoints) + len(self.missing_endpoints)
        verified = len(self.verified_endpoints)
        missing = len(self.missing_endpoints)
        
        lines.append(f"Total Endpoints: {total}")
        lines.append(f"Verified: {verified} ({verified/total*100:.1f}%)")
        lines.append(f"Missing/Invalid: {missing} ({missing/total*100:.1f}%)")
        lines.append("")
        
        if self.missing_endpoints:
            lines.append("="*80)
            lines.append("MISSING OR INVALID ENDPOINTS")
            lines.append("="*80)
            lines.append("")
            
            # Group by module
            by_module = {}
            for endpoint in self.missing_endpoints:
                module = endpoint["module"]
                if module not in by_module:
                    by_module[module] = []
                by_module[module].append(endpoint)
            
            for module, endpoints in sorted(by_module.items()):
                lines.append(f"\n{module.upper()} Module ({len(endpoints)} issues):")
                lines.append("-" * 80)
                for ep in endpoints[:10]:  # Show first 10
                    lines.append(f"  {ep['method']:6} {ep['path']}")
                    lines.append(f"         → {ep['message']}")
                if len(endpoints) > 10:
                    lines.append(f"  ... and {len(endpoints) - 10} more")
        
        lines.append("")
        lines.append("="*80)
        
        return "\n".join(lines)
    
    def save_results(self, output_path: str):
        """Save verification results to JSON"""
        results = {
            "verified_endpoints": self.verified_endpoints,
            "missing_endpoints": self.missing_endpoints,
            "invalid_paths": self.invalid_paths,
            "summary": {
                "total": len(self.verified_endpoints) + len(self.missing_endpoints),
                "verified": len(self.verified_endpoints),
                "missing": len(self.missing_endpoints),
                "invalid_paths": len(self.invalid_paths)
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to: {output_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify API endpoints")
    parser.add_argument(
        "-u", "--api-url",
        default="http://localhost:8000",
        help="API base URL"
    )
    parser.add_argument(
        "-o", "--output",
        default="endpoint_verification_results.json",
        help="Output file for results"
    )
    
    args = parser.parse_args()
    
    verifier = EndpointVerifier(api_url=args.api_url)
    results = verifier.verify_all_endpoints()
    
    print(verifier.generate_report())
    
    # Save results
    output_path = Path(__file__).parent / ".." / "reports" / "acceptance" / "test_results" / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    verifier.save_results(str(output_path))
    
    print(f"\nDetailed results saved to: {output_path}")

