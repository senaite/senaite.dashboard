# -*- coding: utf-8 -*-
"""Data sources that search a dataset in the catalog.

Each source takes `dataset` and `filters` (see fields.py) plus its own
parameters, declared in `params`, and answers with plain JSON. The
`output` of a source names the shape of its answer; a tile type shows
the outputs it accepts (see webpack/app/tiles/index.js):

    scalar  count, span     one number, maybe with its course
    items   group           numbers per value of a field
    series  timeseries      numbers per period, maybe per value
    rows    list            the first objects with some columns

Every search runs as the current user (see search.py).
"""

from collections import Counter

from bika.lims import api
from DateTime import DateTime
from senaite.core.i18n import translate
from senaite.dashboard import messagefactory as _
from senaite.dashboard.exceptions import ValidationError
from senaite.dashboard.interfaces import IDashboardDataSource
from senaite.dashboard.query import timeline
from senaite.dashboard.query.datasets import COL_DATE
from senaite.dashboard.query.datasets import COL_DUE
from senaite.dashboard.query.datasets import COL_STATE
from senaite.dashboard.query.fields import CHOICE
from senaite.dashboard.query.fields import DATE
from senaite.dashboard.query.fields import STATE
from senaite.dashboard.query.fields import USER
from senaite.dashboard.query.labels import get_labels
from senaite.dashboard.query.labels import get_state_title
from senaite.dashboard.query.params import DATASET_PARAMS
from senaite.dashboard.query.params import MAPPING
from senaite.dashboard.query.params import NAME
from senaite.dashboard.query.params import NAMES
from senaite.dashboard.query.params import NUMBER
from senaite.dashboard.query.params import clean_trend
from senaite.dashboard.query.params import is_number
from senaite.dashboard.query.registry import get_dataset
from senaite.dashboard.query.search import NONE
from senaite.dashboard.query.search import build_query
from senaite.dashboard.query.search import count_values
from senaite.dashboard.query.search import get_rids
from senaite.dashboard.query.search import search
from zope.interface import implementer

# Key of the bucket for values the user may not see or that do not fit
OTHER = "__other__"
# Key of the one series of a chart that is not split
TOTAL = "total"

MAX_GROUPS = 50
MAX_STACKS = 12
MAX_ROWS = 50
# A span is measured over the most recent objects only
MAX_SPAN_OBJECTS = 5000

# What a tile that reads every object it finds costs, in catalog
# searches: a group reads the index value of each, a span the dates of
# thousands
SCAN_COST = 10

DEFAULT_PERIODS = 12
DEFAULT_LIMIT = 10
# A list without columns of its own shows the first ones of its dataset
DEFAULT_COLUMNS = 4


def clamp(value, default, low, high):
    """The number within the bounds, or the default when there is none."""
    if value is None:
        return default
    return max(low, min(high, value))


def to_iso(value):
    if isinstance(value, DateTime):
        return value.ISO8601()
    return None


def get_sort_order(value):
    """Newest first, unless asked for the oldest first."""
    return "ascending" if value == "ascending" else "descending"


def with_dataset(spec):
    """The parameters of a source on a dataset."""
    return dict(DATASET_PARAMS, **spec)


def periods_of(params, default):
    """The number of periods asked for, for the cost of a tile.

    The parameters are not checked yet; anything that is not a number
    costs the default.
    """
    periods = params.get("periods")
    if not is_number(periods):
        return default
    return clamp(periods, default, 1, timeline.MAX_PERIODS[timeline.WEEK])


@implementer(IDashboardDataSource)
class DataSource(object):
    """Base of a data source; add-ons subclass it for sources of their own.

    A subclass sets `title`, `output` and `params`, the parameters it
    takes by kind (see params.py; `with_dataset` adds those of a source
    on a dataset), and implements `__call__`. It may override `clean`,
    to check its parameters further, and `cost`, when it causes more
    than one catalog search.
    """
    title = None
    output = None
    params = {}

    def clean(self, params):
        """The parameters, checked further than by their kinds.

        :raises ValidationError: when they are not valid
        """
        return params

    def cost(self, params):
        """How many catalog searches the tile causes, roughly.

        :param params: the parameters as the tile sent them, unchecked
        """
        return 1

    def __call__(self, params, env):
        raise NotImplementedError


# Fields

def get_dataset_query(params, env):
    """Return the dataset of the tile and its catalog query."""
    dataset = get_dataset(params.get("dataset"), env)
    return dataset, build_query(dataset, params.get("filters"), env)


def get_date_field(dataset, name, env):
    """The date field of the name; `created` when there is none."""
    name = name or "created"
    field = dataset.get_field(name, env)
    if field.kind != DATE:
        raise ValidationError(_("${name} is not a date",
                                mapping={"name": name}))
    return field


def get_group_field(dataset, name, env):
    field = dataset.get_field(name, env)
    if not field.groupable:
        raise ValidationError(_("Cannot group by ${name}",
                                mapping={"name": name}))
    return field


# Groups

def get_key_order(field, dataset):
    """The order a field's values have by nature, if any."""
    if field.kind == STATE:
        return dataset.get_states()
    if field.kind == CHOICE:
        return field.get_choice_values()
    return None


def order_keys(counts, field, dataset):
    """States and choices in their order, everything else by count."""
    order = get_key_order(field, dataset)
    if order is None:
        return sorted(counts, key=lambda k: (-counts[k], k))
    return sorted(counts, key=lambda k: (
        order.index(k) if k in order else len(order), k))


def get_group_labels(keys, field, dataset, env):
    """Labels for the keys; None for keys the user may not see."""
    labels = get_labels(
        [key for key in keys if key != NONE], field, dataset, env)
    none = _("Not assigned") if field.kind == USER else _("Not set")
    labels[NONE] = translate(none, to_utf8=False)
    return labels


def to_group(key, label, value):
    return {"key": key, "label": label, "value": value}


def to_groups(counts, field, dataset, env, limit):
    """Return [{key, label, value}] for the largest groups.

    Smaller groups and groups the user may not see add up to "Other".
    """
    keys = order_keys(counts, field, dataset)
    shown = keys[:limit]
    labels = get_group_labels(shown, field, dataset, env)
    groups = [to_group(key, labels[key], counts[key])
              for key in shown if labels.get(key)]
    other = sum(counts.values()) - sum(group["value"] for group in groups)
    if other:
        label = translate(_("Other"), to_utf8=False)
        groups.append(to_group(OTHER, label, other))
    return groups


# Periods

def count_period(dataset, query, field, period, stack_field):
    """Count the objects of one period, per value of the stack field."""
    start, end = period
    period_query = dict(query)
    period_query[field.index] = timeline.to_range(start, end)
    rids = get_rids(search(dataset, period_query))
    if stack_field is None:
        return Counter({TOTAL: len(rids)})
    return count_values(dataset, rids, stack_field)


def count_per_period(dataset, query, field, periods, stack_field=None):
    """Counters of the objects per period."""
    return [count_period(dataset, query, field, period, stack_field)
            for period in periods]


def get_periods(params, default_periods, env):
    interval = params.get("interval", timeline.WEEK)
    periods = params.get("periods", default_periods)
    return interval, timeline.get_periods(interval, periods, env.now)


def stack_values(counts, key, shown):
    """The values of one series of a stack; "Other" takes the rest."""
    if key != OTHER:
        return [count.get(key, 0) for count in counts]
    return [sum(v for k, v in count.items() if k not in shown)
            for count in counts]


def to_series(counts, stack_field, dataset, env):
    """One series per value of the stack field, or one in all."""
    if stack_field is None:
        return [{
            "key": TOTAL,
            "label": translate(_("Total"), to_utf8=False),
            "values": [count[TOTAL] for count in counts],
        }]
    totals = sum(counts, Counter())
    groups = to_groups(totals, stack_field, dataset, env, MAX_STACKS)
    shown = {group["key"] for group in groups} - {OTHER}
    return [{
        "key": group["key"],
        "label": group["label"],
        "values": stack_values(counts, group["key"], shown),
    } for group in groups]


# Rows

def cell_date(value, dataset):
    return to_iso(value)


def cell_state(value, dataset):
    return {
        "value": value,
        "title": get_state_title(value, dataset.portal_type),
    }


def cell_value(value, dataset):
    """Text and numbers as they are; anything else is not shown."""
    if isinstance(value, basestring):
        return api.safe_unicode(value)
    if isinstance(value, (bool, int, long, float)):
        return value
    return None


CELLS = {
    COL_DATE: cell_date,
    COL_DUE: cell_date,
    COL_STATE: cell_state,
}


def to_cell(brain, column, dataset, env):
    """The value of a column of a row, as the page shows it."""
    if not column.is_readable(brain, env):
        return None
    to_json = CELLS.get(column.kind, cell_value)
    return to_json(column.get_value(brain), dataset)


def to_row(brain, columns, dataset, env):
    return {
        "url": dataset.get_url(brain),
        "uid": brain.UID,
        "cells": {column.name: to_cell(brain, column, dataset, env)
                  for column in columns},
    }


# Spans

def span_hours(brain, span):
    """Hours between the two dates of the span, or None."""
    start = getattr(brain, span.start, None)
    end = getattr(brain, span.end, None)
    if not isinstance(start, DateTime) or not isinstance(end, DateTime):
        return None
    if end < start:
        return None
    return (end - start) * 24.0


def percentile(values, fraction):
    return values[int(round(fraction * (len(values) - 1)))]


def summarize_hours(hours, span):
    result = {"count": len(hours), "unit": "hours", "span": span.name,
              "value": None}
    if not hours:
        return result
    result.update({
        "value": sum(hours) / len(hours),
        "median": percentile(hours, 0.5),
        "p90": percentile(hours, 0.9),
        "min": hours[0],
        "max": hours[-1],
    })
    return result


# Sources

class CountSource(DataSource):
    """Number of objects, optionally with its course over time.

    Answer: {"value": 12, "trend": {"interval": "week",
    "buckets": [iso date, ...], "values": [3, 5, ...]}}
    """
    title = _("Count")
    output = "scalar"
    params = with_dataset({"trend": MAPPING})

    def clean(self, params):
        return clean_trend(params)

    def cost(self, params):
        trend = params.get("trend")
        if not isinstance(trend, dict):
            return 1
        return 1 + periods_of(trend, timeline.DEFAULT_TREND["periods"])

    def __call__(self, params, env):
        dataset, query = get_dataset_query(params, env)
        result = {"value": len(search(dataset, query))}
        if params.get("trend"):
            trend = dict(timeline.DEFAULT_TREND, **params["trend"])
            result["trend"] = self.get_trend(dataset, query, trend, env)
        return result

    def get_trend(self, dataset, query, trend, env):
        field = get_date_field(dataset, trend["date_field"], env)
        interval, periods = get_periods(trend, trend["periods"], env)
        counts = count_per_period(dataset, query, field, periods)
        return {
            "interval": interval,
            "buckets": [to_iso(start) for start, end in periods],
            "values": [count[TOTAL] for count in counts],
        }


class GroupSource(DataSource):
    """Number of objects per value of a field.

    Answer: {"total": 40, "kind": field kind, "items": [{"key": value,
    "label": title, "value": 12}, ...]}; the smaller groups and the ones
    the user may not see add up to an item with the key "__other__".
    """
    title = _("Group")
    output = "items"
    params = with_dataset({"group_by": NAME, "limit": NUMBER})

    def cost(self, params):
        return SCAN_COST

    def __call__(self, params, env):
        dataset, query = get_dataset_query(params, env)
        field = get_group_field(dataset, params.get("group_by"), env)
        limit = clamp(params.get("limit"), DEFAULT_LIMIT, 1, MAX_GROUPS)
        rids = get_rids(search(dataset, query))
        counts = count_values(dataset, rids, field)
        return {
            # Objects, not values: an object may have several values
            "total": len(rids),
            "kind": field.kind,
            "items": to_groups(counts, field, dataset, env, limit),
        }


class TimeseriesSource(DataSource):
    """Number of objects per period, optionally stacked by a field.

    Answer: {"interval": "week", "kind": kind of the stack field or
    None, "buckets": [iso date, ...], "series": [{"key", "label",
    "values": [one per bucket]}, ...]}
    """
    title = _("Over time")
    output = "series"
    params = with_dataset({
        "date_field": NAME, "interval": NAME, "periods": NUMBER,
        "stack_by": NAME,
    })

    def cost(self, params):
        return periods_of(params, DEFAULT_PERIODS)

    def __call__(self, params, env):
        dataset, query = get_dataset_query(params, env)
        field = get_date_field(dataset, params.get("date_field"), env)
        interval, periods = get_periods(params, DEFAULT_PERIODS, env)
        stack_field = None
        if params.get("stack_by"):
            stack_field = get_group_field(dataset, params["stack_by"], env)
        counts = count_per_period(dataset, query, field, periods,
                                  stack_field)
        return {
            "interval": interval,
            "kind": stack_field.kind if stack_field else None,
            "buckets": [to_iso(start) for start, end in periods],
            "series": to_series(counts, stack_field, dataset, env),
        }


class ListSource(DataSource):
    """The first objects of a search, with some of their columns.

    Answer: {"total": 40, "columns": [{"name", "title", "kind"}, ...],
    "rows": [{"url", "uid", "cells": {column name: value}}, ...]}
    """
    title = _("List")
    output = "rows"
    params = with_dataset({
        "columns": NAMES, "sort_on": NAME, "sort_order": NAME,
        "limit": NUMBER,
    })

    def get_columns(self, dataset, names, env):
        """The columns asked for, or the first ones of the dataset."""
        if not names:
            return dataset.get_columns(env)[:DEFAULT_COLUMNS]
        return [dataset.get_column(name, env) for name in names]

    def __call__(self, params, env):
        dataset, query = get_dataset_query(params, env)
        columns = self.get_columns(dataset, params.get("columns"), env)
        limit = clamp(params.get("limit"), DEFAULT_LIMIT, 1, MAX_ROWS)
        sort_field = get_date_field(dataset, params.get("sort_on"), env)
        query["sort_on"] = sort_field.index
        query["sort_order"] = get_sort_order(params.get("sort_order"))
        query["sort_limit"] = limit
        results = search(dataset, query)
        return {
            "total": results.actual_result_count,
            "columns": [column.describe() for column in columns],
            "rows": [to_row(brain, columns, dataset, env)
                     for brain in results[:limit]],
        }


class SpanSource(DataSource):
    """How long it takes between two dates, e.g. the turnaround time.

    Measured over the objects that have both dates, the most recent
    first.

    Answer: {"value": mean hours, "median", "p90", "min", "max",
    "count": objects measured, "unit": "hours", "span": span name}
    """
    title = _("Duration")
    output = "scalar"
    params = with_dataset({"span": NAME})

    def cost(self, params):
        return SCAN_COST

    def __call__(self, params, env):
        dataset, query = get_dataset_query(params, env)
        span = dataset.get_span(params.get("span"))
        query["sort_on"] = span.end
        query["sort_order"] = "descending"
        query["sort_limit"] = MAX_SPAN_OBJECTS
        brains = search(dataset, query)[:MAX_SPAN_OBJECTS]
        hours = [span_hours(brain, span) for brain in brains]
        return summarize_hours(sorted(h for h in hours if h is not None),
                               span)
