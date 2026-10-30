# -*- coding: utf-8 -*-
"""Proposals for a new dataset, with examples.

When a manager picks a type, the editor shows what its catalog offers
(see catalogs.py), each index with the kind of field it most likely
is and each column with the kind of its values, both with a few
examples. The examples come from the objects the manager may see and
are labelled the way the dashboard would label them.
"""

from bika.lims import api
from DateTime import DateTime
from senaite.dashboard.access import check_manage
from senaite.dashboard.query import catalogs
from senaite.dashboard.query import fields as kinds
from senaite.dashboard.query.datasets import COL_DATE
from senaite.dashboard.query.datasets import COL_NUMBER
from senaite.dashboard.query.datasets import COL_STATE
from senaite.dashboard.query.datasets import COL_TEXT
from senaite.dashboard.query.datasets import Dataset
from senaite.dashboard.query.fields import Field
from senaite.dashboard.query.labels import get_labels
from senaite.dashboard.query.search import NONE
from senaite.dashboard.query.search import count_values
from senaite.dashboard.query.search import get_metadata
from senaite.dashboard.query.search import get_rids

# Objects looked at to propose the kinds of columns and show examples
SAMPLE_SIZE = 200
SAMPLE_VALUES = 5

# Indexes that hold user ids
USER_INDEXES = ("Creator", "getAnalyst", "getReceivedBy", "getSubmittedBy",
                "getVerifiers")


def type_key(name):
    """A name to compare types by: lower case, without underscores."""
    return name.lower().replace("_", "")


def guess_reference_type(index_name, candidates):
    """The type a UID index points to.

    getClientUID points to Client, sampletype_uid to SampleType.
    """
    name = type_key(index_name)
    name = name[3:] if name.startswith("get") else name
    for suffix in ("uids", "uid"):
        if name.endswith(suffix):
            name = name[:-len(suffix)]
            break
    for candidate in candidates:
        if type_key(candidate["portal_type"]) == name:
            return candidate["portal_type"]
    return None


def guess_field_kind(index):
    name = index.getId()
    if index.meta_type == "DateIndex":
        return kinds.DATE
    if index.meta_type == "BooleanIndex":
        return kinds.BOOLEAN
    if name == "review_state":
        return kinds.STATE
    if catalogs.is_uid_name(name):
        return kinds.REFERENCE
    if name in USER_INDEXES:
        return kinds.USER
    return kinds.TEXT


def guess_column_kind(name, values):
    if name == "review_state":
        return COL_STATE
    present = [value for value in values if value not in (None, "")]
    if present and all(isinstance(value, DateTime) for value in present):
        return COL_DATE
    if present and all(isinstance(value, (int, long, float))
                       and not isinstance(value, bool)
                       for value in present):
        return COL_NUMBER
    return COL_TEXT


def search_type(catalog_id, portal_type):
    return api.search({"portal_type": portal_type}, catalog_id)


def to_text(value):
    if isinstance(value, DateTime):
        return value.ISO8601()
    return api.safe_unicode(value)


def get_column_values(brains, name):
    return [get_metadata(brain, name) for brain in brains]


def sample_column_values(values):
    """Some values of a metadata column, leaving out empty ones.

    A brain answers `Missing.Value` for metadata an object did not
    have when it was cataloged; it reads as an empty text.
    """
    texts = [to_text(value).strip() for value in values
             if value not in (None, [], ())]
    return [text for text in texts if text][:SAMPLE_VALUES]


def sample_field_values(dataset, rids, field, env):
    """Some values of the field, labelled as the user would see them."""
    counts = count_values(dataset, rids, field)
    values = [value for value, count in counts.most_common()
              if value != NONE][:SAMPLE_VALUES]
    if field.kind == kinds.DATE:
        return [catalogs.index_date_text(value) for value in values]
    if field.kind not in (kinds.REFERENCE, kinds.STATE, kinds.USER,
                          kinds.BOOLEAN):
        return [to_text(value) for value in values]
    labels = get_labels(values, field, dataset, env)
    return [labels[value] for value in values if labels.get(value)]


def describe_index(dataset, rids, index, candidates, env):
    """What the editor offers for an index: its kinds and examples."""
    kind = guess_field_kind(index)
    target = None
    if kind == kinds.REFERENCE:
        target = guess_reference_type(index.getId(), candidates)
        kind = kind if target else kinds.TEXT
    field = Field(index.getId(), index.getId(), kind, portal_type=target)
    return {
        "index": index.getId(),
        "meta_type": index.meta_type,
        "kinds": list(catalogs.FIELD_KINDS[index.meta_type]),
        "kind": kind,
        "portal_type": target,
        "samples": sample_field_values(dataset, rids, field, env),
    }


def describe_column(brains, name):
    values = get_column_values(brains, name)
    return {
        "name": name,
        "kind": guess_column_kind(name, values),
        "samples": sample_column_values(values),
    }


def inspect(portal_type, env):
    """What a dataset of the type may offer, with examples.

    The examples come from the objects the manager may see, labelled
    the way the dashboard would label them.
    """
    check_manage(env)
    candidates = catalogs.get_candidates()
    candidate = catalogs.get_candidate(portal_type, candidates)
    catalog_id = candidate["catalog"]
    probe = Dataset("probe", u"", catalog_id, portal_type, [])
    results = search_type(catalog_id, portal_type)
    rids = get_rids(results)[:SAMPLE_SIZE]
    brains = list(results[:SAMPLE_SIZE])
    indexes = catalogs.get_offered_indexes(catalog_id)
    return {
        "type": candidate,
        "count": len(results),
        "fields": [describe_index(probe, rids, indexes[name], candidates,
                                  env) for name in sorted(indexes)],
        "columns": [describe_column(brains, name)
                    for name in catalogs.get_offered_columns(catalog_id)],
        "date_indexes": sorted(catalogs.get_date_indexes(indexes)),
        "candidates": candidates,
    }
