#!/usr/bin/env python3
"""
Update acceptance_config.json with verified endpoint paths
Based on actual API routes from OpenAPI spec
"""

import json
import requests
from pathlib import Path
from typing import Dict, List


def fetch_actual_endpoints(api_url: str = "http://localhost:8000") -> Dict[str, List[str]]:
    """Fetch actual endpoints from OpenAPI spec"""
    try:
        response = requests.get(f"{api_url}/openapi.json", timeout=10)
        if response.status_code == 200:
            spec = response.json()
            paths = spec.get("paths", {})
            
            # Extract API paths with methods
            api_endpoints = {}
            for path, methods in paths.items():
                if path.startswith("/api/"):
                    api_endpoints[path] = [m.upper() for m in methods.keys() if m != "parameters"]
            
            return api_endpoints
    except Exception as e:
        print(f"Error fetching OpenAPI spec: {e}")
        return {}


def update_config_with_actual_endpoints():
    """Update acceptance_config.json with actual endpoint paths"""
    config_path = Path(__file__).parent.parent / "acceptance_config.json"
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Fetch actual endpoints
    print("Fetching actual API endpoints...")
    actual_endpoints = fetch_actual_endpoints()
    
    if not actual_endpoints:
        print("⚠️  Could not fetch endpoints, skipping update")
        return
    
    print(f"Found {len(actual_endpoints)} API paths")
    
    # Update each module
    updated_count = 0
    missing_endpoints = []
    
    for module in config.get("api_modules", []):
        module_name = module["name"]
        base_path = module["base_path"]
        endpoints = module.get("endpoints", [])
        
        updated_endpoints = []
        
        for endpoint in endpoints:
            parts = endpoint.split(" ", 1)
            if len(parts) == 2:
                method, path = parts
                full_path = f"{base_path}{path}"
                
                # Check if endpoint exists
                method_upper = method.upper()
                if full_path in actual_endpoints:
                    methods = actual_endpoints[full_path]
                    if method_upper in methods:
                        updated_endpoints.append(endpoint)
                        continue
                    else:
                        # Try to find correct method
                        if methods:
                            print(f"⚠️  {full_path}: Method {method} not found, available: {methods}")
                            # Use first available method or keep original
                            updated_endpoints.append(endpoint)
                            missing_endpoints.append({
                                "module": module_name,
                                "original": endpoint,
                                "path": full_path,
                                "available_methods": methods
                            })
                        continue
                
                # Try to find similar path
                similar = [p for p in actual_endpoints.keys() 
                          if p.startswith(base_path) and path.split("/")[-1] in p]
                if similar:
                    print(f"⚠️  {full_path} not found, similar: {similar[0]}")
                    # Keep original but note it
                    updated_endpoints.append(endpoint)
                    missing_endpoints.append({
                        "module": module_name,
                        "original": endpoint,
                        "path": full_path,
                        "similar": similar[0]
                    })
                else:
                    # Endpoint not found, keep it but mark as missing
                    updated_endpoints.append(endpoint)
                    missing_endpoints.append({
                        "module": module_name,
                        "original": endpoint,
                        "path": full_path,
                        "status": "not_found"
                    })
            else:
                updated_endpoints.append(endpoint)
        
        if len(updated_endpoints) != len(endpoints):
            updated_count += 1
        
        module["endpoints"] = updated_endpoints
    
    # Save updated config
    backup_path = config_path.with_suffix(".json.backup")
    with open(backup_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"✅ Backup saved to: {backup_path}")
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"✅ Config updated: {config_path}")
    
    # Save missing endpoints report
    if missing_endpoints:
        report_path = Path(__file__).parent.parent.parent.parent / "reports" / "acceptance" / "test_results" / "missing_endpoints.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump({
                "total_missing": len(missing_endpoints),
                "missing_endpoints": missing_endpoints
            }, f, indent=2)
        print(f"✅ Missing endpoints report: {report_path}")
        print(f"\n⚠️  Found {len(missing_endpoints)} endpoints that may need review")


if __name__ == "__main__":
    print("="*60)
    print("Updating Endpoint Configuration")
    print("="*60)
    print()
    update_config_with_actual_endpoints()
    print()
    print("="*60)
    print("Update Complete")
    print("="*60)

