from datetime import datetime
import logging

def to_human_readable_twelve_hours(raw_time: str) -> str | None:
    """
    Convert a time string like '11:56:00' to '11:56am' or '12:56pm'.
    """
    try:
        if raw_time is None:
            logging.error("Attempted to convert time format, but input is None.")
            return None

        raw_time = raw_time.strip()

        time_obj = datetime.strptime(raw_time, "%H:%M:%S")
        return time_obj.strftime("%I:%M%p").lower()

    except (ValueError, TypeError):
        logging.error(f"Invalid time format: {raw_time}")
        return None
