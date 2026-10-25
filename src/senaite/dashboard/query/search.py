# -*- coding: utf-8 -*-
"""Turn the filters of a tile into a catalog search, and count it.

Every search goes through `searchResults`, so the catalog filters the
results by the permissions of the current user. A tile on a global
dashboard therefore shows each user the numbers of what they may see.
"""

from collections import Counter

from bika.lims import api
from senaite.dashboard import messagefactory as _
from senaite.dashboard.exceptions import QueryError
from senaite.dashboard.query.fields import to_query
from senaite.dashboard.query.variables import UNSET
from senaite.dashboard.query.variables import resolve

# Key of the count of objects without a value
NONE = "__none__"


def build_query(dataset, filters, env):
    """Return the catalog query for the filters of a tile.

    :param filters: {index: value}, values may hold placeholders
    """
    if filters and not isinstance(filters, dict):
        raise QueryError(_("Filters must be a mapping"))
    query = dict(dataset.base_query)
    query["portal_type"] = dataset.portal_type
    for name, value in (filters or {}).items():
        field = dataset.get_field(name, env)
        index_query = to_query(field, resolve(value, env))
        if index_query is not UNSET:
            query[field.index] = index_query
    return query


def search(dataset, query):
    """Search the catalog of the dataset as the current user."""
    return api.search(query, dataset.catalog)


def get_rids(results):
    """Return the record ids of a result set without loading brains.

    An unsorted search returns a LazyMap whose `_seq` holds the record
    ids (checked against Products.ZCatalog 5.4). Any other result
    (sorted, scored, merged) keeps something else there; then the
    brains tell the ids.
    """
    rids = list(getattr(results, "_seq", None) or [])
    if len(rids) == len(results) and all(
            isinstance(rid, (int, long)) for rid in rids):
        return rids
    return [brain.getRID() for brain in results]


def get_index(catalog_id, name):
    catalog = api.get_tool(catalog_id)
    return catalog._catalog.getIndex(name)


def get_index_value(catalog_id, name, rid):
    """The value an object has in an index, read from the index."""
    return get_index(catalog_id, name).getEntryForObject(rid, None)


def index_values(index, rid):
    """The values an object has in an index, as a list."""
    value = index.getEntryForObject(rid, None)
    values = value if isinstance(value, (list, tuple)) else [value]
    values = [NONE if item in (None, "") else item for item in values]
    return values or [NONE]


def count_values(dataset, rids, field):
    """Count the objects per value of the field.

    The values come from the index, not from the objects or brains.
    """
    index = get_index(dataset.catalog, field.index)
    counts = Counter()
    for rid in rids:
        counts.update(index_values(index, rid))
    return counts
