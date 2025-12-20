#!/usr/bin/env python3
"""
Scoring Calculator for Acceptance Testing
Calculates completion percentage based on weighted scoring system
"""

import json
from typing import Dict, List, Optional
from pathlib import Path


class ScoringCalculator:
    """Calculate completion percentage and scores for acceptance testing"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with configuration"""
        if config_path is None:
            config_path = Path(__file__).parent / "acceptance_config.json"
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.weights = self.config.get("scoring_weights", {})
        self.pass_criteria = self.config.get("pass_criteria", {})
    
    def calculate_module_score(self, test_results: List[Dict]) -> Dict:
        """
        Calculate score for a single module
        
        Args:
            test_results: List of test result dictionaries with 'status' field
            
        Returns:
            Dictionary with score details
        """
        if not test_results:
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "score": 0.0,
                "percentage": 0.0
            }
        
        total = len(test_results)
        passed = sum(1 for r in test_results if r.get("status") == "passed")
        failed = sum(1 for r in test_results if r.get("status") == "failed")
        skipped = sum(1 for r in test_results if r.get("status") == "skipped")
        
        score = passed / total if total > 0 else 0.0
        percentage = score * 100
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "score": score,
            "percentage": percentage
        }
    
    def calculate_category_score(self, category_results: Dict[str, List[Dict]]) -> Dict:
        """
        Calculate score for a category (e.g., Client Interface)
        
        Args:
            category_results: Dictionary mapping module names to test results
            
        Returns:
            Dictionary with category score details
        """
        all_results = []
        module_scores = {}
        
        for module_name, results in category_results.items():
            module_score = self.calculate_module_score(results)
            module_scores[module_name] = module_score
            all_results.extend(results)
        
        overall_score = self.calculate_module_score(all_results)
        
        return {
            "overall": overall_score,
            "modules": module_scores,
            "module_count": len(category_results)
        }
    
    def calculate_overall_completion(self, test_data: Dict) -> Dict:
        """
        Calculate overall completion percentage
        
        Args:
            test_data: Dictionary with test results for each category:
                - client_interface: Dict of module results
                - admin_interface: Dict of module results
                - api_functionality: Dict of module results
                - data_integrity: Dict of module results
                
        Returns:
            Dictionary with overall completion details
        """
        # Calculate scores for each category
        client_score = self.calculate_category_score(
            test_data.get("client_interface", {})
        )
        admin_score = self.calculate_category_score(
            test_data.get("admin_interface", {})
        )
        api_score = self.calculate_category_score(
            test_data.get("api_functionality", {})
        )
        data_score = self.calculate_category_score(
            test_data.get("data_integrity", {})
        )
        
        # Get weighted scores
        client_weighted = client_score["overall"]["score"] * self.weights.get("client_interface", 0.35)
        admin_weighted = admin_score["overall"]["score"] * self.weights.get("admin_interface", 0.25)
        api_weighted = api_score["overall"]["score"] * self.weights.get("api_functionality", 0.25)
        data_weighted = data_score["overall"]["score"] * self.weights.get("data_integrity", 0.15)
        
        # Calculate overall completion
        overall_completion = client_weighted + admin_weighted + api_weighted + data_weighted
        overall_percentage = overall_completion * 100
        
        # Check pass criteria
        min_completion = self.pass_criteria.get("overall_completion_min", 0.85)
        passes = overall_completion >= min_completion
        
        # Count issues by severity
        issues = self._count_issues(test_data)
        
        return {
            "overall_completion": overall_completion,
            "overall_percentage": overall_percentage,
            "passes": passes,
            "categories": {
                "client_interface": {
                    "score": client_score["overall"]["score"],
                    "percentage": client_score["overall"]["percentage"],
                    "weighted": client_weighted,
                    "weight": self.weights.get("client_interface", 0.35)
                },
                "admin_interface": {
                    "score": admin_score["overall"]["score"],
                    "percentage": admin_score["overall"]["percentage"],
                    "weighted": admin_weighted,
                    "weight": self.weights.get("admin_interface", 0.25)
                },
                "api_functionality": {
                    "score": api_score["overall"]["score"],
                    "percentage": api_score["overall"]["percentage"],
                    "weighted": api_weighted,
                    "weight": self.weights.get("api_functionality", 0.25)
                },
                "data_integrity": {
                    "score": data_score["overall"]["score"],
                    "percentage": data_score["overall"]["percentage"],
                    "weighted": data_weighted,
                    "weight": self.weights.get("data_integrity", 0.15)
                }
            },
            "category_details": {
                "client_interface": client_score,
                "admin_interface": admin_score,
                "api_functionality": api_score,
                "data_integrity": data_score
            },
            "issues": issues,
            "pass_criteria": {
                "required": min_completion,
                "actual": overall_completion,
                "meets_requirement": passes
            }
        }
    
    def _count_issues(self, test_data: Dict) -> Dict:
        """Count issues by severity from test results"""
        issues = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        # Extract issues from all test results
        for category in ["client_interface", "admin_interface", "api_functionality", "data_integrity"]:
            category_data = test_data.get(category, {})
            for module_name, results in category_data.items():
                for result in results:
                    if result.get("status") == "failed":
                        severity = result.get("severity", "medium")
                        if severity in issues:
                            issues[severity] += 1
        
        return issues
    
    def generate_score_summary(self, overall_result: Dict) -> str:
        """Generate human-readable score summary"""
        lines = []
        lines.append("=" * 80)
        lines.append("ACCEPTANCE TEST SCORING SUMMARY")
        lines.append("=" * 80)
        lines.append("")
        
        # Overall completion
        completion = overall_result["overall_completion"]
        percentage = overall_result["overall_percentage"]
        passes = overall_result["passes"]
        
        status = "✅ PASS" if passes else "❌ FAIL"
        lines.append(f"Overall Completion: {percentage:.2f}% ({completion:.4f})")
        lines.append(f"Status: {status}")
        lines.append("")
        
        # Category breakdown
        lines.append("Category Breakdown:")
        lines.append("-" * 80)
        for cat_name, cat_data in overall_result["categories"].items():
            cat_percentage = cat_data["percentage"]
            cat_weight = cat_data["weight"] * 100
            cat_weighted = cat_data["weighted"] * 100
            lines.append(f"  {cat_name.replace('_', ' ').title()}:")
            lines.append(f"    Score: {cat_percentage:.2f}%")
            lines.append(f"    Weight: {cat_weight:.0f}%")
            lines.append(f"    Weighted Contribution: {cat_weighted:.2f}%")
            lines.append("")
        
        # Issues summary
        issues = overall_result["issues"]
        lines.append("Issues Summary:")
        lines.append("-" * 80)
        lines.append(f"  Critical: {issues['critical']}")
        lines.append(f"  High: {issues['high']}")
        lines.append(f"  Medium: {issues['medium']}")
        lines.append(f"  Low: {issues['low']}")
        lines.append("")
        
        # Pass criteria
        criteria = overall_result["pass_criteria"]
        lines.append("Pass Criteria:")
        lines.append("-" * 80)
        lines.append(f"  Required: {criteria['required']*100:.0f}%")
        lines.append(f"  Actual: {criteria['actual']*100:.2f}%")
        lines.append(f"  Meets Requirement: {'Yes' if criteria['meets_requirement'] else 'No'}")
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Example usage
    calculator = ScoringCalculator()
    
    # Example test data
    example_data = {
        "client_interface": {
            "homepage": [
                {"status": "passed", "test": "Page loads"},
                {"status": "passed", "test": "Navigation works"},
                {"status": "failed", "test": "Mobile responsive", "severity": "medium"}
            ],
            "trading": [
                {"status": "passed", "test": "Dashboard loads"},
                {"status": "passed", "test": "Charts render"}
            ]
        },
        "admin_interface": {
            "dashboard": [
                {"status": "passed", "test": "Dashboard loads"},
                {"status": "passed", "test": "Stats display"}
            ]
        },
        "api_functionality": {
            "auth": [
                {"status": "passed", "test": "Login endpoint"},
                {"status": "passed", "test": "Register endpoint"}
            ]
        },
        "data_integrity": {
            "api_frontend_sync": [
                {"status": "passed", "test": "Data matches"},
                {"status": "failed", "test": "Real-time updates", "severity": "high"}
            ]
        }
    }
    
    result = calculator.calculate_overall_completion(example_data)
    print(calculator.generate_score_summary(result))

