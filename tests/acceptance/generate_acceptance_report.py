#!/usr/bin/env python3
"""
Acceptance Test Report Generator
Generates comprehensive acceptance test reports in multiple formats
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

from scoring_calculator import ScoringCalculator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate acceptance test reports in multiple formats"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize report generator"""
        if config_path is None:
            config_path = Path(__file__).parent / "acceptance_config.json"
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.scoring_calculator = ScoringCalculator(config_path)
        self.templates_dir = Path(__file__).parent / "report_templates"
        self.reports_dir = Path(__file__).parent.parent.parent / "reports" / "acceptance"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def load_test_results(self, results_path: str) -> Dict:
        """Load test results from JSON file"""
        with open(results_path, 'r') as f:
            return json.load(f)
    
    def organize_test_results(self, test_results: Dict) -> Dict:
        """Organize test results by category"""
        organized = {
            "client_interface": {},
            "admin_interface": {},
            "api_functionality": {},
            "data_integrity": {}
        }
        
        results = test_results.get("results", [])
        
        for result in results:
            result_type = result.get("type", "unknown")
            category = None
            module = None
            
            if result_type == "api":
                category = "api_functionality"
                # Extract module from path
                path = result.get("path", "")
                if "/api/auth" in path:
                    module = "auth"
                elif "/api/client" in path:
                    module = "client"
                elif "/api/admin" in path:
                    module = "admin"
                elif "/api/financial" in path:
                    module = "financial"
                elif "/api/trading" in path:
                    module = "trading"
                elif "/api/market" in path:
                    module = "market"
                elif "/api/portfolio" in path:
                    module = "portfolio"
                elif "/api/compliance" in path:
                    module = "compliance"
                elif "/api/risk" in path:
                    module = "risk"
                elif "/api/staff" in path:
                    module = "staff"
                elif "/api/users" in path:
                    module = "users"
                elif "/api/advanced" in path:
                    module = "advanced"
                else:
                    module = "other"
            
            elif result_type == "page":
                url = result.get("url", "")
                description = result.get("description", "")
                
                if "client" in url.lower() or "Client:" in description:
                    category = "client_interface"
                    # Extract module from description or URL
                    if "Home" in description or "/" in url:
                        module = "homepage"
                    elif "Login" in description or "/login" in url:
                        module = "authentication"
                    elif "Trading" in description or "/trading" in url:
                        module = "trading"
                    elif "Personal" in description or "/personal" in url:
                        module = "personal_area"
                    else:
                        module = "other"
                
                elif "admin" in url.lower() or "Admin:" in description:
                    category = "admin_interface"
                    if "Dashboard" in description:
                        module = "dashboard"
                    elif "User" in description:
                        module = "user_management"
                    elif "Trading" in description:
                        module = "trading_management"
                    elif "Financial" in description:
                        module = "financial_management"
                    else:
                        module = "other"
            
            # Add to organized structure
            if category and module:
                if module not in organized[category]:
                    organized[category][module] = []
                
                # Convert to test result format
                test_result = {
                    "id": result.get("path") or result.get("url", ""),
                    "status": "passed" if result.get("success", False) else "failed",
                    "category": category,
                    "module": module,
                    "description": result.get("description", ""),
                    "error_message": result.get("error"),
                    "timestamp": result.get("timestamp"),
                    "response_time": result.get("response_time", 0) * 1000 if result.get("response_time") else 0
                }
                
                # Determine severity
                if not test_result["status"] == "passed":
                    if "401" in str(result.get("status_code", "")) or "403" in str(result.get("status_code", "")):
                        test_result["severity"] = "medium"
                    elif result.get("error") and "timeout" in str(result.get("error", "")).lower():
                        test_result["severity"] = "high"
                    else:
                        test_result["severity"] = "medium"
                
                organized[category][module].append(test_result)
        
        return organized
    
    def generate_markdown_report(self, overall_result: Dict, organized_results: Dict, 
                                test_results: Dict) -> str:
        """Generate Markdown report"""
        template_path = self.templates_dir / "report_template.md"
        
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Calculate statistics
        total_tests = test_results.get("total_tests", len(test_results.get("results", [])))
        passed = sum(1 for r in test_results.get("results", []) if r.get("success", False))
        failed = total_tests - passed
        
        # Replace template variables
        replacements = {
            "{{timestamp}}": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "{{environment}}": test_results.get("environment", {}).get("api_url", "unknown"),
            "{{overall_completion}}": f"{overall_result['overall_percentage']:.2f}",
            "{{overall_status}}": "PASS" if overall_result["passes"] else "FAIL",
            "{{total_tests}}": str(total_tests),
            "{{passed_tests}}": str(passed),
            "{{failed_tests}}": str(failed),
            "{{skipped_tests}}": "0",
            "{{critical_issues}}": str(overall_result["issues"]["critical"]),
            "{{high_issues}}": str(overall_result["issues"]["high"]),
            "{{medium_issues}}": str(overall_result["issues"]["medium"]),
            "{{low_issues}}": str(overall_result["issues"]["low"]),
        }
        
        # Category details
        for cat_name, cat_data in overall_result["categories"].items():
            cat_key = cat_name.replace("_", "_").upper()
            replacements["{{" + cat_key + "_SCORE}}"] = f"{cat_data['score']:.4f}"
            replacements["{{" + cat_key + "_PERCENTAGE}}"] = f"{cat_data['percentage']:.2f}"
            replacements["{{" + cat_key + "_WEIGHTED}}"] = f"{cat_data['weighted']*100:.2f}"
        
        # Replace all variables
        for key, value in replacements.items():
            template = template.replace(key, str(value))
        
        return template
    
    def generate_html_report(self, overall_result: Dict, organized_results: Dict,
                             test_results: Dict) -> str:
        """Generate HTML report"""
        template_path = self.templates_dir / "report_template.html"
        
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Calculate statistics
        total_tests = test_results.get("total_tests", len(test_results.get("results", [])))
        passed = sum(1 for r in test_results.get("results", []) if r.get("success", False))
        failed = total_tests - passed
        
        # Determine status class
        completion = overall_result["overall_completion"]
        if completion >= 0.85:
            status_class = "status-pass"
        elif completion >= 0.70:
            status_class = "status-warning"
        else:
            status_class = "status-fail"
        
        # Replace template variables
        replacements = {
            "{{overall_completion}}": f"{overall_result['overall_percentage']:.2f}",
            "{{overall_status}}": "PASS" if overall_result["passes"] else "FAIL",
            "{{overall_status_class}}": status_class,
            "{{total_tests}}": str(total_tests),
            "{{passed_tests}}": str(passed),
            "{{failed_tests}}": str(failed),
            "{{critical_issues}}": str(overall_result["issues"]["critical"]),
            "{{high_issues}}": str(overall_result["issues"]["high"]),
            "{{medium_issues}}": str(overall_result["issues"]["medium"]),
            "{{low_issues}}": str(overall_result["issues"]["low"]),
        }
        
        # Category progress bars
        for cat_name, cat_data in overall_result["categories"].items():
            cat_key = cat_name.replace("_", "_").upper()
            percentage = cat_data["percentage"]
            
            # Determine progress class
            if percentage >= 80:
                progress_class = ""
            elif percentage >= 60:
                progress_class = "warning"
            else:
                progress_class = "danger"
            
            replacements["{{" + cat_key + "_PERCENTAGE}}"] = f"{percentage:.2f}"
            replacements["{{" + cat_key + "_PROGRESS_CLASS}}"] = progress_class
            replacements["{{" + cat_key + "_PASS_RATE}}"] = f"{percentage:.2f}"
            replacements["{{" + cat_key + "_PASSED}}"] = str(int(cat_data.get("passed", 0)))
            replacements["{{" + cat_key + "_TOTAL}}"] = str(int(cat_data.get("total", 0)))
        
        # Replace all variables
        for key, value in replacements.items():
            template = template.replace(key, str(value))
        
        return template
    
    def generate_json_report(self, overall_result: Dict, organized_results: Dict,
                             test_results: Dict) -> Dict:
        """Generate JSON report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "environment": test_results.get("environment", {}),
            "overall_completion": overall_result["overall_completion"],
            "overall_percentage": overall_result["overall_percentage"],
            "overall_status": "pass" if overall_result["passes"] else "fail",
            "total_tests": test_results.get("total_tests", len(test_results.get("results", []))),
            "passed_tests": sum(1 for r in test_results.get("results", []) if r.get("success", False)),
            "failed_tests": sum(1 for r in test_results.get("results", []) if not r.get("success", False)),
            "skipped_tests": 0,
            "categories": overall_result["categories"],
            "issues": overall_result["issues"],
            "test_results": [],
            "recommendations": self._generate_recommendations(overall_result, organized_results),
            "metadata": {
                "tester_name": "Automated Test System",
                "system_version": "1.0",
                "test_duration": 0
            }
        }
        
        # Add test results
        for category, modules in organized_results.items():
            for module, results in modules.items():
                report["test_results"].extend(results)
        
        return report
    
    def _generate_recommendations(self, overall_result: Dict, organized_results: Dict) -> List[Dict]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check overall completion
        if overall_result["overall_completion"] < 0.85:
            recommendations.append({
                "priority": "critical",
                "title": "Overall completion below threshold",
                "description": f"Overall completion is {overall_result['overall_percentage']:.2f}%, below the required 85%",
                "action_items": [
                    "Review failed test cases",
                    "Fix critical and high priority issues",
                    "Re-run acceptance tests"
                ]
            })
        
        # Check critical issues
        if overall_result["issues"]["critical"] > 0:
            recommendations.append({
                "priority": "critical",
                "title": "Critical issues found",
                "description": f"{overall_result['issues']['critical']} critical issues must be fixed before production",
                "action_items": [
                    "Review critical issues list",
                    "Fix all critical issues immediately",
                    "Verify fixes with regression testing"
                ]
            })
        
        # Check category scores
        for cat_name, cat_data in overall_result["categories"].items():
            if cat_data["percentage"] < 80:
                recommendations.append({
                    "priority": "high",
                    "title": f"{cat_name.replace('_', ' ').title()} below threshold",
                    "description": f"{cat_name.replace('_', ' ').title()} completion is {cat_data['percentage']:.2f}%, below 80% threshold",
                    "action_items": [
                        f"Review {cat_name} test results",
                        f"Fix issues in {cat_name}",
                        "Re-test affected modules"
                    ]
                })
        
        return recommendations
    
    def generate_all_reports(self, test_results_path: str, output_prefix: str = None):
        """Generate all report formats"""
        logger.info(f"Loading test results from: {test_results_path}")
        test_results = self.load_test_results(test_results_path)
        
        logger.info("Organizing test results...")
        organized_results = self.organize_test_results(test_results)
        
        logger.info("Calculating scores...")
        overall_result = self.scoring_calculator.calculate_overall_completion(organized_results)
        
        # Generate output filename
        if output_prefix is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_prefix = f"acceptance_report_{timestamp}"
        
        # Generate Markdown report
        logger.info("Generating Markdown report...")
        md_report = self.generate_markdown_report(overall_result, organized_results, test_results)
        md_path = self.reports_dir / f"{output_prefix}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_report)
        logger.info(f"Markdown report saved to: {md_path}")
        
        # Generate HTML report
        logger.info("Generating HTML report...")
        html_report = self.generate_html_report(overall_result, organized_results, test_results)
        html_path = self.reports_dir / f"{output_prefix}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
        logger.info(f"HTML report saved to: {html_path}")
        
        # Generate JSON report
        logger.info("Generating JSON report...")
        json_report = self.generate_json_report(overall_result, organized_results, test_results)
        json_path = self.reports_dir / f"{output_prefix}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2, ensure_ascii=False)
        logger.info(f"JSON report saved to: {json_path}")
        
        # Save detailed results
        results_dir = self.reports_dir / "test_results"
        results_dir.mkdir(exist_ok=True)
        detailed_path = results_dir / f"{output_prefix}_detailed.json"
        with open(detailed_path, 'w', encoding='utf-8') as f:
            json.dump({
                "overall_result": overall_result,
                "organized_results": organized_results,
                "raw_results": test_results
            }, f, indent=2, ensure_ascii=False)
        logger.info(f"Detailed results saved to: {detailed_path}")
        
        # Print summary
        print("\n" + "="*80)
        print("ACCEPTANCE TEST REPORT GENERATION COMPLETE")
        print("="*80)
        print(f"\nOverall Completion: {overall_result['overall_percentage']:.2f}%")
        print(f"Status: {'PASS' if overall_result['passes'] else 'FAIL'}")
        print(f"\nReports generated:")
        print(f"  - Markdown: {md_path}")
        print(f"  - HTML: {html_path}")
        print(f"  - JSON: {json_path}")
        print(f"  - Detailed: {detailed_path}")
        print("="*80 + "\n")
        
        return {
            "markdown": str(md_path),
            "html": str(html_path),
            "json": str(json_path),
            "detailed": str(detailed_path)
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python generate_acceptance_report.py <test_results.json> [output_prefix]")
        sys.exit(1)
    
    results_path = sys.argv[1]
    output_prefix = sys.argv[2] if len(sys.argv) > 2 else None
    
    generator = ReportGenerator()
    generator.generate_all_reports(results_path, output_prefix)

