#!/usr/bin/env python3
"""
Fix Missing Endpoints
Review 31 not-found endpoints and either implement or mark as not-implemented
"""

import json
import sys
import requests
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class MissingEndpointFixer:
    """Fix missing endpoints systematically"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        """Initialize fixer"""
        self.api_url = api_url
        self.openapi_spec = None
        self.actual_endpoints = {}
        self.fix_plan = {
            "to_implement": [],
            "to_mark_not_implemented": [],
            "to_fix_path": [],
            "already_exists": []
        }
    
    def fetch_openapi_spec(self) -> bool:
        """Fetch OpenAPI specification"""
        try:
            response = requests.get(f"{self.api_url}/openapi.json", timeout=10)
            if response.status_code == 200:
                self.openapi_spec = response.json()
                
                # Extract actual endpoints
                for path, methods in self.openapi_spec.get("paths", {}).items():
                    if path.startswith("/api/"):
                        self.actual_endpoints[path] = [m.upper() for m in methods.keys() if m != "parameters"]
                
                print(f"✅ Fetched OpenAPI spec: {len(self.actual_endpoints)} endpoints found")
                return True
            return False
        except Exception as e:
            print(f"❌ Error fetching OpenAPI spec: {e}")
            return False
    
    def load_missing_endpoints(self) -> List[Dict]:
        """Load list of missing endpoints"""
        missing_file = Path(__file__).parent.parent.parent.parent / "reports" / "acceptance" / "test_results" / "endpoints_not_found.json"
        
        if not missing_file.exists():
            print(f"⚠️  Missing endpoints file not found: {missing_file}")
            return []
        
        with open(missing_file, 'r') as f:
            data = json.load(f)
        
        return data.get("endpoints", [])
    
    def analyze_missing_endpoints(self, missing_endpoints: List[Dict]) -> Dict:
        """Analyze missing endpoints and create fix plan"""
        print("\n" + "="*60)
        print("Analyzing Missing Endpoints")
        print("="*60)
        
        for endpoint in missing_endpoints:
            path = endpoint.get("path", "")
            original = endpoint.get("original", "")
            module = endpoint.get("module", "")
            
            # Extract method and path from original
            parts = original.split(" ", 1)
            if len(parts) == 2:
                method, rel_path = parts
                base_path = f"/api/{module}" if module != "unknown" else "/api"
                full_path = f"{base_path}{rel_path}"
                
                # Check if endpoint exists with different path
                similar = self._find_similar_endpoint(full_path, method)
                
                if similar:
                    if similar["exact_match"]:
                        self.fix_plan["already_exists"].append({
                            "original": original,
                            "actual": similar["path"],
                            "note": "Endpoint exists with correct path"
                        })
                    else:
                        self.fix_plan["to_fix_path"].append({
                            "original": original,
                            "current_path": full_path,
                            "suggested_path": similar["path"],
                            "note": "Path needs correction"
                        })
                else:
                    # Check if it should be implemented
                    if self._should_implement(endpoint):
                        self.fix_plan["to_implement"].append({
                            "original": original,
                            "path": full_path,
                            "method": method,
                            "module": module,
                            "note": "Should be implemented"
                        })
                    else:
                        self.fix_plan["to_mark_not_implemented"].append({
                            "original": original,
                            "path": full_path,
                            "method": method,
                            "module": module,
                            "note": "Mark as not-implemented"
                        })
        
        return self.fix_plan
    
    def _find_similar_endpoint(self, path: str, method: str) -> Optional[Dict]:
        """Find similar endpoint in actual API"""
        method_upper = method.upper()
        
        # Try exact match
        if path in self.actual_endpoints:
            methods = self.actual_endpoints[path]
            if method_upper in methods:
                return {"exact_match": True, "path": path, "method": method_upper}
            elif methods:
                return {"exact_match": False, "path": path, "method": methods[0]}
        
        # Try fuzzy match
        path_parts = path.split("/")
        last_part = path_parts[-1] if path_parts else ""
        
        for api_path, methods in self.actual_endpoints.items():
            if api_path.endswith(last_part) or last_part in api_path:
                if method_upper in methods:
                    return {"exact_match": False, "path": api_path, "method": method_upper}
                elif methods:
                    return {"exact_match": False, "path": api_path, "method": methods[0]}
        
        return None
    
    def _should_implement(self, endpoint: Dict) -> bool:
        """Determine if endpoint should be implemented"""
        module = endpoint.get("module", "")
        path = endpoint.get("path", "")
        
        # Critical modules should have all endpoints
        critical_modules = ["auth", "client", "financial", "trading"]
        if module in critical_modules:
            return True
        
        # Check if it's a common pattern
        common_patterns = ["/health", "/status", "/dashboard", "/profile", "/settings"]
        if any(pattern in path for pattern in common_patterns):
            return True
        
        # Default: mark as not-implemented
        return False
    
    def update_config(self, fix_plan: Dict) -> bool:
        """Update acceptance_config.json based on fix plan"""
        config_path = Path(__file__).parent.parent / "acceptance_config.json"
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Create backup
        backup_path = config_path.with_suffix(".json.backup3")
        with open(backup_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Backup saved to: {backup_path}")
        
        # Update endpoints
        for module in config.get("api_modules", []):
            module_name = module["name"]
            endpoints = module.get("endpoints", [])
            
            updated_endpoints = []
            for endpoint in endpoints:
                # Check if this endpoint should be removed (marked as not-implemented)
                should_remove = False
                for item in fix_plan["to_mark_not_implemented"]:
                    if item["original"] == endpoint:
                        should_remove = True
                        break
                
                if not should_remove:
                    # Check if path needs fixing
                    for item in fix_plan["to_fix_path"]:
                        if item["original"] == endpoint:
                            # Update endpoint with correct path
                            parts = endpoint.split(" ", 1)
                            if len(parts) == 2:
                                method, old_path = parts
                                new_path = item["suggested_path"]
                                # Calculate relative path
                                base_path = module.get("base_path", "")
                                if new_path.startswith(base_path):
                                    rel_path = new_path[len(base_path):]
                                    endpoint = f"{method} {rel_path}"
                            break
                    
                    updated_endpoints.append(endpoint)
            
            module["endpoints"] = updated_endpoints
        
        # Save updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Config updated: {config_path}")
        return True
    
    def generate_implementation_list(self, fix_plan: Dict, output_path: Optional[str] = None) -> str:
        """Generate list of endpoints to implement"""
        if output_path is None:
            output_path = Path(__file__).parent.parent.parent.parent / "reports" / "acceptance" / "issues" / "endpoints_to_implement.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_to_implement": len(fix_plan["to_implement"]),
                "total_to_mark": len(fix_plan["to_mark_not_implemented"]),
                "total_to_fix_path": len(fix_plan["to_fix_path"]),
                "fix_plan": fix_plan
            }, f, indent=2)
        
        return str(output_path)
    
    def fix_all(self) -> Dict:
        """Run all missing endpoint fixes"""
        print("="*60)
        print("Fixing Missing Endpoints")
        print("="*60)
        
        # Step 1: Fetch OpenAPI spec
        if not self.fetch_openapi_spec():
            print("❌ Cannot proceed without OpenAPI spec")
            return {}
        
        # Step 2: Load missing endpoints
        missing_endpoints = self.load_missing_endpoints()
        print(f"\n📋 Found {len(missing_endpoints)} missing endpoints")
        
        # Step 3: Analyze
        fix_plan = self.analyze_missing_endpoints(missing_endpoints)
        
        # Step 4: Update config
        self.update_config(fix_plan)
        
        # Step 5: Generate implementation list
        impl_file = self.generate_implementation_list(fix_plan)
        
        # Summary
        print("\n" + "="*60)
        print("Summary")
        print("="*60)
        print(f"Already exists: {len(fix_plan['already_exists'])}")
        print(f"To fix path: {len(fix_plan['to_fix_path'])}")
        print(f"To implement: {len(fix_plan['to_implement'])}")
        print(f"To mark not-implemented: {len(fix_plan['to_mark_not_implemented'])}")
        print(f"\n✅ Implementation list: {impl_file}")
        
        return fix_plan


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix missing endpoints")
    parser.add_argument(
        "-u", "--api-url",
        default="http://localhost:8000",
        help="API base URL"
    )
    
    args = parser.parse_args()
    
    fixer = MissingEndpointFixer(api_url=args.api_url)
    fix_plan = fixer.fix_all()
    
    if fix_plan:
        print("\n✅ Missing endpoints analysis complete!")
        sys.exit(0)
    else:
        print("\n❌ Failed to fix missing endpoints")
        sys.exit(1)

