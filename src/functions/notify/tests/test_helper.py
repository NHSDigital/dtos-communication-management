import helper
import json
import pytest
import requests_mock
import cryptography.hazmat.primitives.asymmetric.rsa as rsa
import uuid


@pytest.fixture
def setup(monkeypatch):
    monkeypatch.setenv("NOTIFY_API_URL", "http://example.com")
    monkeypatch.setenv("TOKEN_URL", "http://tokens.example.com")


def test_send_messages(mocker):
    mocker.patch("helper.get_access_token", return_value="access_token")
    send_message_mock = mocker.patch("helper.send_message", return_value="OK")
    data = {
        "routing_plan": "breast-screening-pilot",
        "recipients": [
            {"nhs_number": "0000000000"},
            {"nhs_number": "0000000001"},
            {"nhs_number": "0000000002"},
        ]
    }
    with requests_mock.Mocker() as rm:
        rm.post(
            "http://example.com/comms", text="access_token"
        )

        response = helper.send_messages(data)

        assert send_message_mock.call_count == 3

        assert response == "OK\nOK\nOK"
        send_message_mock.assert_any_call(
            "access_token",
            helper.ROUTING_PLANS["breast-screening-pilot"],
            {"nhs_number": "0000000000"},
        )
        send_message_mock.assert_any_call(
            "access_token",
            helper.ROUTING_PLANS["breast-screening-pilot"],
            {"nhs_number": "0000000001"},
        )
        send_message_mock.assert_any_call(
            "access_token",
            helper.ROUTING_PLANS["breast-screening-pilot"],
            {"nhs_number": "0000000002"},
        )


def test_send_messages_with_individual_routing_plans(mocker):
    mocker.patch("helper.get_access_token", return_value="access_token")
    test_routing_plans = helper.ROUTING_PLANS.copy()
    test_routing_plans["cervical-screening-pilot"] = "c838b13c-f98c-4def-93f0-515d4e4f4ee1"
    test_routing_plans["bowel-cancer-screening-pilot"] = "0b1e3b13c-f98c-4def-93f0-515d4e4f4ee1"
    routing_plans_mock = mocker.patch("helper.ROUTING_PLANS", test_routing_plans)

    data = {
        "recipients": [
            {"routing_plan": "breast-screening-pilot", "nhs_number": "0000000000"},
            {"routing_plan": "bowel-cancer-screening-pilot", "nhs_number": "0000000001"},
            {"routing_plan": "cervical-screening-pilot", "nhs_number": "0000000002"},
        ]
    }

    send_message_mock = mocker.patch("helper.send_message", return_value="OK")

    with requests_mock.Mocker() as rm:
        rm.post(
            "http://example.com/comms", text="access_token"
        )
        response = helper.send_messages(data)

        assert send_message_mock.call_count == 3
        assert response == "OK\nOK\nOK"
        send_message_mock.assert_any_call(
            "access_token",
            "b838b13c-f98c-4def-93f0-515d4e4f4ee1",
            {"nhs_number": "0000000000"},
        )
        send_message_mock.assert_any_call(
            "access_token",
            "0b1e3b13c-f98c-4def-93f0-515d4e4f4ee1",
            {"nhs_number": "0000000001"},
        )
        send_message_mock.assert_any_call(
            "access_token",
            "c838b13c-f98c-4def-93f0-515d4e4f4ee1",
            {"nhs_number": "0000000002"},
        )


def test_send_message(setup):
    access_token = "access_token"
    routing_plan = "breast-screening-pilot"
    routing_plan_id = helper.ROUTING_PLANS[routing_plan]
    patient_data = {
        "nhs_number": "0000000000",
        "date_of_birth": "1981-10-07",
        "appointment_time": "10:00",
        "appointment_date": "2021-12-01",
        "appointment_type": "Mammogram",
        "appointment_location": "Breast Screening Clinic, 123 High Street, London",
        "correlation_id": "da0b1495-c7cb-468c-9d81-07dee089d728",
    }
    message_data = patient_data.copy()
    message_data["routing_plan"] = routing_plan

    response_text = json.dumps(
        {
            "data": {
                "type": "Message",
                "id": "2WL3qFTEFM0qMY8xjRbt1LIKCzM",
                "attributes": {
                    "messageReference": "da0b1495-c7cb-468c-9d81-07dee089d728",
                    "messageStatus": "created",
                    "timestamps": {
                        "created": "2023-11-17T14:27:51.413Z"
                    },
                    "routingPlan": {
                        "id": "b838b13c-f98c-4def-93f0-515d4e4f4ee1",
                        "version": "ztoe2qRAM8M8vS0bqajhyEBcvXacrGPp"
                    },
                },
            },
        }
    )

    with requests_mock.Mocker() as rm:
        adapter = rm.post(
            "http://example.com/comms/v1/messages", text=response_text
        )
        helper.send_message(access_token, routing_plan_id, message_data)
        expected_request_body = helper.message_body(routing_plan_id, patient_data)

        assert adapter.called
        assert adapter.call_count == 1
        assert adapter.last_request.json() == expected_request_body

def test_message_body():
    routing_plan_id = str(uuid.uuid4())

    data = {
        "nhs_number": "0000000000",
        "date_of_birth": "1990-01-02",
        "appointment_time": "10:00",
        "appointment_date": "2021-12-01",
        "appointment_type": "Mammogram",
        "appointment_location": "Breast Screening Clinic, 123 High Street, London",
    }

    actual = helper.message_body(routing_plan_id, data)

    expected = {
        "data": {
            "type": "Message",
            "attributes": {
                "messageReference": helper.reference_uuid(data["nhs_number"]),
                "routingPlanId": routing_plan_id,
                "recipient": {
                    "nhsNumber": "0000000000",
                    "dateOfBirth": "1990-01-02",
                },
                "personalisation": {
                    "appointmentDate": "2021-12-01",
                    "appointmentLocation": "Breast Screening Clinic, 123 High Street, London",
                    "appointmentTime": "10:00",
                    "appointmentType": "Mammogram",
                },
                "originator": {
                    "odsCode": "X26",
                },
            },
        }
    }

    assert actual == expected


def test_get_access_token(monkeypatch, mocker, setup):
    monkeypatch.setenv("NOTIFY_API_KEY", "an_api_key")
    monkeypatch.setenv("NOTIFY_API_KID", "a_kid")
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    mocker.patch("helper.get_private_key", return_value=private_key)

    with requests_mock.Mocker() as rm:
        rm.post(
            "http://tokens.example.com/",
            json={"access_token": "an_access_token"},
        )
        access_token = helper.get_access_token()
        assert access_token == "an_access_token"
