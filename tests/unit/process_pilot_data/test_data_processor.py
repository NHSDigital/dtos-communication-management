import json
import data_processor
import pytest
import requests_mock


@pytest.fixture
def setup(monkeypatch):
    """Set up environment variables and mock UUID for consistent testing."""
    monkeypatch.setattr(
        "uuid.uuid4",
        lambda: "00000000-0000-0000-0000-000000000000",
    )
    monkeypatch.setenv(
        "NOTIFY_FUNCTION_URL",
        "http://example.com/api/notify/message/send",
    )


def test_process_data_valid_csv(setup):
    """Test processing valid CSV data."""
    response_text = json.dumps({"data": "OK"})
    csv_data = [
        '0000000000,2001-02-03,03M02M2022,10:00:00,"The Royal Shrewsbury Hospital, Breast Screening Office, Shrewsbury, SY3 8XQ"',
        '1111111111,2002-04-04,2024-04-04,11:00,"The Epping Breast Screening Unit, St Margaret\'s Hospital, The Plain, Epping, Essex, CM16 6TN"',
    ]

    expected_request_body = {
        "routing_plan": "breast-screening-pilot",
        "recipients": [
            {
                "nhs_number": "0000000000",
                "date_of_birth": "2001-02-03",
                "appointment_date": "Thursday 03 February 2022",
                "appointment_time": "10:00am",
                "appointment_location": "The Royal Shrewsbury Hospital, Breast Screening Office, Shrewsbury, SY3 8XQ",
                "correlation_id": "00000000-0000-0000-0000-000000000000",
                "contact_telephone_number": "020 3758 2024",
            },
            {
                "nhs_number": "1111111111",
                "date_of_birth": "2002-04-04",
                "appointment_date": "Friday 04 April 2024",
                "appointment_time": "11:00am",
                "appointment_location": "The Epping Breast Screening Unit, St Margaret's Hospital, The Plain, Epping, Essex, CM16 6TN",
                "correlation_id": "00000000-0000-0000-0000-000000000000",
                "contact_telephone_number": "020 3758 2024",
            },
        ],
    }

    with requests_mock.Mocker() as rm:
        adapter = rm.post(
            "http://example.com/api/notify/message/send",
            text=response_text,
        )
        data_processor.process_data("HWA NHS App Pilot 002 SPRPT", csv_data)

        assert adapter.called
        assert adapter.call_count == 1
        assert adapter.last_request.json() == expected_request_body


def test_process_data_missing_csv_data(setup):
    """Test handling CSV data with missing fields."""
    response_text = json.dumps({"data": "OK"})
    csv_data = [
        "0000000000,yyyy-mm-dd",
        "1111111111",
        "2222222222",
    ]

    with requests_mock.Mocker() as rm:
        adapter = rm.post(
            "http://example.com/api/notify/message/send",
            text=response_text,
        )
        data_processor.process_data("JDO", csv_data)

        assert not adapter.called
        assert adapter.call_count == 0
        assert adapter.last_request is None


def test_process_data_invalid_csv_data(setup):
    """Test handling completely invalid CSV data."""
    response_text = json.dumps({"data": "OK"})
    invalid_data = "\n"

    with requests_mock.Mocker() as rm:
        adapter = rm.post(
            "http://example.com/api/notify/message/send",
            text=response_text,
        )
        data_processor.process_data("KMK", invalid_data)

        assert not adapter.called
        assert adapter.call_count == 0
        assert adapter.last_request is None
