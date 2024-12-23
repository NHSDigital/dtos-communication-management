import datastore
import dotenv
import status_recorder

dotenv.load_dotenv(".env.test")


def test_message_status_recorder_saves_message_statuses():
    """Test message status record is saved with correct data when multiple records are sent."""
    message_data = {
        "data": [
            {
                "attributes": {
                    "messageId": "2WL3qFTEFM0qMY8xjRbt1LIKCzM",
                    "messageReference": "ce845717-67bb-46d7-a33d-2a54db12aeaf",
                    "messageStatus": "sending",
                },
                "meta": {
                    "idempotencyKey": "4215af6b3a08339fba3534f3b17cf57cf573c55d25b25b9aae08e42dc9f0z886", #gitleaks:allow
                },
            },
            {
                "attributes": {
                    "messageId": "2WL3qFTEFM0qMY8xjRbt1LIKCzM",
                    "messageReference": "ce845717-67bb-46d7-a33d-2a54db12aeaf",
                    "messageStatus": "delivered",
                },
                "meta": {
                    "idempotencyKey": "2515ae6b3a08339fba3534f3b17cd57cd573c57d25b25b9aae08e42dc9f0a445", #gitleaks:allow
                },
            },
        ]
    }

    status_recorder.save_statuses(message_data)

    with datastore.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT idempotency_key, message_id, message_reference, status FROM message_statuses")
            records = cur.fetchall()
            assert len(records) == 2

            assert records[0] == (
                message_data["data"][0]["meta"]["idempotencyKey"],
                message_data["data"][0]["attributes"]["messageId"],
                message_data["data"][0]["attributes"]["messageReference"],
                message_data["data"][0]["attributes"]["messageStatus"],
            )

            assert records[1] == (
                message_data["data"][1]["meta"]["idempotencyKey"],
                message_data["data"][1]["attributes"]["messageId"],
                message_data["data"][1]["attributes"]["messageReference"],
                message_data["data"][1]["attributes"]["messageStatus"],
            )
