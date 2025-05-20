"""
Unit tests for NHS number validation.
"""

import pytest
from app.utils.nhs_number_validator import is_valid_nhs_number


def test_valid_nhs_number():
    """Test that valid NHS numbers pass validation."""
    # Test cases from NHS Digital documentation
    valid_numbers = [
        "4010232137",  # Example from NHS Digital
        "9876543210",  # Another valid number
    ]

    for nhs_number in valid_numbers:
        is_valid, error = is_valid_nhs_number(nhs_number)
        assert is_valid, f"Valid NHS number {nhs_number} failed validation: {error}"


def test_invalid_nhs_number():
    """Test that invalid NHS numbers fail validation."""
    invalid_cases = [
        ("123456789", "NHS number must be 10 digits long"),
        ("12345678901", "NHS number must be 10 digits long"),
        ("123456789a", "NHS number must contain only digits"),
        ("1111111111", "NHS number cannot be all the same digit"),
        ("1234567890", "Invalid NHS number check digit"),
    ]

    for nhs_number, expected_error in invalid_cases:
        is_valid, error = is_valid_nhs_number(nhs_number)
        assert not is_valid, f"Invalid NHS number {nhs_number} passed validation"
        assert error == expected_error, f"Unexpected error message for {nhs_number}: {error}"
