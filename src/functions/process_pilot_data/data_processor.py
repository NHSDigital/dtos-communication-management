import csv
import logging
import os
import requests
import dateutil.parser


class DataProcessor:
    FIELDNAMES = ("nhs_number", "date_of_birth")
    HEADERS = {
        "Content-type": "application/json",
        "Accept": "application/json",
    }

    @classmethod
    def call(cls, raw_data):
        data = cls(raw_data).__valid_csv_data()
        if not data:
            logging.error("No valid data found")
            return
        post_body = {
            "routing_plan": "breast-screening-pilot",
            "data": data
        }
        response = requests.post(cls.url(), json=post_body, headers=cls.HEADERS)

        if response:
            logging.info(response.text)
        else:
            logging.error(response.text)

        return response.text

    @classmethod
    def url(cls):
        return cls.base_url() + "/api/batch-message/breast-screening-pilot"

    @classmethod
    def base_url(cls):
        return os.environ['BASE_URL']

    def __init__(self, raw_data):
        self.raw_data = raw_data

    def __valid_csv_data(self):
        data = []
        try:
            reader = csv.DictReader(self.raw_data, self.FIELDNAMES)
            for row in reader:
                logging.info(row)
                if self.__valid_row(row):
                    data.append(row)
        except csv.Error:
            logging.error("Invalid CSV data")
            return []
        return data

    def __valid_row(self, row):
        return self.__valid_nhs_number(row["nhs_number"]) and self.__valid_date_of_birth(row["date_of_birth"])

    def __valid_nhs_number(self, nhs_number):
        if not nhs_number:
            return False
        return len(nhs_number) == 10 and nhs_number.isdigit()

    def __valid_date_of_birth(self, date_of_birth):
        if not date_of_birth:
            return False
        try:
            dateutil.parser.parse(date_of_birth)
            return True
        except ValueError:
            return False
