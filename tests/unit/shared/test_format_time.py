import pytest
from datetime import datetime
from format_time import to_human_readable_twelve_hours

def test_valid_time_am():
    """
    Test that a valid morning time converts correctly.
    """
    assert to_human_readable_twelve_hours("07:45:00") == "07:45am"

def test_valid_time_pm():
    """
    Test that a valid afternoon/evening time converts correctly.
    """
    assert to_human_readable_twelve_hours("19:30:00") == "07:30pm"

def test_midnight():
    """
    Test the conversion of midnight (00:00:00).
    """
    assert to_human_readable_twelve_hours("00:00:00") == "12:00am"

def test_noon():
    """
    Test the conversion of noon (12:00:00).
    """
    assert to_human_readable_twelve_hours("12:00:00") == "12:00pm"

def test_edge_case_just_before_noon():
    """
    Test the conversion of a time just before noon.
    """
    assert to_human_readable_twelve_hours("11:59:59") == "11:59am"

def test_edge_case_just_after_noon():
    """
    Test the conversion of a time just after noon.
    """
    assert to_human_readable_twelve_hours("12:00:01") == "12:00pm"

def test_edge_case_just_before_midnight():
    """
    Test the conversion of a time just before midnight.
    """
    assert to_human_readable_twelve_hours("23:59:59") == "11:59pm"

def test_invalid_format():
    """
    Test with an invalid time format.
    """
    assert to_human_readable_twelve_hours("25:00:00") is None

def test_non_numeric_time():
    """
    Test with non-numeric input.
    """
    assert to_human_readable_twelve_hours("abcd:ef:gh") is None

def test_partial_time_string():
    """
    Test with a partial time string.
    """
    assert to_human_readable_twelve_hours("11:56") is None

def test_empty_string():
    """
    Test with an empty string.
    """
    assert to_human_readable_twelve_hours("") is None

def test_none_input():
    """
    Test with None as input.
    """
    assert to_human_readable_twelve_hours(None) is None

def test_whitespace_input():
    """
    Test with input that is just whitespace.
    """
    assert to_human_readable_twelve_hours("   ") is None

def test_leading_trailing_spaces():
    """
    Test with valid time surrounded by spaces.
    """
    assert to_human_readable_twelve_hours(" 11:56:00 ") == "11:56am"
