from flask import Flask, request
import json
import uuid
app = Flask(__name__)


@app.route('/comms/v1/message-batches', methods=['POST'])
def message_batches():
    json_data = request.json or {
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
                "messages": messages_with_ids(json_data["data"]["attributes"]["messages"])
            }
        }
    }), 201


def messages_with_ids(messages: list[dict]) -> list[dict]:
    for message in messages:
        message["id"] = uid27() if not message.get("id") else message["id"]

    return messages


def uid27() -> str:
    return uuid.uuid4().hex[0:27]


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
