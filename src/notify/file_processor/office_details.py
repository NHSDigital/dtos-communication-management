DEFAULT_ROUTING_PLAN_ID = "f134ef50-3d4d-4fc5-8fab-19087a84349f"
SERVICES = {
    "KMK": {
        "name": "Milton Keynes Breast Care Unit",
        "telephone": "01908 995883",
    },
    "HWA": {
        "name": "South West London Breast Screening Service",
        "telephone": "020 3758 2024",
    },
    "JDO": {
        "name": "Dorset Breast Screening Unit",
        "telephone": "01202 665511",
    },
}


def contact_telephone_number(filename: str) -> str | None:
    service = SERVICES.get(code_from_filename(filename))
    return service["telephone"] if service else None


def routing_plan_id(filename: str) -> str:
    service = SERVICES.get(code_from_filename(filename))
    if service:
        return service.get("routing_plan_id", DEFAULT_ROUTING_PLAN_ID)

    return DEFAULT_ROUTING_PLAN_ID


def code_from_filename(filename: str) -> str:
    return filename[0:3].upper()
