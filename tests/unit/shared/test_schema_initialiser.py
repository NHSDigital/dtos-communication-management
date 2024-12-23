import os
import pytest
import schema_initialiser


@pytest.fixture
def mock_connection(mocker):
    return mocker.patch("datastore.connection")


@pytest.fixture()
def mock_cursor(mock_connection):
    return mock_connection().cursor().__enter__()


@pytest.fixture()
def schema_file_path() -> str:
    return f"{os.path.dirname(__file__)}/../../../database/schema.sql"


def test_schema_is_initialised(monkeypatch, mock_connection, mock_cursor, schema_file_path):
    """Test that the schema is initialised."""
    monkeypatch.setenv("SCHEMA_INITIALISED", "")
    monkeypatch.setattr("schema_initialiser.SCHEMA_FILE_PATH", schema_file_path)
    mock_cursor.fetchone.return_value = (None, None)
    schema_file_contents = open(schema_file_path, "r").read()

    schema_initialiser.check_and_initialise_schema(mock_connection())

    assert os.getenv("SCHEMA_INITIALISED") == "true"
    assert mock_cursor.execute.call_count == 2
    mock_cursor.execute.assert_any_call(schema_initialiser.SCHEMA_CHECK)
    mock_cursor.fetchone.assert_called_once()
    mock_cursor.execute.assert_any_call(schema_file_contents)


def test_schema_is_only_initialised_once(monkeypatch, mock_connection, mock_cursor, schema_file_path):
    """Test that the schema is only initialised once."""
    monkeypatch.setenv("SCHEMA_INITIALISED", "")
    monkeypatch.setattr("schema_initialiser.SCHEMA_FILE_PATH", schema_file_path)
    mock_cursor.fetchone.return_value = (None, None)

    schema_initialiser.check_and_initialise_schema(mock_connection())
    assert os.getenv("SCHEMA_INITIALISED") == "true"

    # Reset the call count on the execute mock
    mock_cursor.execute.reset_mock()

    schema_initialiser.check_and_initialise_schema(mock_connection())
    assert mock_cursor.execute.call_count == 0


def test_schema_is_not_initialised_when_already_initialised(monkeypatch, mock_connection, mock_cursor):
    """Test that the schema is not reinitialised when already initialised."""
    # Mock conditions for schema having been intialised
    # but the current process running in a different environment
    monkeypatch.setenv("SCHEMA_INITIALISED", "")
    mock_cursor.fetchone.return_value = ('1', None)

    schema_initialiser.check_and_initialise_schema(mock_connection())
    assert mock_cursor.execute.call_count == 1
    mock_cursor.execute.assert_called_once_with(schema_initialiser.SCHEMA_CHECK)
