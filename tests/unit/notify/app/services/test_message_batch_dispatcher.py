import app.models as models
import app.services.message_batch_dispatcher as message_batch_dispatcher
import pytest
import requests_mock


@pytest.fixture
def setup(monkeypatch):
    monkeypatch.setenv("NOTIFY_API_URL", "http://example.com")


def test_message_batch_dispatcher_succeeds(mocker, setup, consumer, message_batch_post_body, message_batch_post_response):
    """When dispatch is called with a valid body, a success response should be returned."""
    mock_recorder = mocker.patch(
        "app.services.message_batch_recorder.save_batch",
        return_value=(True, "Batch id: 1 saved successfully")
    )
    mock_access_token = mocker.patch("app.utils.access_token.get_token", return_value="token")

    with requests_mock.Mocker() as rm:
        adapter = rm.post(
            "http://example.com/comms/v1/message-batches",
            status_code=201,
            json=message_batch_post_response
        )

        status_code, response = message_batch_dispatcher.dispatch(message_batch_post_body, consumer.id, None)

        assert adapter.call_count == 1
        assert status_code == 201
        assert response == message_batch_post_response

    assert mock_access_token.call_count == 1
    assert mock_recorder.call_count == 1
    mock_recorder.assert_called_with(
        message_batch_post_body,
        message_batch_post_response,
        models.MessageBatchStatuses.SENT,
        consumer.id
    )

def test_message_batch_dispatcher_includes_bearer_token(mocker, setup, consumer, message_batch_post_body, message_batch_post_response):
    """When dispatch is called with a bearer token, the request headers should include it."""
    mock_recorder = mocker.patch(
        "app.services.message_batch_recorder.save_batch",
        return_value=(True, "Batch id: 1 saved successfully")
    )

    with requests_mock.Mocker() as rm:
        adapter = rm.post(
            "http://example.com/comms/v1/message-batches",
            status_code=201,
            json=message_batch_post_response
        )

        status_code, _ = message_batch_dispatcher.dispatch(message_batch_post_body, consumer.id, "client_bearer_token", )

        assert status_code == 201
        assert adapter.last_request.headers["Authorization"] == "Bearer client_bearer_token"


def test_message_batch_dispatcher_fails_with_invalid_body(mocker, setup, consumer, message_batch_post_body):
    """When dispatch is called with an invalid body, a failed response should be returned."""
    mock_recorder = mocker.patch(
        "app.services.message_batch_recorder.save_batch",
        return_value=(True, "Batch id: 1 saved successfully")
    )
    mock_access_token = mocker.patch("app.utils.access_token.get_token", return_value="token")

    with requests_mock.Mocker() as rm:
        adapter = rm.post(
            "http://example.com/comms/v1/message-batches",
            status_code=400,
            json={"error": "Bad request"}
        )

        status_code, response = message_batch_dispatcher.dispatch(message_batch_post_body, consumer.id, None)

        assert adapter.call_count == 1
        assert status_code == 400
        assert response == {"error": "Bad request"}

    assert mock_access_token.call_count == 1
    assert mock_recorder.call_count == 1
    mock_recorder.assert_called_with(
        message_batch_post_body,
        {"error": "Bad request"},
        models.MessageBatchStatuses.FAILED,
        consumer.id
    )
