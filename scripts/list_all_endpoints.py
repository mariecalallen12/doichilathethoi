#!/usr/bin/env python3
"""
Script to list all API endpoints from the FastAPI backend
Scans all endpoint files and extracts route information
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

# Base directory
BASE_DIR = Path(__file__).parent.parent
ENDPOINTS_DIR = BASE_DIR / "backend" / "app" / "api" / "endpoints"

# Route decorator patterns
ROUTE_PATTERNS = [
    r'@router\.(get|post|put|delete|patch|head|options)\s*\(([^)]+)\)',
    r'@router\.(get|post|put|delete|patch|head|options)\s*\(([^)]+),\s*response_model',
    r'@router\.(get|post|put|delete|patch|head|options)\s*\(([^)]+),\s*status_code',
]

def extract_routes_from_file(file_path: Path) -> List[Dict[str, Any]]:
    """Extract all routes from a Python file"""
    routes = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract module name
        module_name = file_path.stem
        
        # Use regex parsing (more reliable for multiline decorators)
        # Pattern to match @router.method( with multiline support
        # First try simple pattern
        route_pattern = r'@router\.(get|post|put|delete|patch|head|options)\s*\(\s*["\']([^"\']+)["\']'
        matches = re.finditer(route_pattern, content, re.MULTILINE)
        
        # Also try pattern that handles multiline decorators with newlines
        if not matches or len(list(matches)) == 0:
            # Reset matches iterator
            route_pattern_multiline = r'@router\.(get|post|put|delete|patch|head|options)\s*\(\s*["\']([^"\']+)["\']'
            matches = re.finditer(route_pattern_multiline, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            method = match.group(1).upper()
            path = match.group(2)
            
            # Find the function definition after this decorator
            start_pos = match.end()
            remaining = content[start_pos:]
            
            # Look for function definition in next 50 lines
            lines = remaining.split('\n')[:50]
            for i, line in enumerate(lines):
                func_match = re.match(r'\s*(async\s+)?def\s+(\w+)', line)
                if func_match:
                    func_name = func_match.group(2)
                    
                    # Extract docstring
                    docstring = ""
                    if i + 1 < len(lines):
                        docstring_line = lines[i + 1].strip()
                        if docstring_line.startswith('"""') or docstring_line.startswith("'''"):
                            # Get full docstring (may span multiple lines)
                            docstring = docstring_line.strip('"""').strip("'''").strip()
                    
                    # Check if already added
                    if not any(r['function'] == func_name and r['method'] == method and r['path'] == path for r in routes):
                        routes.append({
                            'method': method,
                            'path': path,
                            'function': func_name,
                            'module': module_name,
                            'description': docstring,
                            'file': str(file_path.relative_to(BASE_DIR))
                        })
                    break
        
        # Also try AST parsing as supplement
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if function has route decorator
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call):
                            if isinstance(decorator.func, ast.Attribute):
                                if decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                                    method = decorator.func.attr.upper()
                                    
                                    # Extract path from arguments
                                    path = "/"
                                    if decorator.args:
                                        if isinstance(decorator.args[0], ast.Constant):
                                            path = decorator.args[0].value
                                        elif isinstance(decorator.args[0], ast.Str):  # Python < 3.8
                                            path = decorator.args[0].s
                                    
                                    # Get docstring
                                    docstring = ast.get_docstring(node) or ""
                                    
                                    # Check if already added
                                    if not any(r['function'] == node.name and r['method'] == method and r['path'] == path for r in routes):
                                        routes.append({
                                            'method': method,
                                            'path': path,
                                            'function': node.name,
                                            'module': module_name,
                                            'description': docstring,
                                            'file': str(file_path.relative_to(BASE_DIR))
                                        })
        except SyntaxError:
            pass  # AST is just a supplement
        
        # Fallback to old regex patterns if still no routes found
        if not routes:
            for pattern in ROUTE_PATTERNS:
                matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                method = match.group(1).upper()
                params = match.group(2)
                
                # Extract path from params (handle multiline)
                path_match = re.search(r'["\']([^"\']+)["\']', params, re.DOTALL)
                if path_match:
                    path = path_match.group(1).strip()
                else:
                    # Try to find path variable
                    path_var_match = re.search(r'path\s*[:=]\s*["\']([^"\']+)["\']', params, re.DOTALL)
                    if path_var_match:
                        path = path_var_match.group(1).strip()
                    else:
                        path = "/"
                
                # Extract function name (next non-empty line after decorator)
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if match.group(0) in line or (i > 0 and match.group(0) in lines[i-1]):
                        # Look for function definition in next few lines
                        for j in range(i+1, min(i+10, len(lines))):
                            func_line = lines[j].strip()
                            func_match = re.match(r'(async\s+)?def\s+(\w+)', func_line)
                            if func_match:
                                func_name = func_match.group(2)
                                
                                # Extract docstring
                                docstring = ""
                                if j + 1 < len(lines):
                                    docstring_line = lines[j + 1].strip()
                                    if docstring_line.startswith('"""') or docstring_line.startswith("'''"):
                                        docstring = docstring_line.strip('"""').strip("'''").strip()
                                
                                # Check if already added
                                if not any(r['function'] == func_name and r['method'] == method and r['path'] == path for r in routes):
                                    routes.append({
                                        'method': method,
                                        'path': path,
                                        'function': func_name,
                                        'module': module_name,
                                        'description': docstring,
                                        'file': str(file_path.relative_to(BASE_DIR))
                                    })
                                break
                            break
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    
    return routes

def get_router_prefix(file_path: Path) -> str:
    """Get router prefix from main.py"""
    main_py = BASE_DIR / "backend" / "main.py"
    
    try:
        with open(main_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find router include for this module
        module_name = file_path.stem
        pattern = rf'app\.include_router\((\w+)\.router,\s*prefix=["\']([^"\']+)["\']'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            router_var = match.group(1)
            prefix = match.group(2)
            
            # Check if this router matches our module
            import_pattern = rf'from\s+app\.api\.endpoints\s+import\s+.*{module_name}.*as\s+{router_var}'
            if re.search(import_pattern, content):
                return prefix
        
        # Try alternative pattern
        pattern2 = rf'from\s+app\.api\.endpoints\s+import\s+{module_name}'
        if re.search(pattern2, content):
            # Find include_router for this module
            pattern3 = rf'app\.include_router\({module_name}\.router,\s*prefix=["\']([^"\']+)["\']'
            match = re.search(pattern3, content)
            if match:
                return match.group(1)
    
    except Exception as e:
        print(f"Error getting router prefix: {e}")
    
    # Default prefixes based on module name
    prefix_map = {
        'auth': '/api/auth',
        'client': '/api/client',
        'admin': '/api/admin',
        'financial': '/api/financial',
        'market': '/api/market',
        'portfolio': '/api/portfolio',
        'compliance': '/api/compliance',
        'risk_management': '/api/risk-management',
        'staff_referrals': '/api/staff',
        'users': '/api',
        'diagnostics': '/api/diagnostics',
        'alert_rules': '/api',
        'notifications': '/api',
        'audit': '/api',
        'performance': '/api',
        'education': '/api/education',
        'analysis': '/api/analysis',
        'support': '/api/support',
        'legal': '/api/legal',
        'opex_trading': '/api/trading',
        'opex_market': '/api/market',
        'admin_trading': '/api/admin',
    }
    
    return prefix_map.get(file_path.stem, '/api')

def main():
    """Main function to list all endpoints"""
    all_routes = []
    routes_by_module = defaultdict(list)
    
    # Scan all endpoint files
    if not ENDPOINTS_DIR.exists():
        print(f"Error: Endpoints directory not found: {ENDPOINTS_DIR}")
        return
    
    endpoint_files = list(ENDPOINTS_DIR.glob("*.py"))
    endpoint_files = [f for f in endpoint_files if f.name != "__init__.py"]
    
    print(f"Scanning {len(endpoint_files)} endpoint files...")
    
    for file_path in sorted(endpoint_files):
        print(f"Processing {file_path.name}...")
        routes = extract_routes_from_file(file_path)
        
        # Add prefix to paths
        prefix = get_router_prefix(file_path)
        for route in routes:
            # Combine prefix and path
            path = route['path']
            # If path already starts with prefix, don't add it again
            if path.startswith(prefix):
                full_path = path
            else:
                full_path = prefix.rstrip('/') + '/' + path.lstrip('/')
            route['full_path'] = full_path
            route['prefix'] = prefix
            routes_by_module[route['module']].append(route)
            all_routes.append(route)
    
    # Remove duplicates based on (method, full_path) combination
    seen = set()
    unique_routes = []
    for route in all_routes:
        key = (route['method'], route['full_path'])
        if key not in seen:
            seen.add(key)
            unique_routes.append(route)
        else:
            # Keep the first occurrence, log duplicate
            print(f"Warning: Duplicate endpoint found: {route['method']} {route['full_path']} (from {route['file']})")
    
    all_routes = unique_routes
    
    # Sort routes
    all_routes.sort(key=lambda x: (x['module'], x['method'], x['path']))
    
    # Generate report
    print("\n" + "="*80)
    print("API ENDPOINTS SUMMARY")
    print("="*80)
    print(f"\nTotal endpoints found: {len(all_routes)}")
    print(f"Modules: {len(routes_by_module)}")
    
    # Group by module
    print("\n" + "-"*80)
    print("ENDPOINTS BY MODULE")
    print("-"*80)
    
    for module, routes in sorted(routes_by_module.items()):
        print(f"\n{module.upper()} ({len(routes)} endpoints)")
        print("-" * 80)
        for route in routes:
            print(f"  {route['method']:6} {route['full_path']:50} {route['function']}")
            if route['description']:
                print(f"         {route['description'][:70]}")
    
    # Group by method
    print("\n" + "-"*80)
    print("ENDPOINTS BY METHOD")
    print("-"*80)
    
    routes_by_method = defaultdict(list)
    for route in all_routes:
        routes_by_method[route['method']].append(route)
    
    for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
        if method in routes_by_method:
            print(f"\n{method} ({len(routes_by_method[method])} endpoints)")
            for route in sorted(routes_by_method[method], key=lambda x: x['full_path']):
                print(f"  {route['full_path']:60} [{route['module']}]")
    
    # Save to JSON
    output_file = BASE_DIR / "scripts" / "endpoints_list.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total': len(all_routes),
            'modules': len(routes_by_module),
            'endpoints': all_routes,
            'by_module': {k: v for k, v in routes_by_module.items()},
            'by_method': {k: [r['full_path'] for r in v] for k, v in routes_by_method.items()}
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n\nDetailed JSON report saved to: {output_file}")
    
    # Save to markdown
    output_md = BASE_DIR / "scripts" / "endpoints_list.md"
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write("# API Endpoints List\n\n")
        f.write(f"**Total:** {len(all_routes)} endpoints across {len(routes_by_module)} modules\n\n")
        
        f.write("## Endpoints by Module\n\n")
        for module, routes in sorted(routes_by_module.items()):
            f.write(f"### {module.upper()} ({len(routes)} endpoints)\n\n")
            f.write("| Method | Path | Function | Description |\n")
            f.write("|--------|------|----------|-------------|\n")
            for route in routes:
                desc = route['description'].replace('|', '\\|')[:100] if route['description'] else ""
                f.write(f"| {route['method']} | `{route['full_path']}` | `{route['function']}` | {desc} |\n")
            f.write("\n")
    
    print(f"Markdown report saved to: {output_md}")

if __name__ == "__main__":
    main()

