from unittest.mock import MagicMock
import azure.functions as func
from function_app import main, process_file_upload
import json


def test_function_app_calls_flask_app():
    """Test that the function calls the flask app."""
    req = func.HttpRequest(
        method="GET",
        body=b"",
        url="/api/status/health-check",
    )
    mock_context = MagicMock(
        function_directory=".",
        invocation_id="123",
        function_name="Notify"
    )

    func_call = main.build().get_user_function()
    resp = func_call(req, mock_context)

    assert resp.status_code == 200
    assert json.loads(resp.get_body()) == {"status": "healthy"}


def test_function_app_blob_trigger(mocker, csv_data, expected_message_batch_body):
    """Test that the function calls the blob trigger."""
    mock = mocker.patch(
        "app.services.message_batch_dispatcher.dispatch",
        return_value=(201, {"status": "OK"})
    )

    input_stream = func.blob.InputStream(
        data=bytes("\n".join(csv_data), "utf-8"),
        name="file-upload-data/HWA NHS App Pilot 002 SPRPT.csv",
    )

    func_call = process_file_upload.build().get_user_function()
    func_call(input_stream)

    mock.assert_called_once()
    mock.assert_called_with(expected_message_batch_body)
