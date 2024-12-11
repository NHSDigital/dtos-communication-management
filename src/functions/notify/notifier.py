import access_token
import batch_message_recorder
import json
import logging
import os
import requests
import routing_plans
import uuid_generator


def send_messages(data: dict) -> str:
    responses: list = []
    routing_plan_id: str = None
    batch_id = uuid_generator.reference_uuid(json.dumps(data))

    token: str = access_token.get_token()

    if "routing_plan" in data:
        routing_plan_id = routing_plans.get_id(data.pop("routing_plan"))

    if "recipients" in data:
        for message_data in data["recipients"]:
            if "routing_plan" in message_data:
                routing_plan_id = routing_plans.get_id(message_data.pop("routing_plan"))

            response: str = send_message(token, routing_plan_id, message_data, batch_id)
            responses.append(response)

    return "\n".join(responses)


def send_message(token, routing_plan_id, message_data, batch_id) -> str:
    message_reference: str = uuid_generator.uuid4_str()
    body: str = message_body(routing_plan_id, message_reference, message_data)
    correlation_id: str = message_data["correlation_id"]

    batch_message_recorder.save_status(
        batch_message_recorder.NOT_SENT, batch_id, message_reference, message_data)

    response = requests.post(url(), json=body, headers=headers(token, correlation_id))

    logging.info(f"Response from Notify API {url()}: {response.status_code}")
    batch_message_data = message_data.copy()

    if response.status_code == 201:
        logging.info(response.text)
        batch_message_data["message_id"] = response.json()["data"]["id"]
        status = batch_message_recorder.SENT
    else:
        logging.error(response.text)
        status = batch_message_recorder.FAILED

    batch_message_data["details"] = response.text
    batch_message_recorder.save_status(status, batch_id, message_reference, batch_message_data)

    return response.text


def headers(token: str, correlation_id: str) -> dict:
    return {
        "content-type": "application/vnd.api+json",
        "accept": "application/vnd.api+json",
        "x-correlation-id": correlation_id,
        "authorization": "Bearer " + token,
    }


def url() -> str:
    return os.environ["NOTIFY_API_URL"] + "/comms/v1/messages"


def message_body(routing_plan_id: str, message_reference: str, message_data: dict) -> dict:
    nhs_number: str = message_data["nhs_number"]
    date_of_birth: str = message_data["date_of_birth"]
    appointment_time: str = message_data["appointment_time"]
    appointment_date: str = message_data["appointment_date"]
    appointment_location: str = message_data["appointment_location"]
    contact_telephone_number: str = message_data["contact_telephone_number"]

    return {
        "data": {
            "type": "Message",
            "attributes": {
                "messageReference": message_reference,
                "routingPlanId": routing_plan_id,
                "recipient": {
                    "nhsNumber": nhs_number,
                    "dateOfBirth": date_of_birth,
                },
                "personalisation": {
                    "appointment_date": appointment_date,
                    "appointment_location": appointment_location,
                    "appointment_time": appointment_time,
                    "tracking_id": nhs_number,
                    "contact_telephone_number": contact_telephone_number,
                },
            },
        }
    }
