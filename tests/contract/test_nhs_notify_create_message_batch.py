from pact import Consumer, Provider, Term
from pact.matchers import get_generated_values
import app.services.message_batch_dispatcher as message_batch_dispatcher
import pytest
import requests


@pytest.fixture
def create_message_batch_pact():
    pact = Consumer("CommunicationManagementAPI").has_pact_with(
            Provider("NHSNotify"),
            pact_dir="tests/contract")
    pact.start_service()
    yield pact
    pact.stop_service()


def expected_create_message_batch_response():
    return {
        "data": {
            "type": "Message",
            "id": Term(r"[0-9a-zA-Z]+", "2WL3qFTEFM0qMY8xjRbt1LIKCzM"),
            "attributes": {
                "messageBatchReference": Term(r"[0-9a-zA-Z\-]{36}", "da0b1495-c7cb-468c-9d81-07dee089d728"),
                "routingPlan": {
                    "id": Term(r"[0-9a-zA-Z\-]{27}", "2HL3qFTEFM0qMY8xjRbt1LIKCzM"),
                    "name": Term(r"[0-9a-zA-Z\- ]+", "Test Routing Plan"),
                    "version": Term(r"[0-9a-zA-Z]+", "ztoe2qRAM8M8vS0bqajhyEBcvXacrGPp"),
                    "createdDate": Term(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z", "2023-11-17T14:30:00.000Z")
                }
            },
            "messages": [
                {
                    "id": Term(r"[0-9a-zA-Z\-]{27}", "2WL3qFTEFM0qMY8xjRbt1LIKCzM"),
                    "messageReference": Term(r"[0-9a-zA-Z\-]{36}", "da0b1495-c7cb-468c-9d81-07dee089d728"),
                }
            ]
        }
    }


def test_create_message_batch_pact(create_message_batch_pact, message_batch_post_body):
    endpoint = "/comms/v1/message-batches"
    uri = create_message_batch_pact.uri + endpoint
    headers = message_batch_dispatcher.headers("an_access_token")
    (
        create_message_batch_pact.given("A message batch is created")
        .upon_receiving("A request to create a message batch")
        .with_request("post", endpoint, headers=headers, body=message_batch_post_body)
        .will_respond_with(201, body=expected_create_message_batch_response())
    )

    with create_message_batch_pact:
        result = requests.post(uri, headers=headers, json=message_batch_post_body).json()

    assert result == get_generated_values(expected_create_message_batch_response())
