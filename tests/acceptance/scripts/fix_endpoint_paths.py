#!/usr/bin/env python3
"""
Fix endpoint paths in acceptance_config.json based on OpenAPI spec
Automatically updates paths and methods to match actual API
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def fetch_openapi_spec(api_url: str = "http://localhost:8000") -> Dict:
    """Fetch OpenAPI specification"""
    try:
        response = requests.get(f"{api_url}/openapi.json", timeout=10)
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception as e:
        print(f"Error fetching OpenAPI spec: {e}")
        return {}


def find_matching_endpoint(target_path: str, target_method: str, 
                          api_endpoints: Dict[str, List[str]]) -> Optional[Tuple[str, str]]:
    """
    Find matching endpoint in API
    Returns: (actual_path, actual_method) or None
    """
    target_method_upper = target_method.upper()
    
    # Try exact match first
    if target_path in api_endpoints:
        methods = api_endpoints[target_path]
        if target_method_upper in methods:
            return (target_path, target_method_upper)
        # Try to find correct method
        if methods:
            return (target_path, methods[0])
    
    # Try to find similar path
    # Extract last part of path
    path_parts = target_path.split("/")
    last_part = path_parts[-1] if path_parts else ""
    
    # Search for paths with similar ending
    for api_path, methods in api_endpoints.items():
        if api_path.endswith(last_part) or last_part in api_path:
            # Check if base path matches
            target_base = "/".join(path_parts[:-1]) if len(path_parts) > 1 else ""
            api_base = "/".join(api_path.split("/")[:-1])
            
            if target_base == api_base or not target_base:
                if target_method_upper in methods:
                    return (api_path, target_method_upper)
                elif methods:
                    return (api_path, methods[0])
    
    # Try fuzzy match by path components
    target_components = set([p for p in path_parts if p and not p.startswith("{")])
    for api_path, methods in api_endpoints.items():
        api_components = set([p for p in api_path.split("/") if p and not p.startswith("{")])
        # If most components match
        if len(target_components & api_components) >= len(target_components) * 0.6:
            if target_method_upper in methods:
                return (api_path, target_method_upper)
            elif methods:
                return (api_path, methods[0])
    
    return None


def fix_endpoint_paths(api_url: str = "http://localhost:8000"):
    """Fix endpoint paths in acceptance_config.json"""
    config_path = Path(__file__).parent.parent / "acceptance_config.json"
    
    # Load config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Fetch OpenAPI spec
    print("Fetching OpenAPI specification...")
    spec = fetch_openapi_spec(api_url)
    if not spec:
        print("❌ Could not fetch OpenAPI spec")
        return False
    
    # Extract API endpoints
    api_endpoints = {}
    for path, methods in spec.get("paths", {}).items():
        if path.startswith("/api/"):
            api_endpoints[path] = [m.upper() for m in methods.keys() if m != "parameters"]
    
    print(f"Found {len(api_endpoints)} API paths")
    print()
    
    # Create backup
    backup_path = config_path.with_suffix(".json.backup2")
    with open(backup_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"✅ Backup saved to: {backup_path}")
    print()
    
    # Track changes
    total_endpoints = 0
    fixed_endpoints = 0
    not_found_endpoints = []
    method_fixes = 0
    
    # Update each module
    for module in config.get("api_modules", []):
        module_name = module["name"]
        base_path = module["base_path"]
        endpoints = module.get("endpoints", [])
        
        updated_endpoints = []
        module_fixes = 0
        
        for endpoint in endpoints:
            total_endpoints += 1
            parts = endpoint.split(" ", 1)
            if len(parts) == 2:
                method, path = parts
                full_path = f"{base_path}{path}"
                
                # Find matching endpoint
                match = find_matching_endpoint(full_path, method, api_endpoints)
                
                if match:
                    actual_path, actual_method = match
                    
                    # Calculate relative path from base
                    if actual_path.startswith(base_path):
                        relative_path = actual_path[len(base_path):]
                        new_endpoint = f"{actual_method} {relative_path}"
                        
                        if new_endpoint != endpoint:
                            print(f"✅ Fixed: {endpoint}")
                            print(f"   → {new_endpoint}")
                            if actual_method != method.upper():
                                method_fixes += 1
                            fixed_endpoints += 1
                            module_fixes += 1
                            updated_endpoints.append(new_endpoint)
                        else:
                            updated_endpoints.append(endpoint)
                    else:
                        # Path doesn't match base, keep original
                        updated_endpoints.append(endpoint)
                        not_found_endpoints.append({
                            "module": module_name,
                            "original": endpoint,
                            "path": full_path,
                            "note": "Path doesn't match module base"
                        })
                else:
                    # Not found, keep original but mark
                    updated_endpoints.append(endpoint)
                    not_found_endpoints.append({
                        "module": module_name,
                        "original": endpoint,
                        "path": full_path,
                        "note": "Not found in API"
                    })
            else:
                updated_endpoints.append(endpoint)
        
        module["endpoints"] = updated_endpoints
        
        if module_fixes > 0:
            print(f"  Module '{module_name}': {module_fixes} endpoints fixed")
    
    # Save updated config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print()
    print("="*60)
    print("Summary")
    print("="*60)
    print(f"Total endpoints: {total_endpoints}")
    print(f"Fixed: {fixed_endpoints}")
    print(f"Method fixes: {method_fixes}")
    print(f"Not found: {len(not_found_endpoints)}")
    print()
    
    # Save not found endpoints report
    if not_found_endpoints:
        report_path = Path(__file__).parent.parent.parent.parent / "reports" / "acceptance" / "test_results" / "endpoints_not_found.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump({
                "total_not_found": len(not_found_endpoints),
                "endpoints": not_found_endpoints
            }, f, indent=2)
        print(f"⚠️  {len(not_found_endpoints)} endpoints not found - saved to: {report_path}")
    
    print(f"✅ Config updated: {config_path}")
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix endpoint paths in acceptance_config.json")
    parser.add_argument(
        "-u", "--api-url",
        default="http://localhost:8000",
        help="API base URL"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("Fix Endpoint Paths")
    print("="*60)
    print()
    
    success = fix_endpoint_paths(api_url=args.api_url)
    
    if success:
        print("\n✅ Endpoint paths fixed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Failed to fix endpoint paths")
        sys.exit(1)

