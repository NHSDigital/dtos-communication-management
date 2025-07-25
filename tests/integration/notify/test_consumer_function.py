import azure.functions as func
import function_app
import json


def test_create_consumer_missing_key():
    """Test create_consumer function errors when no key supplied."""
    req = func.HttpRequest(
        method="POST",
        body=json.dumps({}).encode(),
        url="/api/consumer",
    )

    func_call = function_app.create_consumer.build().get_user_function()
    response = func_call(req)

    assert response.status_code == 400
    assert "Missing key field" in response.get_body().decode()


def test_create_consumer_errors(teardown_consumer, monkeypatch):
    """Test create_consumer returns error if problem with transaction."""
    monkeypatch.setenv("DATABASE_USER", "wrong_user")
    req = func.HttpRequest(
        method="POST",
        body=json.dumps({ 'key': 'some-consumer'}).encode(),
        url="/api/consumer",
    )

    func_call = function_app.create_consumer.build().get_user_function()
    response = func_call(req)

    assert response.status_code == 500
    assert "FATAL:  role \"wrong_user\" does not exist" in response.get_body().decode()


def test_create_consumer(teardown_consumer):
    """Test create_consumer successful with valid request."""
    req = func.HttpRequest(
        method="POST",
        body=json.dumps({ 'key': 'some-consumer'}).encode(),
        url="/api/consumer",
    )

    func_call = function_app.create_consumer.build().get_user_function()
    response = func_call(req)

    assert response.status_code == 201
    assert 'some-consumer' == json.loads(response.get_body()).get('key')
