import azure.functions as func
import function_app
import json


def test_main_calls_notifier_with_correct_data(mocker):
    """Test that the main function calls the notifier with the correct data."""
    send_messages_mock = mocker.patch("notifier.send_messages")

    input_data = {
        "routing_plan": "breast_screening_first_appointment",
        "recipients": [
            {"nhs_number": "0000000000"},
            {"nhs_number": "0000000001"},
        ],
    }

    req = func.HttpRequest(
        method="POST",
        body=json.dumps(input_data).encode("utf-8"),
        url="/api/notify/message/send",
        route_params={"notification_type": "message"},
    )

    func_call = function_app.main.build().get_user_function()
    func_call(req)

    send_messages_mock.assert_called_once_with(input_data)
