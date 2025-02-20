from flask import Flask
import json
app = Flask(__name__)


@app.route('/comms/v1/message-batches', methods=['POST'])
def message_batches():
    return json.dumps({
        "data": {
            "type": "MessageBatch",
            "id": "2ZljUiS8NjJNs95PqiYOO7gAfJb",
            "attributes": {
                "messageBatchReference": "da0b1495-c7cb-468c-9d81-07dee089d728",
                "routingPlan": {
                    "id": "b838b13c-f98c-4def-93f0-515d4e4f4ee1",
                    "name": "Plan Abc",
                    "version": "ztoe2qRAM8M8vS0bqajhyEBcvXacrGPp",
                    "createdDate": "2023-11-17T14:27:51.413Z"
                },
                "messages": [
                    {
                        "messageReference": "703b8008-545d-4a04-bb90-1f2946ce1575",
                        "id": "2WL3qFTEFM0qMY8xjRbt1LIKCzM"
                    }
                ]
            }
        }
    }), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
