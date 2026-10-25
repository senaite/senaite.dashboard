# -*- coding: utf-8 -*-
"""Periods for charts over time."""

from senaite.dashboard import messagefactory as _
from senaite.dashboard.exceptions import QueryError
from senaite.dashboard.query import calendar_dates as cal

DAY = "day"
WEEK = "week"
MONTH = "month"

# The most periods a chart may ask for, per interval
MAX_PERIODS = {
    DAY: 92,
    WEEK: 104,
    MONTH: 60,
}

# The course of a number, when a tile asks for one without details
DEFAULT_TREND = {"date_field": "created", "interval": WEEK, "periods": 8}

# DateIndex stores minutes; a range ends one minute before the next
# period starts, so that no object falls into two periods.
ONE_MINUTE = 1.0 / 24 / 60


def period_start(date, interval):
    if interval == DAY:
        return date
    if interval == WEEK:
        return cal.start_of_week(date)
    return cal.start_of_month(date)


def shift_period(start, interval, count):
    if interval == DAY:
        return cal.shift_days(start, count)
    if interval == WEEK:
        return cal.shift_days(start, count * 7)
    return cal.shift_months(start, count)


def check_periods(interval, periods):
    if interval not in MAX_PERIODS:
        raise QueryError(_("Unknown interval ${name}",
                           mapping={"name": interval}))
    if not 1 <= periods <= MAX_PERIODS[interval]:
        raise QueryError(_("Between 1 and ${max} periods",
                           mapping={"max": MAX_PERIODS[interval]}))


def get_periods(interval, periods, now):
    """Return [(start, end)] of the last periods, oldest first.

    The last period is the current one, up to its end. Starts and ends
    are local midnight.
    """
    check_periods(interval, periods)
    current = period_start(cal.to_date(now), interval)
    starts = [shift_period(current, interval, offset)
              for offset in range(1 - periods, 2)]
    dates = [cal.to_datetime(start) for start in starts]
    return list(zip(dates[:-1], dates[1:]))


def to_range(start, end):
    """DateIndex query for the period from start up to end."""
    return {"query": [start, end - ONE_MINUTE], "range": "min:max"}
