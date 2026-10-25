# -*- coding: utf-8 -*-
"""What a dataset is made of: fields, columns, spans.

A dataset is the whitelist of the query language: which catalog, which
objects in it, which indexes a filter may touch, what a tile may group
by, which columns a list shows and which spans of time it can measure.
Nothing outside of it can be asked for.

The datasets themselves come from three places: builtin.py has those
senaite.dashboard ships with, add-ons register their own as named
utilities providing IDashboardDataset, and managers define more in the
browser (custom.py). registry.py finds them all.
"""

from bika.lims import api
from collections import OrderedDict
from senaite.dashboard import messagefactory as _
from senaite.dashboard.exceptions import QueryError
from senaite.dashboard.interfaces import IDashboardDataset
from senaite.dashboard.interfaces import IDashboardDatasetExtension
from senaite.dashboard.query.search import get_index_value
from senaite.dashboard.titles import display_title
from zope.component import getUtilitiesFor
from zope.interface import implementer

# Kinds of columns
COL_TEXT = "text"
COL_DATE = "date"
COL_DUE = "due"
COL_STATE = "state"
COL_NUMBER = "number"
COL_PERCENT = "percent"


def index_getter(catalog_id, index):
    """A column getter reading the value an object has in an index.

    For values the catalog indexes but keeps no metadata column for. It
    reads the index, so the object is not woken up.
    """
    def getter(brain):
        return get_index_value(catalog_id, index, brain.getRID())
    return getter


def choice_getter(field, getter=None):
    """A column getter showing the title of the value of a choice field.

    :param getter: reads the raw value; by default the metadata column
        named like the index of the field
    """
    def read(brain):
        if getter is not None:
            return getter(brain)
        return getattr(brain, field.index, None)

    def title(brain):
        value = read(brain)
        return field.get_choice_title(value) if value else None
    return title


class Column(object):
    """A metadata column a list tile may show.

    :param guard: function(brain, env) deciding per row whether the
        user may read the cell; the cell is empty otherwise
    :param getter: function(brain) returning the value, for a value
        the catalog has no metadata column for. It runs for the shown
        rows only, but may wake up their objects.
    :param lab_only: hide the column from users outside the laboratory
    """

    def __init__(self, name, title, kind=COL_TEXT, guard=None,
                 getter=None, lab_only=False):
        self.name = name
        self.title = title
        self.kind = kind
        self.guard = guard
        self.getter = getter
        self.lab_only = lab_only

    def is_available(self, env):
        """Whether the user may show the column in a table."""
        return env.is_lab or not self.lab_only

    def is_readable(self, brain, env):
        return self.guard is None or self.guard(brain, env)

    def get_value(self, brain):
        if self.getter is not None:
            return self.getter(brain)
        value = getattr(brain, self.name, None)
        return value() if callable(value) else value

    def describe(self):
        return {
            "name": self.name,
            "title": display_title(self.title),
            "kind": self.kind,
        }


class Span(object):
    """The time between two dates of an object, e.g. turnaround."""

    def __init__(self, name, title, start, end):
        self.name = name
        self.title = title
        self.start = start
        self.end = end

    def describe(self):
        return {
            "name": self.name,
            "title": display_title(self.title),
            "start": self.start,
            "end": self.end,
        }


@implementer(IDashboardDataset)
class Dataset(object):
    """Objects of one portal type in one catalog.

    :param name: what a tile refers to the dataset by
    :param fields: the `Field`s a tile may filter and group by
    :param columns: the `Column`s a table may show
    :param spans: the `Span`s a tile may measure
    :param states: workflow states in the order a tile shows them;
        states the workflow has besides follow by name
    :param base_query: what every search starts from, besides the
        portal type
    :param listing: the page of the site that lists the objects, where
        the title of a tile leads
    :param url_column: metadata column with the URL a row leads to,
        for objects that are best seen elsewhere (an analysis in its
        sample)
    :param lab_only: hide the dataset from users outside the
        laboratory
    """

    def __init__(self, name, title, catalog, portal_type, fields,
                 columns=(), spans=(), states=(), base_query=None,
                 listing=None, url_column=None, icon=None,
                 lab_only=False):
        self.name = name
        self.title = title
        self.catalog = catalog
        self.portal_type = portal_type
        self.own_fields = list(fields)
        self.own_columns = list(columns)
        self.own_spans = list(spans)
        self.states = list(states)
        self.base_query = dict(base_query or {})
        self.listing = listing
        self.url_column = url_column
        self.icon = icon
        self.lab_only = lab_only

    def get_extensions(self):
        return [extension for name, extension
                in getUtilitiesFor(IDashboardDatasetExtension)
                if extension.dataset == self.name]

    def collect(self, attribute):
        """Own items and those of extensions, by name."""
        items = list(getattr(self, "own_" + attribute))
        for extension in self.get_extensions():
            items.extend(getattr(extension, attribute))
        return OrderedDict((item.name, item) for item in items)

    @property
    def fields(self):
        return self.collect("fields")

    @property
    def columns(self):
        return self.collect("columns")

    @property
    def spans(self):
        return self.collect("spans")

    def is_available(self, env):
        return env.is_lab or not self.lab_only

    def get_fields(self, env):
        return [field for field in self.fields.values()
                if field.is_available(env)]

    def get_field(self, name, env):
        field = self.fields.get(name)
        if field is None or not field.is_available(env):
            raise QueryError(_("Unknown field ${name}",
                               mapping={"name": name}))
        return field

    def get_columns(self, env):
        return [column for column in self.columns.values()
                if column.is_available(env)]

    def get_column(self, name, env):
        column = self.columns.get(name)
        if column is None or not column.is_available(env):
            raise QueryError(_("Unknown column ${name}",
                               mapping={"name": name}))
        return column

    def get_span(self, name):
        span = self.spans.get(name)
        if span is None:
            raise QueryError(_("Unknown span ${name}",
                               mapping={"name": name}))
        return span

    def get_states(self):
        """Workflow states in the order of the workflow.

        The curated order comes first, states it does not know follow.
        """
        wf_tool = api.get_tool("portal_workflow")
        known = []
        for workflow in wf_tool.getWorkflowsFor(self.portal_type):
            known.extend(workflow.states.objectIds())
        ordered = [state for state in self.states if state in known]
        return ordered + sorted(set(known) - set(ordered))

    def get_url(self, brain):
        """Where a row leads: the URL column if there is one."""
        if self.url_column:
            return getattr(brain, self.url_column, None) or brain.getURL()
        return brain.getURL()

    def describe(self, env):
        portal_url = api.get_url(env.portal)
        return {
            "name": self.name,
            "title": display_title(self.title),
            "icon": self.icon,
            "listing": self.listing and "/".join(
                [portal_url, self.listing]),
            "fields": [f.describe() for f in self.get_fields(env)],
            "columns": [c.describe() for c in self.get_columns(env)],
            "spans": [s.describe() for s in self.spans.values()],
        }


@implementer(IDashboardDatasetExtension)
class DatasetExtension(object):
    """Fields, columns and spans an add-on adds to a dataset."""

    def __init__(self, dataset, fields=(), columns=(), spans=()):
        self.dataset = dataset
        self.fields = list(fields)
        self.columns = list(columns)
        self.spans = list(spans)
