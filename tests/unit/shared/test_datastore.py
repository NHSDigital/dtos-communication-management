import datastore
import pytest


@pytest.fixture
def mock_connection(mocker):
    return mocker.patch("datastore.connection")


@pytest.fixture
def mock_cursor(mock_connection):
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
def status_data(autouse=True):
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


def test_create_channel_status_record(mock_cursor):
    """Test the SQL execution of channel status record creation."""
    datastore.create_status_record(status_data, True)

    mock_cursor.execute.assert_called_with(
        datastore.INSERT_STATUS.format(status_table="channel_statuses"),
        status_data,
    )
    mock_cursor.fetchone.assert_called_once()


def test_create_channel_status_record_with_error(mock_cursor):
    """Test the SQL execution of channel status record creation with an error."""
    mock_cursor.execute.side_effect = Exception("Test error")

    with pytest.raises(Exception):
        assert datastore.create_status_record(status_data, True) is False

    mock_cursor.execute.assert_called_with(
        datastore.INSERT_STATUS.format(status_table="channel_statuses"),
        status_data,
    )
    mock_cursor.fetchone.assert_not_called()


def test_create_message_status_record(mock_cursor):
    """Test the SQL execution of message status record creation."""
    datastore.create_status_record(status_data)

    mock_cursor.execute.assert_called_with(
        datastore.INSERT_STATUS.format(status_table="message_statuses"),
        status_data,
    )
    mock_cursor.fetchone.assert_called_once()


def test_create_message_status_record_with_error(mock_cursor):
    """Test the SQL execution of message status record creation with an error."""
    mock_cursor.execute.side_effect = Exception("Test error")

    with pytest.raises(Exception):
        assert datastore.create_status_record(status_data) is False

    mock_cursor.execute.assert_called_with(
        datastore.INSERT_STATUS.format(status_table="message_statuses"),
        status_data,
    )
    mock_cursor.fetchone.assert_not_called()
