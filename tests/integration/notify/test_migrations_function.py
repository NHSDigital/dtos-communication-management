import azure.functions as func
import function_app
import json


def test_migrate_database(monkeypatch):
    """Test migrate_database function calls alembic."""
    monkeypatch.setenv("DATABASE_PASSWORD", "password")

    req = func.HttpRequest(
        method="POST",
        body=json.dumps({}).encode(),
        headers={"x-migration-key": "password"},
        url="/api/migrate-database",
    )

    func_call = function_app.migrate_database.build().get_user_function()
    response = func_call(req)

    assert response.status_code == 200
    assert "Database migration complete: Current revision(s)" in response.get_body().decode()


def test_migrate_database_unauthorized(monkeypatch):
    """Test migrate_database function returns 401 if unauthorized."""
    monkeypatch.setenv("DATABASE_PASSWORD", "password")

    req = func.HttpRequest(
        method="POST",
        body=json.dumps({}).encode(),
        headers={"x-migration-key": "wrong_password"},
        url="/api/migrate-database",
    )

    func_call = function_app.migrate_database.build().get_user_function()
    response = func_call(req)

    assert response.status_code == 401
    assert response.get_body().decode() == "Unauthorized"
