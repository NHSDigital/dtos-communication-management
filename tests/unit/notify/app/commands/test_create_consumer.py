from app import create_app
from app.models import Consumer
from sqlalchemy.orm import Session
from sqlalchemy import exists
import app.utils.database as database
import pytest


@pytest.fixture
def runner():
    app = create_app()
    yield app.test_cli_runner()


def test_creates_consumer_with_new_key(runner, teardown_consumer):
    key = "some-consumer"
    assert Session(database.engine()).query(exists().where(Consumer.key==key)).scalar() == False
    result = runner.invoke(args=["create-consumer", key])
    assert Session(database.engine()).query(exists().where(Consumer.key==key)).scalar() == True
    assert f"Consumer with key '{key}' created" in result.output


def test_errors_with_existing_key(runner, consumer):
    key = "some-consumer"
    result = runner.invoke(args=["create-consumer", key])
    assert f"Consumer with key '{key}' already exists" in result.output


def test_errors_with_db_error(runner, teardown_consumer, monkeypatch):
    monkeypatch.setenv("DATABASE_USER", "wrong_user")
    key = "some-consumer"
    result = runner.invoke(args=["create-consumer", key])
    assert "FATAL:  role \"wrong_user\" does not exist\n\n" in result.output
