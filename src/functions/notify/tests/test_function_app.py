from function_app import main
import azure.functions as func
import json


class TestFunction:
    def test_main(self, mocker):
        mock = mocker.patch("function_app.send_messages")
        data = {
            "routing_plan": "breast-screening-pilot",
            "recipients": [
                {
                    "nhs_number": "0000000000",
                },
                {
                    "nhs_number": "0000000001",
                }
            ]

        }
        req = func.HttpRequest(
            method="POST",
            body=bytes(json.dumps(data).encode("utf-8")),
            url="/api/notify/message/send",
            route_params={"notification_type": "message"},
        )

        func_call = main.build().get_user_function()
        func_call(req)

        mock.assert_called_once()
        mock.assert_called_with(data)
