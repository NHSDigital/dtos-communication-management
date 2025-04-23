from datetime import datetime

CRYSTAL_REPORT_EXTRACT_FORMAT = "%dM%mM%Y"


def _to_format(date_str: str, desired_format: str) -> str | None:
    try:
        # If we can parse the date string in the desired format, we can return it as-is
        datetime.strptime(date_str, desired_format)
        return date_str
    except ValueError:
        pass

    try:
        return datetime.strptime(date_str, CRYSTAL_REPORT_EXTRACT_FORMAT).strftime(desired_format)
    except ValueError:
        return None


def to_human_readable_date(date_str: str) -> str | None:
    return _to_format(date_str, "%A %d %B %Y")
