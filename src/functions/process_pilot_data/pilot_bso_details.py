SERVICES = {
    # TODO: Use the correct keys here
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


# Expectd file name: XXX NHS App Pilot 002 SPRPT
# Where XXX is the code
def code_from_filename(filename: str) -> str:
    return filename.split(" ")[0]


def contact_telephone_number(code: str) -> str:
    service = SERVICES.get(code)
    return service["telephone"] if service else None
