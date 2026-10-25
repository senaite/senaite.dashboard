# -*- coding: utf-8 -*-
"""Days, weeks and months in local time.

Boundaries are computed on calendar dates and only then turned into
DateTime, at local midnight of that date. Subtracting days from a
DateTime instead keeps its offset, and lands an hour off on the other
side of a daylight saving change.
"""

import datetime

from DateTime import DateTime


def to_date(value):
    """The calendar date of a DateTime, in its own time zone."""
    return datetime.date(value.year(), value.month(), value.day())


def to_datetime(date):
    """Local midnight of a calendar date."""
    return DateTime(date.year, date.month, date.day)


def shift_days(date, days):
    return date + datetime.timedelta(days=days)


def shift_months(date, months):
    """The first of the month `months` away from the date's month."""
    index = date.year * 12 + date.month - 1 + months
    year, month = divmod(index, 12)
    return datetime.date(year, month + 1, 1)


def start_of_week(date):
    """Monday of the week of the date."""
    return shift_days(date, -date.weekday())


def start_of_month(date):
    return date.replace(day=1)


def start_of_year(date):
    return date.replace(month=1, day=1)
