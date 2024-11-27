import csv
import dateutil.parser
import logging
import os
import pilot_bso_details
import requests
import uuid

FIELDNAMES = ("nhs_number", "date_of_birth", "appointment_date", "appointment_time", "appointment_location")
HEADERS = {
    "Content-type": "application/json",
    "Accept": "application/json",
}


def process_data(filename, raw_data) -> str:
    bso_code = pilot_bso_details.code_from_filename(filename)
    data = valid_csv_data(bso_code, raw_data)

    if not data:
        logging.error("No valid data found")
        return
    response = requests.post(notify_function_url(), json=post_body(data), headers=HEADERS)

    if response:
        logging.info(response.text)
    else:
        logging.error(response.text)

    return response.text


def post_body(data: dict) -> dict:
    return {
        "routing_plan": "breast-screening-pilot",
        "recipients": data,
    }


def valid_csv_data(bso_code: str, raw_data: dict) -> list:
    contact_telephone_number = pilot_bso_details.contact_telephone_number(bso_code)
    data = []
    try:
        reader = csv.DictReader(raw_data, FIELDNAMES)
        for row in reader:
            if valid_row(row):
                row["correlation_id"] = str(uuid.uuid4())
                row["contact_telephone_number"] = contact_telephone_number
                data.append(row)
    except csv.Error:
        logging.error("Invalid CSV data")
        return []
    return data


def valid_row(row) -> bool:
    return (
        valid_nhs_number(row["nhs_number"]) and
        valid_date_or_time(row["date_of_birth"]) and
        valid_date_or_time(row["appointment_date"]) and
        valid_date_or_time(row["appointment_time"]) and
        row["appointment_location"]
    )


def valid_nhs_number(nhs_number: str) -> bool:
    if not nhs_number:
        return False
    return len(nhs_number) == 10 and nhs_number.isdigit()


def valid_date_or_time(val: str) -> bool:
    if not val:
        return False
    try:
        dateutil.parser.parse(val)
        return True
    except ValueError:
        return False


def notify_function_url() -> str:
    return os.getenv("NOTIFY_FUNCTION_URL")
