import azure.functions as func
import dotenv
import function_app
import hashlib
import hmac
import json
import os
import psycopg2
import pytest

ENV_FILE = os.getenv("ENV_FILE", ".env.test")


@pytest.fixture()
def setup(mocker):
    dotenv.load_dotenv(dotenv_path=ENV_FILE)


@pytest.fixture
def callback_request_body():
    return {
        "data": [
            {
                "type": "ChannelStatus",
                "attributes": {
                    "messageId": "2WL3qFTEFM0qMY8xjRbt1LIKCzM",
                    "messageReference": "1642109b-69eb-447f-8f97-ab70a74f5db4",
                    "cascadeType": "primary",
                    "cascadeOrder": 1,
                    "channel": "nhsapp",
                    "channelStatus": "delivered",
                    "channelStatusDescription": " ",
                    "supplierStatus": "delivered",
                    "timestamp": "2023-11-17T14:27:51.413Z",
                    "retryCount": 1
                },
                "links": {
                    "message": "https://api.service.nhs.uk/comms/v1/messages/2WL3qFTEFM0qMY8xjRbt1LIKCzM"
                },
                "meta": {
                    "idempotencyKey": "2515ae6b3a08339fba3534f3b17cd57cd573c57d25b25b9aae08e42dc9f0a445" #gitleaks:allow
                }
            }
        ]
    }


def assert_channel_status_record_created():
    connection = psycopg2.connect(
        dbname=os.environ["DATABASE_NAME"],
        user=os.environ["DATABASE_USER"],
        host=os.environ["DATABASE_HOST"],
        password=os.environ["DATABASE_PASSWORD"]
    )
    with connection as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT details, message_id, status FROM channel_statuses ORDER BY created_at")
            records = cur.fetchall()

            assert len(records) == 1

            details, message_id, status = records[0]
            attributes = details["attributes"]

            assert message_id == "2WL3qFTEFM0qMY8xjRbt1LIKCzM"
            assert status == "delivered"
            assert attributes["messageReference"] == "1642109b-69eb-447f-8f97-ab70a74f5db4"
            assert attributes["cascadeType"] == "primary"
            assert attributes["channel"] == "nhsapp"
            assert status == "delivered"


def test_notify_callback_to_channel_status_saved(monkeypatch, callback_request_body):
    """Test that a callback request creates database records."""
    monkeypatch.setenv('APPLICATION_ID', 'application_id')
    monkeypatch.setenv('NOTIFY_API_KEY', 'api_key')
    req_body = json.dumps(callback_request_body)
    signature = hmac.new(
        bytes('application_id.api_key', 'ASCII'),
        msg=bytes(req_body, 'ASCII'),
        digestmod=hashlib.sha256
    ).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "x-api-key": "api_key",
        "x-hmac-sha256-signature": signature,
    }
    req = func.HttpRequest(
        method="POST",
        headers=headers,
        body=bytes(req_body, "utf-8"),
        url="/api/notify/message/send",
        route_params={"notification_type": "message"},
    )

    func_call = function_app.main.build().get_user_function()
    assert 200 == func_call(req).status_code
    assert_channel_status_record_created()
