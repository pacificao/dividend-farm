# utils/datetime_utils.py

from datetime import datetime, timedelta

def get_today() -> datetime:
    """Returns today's date with no time component."""
    return datetime.now().date()

def get_future_date(days_ahead: int) -> datetime:
    """Returns the date 'days_ahead' days from today."""
    return datetime.now().date() + timedelta(days=days_ahead)

def format_date(date_obj: datetime, format_str: str = "%Y-%m-%d") -> str:
    """Formats a datetime object into a string."""
    return date_obj.strftime(format_str)

def parse_date(date_str: str, format_str: str = "%Y-%m-%d") -> datetime:
    """Parses a string into a datetime object."""
    return datetime.strptime(date_str, format_str)

def days_between(start_date: datetime, end_date: datetime) -> int:
    """Returns the number of days between two dates."""
    return (end_date - start_date).days