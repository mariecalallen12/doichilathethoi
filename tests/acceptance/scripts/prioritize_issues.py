#!/usr/bin/env python3
"""
Prioritize Issues
Create priority matrix and actionable fix plan
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class IssuePrioritizer:
    """Prioritize issues for systematic fixing"""
    
    def __init__(self):
        """Initialize prioritizer"""
        self.priority_matrix = {
            "critical": {
                "description": "Blocks core functionality",
                "examples": ["Auth failures", "Server errors", "Critical endpoints down"],
                "fix_order": 1
            },
            "high": {
                "description": "Affects major features",
                "examples": ["Major endpoints failing", "High-traffic endpoints"],
                "fix_order": 2
            },
            "medium": {
                "description": "Affects minor features",
                "examples": ["Less-used endpoints", "Edge cases"],
                "fix_order": 3
            },
            "low": {
                "description": "Nice to have",
                "examples": ["Optional features", "Enhancements"],
                "fix_order": 4
            }
        }
    
    def prioritize(self, issue_report_file: str) -> Dict:
        """Create prioritized fix plan"""
        with open(issue_report_file, 'r') as f:
            analysis = json.load(f)
        
        issues = analysis.get("issues", [])
        
        # Group by priority
        by_priority = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        for issue in issues:
            priority = issue.get("priority", "medium")
            by_priority[priority].append(issue)
        
        # Create fix plan
        fix_plan = {
            "total_issues": len(issues),
            "by_priority": {p: len(issues) for p, issues in by_priority.items()},
            "fix_order": [],
            "estimated_time": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }
        
        # Estimate time and create fix order
        time_estimates = {
            "low": 0.5,  # 30 minutes
            "medium": 2,  # 2 hours
            "high": 4,   # 4 hours
            "critical": 8  # 8 hours (may need investigation)
        }
        
        for priority in ["critical", "high", "medium", "low"]:
            issues_list = by_priority[priority]
            fix_plan["fix_order"].extend(issues_list)
            
            # Estimate total time
            total_time = 0
            for issue in issues_list:
                effort = issue.get("fix_effort", "medium")
                if effort == "low":
                    total_time += time_estimates["low"]
                elif effort == "high":
                    total_time += time_estimates["high"]
                else:
                    total_time += time_estimates["medium"]
            
            fix_plan["estimated_time"][priority] = total_time
        
        # Add recommendations
        fix_plan["recommendations"] = self._generate_recommendations(by_priority, fix_plan)
        
        return {
            "prioritization": fix_plan,
            "priority_matrix": self.priority_matrix,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_recommendations(self, by_priority: Dict, fix_plan: Dict) -> List[str]:
        """Generate recommendations for fixing"""
        recommendations = []
        
        # Critical issues
        if by_priority["critical"]:
            recommendations.append(
                f"URGENT: Fix {len(by_priority['critical'])} critical issues first. "
                f"Estimated time: {fix_plan['estimated_time']['critical']:.1f} hours"
            )
        
        # High priority
        if by_priority["high"]:
            recommendations.append(
                f"Fix {len(by_priority['high'])} high priority issues next. "
                f"Estimated time: {fix_plan['estimated_time']['high']:.1f} hours"
            )
        
        # Quick wins
        low_effort = [i for i in fix_plan["fix_order"] if i.get("fix_effort") == "low"]
        if low_effort:
            recommendations.append(
                f"Quick wins: {len(low_effort)} issues with low fix effort. "
                "Fix these first for quick improvement."
            )
        
        # Module focus
        module_counts = {}
        for issue in fix_plan["fix_order"]:
            module = issue.get("module", "unknown")
            module_counts[module] = module_counts.get(module, 0) + 1
        
        if module_counts:
            worst_module = max(module_counts.items(), key=lambda x: x[1])
            recommendations.append(
                f"Focus on '{worst_module[0]}' module: {worst_module[1]} issues need attention"
            )
        
        return recommendations
    
    def generate_fix_plan(self, prioritization: Dict, output_path: Optional[str] = None) -> str:
        """Generate actionable fix plan"""
        if output_path is None:
            output_path = Path(__file__).parent.parent.parent.parent / "reports" / "acceptance" / "issues" / "fix_plan.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(prioritization, f, indent=2)
        
        return str(output_path)
    
    def print_prioritization(self, prioritization: Dict):
        """Print prioritization in readable format"""
        fix_plan = prioritization["prioritization"]
        
        print("\n" + "="*60)
        print("ISSUE PRIORITIZATION")
        print("="*60)
        
        print(f"\n📊 Total Issues: {fix_plan['total_issues']}")
        
        print(f"\n🎯 Issues by Priority:")
        for priority, count in fix_plan['by_priority'].items():
            matrix_info = self.priority_matrix[priority]
            print(f"  {priority.upper()}: {count} issues")
            print(f"    Description: {matrix_info['description']}")
            print(f"    Estimated Time: {fix_plan['estimated_time'][priority]:.1f} hours")
        
        print(f"\n📋 Fix Order (Top 10):")
        for i, issue in enumerate(fix_plan['fix_order'][:10], 1):
            print(f"  {i}. {issue['method']} {issue['path']}")
            print(f"     Priority: {issue.get('priority', 'unknown')}, "
                  f"Effort: {issue.get('fix_effort', 'unknown')}, "
                  f"Score: {issue.get('priority_score', 0)}")
        
        if prioritization.get('recommendations'):
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(prioritization['recommendations'], 1):
                print(f"  {i}. {rec}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Prioritize issues for fixing")
    parser.add_argument(
        "issue_report_file",
        help="Path to issue report JSON file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path"
    )
    
    args = parser.parse_args()
    
    prioritizer = IssuePrioritizer()
    prioritization = prioritizer.prioritize(args.issue_report_file)
    
    prioritizer.print_prioritization(prioritization)
    
    output_path = prioritizer.generate_fix_plan(prioritization, args.output)
    print(f"\n✅ Fix plan saved to: {output_path}")

