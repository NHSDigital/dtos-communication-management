import datastore
import pytest


@pytest.fixture
def mock_connection(mocker):
    return mocker.patch("datastore.connection")


@pytest.fixture
def mock_cursor(mocker, mock_connection):
    return mock_connection().__enter__().cursor().__enter__()


@pytest.fixture
def batch_message_data(autouse=True):
    return {
        "batch_id": "0b3b3b3b-3b3b-3b3b-3b3b-3b3b3b3b3b3b",
        "details": "Test details",
        "message_reference": "0b3b3b3b-3b3b-3b-3b3b-3b3b3b3b3b3b",
        "nhs_number": "1234567890",
        "recipient_id": "e3e7b3b3-3b3b-3b-3b3b-3b3b3b3b3b3b",
        "status": "test_status",
    }


@pytest.fixture
def message_status_data(autouse=True):
    return {
        "idempotency_key": "0b3b3b3b-3b3b-3b3b-3b3b-3b3b3b3b3b3b",
        "message_id": "0x0x0x0xabx0x0",
        "message_reference": "0b3b3b3b-3b3b-3b3b-3b3b-3b3b3b3b3b3b",
        "details": "Test details",
        "status": "test_status",
    }


def test_create_batch_message_record(mock_cursor):
    """Test the SQL execution of batch message record creation."""
    datastore.create_batch_message_record(batch_message_data)

    mock_cursor.execute.assert_called_with(datastore.INSERT_BATCH_MESSAGE, batch_message_data)
    mock_cursor.fetchone.assert_called_once()


def test_create_batch_message_record_with_error(mock_cursor):
    """Test the SQL execution of batch message record creation with an error."""
    mock_cursor.execute.side_effect = Exception("Test error")

    with pytest.raises(Exception):
        assert datastore.create_batch_message_record(batch_message_data) is False

    mock_cursor.execute.assert_called_with(datastore.INSERT_BATCH_MESSAGE, batch_message_data)
    mock_cursor.fetchone.assert_not_called()


def test_create_message_status_record(mock_cursor):
    """Test the SQL execution of message status record creation."""
    datastore.create_message_status_record(message_status_data)

    mock_cursor.execute.assert_called_with(datastore.INSERT_MESSAGE_STATUS, message_status_data)
    mock_cursor.fetchone.assert_called_once()


def test_create_message_status_record_with_error(mock_cursor):
    """Test the SQL execution of message status record creation with an error."""
    mock_cursor.execute.side_effect = Exception("Test error")

    with pytest.raises(Exception):
        assert datastore.create_message_status_record(message_status_data) is False

    mock_cursor.execute.assert_called_with(datastore.INSERT_MESSAGE_STATUS, message_status_data)
    mock_cursor.fetchone.assert_not_called()


def test_schema_is_initialised_once(monkeypatch, mock_connection):
    """Test that the schema is initialised."""
    schema_file_path = f"{datastore.os.path.dirname(__file__)}/../../../database/schema.sql"
    monkeypatch.setenv("SCHEMA_INITIALISED", "")
    monkeypatch.setattr("datastore.SCHEMA_FILE_PATH", schema_file_path)
    mock_connection().cursor().__enter__().fetchone.return_value = (None, None)

    schema_file_contents = open(schema_file_path).read()

    datastore.check_and_initialise_schema(mock_connection())
    datastore.check_and_initialise_schema(mock_connection())

    assert mock_connection().cursor().__enter__().execute.call_count == 2
    mock_connection().cursor().__enter__().execute.assert_any_call(datastore.BATCH_MESSAGES_EXISTS)
    mock_connection().cursor().__enter__().fetchone.assert_called_once()
    mock_connection().cursor().__enter__().execute.assert_any_call(schema_file_contents)
