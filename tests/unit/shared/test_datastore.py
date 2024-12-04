import datastore
import pytest
import time


@pytest.fixture
def mock_cursor(mocker):
    mock_connection = mocker.patch("datastore.connection")
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


def test_fetch_database_password_from_env(monkeypatch):
    """Test the fetching of the database password from the environment."""
    monkeypatch.setenv("DATABASE_PASSWORD", "test_password")

    assert datastore.fetch_database_password() == "test_password"


def test_fetch_database_password_from_credential(monkeypatch, mocker):
    """Test the fetching of the database password from the environment."""
    mock_token = mocker.MagicMock()
    mock_token.token = "token_password"
    mock_credential = mocker.MagicMock()
    mock_credential.get_token.return_value = mock_token
    mocker.patch("datastore.DefaultAzureCredential", return_value=mock_credential)

    assert datastore.fetch_database_password() == "token_password"
