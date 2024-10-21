import csv
import logging
import os
import requests
import dateutil.parser

FIELDNAMES = ("nhs_number", "date_of_birth")
HEADERS = {
    "Content-type": "application/json",
    "Accept": "application/json",
}


def process_data(raw_data):
    data = valid_csv_data(raw_data)
    if not data:
        logging.error("No valid data found")
        return
    post_body = {
        "routing_plan": "breast-screening-pilot",
        "data": data
    }
    response = requests.post(url(), json=post_body, headers=HEADERS)

    if response:
        logging.info(response.text)
    else:
        logging.error(response.text)

    return response.text


def valid_csv_data(raw_data):
    data = []
    try:
        reader = csv.DictReader(raw_data, FIELDNAMES)
        for row in reader:
            if valid_row(row):
                data.append(row)
    except csv.Error:
        logging.error("Invalid CSV data")
        return []
    return data


def valid_row(row):
    return valid_nhs_number(row["nhs_number"]) and valid_date_of_birth(row["date_of_birth"])


def valid_nhs_number(nhs_number):
    if not nhs_number:
        return False
    return len(nhs_number) == 10 and nhs_number.isdigit()


def valid_date_of_birth(date_of_birth):
    if not date_of_birth:
        return False
    try:
        dateutil.parser.parse(date_of_birth)
        return True
    except ValueError:
        return False


def url():
    return base_url() + "/api/batch-message/breast-screening-pilot"


def base_url():
    return os.environ['BASE_URL']
