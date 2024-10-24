import csv
import logging
import os
import requests
import dateutil.parser
import uuid

FIELDNAMES = ("nhs_number", "date_of_birth", "appointment_date", "appointment_time", "appointment_location", "appointment_type")
HEADERS = {
    "Content-type": "application/json",
    "Accept": "application/json",
}


def process_data(raw_data) -> str:
    data = valid_csv_data(raw_data)
    if not data:
        logging.error("No valid data found")
        return
    post_body = {"routing_plan": "breast-screening-pilot", "recipients": data}
    response = requests.post(notify_function_url(), json=post_body, headers=HEADERS)

    if response:
        logging.info(response.text)
    else:
        logging.error(response.text)

    return response.text


def valid_csv_data(raw_data) -> list:
    data = []
    try:
        reader = csv.DictReader(raw_data, FIELDNAMES)
        for row in reader:
            if valid_row(row):
                row["correlation_id"] = str(uuid.uuid4())
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
        row["appointment_location"] and
        row["appointment_type"]
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


def notify_function_url():
    return os.environ["NOTIFY_FUNCTION_URL"]
