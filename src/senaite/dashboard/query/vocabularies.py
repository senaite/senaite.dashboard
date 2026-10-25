# -*- coding: utf-8 -*-
"""Choices the tile editor offers for a filter."""

from bika.lims import api
from senaite.core.catalog import SETUP_CATALOG
from senaite.dashboard.query import fields
from senaite.dashboard.query.labels import get_labels
from senaite.dashboard.query.search import NONE
from senaite.dashboard.query.search import build_query
from senaite.dashboard.query.search import count_values
from senaite.dashboard.query.search import get_rids
from senaite.dashboard.query.search import search

# More choices than this are not a list anybody picks from
MAX_CHOICES = 500
# Values for choices are collected from at most this many objects
MAX_SCANNED = 20000


def to_choices(labels, order=None):
    """Return [{value, title}] for the labels the user may see."""
    values = order or sorted(labels, key=lambda v: labels[v] or u"")
    return [{"value": value, "title": labels[value]}
            for value in values if labels.get(value)]


def state_choices(field, dataset, env):
    states = dataset.get_states()
    labels = get_labels(states, field, dataset, env)
    return to_choices(labels, order=states)


def reference_choices(field, dataset, env):
    brains = api.search({
        "portal_type": field.portal_type,
        "is_active": True,
        "sort_on": "sortable_title",
    })[:MAX_CHOICES]
    return [{"value": api.get_uid(brain),
             "title": api.safe_unicode(brain.Title)} for brain in brains]


def keyword_choices(field, dataset, env):
    brains = api.search({
        "portal_type": "AnalysisService",
        "is_active": True,
        "sort_on": "sortable_title",
    }, SETUP_CATALOG)[:MAX_CHOICES]
    return [{"value": brain.getKeyword,
             "title": api.safe_unicode(brain.Title)} for brain in brains]


def boolean_choices(field, dataset, env):
    labels = get_labels([True, False], field, dataset, env)
    return to_choices(labels, order=[True, False])


def visible_choices(field, dataset, env):
    """Values of the field among the objects the user may see.

    Not the values of the index: those are the values of all objects,
    including the ones the user may not see.
    """
    query = build_query(dataset, {}, env)
    rids = get_rids(search(dataset, query))[:MAX_SCANNED]
    counts = count_values(dataset, rids, field)
    values = [value for value in counts if value != NONE][:MAX_CHOICES]
    return to_choices(get_labels(values, field, dataset, env))


def choice_choices(field, dataset, env):
    values = field.get_choice_values()
    labels = get_labels(values, field, dataset, env)
    return to_choices(labels, order=values)


def no_choices(field, dataset, env):
    return []


CHOICES = {
    fields.STATE: state_choices,
    fields.REFERENCE: reference_choices,
    fields.KEYWORD: keyword_choices,
    fields.BOOLEAN: boolean_choices,
    fields.USER: visible_choices,
    fields.TEXT: visible_choices,
    fields.CHOICE: choice_choices,
    fields.DATE: no_choices,
}


def get_choices(field, dataset, env):
    """Return [{value, title}] for a filter of the tile editor."""
    choices = fields.get_by_kind(CHOICES, field)
    return choices(field, dataset, env)
