from datetime import datetime
import re

def get_date_from_timestamp(timestamp):
    return datetime.utcfromtimestamp(timestamp).date()

def get_todays_date():
    return datetime.utcnow().date()

def normalize_string(value):
    """Remove non-alphanumeric characters and convert to lowercase."""
    if not value:
        return ""
    if not isinstance(value, str):
        value = str(value)
    return re.sub(r'[^a-zA-Z0-9]', '', value).lower()

