#!/usr/bin/env python3
"""
Error Analyzer
Analyze test errors and provide actionable suggestions
"""

import json
from typing import Dict, List, Optional
from pathlib import Path
from collections import defaultdict


class ErrorAnalyzer:
    """Analyze errors from test results and provide suggestions"""
    
    def __init__(self):
        """Initialize analyzer"""
        self.error_patterns = {
            401: {
                "category": "Authentication",
                "common_causes": [
                    "Missing or invalid auth token",
                    "Token expired",
                    "Incorrect credentials"
                ],
                "suggestions": [
                    "Check if auth token is included in Authorization header",
                    "Verify token is not expired",
                    "Try refreshing the token",
                    "Verify user credentials are correct"
                ]
            },
            403: {
                "category": "Authorization",
                "common_causes": [
                    "Insufficient permissions",
                    "User role doesn't have access",
                    "Account not approved"
                ],
                "suggestions": [
                    "Check user role and permissions",
                    "Verify account is approved (is_approved=True)",
                    "Check if endpoint requires specific role",
                    "Review access control rules"
                ]
            },
            404: {
                "category": "Not Found",
                "common_causes": [
                    "Endpoint path incorrect",
                    "Endpoint not implemented",
                    "HTTP method mismatch"
                ],
                "suggestions": [
                    "Verify endpoint path matches API documentation",
                    "Check if endpoint is implemented",
                    "Try different HTTP method (GET vs POST)",
                    "Check OpenAPI spec for correct path"
                ]
            },
            405: {
                "category": "Method Not Allowed",
                "common_causes": [
                    "Wrong HTTP method",
                    "Method not supported for this endpoint"
                ],
                "suggestions": [
                    "Check API documentation for correct HTTP method",
                    "Try GET instead of POST or vice versa",
                    "Verify method in OpenAPI spec"
                ]
            },
            422: {
                "category": "Validation Error",
                "common_causes": [
                    "Missing required fields",
                    "Invalid data format",
                    "Data type mismatch"
                ],
                "suggestions": [
                    "Check request payload structure",
                    "Verify all required fields are present",
                    "Check data types match API schema",
                    "Review validation error details in response"
                ]
            },
            429: {
                "category": "Rate Limiting",
                "common_causes": [
                    "Too many requests",
                    "Rate limit exceeded"
                ],
                "suggestions": [
                    "Wait before retrying",
                    "Reduce request frequency",
                    "Check rate limit settings",
                    "Use exponential backoff"
                ]
            },
            500: {
                "category": "Server Error",
                "common_causes": [
                    "Backend implementation error",
                    "Database connection issue",
                    "Internal server error"
                ],
                "suggestions": [
                    "Check server logs for details",
                    "Verify backend service is running",
                    "Check database connectivity",
                    "Review backend error handling"
                ]
            }
        }
    
    def analyze(self, test_results: List[Dict]) -> Dict:
        """Analyze test results and provide insights"""
        analysis = {
            "total_tests": len(test_results),
            "passed": 0,
            "failed": 0,
            "errors_by_status": defaultdict(int),
            "errors_by_category": defaultdict(list),
            "errors_by_module": defaultdict(list),
            "common_issues": [],
            "recommendations": []
        }
        
        for result in test_results:
            if result.get("success"):
                analysis["passed"] += 1
            else:
                analysis["failed"] += 1
                status_code = result.get("status_code")
                
                if status_code:
                    analysis["errors_by_status"][status_code] += 1
                    
                    # Categorize error
                    if status_code in self.error_patterns:
                        pattern = self.error_patterns[status_code]
                        category = pattern["category"]
                        analysis["errors_by_category"][category].append({
                            "path": result.get("path"),
                            "method": result.get("method"),
                            "status": status_code,
                            "error": result.get("error")
                        })
                
                # Group by module
                description = result.get("description", "")
                if ":" in description:
                    module = description.split(":")[0]
                    analysis["errors_by_module"][module].append(result)
        
        # Generate common issues
        analysis["common_issues"] = self._identify_common_issues(analysis)
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _identify_common_issues(self, analysis: Dict) -> List[Dict]:
        """Identify common issues"""
        issues = []
        
        # Most common status codes
        if analysis["errors_by_status"]:
            most_common_status = max(analysis["errors_by_status"].items(), key=lambda x: x[1])
            status_code, count = most_common_status
            
            if status_code in self.error_patterns:
                pattern = self.error_patterns[status_code]
                issues.append({
                    "type": pattern["category"],
                    "status_code": status_code,
                    "count": count,
                    "percentage": (count / analysis["failed"] * 100) if analysis["failed"] > 0 else 0,
                    "common_causes": pattern["common_causes"]
                })
        
        # Module with most errors
        if analysis["errors_by_module"]:
            worst_module = max(analysis["errors_by_module"].items(), key=lambda x: len(x[1]))
            module, errors = worst_module
            issues.append({
                "type": "Module Issues",
                "module": module,
                "error_count": len(errors),
                "description": f"Module '{module}' has {len(errors)} errors"
            })
        
        return issues
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        total = analysis["total_tests"]
        failed = analysis["failed"]
        pass_rate = ((total - failed) / total * 100) if total > 0 else 0
        
        # Overall recommendations
        if pass_rate < 90:
            recommendations.append(f"Current pass rate is {pass_rate:.1f}%, need to improve by {90 - pass_rate:.1f}% to reach 90%")
        
        # Status code specific recommendations
        for status_code, count in sorted(analysis["errors_by_status"].items(), key=lambda x: x[1], reverse=True):
            if status_code in self.error_patterns:
                pattern = self.error_patterns[status_code]
                percentage = (count / failed * 100) if failed > 0 else 0
                
                if percentage > 30:  # More than 30% of errors
                    recommendations.append(
                        f"Priority: Fix {pattern['category']} issues ({count} errors, {percentage:.1f}% of failures). "
                        f"Suggestions: {', '.join(pattern['suggestions'][:2])}"
                    )
        
        # Module specific recommendations
        if analysis["errors_by_module"]:
            worst_module = max(analysis["errors_by_module"].items(), key=lambda x: len(x[1]))
            module, errors = worst_module
            if len(errors) > 5:
                recommendations.append(
                    f"Focus on '{module}' module: {len(errors)} errors need attention"
                )
        
        # Authentication recommendations
        auth_errors = len(analysis["errors_by_category"].get("Authentication", [])) + \
                     len(analysis["errors_by_category"].get("Authorization", []))
        if auth_errors > 0:
            recommendations.append(
                f"Fix authentication issues: {auth_errors} endpoints need valid auth tokens. "
                "Run approve_test_accounts.py to approve test accounts."
            )
        
        return recommendations
    
    def generate_report(self, analysis: Dict, output_path: Optional[str] = None) -> str:
        """Generate analysis report"""
        if output_path is None:
            output_path = Path(__file__).parent.parent.parent.parent / "reports" / "acceptance" / "debug" / "error_analysis.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        return str(output_path)
    
    def print_analysis(self, analysis: Dict):
        """Print analysis in readable format"""
        print("\n" + "="*60)
        print("ERROR ANALYSIS")
        print("="*60)
        
        print(f"\n📊 Summary:")
        print(f"  Total Tests: {analysis['total_tests']}")
        print(f"  Passed: {analysis['passed']}")
        print(f"  Failed: {analysis['failed']}")
        pass_rate = (analysis['passed'] / analysis['total_tests'] * 100) if analysis['total_tests'] > 0 else 0
        print(f"  Pass Rate: {pass_rate:.2f}%")
        
        if analysis['errors_by_status']:
            print(f"\n📈 Errors by Status Code:")
            for status, count in sorted(analysis['errors_by_status'].items(), key=lambda x: x[1], reverse=True):
                if status in self.error_patterns:
                    category = self.error_patterns[status]['category']
                    print(f"  {status} ({category}): {count}")
                else:
                    print(f"  {status}: {count}")
        
        if analysis['common_issues']:
            print(f"\n⚠️  Common Issues:")
            for issue in analysis['common_issues']:
                print(f"  - {issue.get('type', 'Unknown')}: {issue.get('count', issue.get('error_count', 0))} occurrences")
        
        if analysis['recommendations']:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(analysis['recommendations'], 1):
                print(f"  {i}. {rec}")


if __name__ == "__main__":
    # Test with sample data
    analyzer = ErrorAnalyzer()
    
    sample_results = [
        {"success": False, "status_code": 404, "path": "/api/test", "method": "GET", "error": "Not found"},
        {"success": False, "status_code": 401, "path": "/api/user", "method": "GET", "error": "Unauthorized"},
        {"success": True, "status_code": 200, "path": "/api/health", "method": "GET"}
    ]
    
    analysis = analyzer.analyze(sample_results)
    analyzer.print_analysis(analysis)

