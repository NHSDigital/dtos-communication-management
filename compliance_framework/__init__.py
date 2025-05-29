"""
Compliance Framework for tracking requirements and risks in tests.
"""

from .types import (
    RequirementId,
    RiskId,
    RiskIds,
    ComplianceMetadata,
    TestStatus,
    TestResult,
    RequirementCoverage,
    RiskCoverage,
    ComplianceReport
)
from .decorators import compliance
from .report_writers import ReportWriter, JsonReportWriter, HtmlReportWriter

__version__ = "0.1.0"

__all__ = [
    "compliance",
    "ComplianceMetadata",
    "RequirementId",
    "RiskId",
    "RiskIds",
    "TestStatus",
    "TestResult",
    "RequirementCoverage",
    "RiskCoverage",
    "ComplianceReport",
    "ReportWriter",
    "JsonReportWriter",
    "HtmlReportWriter"
]

# Register the pytest plugin
pytest_plugins = ["compliance_framework.plugin"]
