# -*- coding: utf-8 -*-
"""Check the parameters of a tile before anything is done with them.

Each data source declares the parameters it takes and their kinds.
Parameters are reduced to those, so that unknown keys neither reach a
source nor make every request a new cache entry, and a parameter of
the wrong kind is a ValidationError (a 400), never a TypeError (a 500).
"""

import re

from senaite.dashboard import messagefactory as _
from senaite.dashboard.exceptions import ValidationError

# Kinds of parameters
NAME = "name"
NAMES = "names"
MAPPING = "mapping"
NUMBER = "number"

# Names of datasets, fields, columns, spans and intervals; `\Z`, as
# `$` also matches before a newline at the end
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,63}\Z")
MAX_NAMES = 30

# The parameters every source on a dataset takes
DATASET_PARAMS = {
    "dataset": NAME,
    "filters": MAPPING,
}

# The parameters of a trend, the course of a number over time
TREND_PARAMS = {
    "date_field": NAME,
    "interval": NAME,
    "periods": NUMBER,
}


def invalid(key):
    return ValidationError(_("Invalid parameter ${name}",
                             mapping={"name": key}))


def is_name(value):
    return isinstance(value, basestring) and bool(NAME_RE.match(value))


def clean_name(key, value):
    if not is_name(value):
        raise invalid(key)
    return str(value)


def clean_names(key, value):
    if not isinstance(value, list) or len(value) > MAX_NAMES:
        raise invalid(key)
    return [clean_name(key, item) for item in value]


def clean_mapping(key, value):
    if not isinstance(value, dict):
        raise invalid(key)
    return value


def is_number(value):
    """Whether the value is a whole number.

    A bool is an int in Python, but never a number of periods.
    """
    return isinstance(value, (int, long)) and not isinstance(value, bool)


def clean_number(key, value):
    if not is_number(value):
        raise invalid(key)
    return value


CLEANERS = {
    NAME: clean_name,
    NAMES: clean_names,
    MAPPING: clean_mapping,
    NUMBER: clean_number,
}


def clean_params(params, spec):
    """Return the parameters the spec declares, checked.

    Empty values (None, "") are left out, so that "not set" has one
    spelling.

    :param spec: {name: kind}
    :raises ValidationError: for a parameter of the wrong kind
    """
    if not isinstance(params, dict):
        raise ValidationError(_("Parameters must be a mapping"))
    cleaned = {}
    for key, kind in spec.items():
        value = params.get(key)
        if value in (None, "", [], {}):
            continue
        cleaned[key] = CLEANERS[kind](key, value)
    return cleaned


def clean_trend(params):
    """Check the nested trend of a count, if there is one."""
    if "trend" in params:
        params["trend"] = clean_params(params["trend"], TREND_PARAMS)
    return params
