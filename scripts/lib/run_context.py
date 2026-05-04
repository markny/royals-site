import os
from datetime import date


DATE_ENV = "TRACKER_AS_OF_DATE"


def as_of_date():
    value = os.environ.get(DATE_ENV)
    if value:
        return date.fromisoformat(value)
    return date.today()


def season():
    return as_of_date().year
