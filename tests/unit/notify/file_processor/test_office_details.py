import file_processor.office_details as office_details


def test_code_for_filename():
    """Test extraction of 3 character BSO code from filename"""
    assert office_details.code_from_filename("KMK NHS App Pilot 002 SPRPT") == "KMK"
    assert office_details.code_from_filename("JDO NHS App Pilot") == "JDO"
    assert office_details.code_from_filename("HWA NHS") == "HWA"
    assert office_details.code_from_filename("hwa NHS") == "HWA"
    assert office_details.code_from_filename("HwA NHS") == "HWA"
    assert office_details.code_from_filename("XXX ABC") == "XXX"


def test_contact_telephone_number():
    """Test retrieval of contact telephone number from BSO code"""
    assert office_details.contact_telephone_number("KMK NHS App Pilot 002 SPRPT") == "01908 995883"
    assert office_details.contact_telephone_number("HWA NHS App Pilot 002 SPRPT") == "020 3758 2024"
    assert office_details.contact_telephone_number("JDO NHS App Pilot 002 SPRPT") == "01202 665511"
    assert office_details.contact_telephone_number("XXX NHS App Pilot 002 SPRPT") is None


def test_routing_plan_id():
    """Test retrieval of routing plan ID from BSO code"""
    assert office_details.routing_plan_id("KMK NHS App Pilot 002 SPRPT") == "f134ef50-3d4d-4fc5-8fab-19087a84349f"
    assert office_details.routing_plan_id("HWA NHS App Pilot 002 SPRPT") == "f134ef50-3d4d-4fc5-8fab-19087a84349f"
    assert office_details.routing_plan_id("JDO NHS App Pilot 002 SPRPT") == "f134ef50-3d4d-4fc5-8fab-19087a84349f"
    assert office_details.routing_plan_id("XXX NHS App Pilot 002 SPRPT") == "f134ef50-3d4d-4fc5-8fab-19087a84349f"
