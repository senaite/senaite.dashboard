# -*- coding: utf-8 -*-
"""Placeholders a tile may use instead of fixed values.

A global dashboard is shared by everybody, so a tile cannot name the
user or the client it is meant for. It says `$user` or `$client`, and
the server puts in the values of whoever is looking. Dates work the
same way: `$today-30d` stays thirty days back however old the
dashboard gets.

Syntax: `$<name>` optionally followed by an offset `+<n><unit>` or
`-<n><unit>`. Units are h(ours), d(ays), w(eeks), m(onths) and
y(ears); months and years are calendar months and years.
"""

import re

from senaite.dashboard import messagefactory as _
from senaite.dashboard.exceptions import QueryError
from senaite.dashboard.query import calendar_dates as cal

VARIABLE_RE = re.compile(
    r"^\$(?P<name>[a-z_]+)"
    r"(?:(?P<sign>[+-])(?P<amount>\d{1,4})(?P<unit>[hdwmy]))?\Z")

# Placeholders that stand for a calendar date
DATE_STARTS = {
    "today": lambda today: today,
    "week": cal.start_of_week,
    "month": cal.start_of_month,
    "year": cal.start_of_year,
}


class Unset(object):
    """Value of a variable that does not apply to the current user.

    `$client` of a laboratory user is unset; a filter on it is dropped,
    so the same tile shows one client to a client contact and every
    client to the laboratory.
    """

    def __repr__(self):
        return "UNSET"

    def __nonzero__(self):
        return False


UNSET = Unset()


def is_variable(value):
    """Return whether the value is a placeholder."""
    return isinstance(value, basestring) and value.startswith("$")


def invalid(token):
    return QueryError(_("Invalid placeholder ${name}",
                        mapping={"name": token}))


def shift_date(date, amount, unit):
    """A calendar date moved by a signed amount of days to years."""
    if unit == "d":
        return cal.shift_days(date, amount)
    if unit == "w":
        return cal.shift_days(date, amount * 7)
    months = amount if unit == "m" else amount * 12
    day = min(date.day, 28)
    return cal.shift_months(date, months).replace(day=day)


def resolve_date(name, amount, unit, env):
    """A placeholder for a date: local midnight, moved by the offset."""
    date = DATE_STARTS[name](cal.to_date(env.now))
    if unit == "h":
        return cal.to_datetime(date) + amount / 24.0
    if unit:
        date = shift_date(date, amount, unit)
    return cal.to_datetime(date)


def resolve_now(amount, unit, env):
    """The current time, moved by the offset; days keep the time."""
    if unit in (None, "h"):
        return env.now + amount / 24.0
    today = cal.to_date(env.now)
    time_of_day = env.now - cal.to_datetime(today)
    return cal.to_datetime(shift_date(today, amount, unit)) + time_of_day


def resolve_moment(token, name, amount, unit, env):
    """A placeholder for a date or the time, moved by the offset.

    An offset of thousands of years leaves the calendar; that is an
    invalid placeholder, not an error of the server.
    """
    try:
        if name == "now":
            return resolve_now(amount, unit, env)
        return resolve_date(name, amount, unit, env)
    except (ValueError, OverflowError):
        raise invalid(token)


def resolve_variable(token, env):
    """Return the value of a single placeholder such as `$today-30d`."""
    match = VARIABLE_RE.match(token)
    if not match:
        raise invalid(token)
    name, unit = match.group("name"), match.group("unit")
    amount = int(match.group("amount") or 0)
    if match.group("sign") == "-":
        amount = -amount
    if name in DATE_STARTS or name == "now":
        return resolve_moment(token, name, amount, unit, env)
    if unit:
        raise invalid(token)
    if name == "user":
        return env.user_id
    if name == "client":
        return env.client_uid or UNSET
    raise invalid(token)


def resolve(value, env):
    """Resolve the placeholders anywhere in a JSON-like value."""
    if is_variable(value):
        return resolve_variable(value, env)
    if isinstance(value, dict):
        return {key: resolve(val, env) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [resolve(item, env) for item in value]
    return value
