import json
import pytest
import requests_mock
from process_pilot_data.helper import process_data


class TestHelper:
    @pytest.fixture
    def setup(self, monkeypatch):
        monkeypatch.setenv(
            "BATCH_NOTIFY_URL",
            "http://example.com/api/batch-notify/breast-screening-pilot",
        )

    def test_process_data(self, setup):
        response_text = json.dumps({"data": "OK"})
        csv_data = [
            "0000000000,2001-02-03",
            "1111111111,2002-04-04",
            "2222222222,1985-05-04",
        ]

        expected_request_body = {
            "routing_plan": "breast-screening-pilot",
            "data": [
                {"nhs_number": "0000000000", "date_of_birth": "2001-02-03"},
                {"nhs_number": "1111111111", "date_of_birth": "2002-04-04"},
                {"nhs_number": "2222222222", "date_of_birth": "1985-05-04"},
            ],
        }
        with requests_mock.Mocker() as rm:
            adapter = rm.post(
                "http://example.com/api/batch-notify/breast-screening-pilot",
                text=response_text,
            )
            process_data(csv_data)

            assert adapter.called
            assert adapter.call_count == 1
            assert adapter.last_request.json() == expected_request_body

    def test_process_data_with_missing_csv_data(self, setup):
        response_text = json.dumps({"data": "OK"})
        csv_data = [
            "0000000000,yyyy-mm-dd",
            "1111111111",
            "2222222222",
        ]

        with requests_mock.Mocker() as rm:
            adapter = rm.post(
                "http://example.com/api/batch-notify/breast-screening-pilot",
                text=response_text,
            )
            process_data(csv_data)

            assert not adapter.called
            assert adapter.call_count == 0
            assert adapter.last_request is None

    def test_process_data_with_invalid_csv_data(self, setup):
        response_text = json.dumps({"data": "OK"})
        invalid_data = "\n"

        with requests_mock.Mocker() as rm:
            adapter = rm.post(
                "http://example.com/api/batch-notify/breast-screening-pilot",
                text=response_text,
            )
            process_data(invalid_data)

            assert not adapter.called
            assert adapter.call_count == 0
            assert adapter.last_request is None
