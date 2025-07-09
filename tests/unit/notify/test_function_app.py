from unittest.mock import MagicMock
import azure.functions as func
from function_app import main
import json


def test_function_app_calls_flask_app():
    """Test that the function calls the flask app."""
    req = func.HttpRequest(
        method="GET",
        body=b"",
        url="/api/healthcheck",
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
