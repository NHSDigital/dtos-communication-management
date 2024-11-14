import json
import logging
import notifier
import pytest
import requests_mock
import uuid
import routing_plans


@pytest.fixture
def setup(monkeypatch):
    monkeypatch.setenv("NOTIFY_API_URL", "http://example.com")


def test_send_messages(mocker):
    mocker.patch("access_token.get_token", return_value="an_access_token")
    send_message_mock = mocker.patch("notifier.send_message", return_value="OK")
    data = {
        "routing_plan": "breast-screening-pilot",
        "recipients": [
            {"nhs_number": "0000000000"},
            {"nhs_number": "0000000001"},
        ]
    }

    response = notifier.send_messages(data)

    assert send_message_mock.call_count == 2

    assert response == "OK\nOK"
    send_message_mock.assert_any_call(
        "an_access_token",
        routing_plans.get_id("breast-screening-pilot"),
        {"nhs_number": "0000000000"},
    )
    send_message_mock.assert_any_call(
        "an_access_token",
        routing_plans.get_id("breast-screening-pilot"),
        {"nhs_number": "0000000001"},
    )


def test_send_messages_with_individual_routing_plans(mocker):
    mocker.patch("access_token.get_token", return_value="an_access_token")

    data = {
        "recipients": [
            {"routing_plan": "breast-screening-pilot", "nhs_number": "0000000000"},
            {"routing_plan": "bowel-screening-pilot", "nhs_number": "0000000001"},
        ]
    }

    send_message_mock = mocker.patch("notifier.send_message", return_value="OK")

    response = notifier.send_messages(data)

    assert send_message_mock.call_count == 2
    assert response == "OK\nOK"
    send_message_mock.assert_any_call(
        "an_access_token",
        "b838b13c-f98c-4def-93f0-515d4e4f4ee1",
        {"nhs_number": "0000000000"},
    )
    send_message_mock.assert_any_call(
        "an_access_token",
        "b1e3b13c-f98c-4def-93f0-515d4e4f4ee1",
        {"nhs_number": "0000000001"},
    )


def test_send_message(setup):
    access_token = "access_token"
    routing_plan = "breast-screening-pilot"
    routing_plan_id = routing_plans.get_id(routing_plan)
    message_data = {
        "nhs_number": "0000000000",
        "date_of_birth": "1981-10-07",
        "appointment_time": "10:00",
        "appointment_date": "2021-12-01",
        "appointment_location": "Breast Screening Clinic, 123 High Street, London",
        "correlation_id": "da0b1495-c7cb-468c-9d81-07dee089d728",
        "contact_telephone_number": "012345678",
        "routing_plan": routing_plan,
    }

    response_text = json.dumps(
        {
            "data": {
                "type": "Message",
                "id": "2WL3qFTEFM0qMY8xjRbt1LIKCzM",
                "attributes": {
                    "messageReference": "da0b1495-c7cb-468c-9d81-07dee089d728",
                    "messageStatus": "created",
                    "timestamps": {
                        "created": "2023-11-17T14:27:51.413Z"
                    },
                    "routingPlan": {
                        "id": "b838b13c-f98c-4def-93f0-515d4e4f4ee1",
                        "version": "ztoe2qRAM8M8vS0bqajhyEBcvXacrGPp"
                    },
                },
            },
        }
    )

    expected_request_body = notifier.message_body(routing_plan_id, message_data)

    with requests_mock.Mocker() as rm:
        adapter = rm.post(
            "http://example.com/comms/v1/messages", text=response_text
        )
        notifier.send_message(access_token, routing_plan_id, message_data)

        assert adapter.called
        assert adapter.call_count == 1
        assert adapter.last_request.json() == expected_request_body


def test_send_message_with_error_response(mocker, setup):
    access_token = "access_token"
    routing_plan = "breast-screening-pilot"
    routing_plan_id = routing_plans.get_id(routing_plan)
    message_data = {
        "routing_plan": routing_plan,
        "nhs_number": "0000000000",
        "date_of_birth": "1981-10-07",
        "appointment_time": "10:00",
        "appointment_date": "2021-12-01",
        "appointment_location": "Breast Screening Clinic, 123 High Street, London",
        "correlation_id": "da0b1495-c7cb-468c-9d81-07dee089d728",
        "contact_telephone_number": "012345678",
    }

    response_text = json.dumps(
        {
            "errors": [
                {
                    "status": "401",
                    "title": "Access Denied",
                    "detail": "Access token missing",
                },
            ],
        },
    )

    error_logging_spy = mocker.spy(logging, "error")

    with requests_mock.Mocker() as rm:
        adapter = rm.post(
            "http://example.com/comms/v1/messages", status_code=401, text=response_text
        )
        result = notifier.send_message(access_token, routing_plan_id, message_data)

        assert adapter.called
        assert adapter.call_count == 1
        assert result == response_text
        error_logging_spy.assert_called_once_with(response_text)


def test_message_body():
    routing_plan_id = str(uuid.uuid4())

    data = {
        "nhs_number": "0000000000",
        "date_of_birth": "1990-01-02",
        "appointment_time": "10:00",
        "appointment_date": "2021-12-01",
        "appointment_location": "Breast Screening Clinic, 123 High Street, London",
        "correlation_id": "da0b1495-c7cb-468c-9d81-07dee089d728",
        "contact_telephone_number": "012345678",
    }

    actual = notifier.message_body(routing_plan_id, data)

    expected = {
        "data": {
            "type": "Message",
            "attributes": {
                "messageReference": notifier.message_reference(data),
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
