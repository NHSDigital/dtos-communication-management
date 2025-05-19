"""
Utility functions for validating NHS numbers using functional programming practices.
"""
from typing import Tuple
from functools import reduce
from operator import mul, add


def remove_spaces(nhs_number: str | None) -> str | None:
    if nhs_number is None:
        return None
    return nhs_number.replace(" ", "")


def is_digits_only(nhs_number: str | None) -> bool:
    return nhs_number is not None and nhs_number.isdigit()


def has_correct_length(nhs_number: str | None) -> bool:
    return nhs_number is not None and len(nhs_number) == 10


def has_unique_digits(nhs_number: str | None) -> bool:
    return nhs_number is not None and len(set(nhs_number)) > 1


def calculate_check_digit(nhs_number: str) -> int:
    # Create list of weights (10 to 2)
    weights = range(10, 1, -1)

    # Multiply each digit by its weight and sum
    total = reduce(
        add,
        map(
            lambda x: mul(int(x[0]), x[1]),
            zip(nhs_number[:9], weights)
        )
    )

    # Calculate check digit
    check_digit = 11 - (total % 11)

    return 0 if check_digit == 11 else check_digit


def validate_check_digit(nhs_number: str) -> bool:
    check_digit = calculate_check_digit(nhs_number)
    return check_digit != 10 and check_digit == int(nhs_number[9])


def get_validation_error(nhs_number: str) -> str:
    if not is_digits_only(nhs_number):
        return "NHS number must contain only digits"

    if not has_correct_length(nhs_number):
        return "NHS number must be 10 digits long"

    if not has_unique_digits(nhs_number):
        return "NHS number cannot be all the same digit"

    if not validate_check_digit(nhs_number):
        return "Invalid NHS number check digit"

    return ""


def is_valid_nhs_number(nhs_number: str) -> Tuple[bool, str]:
    clean_number = remove_spaces(nhs_number)
    error = get_validation_error(clean_number)

    return (not bool(error), error)
