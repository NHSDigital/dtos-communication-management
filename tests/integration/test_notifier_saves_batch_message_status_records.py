import datastore
import dotenv
import notifier
import os
import requests_mock
import uuid
import uuid_generator

dotenv.load_dotenv(".env.test")


def test_notifier_saves_batch_message_records(mocker):
    """Test database record is saved with correct data"""
    batch_id = str(uuid.uuid4())
    routing_plan_id = str(uuid.uuid4())
    message_reference = "da0b1495-c7cb-468c-9d81-07dee089d728"
    mocker.patch("uuid_generator.uuid4_str", return_value=message_reference)
    message_data = {
        "nhs_number": "0000000000",
        "date_of_birth": "1981-10-07",
        "appointment_time": "10:00",
        "appointment_date": "2021-12-01",
        "appointment_location": "Breast Screening Clinic, 123 High Street, London",
        "correlation_id": "da0b1495-c7cb-468c-9d81-07dee089d728",
        "contact_telephone_number": "012345678",
    }
    response_json = {"data": {"id": "2WL3qFTEFM0qMY8xjRbt1LIKCzM"}}

    with requests_mock.Mocker() as rm:
        rm.post(
            f"{os.getenv('NOTIFY_API_URL')}/comms/v1/messages",
            status_code=201,
            json=response_json,
        )

        notifier.send_message("access_token", routing_plan_id, message_data, batch_id)

    with datastore.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT batch_id, details, message_reference, nhs_number, status FROM batch_messages")
            records = cur.fetchall()
            assert len(records) == 2

            assert records[0] == (
                batch_id,
                message_data,
                message_reference,
                message_data["nhs_number"],
                "not_sent",
            )

            assert records[1] == (
                batch_id,
                response_json,
                message_reference,
                message_data["nhs_number"],
                "sent",
            )
