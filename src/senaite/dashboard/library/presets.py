# -*- coding: utf-8 -*-
"""The tile library as a user sees it.

Presets come from every provider, a named utility providing
IDashboardPresetProvider: the ones senaite.dashboard ships with, the
tiles managers saved, and those of add-ons. A user is offered only the
presets whose dataset and fields they may use.
"""

from senaite.core.i18n import translate
from senaite.dashboard.exceptions import QueryError
from senaite.dashboard.interfaces import IDashboardPresetProvider
from senaite.dashboard.library.builtin import CATEGORIES
from senaite.dashboard.library.builtin import GENERAL_CATEGORY
from senaite.dashboard.query.registry import get_dataset
from zope.component import getUtilitiesFor


# Parameters of a tile that name a field
FIELD_PARAMS = ("group_by", "stack_by", "date_field", "sort_on")


def as_mapping(value):
    return value if isinstance(value, dict) else {}


def get_used_fields(params):
    """Names of the fields a tile filters, groups or sorts by.

    A saved tile is checked only as far as a tile is, so its parameters
    may be of any kind; whatever is not a name names no field.
    """
    names = list(as_mapping(params.get("filters")))
    names.extend(params.get(key) for key in FIELD_PARAMS)
    names.append(as_mapping(params.get("trend")).get("date_field"))
    return [name for name in names if name and isinstance(name, basestring)]


def is_available(preset, env):
    """Whether the user may use everything the preset asks for."""
    params = as_mapping(preset["tile"].get("params"))
    if not params.get("dataset"):
        return True
    try:
        dataset = get_dataset(params["dataset"], env)
        for name in get_used_fields(params):
            dataset.get_field(name, env)
    except QueryError:
        return False
    return True


def get_presets(env):
    """Return the presets the user can use, from all providers."""
    presets = []
    for name, provider in getUtilitiesFor(IDashboardPresetProvider):
        presets.extend(p for p in provider(env) if is_available(p, env))
    return presets


def get_provided_categories():
    """Categories of the add-ons, in the order of their providers."""
    categories = []
    for name, provider in sorted(
            getUtilitiesFor(IDashboardPresetProvider)):
        categories.extend(getattr(provider, "categories", ()))
    return categories


def get_categories():
    """All categories; those of add-ons before "General"."""
    categories = CATEGORIES + get_provided_categories() + [GENERAL_CATEGORY]
    return [{"id": key, "title": translate(title, to_utf8=False)}
            for key, title in categories]
