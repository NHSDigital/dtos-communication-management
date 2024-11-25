import pytest
import format_date

def test_to_date_of_birth():
    """Test date of birth formatting."""
    valid_test_cases = [
        ("25M01M1985", "1985-01-25"),
        ("01M02M2000", "2000-02-01"),
        ("15M03M1999", "1999-03-15"),
        ("30M12M2022", "2022-12-30"),
        ("1985-01-25", "1985-01-25"), # Already in correct format - should return as is
    ]

    invalid_test_cases = [
        "32M01M1985",  # Invalid day
        "15M13M1999",  # Invalid month
        "01M00M2000",  # Invalid month
        "",
    ]

    for input_date, expected_output in valid_test_cases:
        result = format_date.to_date_of_birth(input_date)
        assert result == expected_output, f"Expected {expected_output}, but got {result} for input {input_date}"

    for input_date in invalid_test_cases:
        result = format_date.to_date_of_birth(input_date)
        assert result is None, f"Expected None, but got {result} for invalid input {input_date}"
