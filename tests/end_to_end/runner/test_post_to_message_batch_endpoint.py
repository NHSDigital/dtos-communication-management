import app.utils.database as database
import app.models as models
import app.utils.hmac_signature as hmac_signature
import dotenv
import json
import os
import requests
from sqlalchemy.sql.expression import select
from sqlalchemy.orm import Session

ENV_FILE = os.getenv("ENV_FILE", ".env.test")
dotenv.load_dotenv(dotenv_path=ENV_FILE)


def post_to_message_batch_endpoint(message_batch_post_body):
    signature = hmac_signature.create_digest(
        f"{os.getenv('CLIENT_APPLICATION_ID')}.{os.getenv('CLIENT_API_KEY')}",
        json.dumps(message_batch_post_body, sort_keys=True)
    )

    headers = {
        "Content-Type": "application/json",
        "x-api-key": os.getenv('CLIENT_API_KEY'),
        "x-hmac-sha256-signature": signature,
    }

    return requests.post(
        os.getenv('NOTIFY_FUNCTION_URL'),
        headers=headers,
        json=message_batch_post_body
    )


def test_post_to_message_batch_endpoint(message_batch_post_body):
    response = post_to_message_batch_endpoint(message_batch_post_body)
    response_json = response.json()

    assert response.status_code == 201
    assert response_json["status"] == "success"
    assert response_json["response"]["data"]["id"] == "2ZljUiS8NjJNs95PqiYOO7gAfJb"


def test_post_to_message_batch_endpoint_saves_to_database(message_batch_post_body, message_batch_post_response):
    response = post_to_message_batch_endpoint(message_batch_post_body)

    assert response.status_code == 201

    with Session(database.engine()) as session:
        message_batch = session.scalars(select(models.MessageBatch)).all()[0]
        messages = session.scalars(select(models.Message)).all()

        assert message_batch.id == messages[0].batch_id
        assert message_batch.batch_id == message_batch_post_response["data"]["id"]
        assert str(message_batch.batch_reference) == message_batch_post_response["data"]["attributes"]["messageBatchReference"]
        assert message_batch.details == message_batch_post_body
        assert message_batch.status == models.MessageBatchStatuses.SENT

        assert len(messages) == 1
        assert messages[0].batch_id == message_batch.id
        assert str(messages[0].message_reference) == message_batch_post_response["data"]["attributes"]["messages"][0]["messageReference"]
