import azure.functions as func
import function_app
import json


def test_main(mocker):
    mock = mocker.patch("logging.info")
    data = {
        "data": [
            {
                "type": "MessageStatus",
                "attributes": {
                    "messageId": "2WL3qFTEFM0qMY8xjRbt1LIKCzM",
                    "messageReference": "1642109b-69eb-447f-8f97-ab70a74f5db4",
                    "messageStatus": "sending",
                    "messageStatusDescription": " ",
                    "channels": [
                        {
                            "type": "email",
                            "channelStatus": "delivered"
                        }
                    ],
                    "timestamp": "2023-11-17T14:27:51.413Z",
                    "routingPlan": {
                        "id": "b838b13c-f98c-4def-93f0-515d4e4f4ee1",
                        "version": "ztoe2qRAM8M8vS0bqajhyEBcvXacrGPp"
                    }
                }
            }
        ]
    }
    req = func.HttpRequest(
        method="POST",
        body=bytes(json.dumps(data).encode("utf-8")),
        url="/api/status/callback",
    )

    func_call = function_app.main.build().get_user_function()
    func_call(req)

    mock.assert_called_once()
    mock.assert_called_with(data)
