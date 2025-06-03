"""
Pytest plugin for compliance metadata collection and reporting.
"""
from typing import Dict, List
import pytest
from datetime import datetime
from pathlib import Path
from .types import (
    ComplianceMetadata,
    RequirementId,
    RiskId,
    TestStatus,
    TestResult,
    RequirementCoverage,
    RiskCoverage,
    ComplianceReport
)
from .report_writers import JsonReportWriter, HtmlReportWriter

def pytest_configure(config):
    """Register the compliance marker."""
    config.addinivalue_line(
        "markers",
        "compliance: mark test with compliance requirements and risks"
    )

def pytest_collection_modifyitems(config, items):
    """Collect compliance metadata during test collection."""
    if config.getoption("--compliance-report"):
        for item in items:
            if hasattr(item.function, '_compliance_metadata'):
                metadata: ComplianceMetadata = item.function._compliance_metadata
                item.user_properties.append(('compliance_requirements', ','.join(metadata.all_requirements)))
                item.user_properties.append(('compliance_risks', ','.join(metadata.all_risks)))
                item.user_properties.append(('compliance_metadata', metadata))

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach compliance metadata to the test report so it persists for the summary."""
    outcome = yield
    report = outcome.get_result()
    if call.when == 'call':
        metadata = getattr(item.function, '_compliance_metadata', None)
        if metadata:
            report.compliance_requirements = metadata.all_requirements
            report.compliance_risks = metadata.all_risks
            report.compliance_mapping = metadata.requirements
            report.test_id = item.nodeid
            report.test_duration = report.duration
            report.test_completed_at = datetime.now()

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Generate compliance reports at the end of the test run."""
    if not config.getoption("--compliance-report"):
        return

    if not terminalreporter.stats:
        return

    # Collect all compliance data
    requirements: Dict[RequirementId, RequirementCoverage] = {}
    risks: Dict[RiskId, RiskCoverage] = {}
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    skipped_tests = 0

    # Process all test reports
    for status, reports in terminalreporter.stats.items():
        for report in reports:
            total_tests += 1
            if status == 'passed':
                passed_tests += 1
            elif status in ['failed', 'error']:
                failed_tests += 1
            elif status == 'skipped':
                skipped_tests += 1

            compliance_mapping = getattr(report, 'compliance_mapping', None)
            if not compliance_mapping:
                continue

            test_result = TestResult(
                test_id=getattr(report, 'test_id', 'unknown'),
                status=TestStatus(status),
                duration=getattr(report, 'test_duration', 0.0),
                completed_at=getattr(report, 'test_completed_at', datetime.now())
            )

            # Update requirements coverage
            for req_id, risk_ids in compliance_mapping.items():
                if req_id not in requirements:
                    requirements[req_id] = RequirementCoverage(
                        requirement_id=req_id,
                        risks=risk_ids,
                        tests=[]
                    )
                requirements[req_id].tests.append(test_result)

                # Update risks coverage
                for risk_id in risk_ids:
                    if risk_id not in risks:
                        risks[risk_id] = RiskCoverage(
                            risk_id=risk_id,
                            requirements=[req_id],
                            tests=[]
                        )
                    elif req_id not in risks[risk_id].requirements:
                        risks[risk_id].requirements.append(req_id)
                    risks[risk_id].tests.append(test_result)

    # Create the compliance report
    report = ComplianceReport(
        requirements=requirements,
        risks=risks,
        generated_at=datetime.now(),
        total_tests=total_tests,
        passed_tests=passed_tests,
        failed_tests=failed_tests,
        skipped_tests=skipped_tests
    )

    # Write reports
    output_dir = Path(config.getoption("--compliance-report-dir", "compliance_reports"))
    output_dir.mkdir(exist_ok=True)

    # Write JSON report
    json_writer = JsonReportWriter()
    json_writer.write(report, output_dir / "compliance_report.json")

    # Write HTML report
    html_writer = HtmlReportWriter()
    html_writer.write(report, output_dir / "compliance_report.html")

def pytest_addoption(parser):
    """Add command line options for the compliance framework."""
    parser.addoption(
        "--compliance-report",
        action="store_true",
        help="Generate compliance reports"
    )
    parser.addoption(
        "--compliance-report-dir",
        default="compliance_reports",
        help="Directory to write compliance reports to"
    )
