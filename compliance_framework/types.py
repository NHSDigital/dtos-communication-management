"""Type definitions and metadata structures for the compliance framework."""
from dataclasses import dataclass
from typing import Dict, List, Union, TypeVar, Callable, Any, Optional
from datetime import datetime
from enum import Enum

# Type definitions
RequirementId = str
RiskId = str
RiskIds = List[RiskId]
TestId = str

# Type for the test function
F = TypeVar('F', bound=Callable[..., Any])

class TestStatus(Enum):
    """Status of a test execution."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    XFAIL = "xfail"
    XPASS = "xpass"

@dataclass
class TestResult:
    """Information about a test execution."""
    test_id: TestId
    status: TestStatus
    duration: float  # in seconds
    completed_at: datetime
    is_active: bool = True

@dataclass
class RiskCoverage:
    """Coverage information for a risk."""
    risk_id: RiskId
    requirements: List[RequirementId]
    tests: List[TestResult]

@dataclass
class RequirementCoverage:
    """Coverage information for a requirement."""
    requirement_id: RequirementId
    risks: List[RiskId]
    tests: List[TestResult]

@dataclass
class ComplianceReport:
    """Complete compliance report data structure."""
    requirements: Dict[RequirementId, RequirementCoverage]
    risks: Dict[RiskId, RiskCoverage]
    generated_at: datetime
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int

@dataclass
class ComplianceMetadata:
    """
    Structured metadata for compliance tracking.

    Attributes:
        requirements: Dictionary mapping requirement IDs to their associated risk IDs.
    """
    requirements: Dict[RequirementId, RiskIds]

    @property
    def all_requirements(self) -> List[RequirementId]:
        """Get all requirement IDs."""
        return list(self.requirements.keys())

    @property
    def all_risks(self) -> List[RiskId]:
        """Get all unique risk IDs."""
        return list(set(
            risk_id
            for risks in self.requirements.values()
            for risk_id in risks
        ))

    def get_risks_for_requirement(self, requirement_id: RequirementId) -> RiskIds:
        """Get all risk IDs associated with a specific requirement."""
        return self.requirements.get(requirement_id, [])

    def get_requirements_for_risk(self, risk_id: RiskId) -> List[RequirementId]:
        """Get all requirements that are associated with a specific risk."""
        return [
            req_id
            for req_id, risk_ids in self.requirements.items()
            if risk_id in risk_ids
        ]

    def __post_init__(self):
        """Validate the metadata after initialization."""
        # Validate requirement ID format
        for req_id in self.requirements:
            if not req_id.startswith("DTOSS-"):
                raise ValueError(f"Invalid requirement ID format: {req_id}")

        # Validate risk ID format
        for risk_ids in self.requirements.values():
            for risk_id in risk_ids:
                if not risk_id.startswith("RISK-"):
                    raise ValueError(f"Invalid risk ID format: {risk_id}")
