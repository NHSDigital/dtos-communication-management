from datetime import datetime

def to_date_of_birth(date_str: str) -> str | None:
    try:
        # If we can parse the date string as a date, it's already in the correct format - return as-is
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        pass

    try:
        return datetime.strptime(date_str, "%dM%mM%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None

# STAGE 2 - Incident clients booked into specified clinic(s) and date(s),1234567890,"BLAKE, KENNETH, MR",07M11M1989,EP700,25M11M2024,11:56:00,Edgware Prospect Clinics
