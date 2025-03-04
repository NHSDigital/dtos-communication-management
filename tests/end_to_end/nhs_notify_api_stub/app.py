from flask import Flask, request
import asyncio
import dotenv
import json
import os
import requests
import time
import utils.hmac_signature as hmac_signature
import uuid

app = Flask(__name__)

dotenv.load_dotenv()


@app.route('/comms/v1/message-batches', methods=['POST'])
def message_batches():
    json_data = request.json or default_response_data()

    messages = messages_with_ids(json_data["data"]["attributes"]["messages"])
    queue_status_callbacks(messages)

    return json.dumps({
        "data": {
            "type": "MessageBatch",
            "id": json_data["data"].get("id") or "2ZljUiS8NjJNs95PqiYOO7gAfJb",
            "attributes": {
                "messageBatchReference": json_data["data"]["attributes"]["messageBatchReference"],
                "routingPlan": {
                    "id": "b838b13c-f98c-4def-93f0-515d4e4f4ee1",
                    "name": "Plan Abc",
                    "version": "ztoe2qRAM8M8vS0bqajhyEBcvXacrGPp",
                    "createdDate": "2023-11-17T14:27:51.413Z"
                },
                "messages": messages
            }
        }
    }), 201


def default_response_data():
    return {
        "data": {
            "id": "2ZljUiS8NjJNs95PqiYOO7gAfJb",
            "attributes": {
                "messageBatchReference": "da0b1495-c7cb-468c-9d81-07dee089d728",
                "messages": [
                    {
                        "messageReference": "703b8008-545d-4a04-bb90-1f2946ce1575",
                        "id": "2WL3qFTEFM0qMY8xjRbt1LIKCzM"
                    }
                ]
            }
        }
    }


def queue_status_callbacks(messages):
    for message in messages:
        asyncio.run(send_status_callbacks(message))


async def send_status_callbacks(message):
    time.sleep(1)

    post_callback(channel_status(message, status="sending", supplier_status="received"))
    post_callback(channel_status(message, supplier_status="notified"))
    post_callback(channel_status(message, supplier_status="read"))
    post_callback(message_status(message))


def post_callback(post_body):
    client_endpoint = f"{os.getenv('NOTIFY_FUNCTION_BASE_URL')}/status/create"
    signature_secret = f"{os.getenv('APPLICATION_ID')}.{os.getenv('NOTIFY_API_KEY')}"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": os.getenv("NOTIFY_API_KEY"),
        "x-hmac-sha256-signature": hmac_signature.create_digest(signature_secret, json.dumps(post_body, sort_keys=True))
    }
    requests.post(client_endpoint, headers=headers, json=post_body)


def channel_status(message, status="delivered", supplier_status="read"):
    return {
        "data": [
            {
                "type": "ChannelStatus",
                "attributes": {
                    "messageId": message["id"],
                    "messageReference": message["messageReference"],
                    "cascadeType": "primary",
                    "cascadeOrder": 1,
                    "channel": "nhsapp",
                    "channelStatus": status,
                    "channelStatusDescription": " ",
                    "supplierStatus": supplier_status,
                    "timestamp": "2023-11-17T14:27:51.413Z",
                    "retryCount": 1
                },
                "links": {
                    "message": f"http://nhs-notify-api-stub/comms/v1/messages/{message['id']}"
                },
                "meta": {
                    "idempotencyKey": uid(64) #gitleaks:allow
                }
            }
        ]
    }


def message_status(message, message_status="sending", channel_status="delivered"):
    return {
        "data": [
            {
                "type": "MessageStatus",
                "attributes": {
                    "messageId": message["id"],
                    "messageReference": message["messageReference"],
                    "messageStatus": message_status,
                    "messageStatusDescription": " ",
                    "channels": [
                        {
                            "type": "email",
                            "channelStatus": channel_status
                        }
                    ],
                    "timestamp": "2023-11-17T14:27:51.413Z",
                    "routingPlan": {
                        "id": "b838b13c-f98c-4def-93f0-515d4e4f4ee1",
                        "name": "Plan Abc",
                        "version": "ztoe2qRAM8M8vS0bqajhyEBcvXacrGPp",
                        "createdDate": "2023-11-17T14:27:51.413Z"
                    }
                },
                "links": {
                    "message": f"http://nhs-notify-api-stub/comms/v1/messages/{message['id']}"
                },
                "meta": {
                    "idempotencyKey": uid(64) #gitleaks:allow
                }
            }
        ]
    }


def messages_with_ids(messages: list[dict]) -> list[dict]:
    for message in messages:
        message["id"] = uid(27) if not message.get("id") else message["id"]

    return messages


def uid(n) -> str:
    return uuid.uuid4().hex[0:n]


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
