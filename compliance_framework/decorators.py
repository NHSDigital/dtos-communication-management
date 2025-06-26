"""Decorators for compliance tracking in tests."""

from typing import Callable, Dict, List, Union
from .types import (
    RequirementId,
    RiskId,
    RiskIds,
    ComplianceMetadata,
    F
)

def compliance(requirements: Dict[RequirementId, Union[RiskId, RiskIds]]) -> Callable[[F], F]:
    """
    Decorator for tracking compliance requirements and their associated risks.

    Args:
        requirements: Dictionary mapping requirement IDs to their associated risk IDs.
            Each requirement can have either a single risk ID (string) or multiple risk IDs (list).

    Example:
        @compliance({
            "DTOSS-789": ["RISK-126", "RISK-127"],
            "DTOSS-790": "RISK-128"
        })
        def test_security():
            ...
    """
    def decorator(func: F) -> F:
        # Convert single risk IDs to lists for consistency
        normalized_requirements = {
            req_id: [risk_id] if isinstance(risk_id, str) else risk_id
            for req_id, risk_id in requirements.items()
        }

        # Validate the requirements mapping
        for req_id, risk_ids in normalized_requirements.items():
            if not isinstance(req_id, str):
                raise TypeError(f"Requirement ID must be a string, got {type(req_id)}")
            if not isinstance(risk_ids, list):
                raise TypeError(f"Risk IDs must be a list, got {type(risk_ids)}")
            if not all(isinstance(risk_id, str) for risk_id in risk_ids):
                raise TypeError("All risk IDs must be strings")

        # Store the metadata in a structured way
        func._compliance_metadata = ComplianceMetadata(
            requirements=normalized_requirements
        )

        return func
    return decorator
