"""
Report writers for compliance framework.
"""
from abc import ABC, abstractmethod
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from jinja2 import Environment, PackageLoader, select_autoescape

from .types import (
    ComplianceReport,
    RequirementCoverage,
    RiskCoverage,
    TestResult,
    TestStatus
)

class ReportWriter(ABC):
    """Base class for compliance report writers."""

    @abstractmethod
    def write(self, report: ComplianceReport, output_path: Path) -> None:
        """Write the compliance report to the specified path."""
        pass

class JsonReportWriter(ReportWriter):
    """Writer for JSON format compliance reports."""

    def write(self, report: ComplianceReport, output_path: Path) -> None:
        """Write the compliance report as JSON."""
        # Convert the report to a dictionary
        report_dict = {
            "generated_at": report.generated_at.isoformat(),
            "total_tests": report.total_tests,
            "passed_tests": report.passed_tests,
            "failed_tests": report.failed_tests,
            "skipped_tests": report.skipped_tests,
            "requirements": {
                req_id: {
                    "requirement_id": coverage.requirement_id,
                    "risks": coverage.risks,
                    "tests": [
                        {
                            "test_id": test.test_id,
                            "status": test.status.value,
                            "duration": test.duration,
                            "completed_at": test.completed_at.isoformat(),
                            "is_active": test.is_active
                        }
                        for test in coverage.tests
                    ]
                }
                for req_id, coverage in report.requirements.items()
            },
            "risks": {
                risk_id: {
                    "risk_id": coverage.risk_id,
                    "requirements": coverage.requirements,
                    "tests": [
                        {
                            "test_id": test.test_id,
                            "status": test.status.value,
                            "duration": test.duration,
                            "completed_at": test.completed_at.isoformat(),
                            "is_active": test.is_active
                        }
                        for test in coverage.tests
                    ]
                }
                for risk_id, coverage in report.risks.items()
            }
        }

        # Write to file
        with open(output_path, 'w') as f:
            json.dump(report_dict, f, indent=2)

class HtmlReportWriter(ReportWriter):
    """Writer for HTML format compliance reports."""

    def __init__(self):
        """Initialize the HTML report writer with Jinja2 environment."""
        self.env = Environment(
            loader=PackageLoader('compliance_framework', 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def write(self, report: ComplianceReport, output_path: Path) -> None:
        """Write the compliance report as HTML."""
        template = self.env.get_template('compliance_report.html')

        # Prepare template context
        context = {
            "report": report,
            "generated_at": report.generated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "test_summary": {
                "total": report.total_tests,
                "passed": report.passed_tests,
                "failed": report.failed_tests,
                "skipped": report.skipped_tests,
                "pass_rate": (report.passed_tests / report.total_tests * 100) if report.total_tests > 0 else 0
            }
        }

        # Render and write to file
        html_content = template.render(**context)
        with open(output_path, 'w') as f:
            f.write(html_content)
