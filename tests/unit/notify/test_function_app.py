from unittest.mock import MagicMock
import azure.functions as func
from function_app import main, migrate_database
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


def test_function_app_migrates(mocker, monkeypatch):
    """Test that the function calls to migrate."""
    monkeypatch.setenv("DATABASE_PASSWORD", "password")
    mocked_migrate = mocker.patch(
        "function_app.alembic_migrate",
        return_value=("success")
    )
    mocked_migrate.start()

    req = func.HttpRequest(
        method="POST",
        body=json.dumps({}).encode(),
        headers={"x-migration-key": "password"},
        url="/api/migrate-database",
    )

    func_call = migrate_database.build().get_user_function()
    func_call(req)

    mocked_migrate.assert_called_once()
