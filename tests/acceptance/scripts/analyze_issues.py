#!/usr/bin/env python3
"""
Analyze Issues from Test Results
Categorize and score issues by priority and impact
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime


class IssueAnalyzer:
    """Analyze issues from test results"""
    
    def __init__(self):
        """Initialize analyzer"""
        self.issue_categories = {
            "authentication": {
                "status_codes": [401, 403],
                "priority_weight": 10,
                "impact_weight": 9
            },
            "not_found": {
                "status_codes": [404],
                "priority_weight": 7,
                "impact_weight": 6
            },
            "validation": {
                "status_codes": [422],
                "priority_weight": 6,
                "impact_weight": 5
            },
            "method_error": {
                "status_codes": [405],
                "priority_weight": 5,
                "impact_weight": 4
            },
            "rate_limit": {
                "status_codes": [429],
                "priority_weight": 3,
                "impact_weight": 3
            },
            "server_error": {
                "status_codes": [500, 502, 503],
                "priority_weight": 9,
                "impact_weight": 10
            }
        }
        
        self.critical_modules = ["auth", "client", "financial", "trading"]
        self.high_priority_modules = ["admin", "portfolio", "compliance"]
    
    def analyze(self, test_results_file: str) -> Dict:
        """Analyze issues from test results"""
        with open(test_results_file, 'r') as f:
            data = json.load(f)
        
        results = data.get("results", [])
        
        issues = []
        for result in results:
            if not result.get("success", False):
                issue = self._categorize_issue(result)
                if issue:
                    issues.append(issue)
        
        # Calculate priorities
        for issue in issues:
            issue["priority_score"] = self._calculate_priority_score(issue)
            issue["fix_effort"] = self._estimate_fix_effort(issue)
        
        # Sort by priority
        issues.sort(key=lambda x: x["priority_score"], reverse=True)
        
        # Group by category
        issues_by_category = defaultdict(list)
        for issue in issues:
            issues_by_category[issue["category"]].append(issue)
        
        # Generate summary
        summary = {
            "total_issues": len(issues),
            "by_category": {cat: len(issues) for cat, issues in issues_by_category.items()},
            "by_priority": {
                "critical": len([i for i in issues if i["priority"] == "critical"]),
                "high": len([i for i in issues if i["priority"] == "high"]),
                "medium": len([i for i in issues if i["priority"] == "medium"]),
                "low": len([i for i in issues if i["priority"] == "low"])
            },
            "critical_issues": [i for i in issues if i["priority"] == "critical"][:10],
            "high_priority_issues": [i for i in issues if i["priority"] == "high"][:10]
        }
        
        return {
            "summary": summary,
            "issues": issues,
            "issues_by_category": dict(issues_by_category),
            "timestamp": datetime.now().isoformat()
        }
    
    def _categorize_issue(self, result: Dict) -> Dict:
        """Categorize an issue"""
        status_code = result.get("status_code")
        path = result.get("path", "")
        method = result.get("method", "")
        description = result.get("description", "")
        
        # Extract module
        module = "unknown"
        if ":" in description:
            module = description.split(":")[0].strip()
        
        # Find category
        category = "unknown"
        for cat_name, cat_info in self.issue_categories.items():
            if status_code in cat_info["status_codes"]:
                category = cat_name
                break
        
        issue = {
            "path": path,
            "method": method,
            "status_code": status_code,
            "module": module,
            "category": category,
            "description": description,
            "error": result.get("error"),
            "response_data": result.get("response_data")
        }
        
        return issue
    
    def _calculate_priority_score(self, issue: Dict) -> int:
        """Calculate priority score (higher = more urgent)"""
        score = 0
        
        # Category weight
        category = issue["category"]
        if category in self.issue_categories:
            score += self.issue_categories[category]["priority_weight"]
            score += self.issue_categories[category]["impact_weight"]
        
        # Module weight
        module = issue["module"]
        if module in self.critical_modules:
            score += 5
        elif module in self.high_priority_modules:
            score += 3
        
        # Status code weight
        status_code = issue["status_code"]
        if status_code == 500:
            score += 10  # Server errors are critical
        elif status_code in [401, 403]:
            score += 8  # Auth errors block access
        elif status_code == 404:
            score += 4  # Not found is common but fixable
        
        return score
    
    def _estimate_fix_effort(self, issue: Dict) -> str:
        """Estimate fix effort"""
        category = issue["category"]
        status_code = issue["status_code"]
        
        if status_code == 500:
            return "high"  # Requires backend investigation
        elif status_code in [401, 403]:
            return "low"  # Usually just need to approve accounts or add auth
        elif status_code == 404:
            return "medium"  # May need to implement endpoint or fix path
        elif status_code == 422:
            return "low"  # Usually just fix payload
        elif status_code == 405:
            return "low"  # Just change HTTP method
        elif status_code == 429:
            return "low"  # Just wait or adjust rate limits
        
        return "medium"
    
    def _determine_priority(self, score: int) -> str:
        """Determine priority level from score"""
        if score >= 20:
            return "critical"
        elif score >= 15:
            return "high"
        elif score >= 10:
            return "medium"
        else:
            return "low"
    
    def generate_report(self, analysis: Dict, output_path: Optional[str] = None) -> str:
        """Generate issue analysis report"""
        if output_path is None:
            output_path = Path(__file__).parent.parent.parent.parent / "reports" / "acceptance" / "issues" / "issue_report.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Add priority labels
        for issue in analysis["issues"]:
            issue["priority"] = self._determine_priority(issue["priority_score"])
        
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        return str(output_path)
    
    def print_summary(self, analysis: Dict):
        """Print analysis summary"""
        summary = analysis["summary"]
        
        print("\n" + "="*60)
        print("ISSUE ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"\n📊 Total Issues: {summary['total_issues']}")
        
        print(f"\n📈 By Category:")
        for category, count in sorted(summary['by_category'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: {count}")
        
        print(f"\n🎯 By Priority:")
        for priority, count in summary['by_priority'].items():
            print(f"  {priority}: {count}")
        
        if summary['critical_issues']:
            print(f"\n🚨 Top Critical Issues:")
            for i, issue in enumerate(summary['critical_issues'][:5], 1):
                print(f"  {i}. {issue['method']} {issue['path']} ({issue['category']}, score: {issue['priority_score']})")
        
        if summary['high_priority_issues']:
            print(f"\n⚠️  Top High Priority Issues:")
            for i, issue in enumerate(summary['high_priority_issues'][:5], 1):
                print(f"  {i}. {issue['method']} {issue['path']} ({issue['category']}, score: {issue['priority_score']})")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze issues from test results")
    parser.add_argument(
        "test_results_file",
        help="Path to test results JSON file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path"
    )
    
    args = parser.parse_args()
    
    analyzer = IssueAnalyzer()
    analysis = analyzer.analyze(args.test_results_file)
    
    analyzer.print_summary(analysis)
    
    output_path = analyzer.generate_report(analysis, args.output)
    print(f"\n✅ Report saved to: {output_path}")

