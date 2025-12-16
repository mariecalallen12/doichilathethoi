#!/usr/bin/env python3
"""
Script to verify all backend endpoints for Education, Analysis, Support, and Legal modules.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from fastapi import FastAPI
from backend.main import app

def verify_routes():
    """Verify all routes are registered"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                'path': route.path,
                'methods': list(route.methods)
            })
    
    # Expected endpoints
    expected = {
        'education': [
            ('/api/education/videos', ['GET']),
            ('/api/education/videos/{video_id}', ['GET']),
            ('/api/education/ebooks', ['GET']),
            ('/api/education/ebooks/{ebook_id}', ['GET']),
            ('/api/education/calendar', ['GET']),
            ('/api/education/reports', ['GET']),
            ('/api/education/reports/{report_id}', ['GET']),
            ('/api/education/progress', ['POST']),
        ],
        'analysis': [
            ('/api/analysis/technical/{symbol}', ['GET']),
            ('/api/analysis/fundamental/{symbol}', ['GET']),
            ('/api/analysis/sentiment', ['GET']),
            ('/api/analysis/signals', ['GET']),
            ('/api/analysis/backtest', ['POST']),
        ],
        'support': [
            ('/api/support/articles', ['GET']),
            ('/api/support/articles/{article_id}', ['GET']),
            ('/api/support/categories', ['GET']),
            ('/api/support/search', ['POST']),
            ('/api/support/contact', ['POST']),
            ('/api/support/offices', ['GET']),
            ('/api/support/channels', ['GET']),
            ('/api/support/faq', ['GET']),
            ('/api/support/faq/{category}', ['GET']),
            ('/api/support/faq/search', ['POST']),
        ],
        'legal': [
            ('/api/legal/terms', ['GET']),
            ('/api/legal/terms/version/{version}', ['GET']),
            ('/api/legal/privacy', ['GET']),
            ('/api/legal/privacy/version/{version}', ['GET']),
            ('/api/legal/risk-warning', ['GET']),
            ('/api/legal/complaints', ['GET', 'POST']),
            ('/api/legal/complaints/{complaint_id}', ['GET', 'PUT']),
        ]
    }
    
    results = {}
    all_passed = True
    
    for module, endpoints in expected.items():
        module_routes = [r for r in routes if f'/api/{module}' in r['path']]
        results[module] = {'expected': len(endpoints), 'found': len(module_routes), 'endpoints': []}
        
        for path, methods in endpoints:
            # Normalize path for comparison (remove path parameters)
            found = False
            for route in module_routes:
                route_path = route['path']
                # Check if paths match (accounting for path parameters)
                if route_path == path or route_path.replace('{', '').replace('}', '') == path.replace('{', '').replace('}', ''):
                    route_methods = [m for m in route['methods'] if m != 'HEAD' and m != 'OPTIONS']
                    if set(methods).issubset(set(route_methods)):
                        found = True
                        results[module]['endpoints'].append({
                            'path': path,
                            'methods': methods,
                            'status': '✅'
                        })
                        break
            
            if not found:
                all_passed = False
                results[module]['endpoints'].append({
                    'path': path,
                    'methods': methods,
                    'status': '❌'
                })
    
    # Print results
    print("=" * 80)
    print("BACKEND ENDPOINTS VERIFICATION REPORT")
    print("=" * 80)
    print()
    
    for module, result in results.items():
        print(f"\n{module.upper()} MODULE:")
        print(f"  Expected: {result['expected']} endpoints")
        print(f"  Found: {result['found']} routes")
        print()
        
        for endpoint in result['endpoints']:
            methods_str = ', '.join(endpoint['methods'])
            print(f"  {endpoint['status']} {endpoint['path']} [{methods_str}]")
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL ENDPOINTS VERIFIED")
    else:
        print("❌ SOME ENDPOINTS MISSING")
    print("=" * 80)
    
    return all_passed

if __name__ == '__main__':
    success = verify_routes()
    sys.exit(0 if success else 1)

