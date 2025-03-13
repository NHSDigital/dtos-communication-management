from app.utils.uuid_generator import reference_uuid
import app.validators.schema_validator as schema_validator
import csv
import logging
import file_processor.format_time as format_time
import file_processor.format_date as format_date
import file_processor.office_details as office_details
import re

FIELDNAMES = (
    "stage", # Not sent to Notify
    "nhs_number",
    "sx_code", # Not sent to Notify
    "full_name", # Not sent to Notify
    "date_of_birth",
    "office_code", # Not sent to Notify
    "appointment_date",
    "appointment_time",
    "appointment_location"
)


def message_batch_body(filename, raw_data) -> dict | None:
    contact_telephone_number = office_details.contact_telephone_number(filename)
    routing_plan_id = office_details.routing_plan_id(filename)
    message_batch_reference = reference_uuid(f"{routing_plan_id}.{filename}")

    messages_data = []
    try:
        reader = csv.DictReader(raw_data, FIELDNAMES)
        for row in reader:
            if valid_row(row):
                nhs_number = row["nhs_number"]
                appointment_date = format_date.to_human_readable_date(row["appointment_date"])
                appointment_time = format_time.to_human_readable_twelve_hours(row["appointment_time"])
                message_reference = reference_uuid(f"{nhs_number}.{appointment_date}.{appointment_time}")

                personalisation_data = personalisation(
                    appointment_date,
                    row["appointment_location"],
                    appointment_time,
                    contact_telephone_number,
                    nhs_number
                )
                messages_data.append(
                    message(
                        message_reference,
                        nhs_number,
                        personalisation_data
                    )
                )
            else:
                logging.info("Omitting invalid row: %s", row)

    except csv.Error:
        logging.error("Invalid CSV data")

    if messages_data:
        body = message_batch(routing_plan_id, message_batch_reference, messages_data)
        if schema_validator.validate_with_schema(body):
            return body

    return None


def valid_row(row) -> bool:
    return (
        valid_nhs_number(row["nhs_number"]) and
        valid_date_or_time(row["date_of_birth"]) and
        valid_date_or_time(row["appointment_date"]) and
        valid_date_or_time(row["appointment_time"]) and
        row["appointment_location"]
    )


def valid_nhs_number(nhs_number: str) -> bool:
    return bool(nhs_number) and len(nhs_number) == 10 and nhs_number.isdigit()


def valid_date_or_time(val: str) -> bool:
    if not val or not val.strip():
        return False

    date_or_time_pattern = r"^\d{2}[M:]\d{2}[M:](\d{4}|\d{2})$"

    return bool(re.match(date_or_time_pattern, val))


def message_batch(
        routing_plan_id: str,
        message_batch_reference: str,
        messages: list[dict]) -> dict:

    return {
        "data": {
            "type": "MessageBatch",
            "attributes": {
                "routingPlanId": routing_plan_id,
                "messageBatchReference": message_batch_reference,
                "messages": messages
            }
        }
    }


def message(
        message_reference: str,
        nhs_number: str,
        personalisation_data: dict) -> dict:

    return {
        "messageReference": message_reference,
        "recipient": {
            "nhsNumber": nhs_number,
        },
        "originator": {
            "odsCode": "T8T9T"
        },
        "personalisation": personalisation_data
    }


def personalisation(
        appointment_date: str,
        appointment_location: str,
        appointment_time: str,
        contact_telephone_number: str,
        nhs_number: str) -> dict:

    return {
        "appointment_date": appointment_date,
        "appointment_location": appointment_location,
        "appointment_time": appointment_time,
        "contact_telephone_number": contact_telephone_number,
        "tracking_id": nhs_number,
    }
