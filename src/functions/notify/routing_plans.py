import os

breast_screening_first_appointment_plans = {
    "sandbox": "b838b13c-f98c-4def-93f0-515d4e4f4ee1"
}

bowel_screening_first_appointment_plans = {
    "sandbox": "b1e3b13c-f98c-4def-93f0-515d4e4f4ee1"
}

ROUTING_PLANS = {
    "breast-screening-pilot": breast_screening_first_appointment_plans,
    "bowel-screening-pilot": bowel_screening_first_appointment_plans
}

def get_id(key: str) -> str | None:
    return ROUTING_PLANS.get(key)[os.getenv("ENVIRONMENT") or "sandbox"]
