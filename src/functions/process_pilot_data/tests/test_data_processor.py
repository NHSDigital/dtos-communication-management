import json
import pytest
import requests_mock

from unittest.mock import MagicMock
from process_pilot_data.data_processor import DataProcessor


class TestDataProcessor:
    @pytest.fixture
    def setup(self):
        mock_base_url = MagicMock(name="base_url")
        mock_base_url.return_value = "http://example.com"
        DataProcessor.base_url = mock_base_url

    def test_call(self, setup):
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
            ]
        }
        with requests_mock.Mocker() as rm:
            adapter = rm.post(
                'http://example.com/api/batch-message/breast-screening-pilot',
                text=response_text
            )
            DataProcessor.call(csv_data)

            assert adapter.called
            assert adapter.call_count == 1
            assert adapter.last_request.json() == expected_request_body

    def test_call_with_missing_csv_data(self, setup):
        response_text = json.dumps({"data": "OK"})
        csv_data = [
            "0000000000,yyyy-mm-dd",
            "1111111111",
            "2222222222",
        ]

        with requests_mock.Mocker() as rm:
            adapter = rm.post(
                'http://example.com/batch-message/breast-screening-pilot',
                text=response_text
            )
            DataProcessor.call(csv_data)

            assert not adapter.called
            assert adapter.call_count == 0
            assert adapter.last_request is None

    def test_call_with_invalid_csv_data(self, setup):
        response_text = json.dumps({"data": "OK"})
        invalid_data = "\n"

        with requests_mock.Mocker() as rm:
            adapter = rm.post(
                'http://example.com/batch-message/breast-screening-pilot',
                text=response_text
            )
            DataProcessor.call(invalid_data)

            assert not adapter.called
            assert adapter.call_count == 0
            assert adapter.last_request is None
