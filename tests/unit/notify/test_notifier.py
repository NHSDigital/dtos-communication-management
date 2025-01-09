import json
import logging
import notifier
import pytest
import requests_mock
import routing_plans
import uuid
import uuid_generator


@pytest.fixture
def setup(monkeypatch):
    """Set up environment variables for tests."""
    monkeypatch.setenv("NOTIFY_API_URL", "http://example.com")


@pytest.fixture
def message_data():
    """Sample message data."""
    return {
        "nhs_number": "0000000000",
        "date_of_birth": "1981-10-07",
        "appointment_time": "10:00",
        "appointment_date": "2021-12-01",
        "appointment_location": "Breast Screening Clinic, 123 High Street, London",
        "correlation_id": "da0b1495-c7cb-468c-9d81-07dee089d728",
        "contact_telephone_number": "012345678",
    }


@pytest.fixture
def response_text():
    """Sample successful response text."""
    return json.dumps(
        {
            "data": {
                "type": "Message",
                "id": "2WL3qFTEFM0qMY8xjRbt1LIKCzM",
                "attributes": {
                    "messageReference": "da0b1495-c7cb-468c-9d81-07dee089d728",
                    "messageStatus": "created",
                    "timestamps": {"created": "2023-11-17T14:27:51.413Z"},
                    "routingPlan": {
                        "id": "b838b13c-f98c-4def-93f0-515d4e4f4ee1",
                        "version": "ztoe2qRAM8M8vS0bqajhyEBcvXacrGPp",
                    },
                },
            }
        }
    )


@pytest.fixture
def error_response_text():
    """Sample error response text."""
    return json.dumps(
        {
            "errors": [
                {
                    "status": "401",
                    "title": "Access Denied",
                    "detail": "Access token missing",
                }
            ]
        }
    )


def test_send_messages_success(mocker):
    """Test sending multiple messages successfully."""
    mocker.patch("access_token.get_token", return_value="an_access_token")
    send_message_mock = mocker.patch("notifier.send_message", return_value="OK")

    data = {
        "routing_plan": "breast-screening-pilot",
        "recipients": [
            {"nhs_number": "0000000000"},
            {"nhs_number": "0000000001"},
        ],
    }
    expected_batch_id = uuid_generator.reference_uuid(json.dumps(data))

    response = notifier.send_messages(data)

    assert send_message_mock.call_count == 2
    assert response == "OK\nOK"

    send_message_mock.assert_any_call(
        "an_access_token",
        routing_plans.get_id("breast-screening-pilot"),
        {"nhs_number": "0000000000"},
        expected_batch_id,
    )
    send_message_mock.assert_any_call(
        "an_access_token",
        routing_plans.get_id("breast-screening-pilot"),
        {"nhs_number": "0000000001"},
        expected_batch_id,
    )


def test_send_messages_with_exception_raised_on_first_item(mocker):
    """Test sending multiple messages with an exception raised on the first item."""
    mocker.patch("access_token.get_token", return_value="an_access_token")
    send_message_mock = mocker.patch("notifier.send_message", return_value="OK")

    def side_effect(*args, **kwargs):
        if args[2]['nhs_number'] == "0000000000":
            raise Exception("Error sending message")

        return mocker.DEFAULT

    send_message_mock.side_effect = side_effect

    data = {
        "routing_plan": "breast-screening-pilot",
        "recipients": [
            {"nhs_number": "0000000000"},
            {"nhs_number": "0000000001"},
        ],
    }

    response = notifier.send_messages(data)

    assert send_message_mock.call_count == 2
    assert response == "OK"


def test_send_message_success(mocker, setup, message_data, response_text):
    """Test sending a single message successfully."""
    mock_recorder = mocker.patch("batch_message_recorder.save_status")
    message_reference = "da0b1495-c7cb-468c-9d81-07dee089d728"
    mocker.patch("uuid_generator.uuid4_str", return_value=message_reference)
    access_token = "access_token"
    routing_plan = "breast-screening-pilot"
    routing_plan_id = routing_plans.get_id(routing_plan)
    message_data["routing_plan"] = routing_plan
    batch_id = uuid_generator.reference_uuid(json.dumps(message_data))

    expected_request_body = notifier.message_body(routing_plan_id, message_reference, message_data)

    with requests_mock.Mocker() as rm:
        adapter = rm.post(
            "http://example.com/comms/v1/messages", status_code=201, text=response_text
        )
        notifier.send_message(access_token, routing_plan_id, message_data, batch_id)

        assert adapter.called
        assert adapter.call_count == 1
        assert adapter.last_request.json() == expected_request_body
        mock_recorder.assert_any_call("not_sent", batch_id, message_reference, message_data)
        modified_message_data = message_data.copy()
        modified_message_data["message_id"] = "2WL3qFTEFM0qMY8xjRbt1LIKCzM"
        modified_message_data["details"] = response_text
        mock_recorder.assert_any_call("sent", batch_id, message_reference, modified_message_data)


def test_send_message_logs_error(mocker, setup, error_response_text, message_data):
    """Test logging and handling of error responses during message sending."""
    mock_recorder = mocker.patch("batch_message_recorder.save_status")
    access_token = "access_token"
    routing_plan = "breast-screening-pilot"
    routing_plan_id = routing_plans.get_id(routing_plan)
    batch_id = uuid_generator.reference_uuid(json.dumps(message_data))
    message_reference = "da0b1495-c7cb-468c-9d81-07dee089d728"
    mocker.patch("uuid_generator.uuid4_str", return_value=message_reference)

    error_logging_spy = mocker.spy(logging, "error")

    with requests_mock.Mocker() as rm:
        rm.post(
            "http://example.com/comms/v1/messages", status_code=401, text=error_response_text
        )
        result = notifier.send_message(access_token, routing_plan_id, message_data, batch_id)

        assert result == error_response_text
        error_logging_spy.assert_called_once_with(error_response_text)
        mock_recorder.assert_any_call("not_sent", batch_id, message_reference, message_data)
        modified_message_data = message_data.copy()
        modified_message_data["details"] = error_response_text
        mock_recorder.assert_any_call("failed", batch_id, message_reference, modified_message_data)


def test_message_body(monkeypatch):
    """Test message body generation."""
    routing_plan_id = str(uuid.uuid4())
    message_reference = "da0b1495-c7cb-468c-9d81-07dee089d728"
    monkeypatch.setattr(uuid, "uuid4", lambda: uuid.UUID("00000000-0000-0000-0000-000000000000"))

    data = {
        "nhs_number": "0000000000",
        "date_of_birth": "1990-01-02",
        "appointment_time": "10:00",
        "appointment_date": "2021-12-01",
        "appointment_location": "Breast Screening Clinic, 123 High Street, London",
        "correlation_id": "da0b1495-c7cb-468c-9d81-07dee089d728",
        "contact_telephone_number": "012345678",
    }

    actual = notifier.message_body(routing_plan_id, message_reference, data)

    expected = {
        "data": {
            "type": "Message",
            "attributes": {
                "messageReference": "da0b1495-c7cb-468c-9d81-07dee089d728",
                "routingPlanId": routing_plan_id,
                "recipient": {
                    "nhsNumber": "0000000000",
                    "dateOfBirth": "1990-01-02",
                },
                "personalisation": {
                    "appointment_date": "2021-12-01",
                    "appointment_location": "Breast Screening Clinic, 123 High Street, London",
                    "appointment_time": "10:00",
                    "tracking_id": "0000000000",
                    "contact_telephone_number": "012345678",
                },
            },
        }
    }

    assert actual == expected
