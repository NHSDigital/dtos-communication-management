from pact import Consumer, Provider, Term
from pact.matchers import get_generated_values
import notifier
import pytest
import requests


def create_message_client(uri, message):
    return requests.post(uri, headers=headers(), json=message).json()


@pytest.fixture
def create_message_pact():
    pact = Consumer("NotifyAzureFunction").has_pact_with(
            Provider("NHSNotify"),
            pact_dir="tests/pacts")
    pact.start_service()
    yield pact
    pact.stop_service()


def expected_create_message_response():
    return {
        "data": {
            "type": "Message",
            "id": Term(r"[0-9a-zA-Z]+", "2WL3qFTEFM0qMY8xjRbt1LIKCzM"),
            "attributes": {
                "messageReference": Term(r"[0-9a-zA-Z\-]{36}", "da0b1495-c7cb-468c-9d81-07dee089d728"),
                "messageStatus": "created",
                "timestamps": {
                    "created": Term(
                        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z",
                        "2023-11-17T14:27:51.413Z"
                    ),
                },
                "routingPlan": {
                    "id": Term(r"[0-9a-zA-Z\-]{36}", "b838b13c-f98c-4def-93f0-515d4e4f4ee1"),
                    "version": Term(r"[0-9a-zA-Z]+", "ztoe2qRAM8M8vS0bqajhyEBcvXacrGPp")
                }
            },
            "links": {
                "self": Term(
                    r"https://[a-z\.]*api\.service\.nhs\.uk/comms/v1/messages/[aA-zZ0-9]+",
                    "https://sandbox.api.service.nhs.uk/comms/v1/messages/2WL3qFTEFM0qMY8xjRbt1LIKCzM"
                )
            }
        }
    }


def headers():
    return notifier.headers("an_access_token", "e3e3b3b3-3b3b-3b3b-3b3b-3b3b3b3b3b3b")


def message_body() -> dict:
    return notifier.message_body("b838b13c-f98c-4def-93f0-515d4e4f4ee1", {
        "nhs_number": "9990548609",
        "date_of_birth": "1990-01-01",
        "appointment_time": "14:30",
        "appointment_date": "2023-11-17",
        "appointment_location": "The Hospital",
        "contact_telephone_number": "01234567890",
    })


def test_create_message_pact(create_message_pact):
    (
        create_message_pact.given("A message is created")
        .upon_receiving("A request to create a message")
        .with_request("post", "/comms/v1/messages", headers=headers(), body=message_body())
        .will_respond_with(201, body=expected_create_message_response())
    )

    with create_message_pact:
        result = create_message_client(create_message_pact.uri + "/comms/v1/messages", message_body())

    assert result == get_generated_values(expected_create_message_response())
