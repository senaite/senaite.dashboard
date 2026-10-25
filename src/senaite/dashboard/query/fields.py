# -*- coding: utf-8 -*-
"""The fields of a dataset: what a tile may filter and group by.

A field names a catalog index and says what kind of values it holds.
The kind decides how a filter value becomes a catalog query, where the
choices for the tile editor come from, and how a raw index value is
shown to the user.
"""

from bika.lims import api
from senaite.core.api import dtime
from senaite.core.i18n import translate
from senaite.dashboard import messagefactory as _
from senaite.dashboard.exceptions import QueryError
from senaite.dashboard.query.variables import UNSET
from senaite.dashboard.titles import display_title

# Kinds of fields
STATE = "state"
REFERENCE = "reference"
USER = "user"
KEYWORD = "keyword"
DATE = "date"
BOOLEAN = "boolean"
TEXT = "text"
CHOICE = "choice"

# A filter on a list of values is one OR query; this caps its length
MAX_FILTER_VALUES = 100


class Field(object):
    """A catalog index a tile may filter or group by.

    :param index: the catalog index
    :param title: message id shown in the tile editor
    :param kind: one of the kinds above
    :param portal_type: for references, the type the UIDs point to
    :param groupable: whether a tile may group by this field
    :param lab_only: hide the field from users outside the laboratory
    :param choices: for choices, the values and their titles (message
        ids) in the order they are offered and grouped in
    """

    def __init__(self, index, title, kind, portal_type=None,
                 groupable=True, lab_only=False, choices=()):
        self.index = index
        self.title = title
        self.kind = kind
        self.portal_type = portal_type
        self.groupable = groupable and kind != DATE
        self.lab_only = lab_only
        self.choices = list(choices)

    @property
    def name(self):
        return self.index

    def is_available(self, env):
        """Whether the user may filter and group by the field."""
        return env.is_lab or not self.lab_only

    def get_choice_values(self):
        return [value for value, title in self.choices]

    def get_choice_title(self, value):
        """The translated title of a value of a choice field."""
        titles = dict(self.choices)
        if value not in titles:
            return api.safe_unicode(value)
        return translate(titles[value], to_utf8=False)

    def describe(self):
        return {
            "name": self.name,
            "title": display_title(self.title),
            "kind": self.kind,
            "groupable": self.groupable,
        }


def to_list(value):
    """Return the value as a list of its non-empty items."""
    if not isinstance(value, (list, tuple)):
        value = [value]
    return [item for item in value if item not in (None, "", UNSET)]


def to_date_query(value):
    """Return a DateIndex range query for {"min": ..., "max": ...}."""
    if not isinstance(value, dict):
        raise QueryError(_("A date filter needs a min or a max"))
    bounds = []
    ranges = []
    for key in ("min", "max"):
        if value.get(key) in (None, "", UNSET):
            continue
        date = dtime.to_DT(value[key])
        if date is None:
            raise QueryError(_("Not a date: ${value}",
                               mapping={"value": value[key]}))
        bounds.append(date)
        ranges.append(key)
    if not bounds:
        return UNSET
    return {"query": bounds, "range": ":".join(ranges)}


def to_values_query(value):
    """Return a FieldIndex/KeywordIndex query for one or many values.

    `{"not": [...]}` excludes values instead.
    """
    negate = isinstance(value, dict)
    values = to_list(value.get("not") if negate else value)
    if len(values) > MAX_FILTER_VALUES:
        raise QueryError(_("A filter takes at most ${count} values",
                           mapping={"count": MAX_FILTER_VALUES}))
    if not all(isinstance(item, basestring) for item in values):
        raise QueryError(_("Filter values must be text"))
    if not values:
        return UNSET
    return {"not": values} if negate else {"query": values}


def to_boolean_query(value):
    """Return a BooleanIndex query for true or false."""
    if not isinstance(value, bool):
        raise QueryError(_("A yes or no filter needs true or false"))
    return value


def to_query(field, value):
    """Return the catalog query of a filter on the field.

    UNSET means the filter does not apply and is left out.
    """
    if value is UNSET:
        return UNSET
    if field.kind == DATE:
        return to_date_query(value)
    if field.kind == BOOLEAN:
        return to_boolean_query(value)
    return to_values_query(value)


def get_by_kind(registry, field):
    """What the registry holds for the kind of the field.

    An unknown kind is an error rather than a fallback that shows raw
    index values: a raw value may be something the user must not see.

    :param registry: {kind: function}
    :raises QueryError: when the registry does not know the kind
    """
    function = registry.get(field.kind)
    if function is None:
        raise QueryError(_("Fields of kind ${kind} cannot be shown",
                           mapping={"kind": field.kind}))
    return function
