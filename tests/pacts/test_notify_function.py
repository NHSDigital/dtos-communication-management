from pact import Consumer, Provider
import data_processor
import pytest
import requests


def notify_client(uri, message):
    return requests.post(uri, headers=headers(), json=message).json()


@pytest.fixture
def notify_pact():
    pact = (
            Consumer("ProcessPilotDataFunction").has_pact_with(
                Provider("NotifyFunction"),
                pact_dir="tests/pacts")
            )
    pact.start_service()
    yield pact
    pact.stop_service()


def expected_notify_response():
    # TODO: Update this response once we have an implementation
    return {}


def headers():
    return data_processor.HEADERS


def body() -> dict:
    return data_processor.post_body(
        [
            {
                "nhs_number": "1234567890",
                "date_of_birth": "1990-01-01",
                "appointment_date": "2023-11-17",
                "appointment_time": "14:30",
                "appointment_location": "The Hospital",
            }
        ]
    )


def test_notify_create_message(notify_pact):
    expected_response = expected_notify_response()
    notify_body = body()
    (
        notify_pact.given("Recipient data is sent")
        .upon_receiving("A request to notify recipients")
        .with_request("post", "/api/notify/send", body=notify_body)
        .will_respond_with(201, body=expected_response)
    )

    with notify_pact:
        result = notify_client(notify_pact.uri + "/api/notify/send", notify_body)

    assert result == expected_response
