import file_processor.csv_file_processor as csv_file_processor
import pytest


pytestmark = pytest.mark.test_id([
    "DTOSS-4691#1.1",
    "DTOSS-4691#2.1",
    "DTOSS-4691#3.1",
    "DTOSS-4691#3.2",
    "DTOSS-4691#3.3"
    ])

def test_process_data_valid_csv(csv_data, expected_message_batch_body):
    """Test processing valid CSV data."""
    result = csv_file_processor.message_batch_body("HWA NHS App Pilot 002 SPRPT", csv_data)
    assert result == expected_message_batch_body


def test_process_data_missing_csv_data():
    """Test handling CSV data with missing fields."""
    csv_data = [
        "0000000000,yyyy-mm-dd",
        "1111111111",
        "2222222222",
    ]

    result = csv_file_processor.message_batch_body("JDO", csv_data)

    assert result is None


def test_process_data_invalid_csv_data():
    """Test handling completely invalid CSV data."""
    invalid_data = "\n"

    result = csv_file_processor.message_batch_body("KMK", invalid_data)
    assert result is None
