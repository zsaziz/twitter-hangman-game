import time
from datetime import datetime, timezone

DEFAULT_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_DATETIME_FORMAT = '%Y-%m-%dT%H-%M-%S'


def get_todays_date(datetime_format: str = None, return_datetime: bool = False):
    todays_date = datetime.today().astimezone().replace(hour=0, minute=0, second=0, microsecond=0)
    if return_datetime:
        return todays_date
    return todays_date.strftime(datetime_format if datetime_format else DEFAULT_DATE_FORMAT)


def get_todays_date_time(datetime_format: str = DEFAULT_DATETIME_FORMAT, return_datetime: bool = False):
    todays_date = datetime.today().astimezone()
    if return_datetime:
        return todays_date
    return todays_date.strftime(datetime_format)


def get_date(date_string: str):
    return datetime.fromisoformat(date_string).astimezone().date()


def get_timestamp_in_seconds():
    return int(datetime.now().astimezone().timestamp())


def get_date_from_timestamp(timestamp: int, datetime_format: str = DEFAULT_DATE_FORMAT):
    date = datetime.fromtimestamp(timestamp).astimezone()
    return date.strftime(datetime_format)
