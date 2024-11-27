from datetime import datetime
import logging

def to_human_readable_twelve_hours(raw_time: str) -> str | None:
    """
    Convert a time string like '11:56:00' to '11:56am' or '12:56pm'.
    """
    try:
        time_obj = datetime.strptime(raw_time, "%H:%M:%S")
        return time_obj.strftime("%I:%M%p").lower()

    except ValueError:
        logging.error(f"Invalid time format: {raw_time}")
        return None
