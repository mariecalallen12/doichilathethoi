#!/usr/bin/env python3
"""
Generate Production Readiness Report
Comprehensive assessment with risk analysis and Go/No-Go recommendation
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Import quality gates
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    # QualityGate is imported if needed, but not required for this script
except ImportError:
    QualityGate = None


class ProductionReadinessReporter:
    """Generate production readiness report"""
    
    def __init__(self):
        """Initialize reporter"""
        self.criteria = {
            "completion_rate": 0.90,
            "critical_issues": 0,
            "high_issues": 5,
            "response_time_p95": 2.0,
            "error_rate": 0.01
        }
    
    def load_test_results(self, test_results_file: str) -> Dict:
        """Load test results"""
        with open(test_results_file, 'r') as f:
            return json.load(f)
    
    def load_quality_gate_report(self, quality_report_file: str) -> Dict:
        """Load quality gate report"""
        with open(quality_report_file, 'r') as f:
            return json.load(f)
    
    def assess_readiness(self, test_results: Dict, quality_report: Dict = None,
                        load_test_results: Dict = None,
                        stability_test_results: Dict = None) -> Dict:
        """Assess production readiness"""
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "technical_readiness": {},
            "performance_readiness": {},
            "security_readiness": {},
            "stability_readiness": {},
            "overall_readiness": {},
            "risks": [],
            "recommendations": [],
            "go_no_go": "PENDING"
        }
        
        # Technical readiness
        results = test_results.get("results", [])
        total = len(results)
        passed = sum(1 for r in results if r.get("success", False))
        completion_rate = passed / total if total > 0 else 0
        
        assessment["technical_readiness"] = {
            "completion_rate": completion_rate,
            "meets_criteria": completion_rate >= self.criteria["completion_rate"],
            "total_tests": total,
            "passed": passed
        }
        
        # Quality gates
        if quality_report:
            all_passed = quality_report.get("all_passed", False)
            assessment["technical_readiness"]["quality_gates_passed"] = all_passed
        
        # Performance readiness
        if load_test_results:
            analysis = load_test_results.get("analysis", {})
            rt = analysis.get("response_times", {})
            p95 = rt.get("p95", 0)
            
            assessment["performance_readiness"] = {
                "p95_response_time": p95,
                "meets_criteria": p95 <= self.criteria["response_time_p95"],
                "requests_per_second": analysis.get("requests_per_second", 0),
                "success_rate": analysis.get("success_rate", 0)
            }
        
        # Stability readiness
        if stability_test_results:
            analysis = stability_test_results.get("analysis", {})
            issues = analysis.get("stability_issues", [])
            
            assessment["stability_readiness"] = {
                "test_duration_hours": analysis.get("test_duration_hours", 0),
                "stability_issues": len(issues),
                "meets_criteria": len(issues) == 0,
                "memory_trend": analysis.get("memory_trend", "unknown")
            }
        
        # Overall assessment
        all_criteria_met = (
            assessment["technical_readiness"].get("meets_criteria", False) and
            assessment.get("performance_readiness", {}).get("meets_criteria", True) and
            assessment.get("stability_readiness", {}).get("meets_criteria", True)
        )
        
        assessment["overall_readiness"] = {
            "all_criteria_met": all_criteria_met,
            "ready_for_production": all_criteria_met
        }
        
        # Risk analysis
        assessment["risks"] = self._identify_risks(assessment)
        
        # Recommendations
        assessment["recommendations"] = self._generate_recommendations(assessment)
        
        # Go/No-Go decision
        if all_criteria_met and len(assessment["risks"]) == 0:
            assessment["go_no_go"] = "GO"
        elif all_criteria_met:
            assessment["go_no_go"] = "GO_WITH_CONDITIONS"
        else:
            assessment["go_no_go"] = "NO_GO"
        
        return assessment
    
    def _identify_risks(self, assessment: Dict) -> List[Dict]:
        """Identify risks"""
        risks = []
        
        # Technical risks
        if not assessment["technical_readiness"].get("meets_criteria", False):
            risks.append({
                "category": "Technical",
                "severity": "High",
                "description": "Completion rate below 90%",
                "impact": "Some features may not work correctly"
            })
        
        # Performance risks
        perf = assessment.get("performance_readiness", {})
        if perf and not perf.get("meets_criteria", True):
            risks.append({
                "category": "Performance",
                "severity": "Medium",
                "description": "Response times above threshold",
                "impact": "User experience may be degraded"
            })
        
        # Stability risks
        stability = assessment.get("stability_readiness", {})
        if stability and stability.get("stability_issues", 0) > 0:
            risks.append({
                "category": "Stability",
                "severity": "High",
                "description": "Stability issues detected",
                "impact": "System may become unstable over time"
            })
        
        return risks
    
    def _generate_recommendations(self, assessment: Dict) -> List[str]:
        """Generate recommendations"""
        recommendations = []
        
        # Technical recommendations
        tech = assessment["technical_readiness"]
        if not tech.get("meets_criteria", False):
            rate = tech.get("completion_rate", 0)
            gap = self.criteria["completion_rate"] - rate
            recommendations.append(
                f"Improve completion rate by {gap*100:.1f}% to meet 90% threshold"
            )
        
        # Performance recommendations
        perf = assessment.get("performance_readiness", {})
        if perf and not perf.get("meets_criteria", True):
            p95 = perf.get("p95_response_time", 0)
            recommendations.append(
                f"Optimize response times: P95 is {p95:.2f}s, target is {self.criteria['response_time_p95']}s"
            )
        
        # Stability recommendations
        stability = assessment.get("stability_readiness", {})
        if stability and stability.get("stability_issues", 0) > 0:
            recommendations.append(
                "Address stability issues before production deployment"
            )
        
        if not recommendations:
            recommendations.append("All criteria met - ready for production")
        
        return recommendations
    
    def generate_markdown_report(self, assessment: Dict, output_path: Optional[str] = None) -> str:
        """Generate markdown report"""
        if output_path is None:
            output_path = Path(__file__).parent.parent.parent.parent / "reports" / "acceptance" / "production_readiness_report.md"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        go_no_go = assessment.get("go_no_go", "PENDING")
        go_status = "✅ GO" if go_no_go == "GO" else "⚠️ GO WITH CONDITIONS" if go_no_go == "GO_WITH_CONDITIONS" else "❌ NO GO"
        
        report = f"""# Production Readiness Report

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Status**: {go_status}

---

## Executive Summary

This report assesses the production readiness of the Digital Utopia Platform based on comprehensive testing and validation.

**Overall Assessment**: {go_no_go}

---

## 1. Technical Readiness

"""
        
        tech = assessment.get("technical_readiness", {})
        completion_rate = tech.get("completion_rate", 0)
        meets_criteria = tech.get("meets_criteria", False)
        
        report += f"""
### 1.1 Acceptance Testing

- **Completion Rate**: {completion_rate*100:.2f}%
- **Target**: ≥ 90%
- **Status**: {'✅ PASS' if meets_criteria else '❌ FAIL'}
- **Total Tests**: {tech.get('total_tests', 0)}
- **Passed**: {tech.get('passed', 0)}

"""
        
        if quality_report := assessment.get("quality_gates_passed"):
            report += f"""
### 1.2 Quality Gates

- **Status**: {'✅ PASS' if quality_report else '❌ FAIL'}
- All quality gates: {'Passed' if quality_report else 'Failed'}

"""
        
        # Performance
        perf = assessment.get("performance_readiness", {})
        if perf:
            report += f"""
## 2. Performance Readiness

- **P95 Response Time**: {perf.get('p95_response_time', 0):.2f}s
- **Target**: ≤ {self.criteria['response_time_p95']}s
- **Status**: {'✅ PASS' if perf.get('meets_criteria', False) else '❌ FAIL'}
- **Requests/Second**: {perf.get('requests_per_second', 0):.2f}
- **Success Rate**: {perf.get('success_rate', 0)*100:.2f}%

"""
        
        # Stability
        stability = assessment.get("stability_readiness", {})
        if stability:
            report += f"""
## 3. Stability Readiness

- **Test Duration**: {stability.get('test_duration_hours', 0):.2f} hours
- **Stability Issues**: {stability.get('stability_issues', 0)}
- **Status**: {'✅ PASS' if stability.get('meets_criteria', False) else '❌ FAIL'}
- **Memory Trend**: {stability.get('memory_trend', 'unknown')}

"""
        
        # Risks
        risks = assessment.get("risks", [])
        if risks:
            report += f"""
## 4. Risk Analysis

"""
            for i, risk in enumerate(risks, 1):
                report += f"""
### Risk {i}: {risk.get('category')}

- **Severity**: {risk.get('severity', 'Unknown')}
- **Description**: {risk.get('description', '')}
- **Impact**: {risk.get('impact', '')}

"""
        else:
            report += """
## 4. Risk Analysis

✅ No significant risks identified.

"""
        
        # Recommendations
        recommendations = assessment.get("recommendations", [])
        report += f"""
## 5. Recommendations

"""
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
        
        report += f"""
---

## 6. Go/No-Go Decision

**Decision**: **{go_status}**

"""
        
        if go_no_go == "GO":
            report += """
✅ **APPROVED FOR PRODUCTION**

All criteria have been met. The system is ready for production deployment.

"""
        elif go_no_go == "GO_WITH_CONDITIONS":
            report += """
⚠️ **APPROVED WITH CONDITIONS**

The system meets most criteria but has some risks. Address the recommendations before deployment.

"""
        else:
            report += """
❌ **NOT APPROVED**

The system does not meet production readiness criteria. Address critical issues before deployment.

"""
        
        report += f"""
---

## Sign-off

**Technical Lead**: _______________ Date: _______  
**Product Owner**: _______________ Date: _______  
**Security Lead**: _______________ Date: _______  
**Operations Lead**: _______________ Date: _______

---

*Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        
        with open(output_path, 'w') as f:
            f.write(report)
        
        return str(output_path)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate production readiness report")
    parser.add_argument(
        "test_results_file",
        help="Path to test results JSON file"
    )
    parser.add_argument(
        "-q", "--quality-report",
        help="Path to quality gate report JSON file"
    )
    parser.add_argument(
        "-l", "--load-test",
        help="Path to load test results JSON file"
    )
    parser.add_argument(
        "-s", "--stability-test",
        help="Path to stability test results JSON file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output markdown file path"
    )
    
    args = parser.parse_args()
    
    reporter = ProductionReadinessReporter()
    
    # Load data
    test_results = reporter.load_test_results(args.test_results_file)
    
    quality_report = None
    if args.quality_report:
        quality_report = reporter.load_quality_gate_report(args.quality_report)
    
    load_test_results = None
    if args.load_test:
        with open(args.load_test, 'r') as f:
            load_test_results = json.load(f)
    
    stability_test_results = None
    if args.stability_test:
        with open(args.stability_test, 'r') as f:
            stability_test_results = json.load(f)
    
    # Assess
    assessment = reporter.assess_readiness(
        test_results,
        quality_report,
        load_test_results,
        stability_test_results
    )
    
    # Generate report
    report_path = reporter.generate_markdown_report(assessment, args.output)
    
    print("="*60)
    print("PRODUCTION READINESS ASSESSMENT")
    print("="*60)
    print(f"\nGo/No-Go Decision: {assessment['go_no_go']}")
    print(f"\nTechnical Readiness: {assessment['technical_readiness'].get('completion_rate', 0)*100:.2f}%")
    
    if assessment.get('risks'):
        print(f"\n⚠️  Risks Identified: {len(assessment['risks'])}")
        for risk in assessment['risks']:
            print(f"  - {risk.get('category')}: {risk.get('description')}")
    
    print(f"\n✅ Report generated: {report_path}")

