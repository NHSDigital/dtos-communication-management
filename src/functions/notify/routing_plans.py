import os

breast_screening_first_appointment_plans = {
    "development": "b838b13c-f98c-4def-93f0-515d4e4f4ee1",
    "integration": "97eaad14-a72c-45f3-bbcd-c0071113c1c2",
    "nft": "97eaad14-a72c-45f3-bbcd-c0071113c1c2",
    "pre_production": "97eaad14-a72c-45f3-bbcd-c0071113c1c2",
    "production": "97eaad14-a72c-45f3-bbcd-c0071113c1c2",
}

bowel_screening_first_appointment_plans = {
    "sandbox": "b1e3b13c-f98c-4def-93f0-515d4e4f4ee1"
}

ROUTING_PLANS = {
    "breast-screening-pilot": breast_screening_first_appointment_plans,
    "bowel-screening-pilot": bowel_screening_first_appointment_plans
}


def get_id(key: str) -> str | None:
    return ROUTING_PLANS.get(key)[(os.getenv("ENVIRONMENT", "development").lower())]
