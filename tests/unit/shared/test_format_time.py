import unittest
from datetime import datetime

import format_time

class TestFormatTime(unittest.TestCase):
    def test_valid_time_morning(self):
        """Test a valid morning time."""
        self.assertEqual(format_time.to_human_readable_twelve_hours("08:30:00"), "08:30am")

    def test_valid_time_afternoon(self):
        """Test a valid afternoon time."""
        self.assertEqual(format_time.to_human_readable_twelve_hours.to_human_readable_twelve_hours("13:45:00"), "01:45pm")

    def test_valid_time_noon(self):
        """Test the edge case for noon."""
        self.assertEqual(format_time.to_human_readable_twelve_hours("12:00:00"), "12:00pm")

    def test_valid_time_midnight(self):
        """Test the edge case for midnight."""
        self.assertEqual(format_time.to_human_readable_twelve_hours("00:00:00"), "12:00am")

    def test_invalid_time_format(self):
        """Test an invalid time format."""
        self.assertIsNone(format_time.to_human_readable_twelve_hours("25:00:00"))  # Out of range

    def test_malformed_time(self):
        """Test a completely malformed time."""
        self.assertIsNone(format_time.to_human_readable_twelve_hours("not-a-time"))

    def test_empty_time_string(self):
        """Test an empty string."""
        self.assertIsNone(format_time.to_human_readable_twelve_hours(""))

    def test_none_input(self):
        """Test None as input."""
        self.assertIsNone(format_time.to_human_readable_twelve_hours(None))
