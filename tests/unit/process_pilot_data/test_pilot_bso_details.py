import pilot_bso_details


def test_code_for_filename():
    assert pilot_bso_details.code_from_filename("KMK NHS App Pilot 002 SPRPT") == "KMK"
    assert pilot_bso_details.code_from_filename("JDO NHS App Pilot") == "JDO"
    assert pilot_bso_details.code_from_filename("HWA NHS") == "HWA"
    assert pilot_bso_details.code_from_filename("XXX ABC") == "XXX"


def test_contact_telephone_number():
    assert pilot_bso_details.contact_telephone_number("KMK") == "01908 995883"
    assert pilot_bso_details.contact_telephone_number("HWA") == "020 3758 2024"
    assert pilot_bso_details.contact_telephone_number("JDO") == "01202 665511"
    assert pilot_bso_details.contact_telephone_number("XXX") is None
