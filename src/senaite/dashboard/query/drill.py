# -*- coding: utf-8 -*-
"""The objects behind a number of a tile, for opening the tile.

A click on a part of a donut, a group of a bar list, a column of a
chart or the number of a count asks which objects it counts. They come
from the same search the tile counts with, narrowed the way the tile
split it: by a value of a field, by a period, or both. So the list
shows exactly the objects the number counts, as the current user may
see them.

An object of a list opens in the tile too, when its dataset links it
to other objects: a sample shows its analyses, an analysis opens its
sample.
"""

import json
from collections import Counter
from urllib import urlencode

from bika.lims import api
from senaite.dashboard import messagefactory as _
from senaite.dashboard.exceptions import NotFound
from senaite.dashboard.exceptions import ValidationError
from senaite.dashboard.query import timeline
from senaite.dashboard.query.compute import clean_source_params
from senaite.dashboard.query.compute import get_source
from senaite.dashboard.query.params import is_name
from senaite.dashboard.query.params import is_number
from senaite.dashboard.query.registry import get_dataset
from senaite.dashboard.query.search import build_query
from senaite.dashboard.query.search import count_values
from senaite.dashboard.query.search import get_index
from senaite.dashboard.query.search import get_index_value
from senaite.dashboard.query.search import get_rids
from senaite.dashboard.query.search import index_values
from senaite.dashboard.query.search import search
from senaite.dashboard.query.sources import DEFAULT_LIMIT
from senaite.dashboard.query.sources import DEFAULT_PERIODS
from senaite.dashboard.query.sources import MAX_GROUPS
from senaite.dashboard.query.sources import MAX_STACKS
from senaite.dashboard.query.sources import OTHER
from senaite.dashboard.query.sources import clamp
from senaite.dashboard.query.sources import count_per_period
from senaite.dashboard.query.sources import get_dataset_query
from senaite.dashboard.query.sources import get_date_field
from senaite.dashboard.query.sources import get_group_field
from senaite.dashboard.query.sources import get_group_labels
from senaite.dashboard.query.sources import get_periods
from senaite.dashboard.query.sources import to_cell
from senaite.dashboard.query.sources import to_groups
from senaite.dashboard.query.sources import to_iso
from senaite.dashboard.titles import display_title

# Rows of one answer; the page asks for more as the user scrolls on
PAGE_SIZE = 50
# Values a facet offers, the most frequent first
MAX_FACET_VALUES = 8

# The sources whose tiles open, and the parameter that splits them
SPLIT_PARAMS = {
    "count": None,
    "group": "group_by",
    "timeseries": "stack_by",
}


# Selection

def get_split_field(name, params, dataset, env):
    """The field the source split its count by, or None."""
    param = SPLIT_PARAMS[name]
    if not param or not params.get(param):
        return None
    return get_group_field(dataset, params[param], env)


def find_period(periods, bucket):
    """The period of a chart that starts at the bucket."""
    for start, end in periods:
        if to_iso(start) == bucket:
            return start, end
    raise ValidationError(_("This period is not shown any more. Refresh "
                            "the dashboard."))


def shown_keys(name, params, dataset, query, field, env):
    """The values a tile shows on their own; the rest is "Other"."""
    if name == "group":
        rids = get_rids(search(dataset, query))
        counts = count_values(dataset, rids, field)
        limit = clamp(params.get("limit"), DEFAULT_LIMIT, 1, MAX_GROUPS)
        groups = to_groups(counts, field, dataset, env, limit)
    else:
        date_field = get_date_field(dataset, params.get("date_field"), env)
        interval, periods = get_periods(params, DEFAULT_PERIODS, env)
        counts = count_per_period(dataset, query, date_field, periods,
                                  field)
        groups = to_groups(sum(counts, Counter()), field, dataset, env,
                           MAX_STACKS)
    return {group["key"] for group in groups} - {OTHER}


def has_value(values, key):
    return key in values


def has_other_value(values, shown):
    return any(value not in shown for value in values)


def narrow_by_value(dataset, rids, field, accept):
    """The objects whose values in the index of the field pass."""
    index = get_index(dataset.catalog, field.index)
    return [rid for rid in rids if accept(index_values(index, rid))]


def narrow_by_key(dataset, rids, field, key, other_keys):
    if key == OTHER:
        return narrow_by_value(dataset, rids, field,
                               lambda values: has_other_value(
                                   values, other_keys()))
    return narrow_by_value(dataset, rids, field,
                           lambda values: has_value(values, key))


def select_tile(tile, pick, env):
    """The dataset of a tile and the objects of the part picked.

    :param pick: {"key": value of the split field, "bucket": iso start
        of a period of a chart}; both optional
    :returns: (dataset, record ids, split field or None)
    """
    name = tile.get("source")
    if name not in SPLIT_PARAMS:
        raise ValidationError(_("This tile does not open"))
    params = clean_source_params(get_source(name), tile.get("params") or {})
    dataset, query = get_dataset_query(params, env)
    field = get_split_field(name, params, dataset, env)
    whole = dict(query)
    if name == "timeseries" and pick.get("bucket"):
        date_field = get_date_field(dataset, params.get("date_field"), env)
        interval, periods = get_periods(params, DEFAULT_PERIODS, env)
        start, end = find_period(periods, pick["bucket"])
        query[date_field.index] = timeline.to_range(start, end)
    rids = get_rids(search(dataset, query))
    key = pick.get("key")
    if field is not None and key is not None:
        def other_keys():
            return shown_keys(name, params, dataset, whole, field, env)
        rids = narrow_by_key(dataset, rids, field, key, other_keys)
    return dataset, rids, field


def find_brain(dataset, uid, env):
    """The object of the UID in the dataset, as the user may see it."""
    query = build_query(dataset, None, env)
    query["UID"] = uid
    results = search(dataset, query)
    if not len(results):
        raise NotFound(_("The object is gone or you may not see it"))
    return results[0]


def select_children(dataset, brain, env):
    """The objects shown below an opened object, and their dataset."""
    link = dataset.children
    children = get_dataset(link.dataset, env)
    query = build_query(children, None, env)
    query[link.index] = link.value(brain, dataset)
    return children, get_rids(search(children, query))


def follow_parent(dataset, brain, env):
    """The object a row opens instead of its own, e.g. its sample."""
    link = dataset.parent
    target = get_dataset(link.dataset, env)
    value = link.value(brain, dataset)
    if not value:
        raise NotFound(_("The object is gone or you may not see it"))
    query = build_query(target, None, env)
    query[link.index] = value
    results = search(target, query)
    if not len(results):
        raise NotFound(_("The object is gone or you may not see it"))
    return target, results[0]


# Facets

def facet_values(dataset, rids, field, env):
    """[{key, label, count}] of the most frequent values."""
    counts = count_values(dataset, rids, field)
    keys = sorted(counts, key=lambda k: (-counts[k], k))
    keys = keys[:MAX_FACET_VALUES]
    labels = get_group_labels(keys, field, dataset, env)
    return [{"key": key, "label": labels[key], "count": counts[key]}
            for key in keys if labels.get(key)]


def get_facets(dataset, split_field, env):
    """The fields to narrow by, but the one the tile split by."""
    split = split_field.name if split_field else None
    return [field for field in dataset.get_facets(env)
            if field.name != split]


def clean_scope(scope, facets):
    """The values picked per facet, of the facets offered only."""
    if not isinstance(scope, dict):
        raise ValidationError(_("Invalid parameter ${name}",
                                mapping={"name": "scope"}))
    names = {field.name for field in facets}
    cleaned = {}
    for name, value in scope.items():
        if value in (None, ""):
            continue
        if name not in names or not isinstance(value, basestring):
            raise ValidationError(_("Invalid parameter ${name}",
                                    mapping={"name": "scope"}))
        cleaned[name] = value
    return cleaned


def narrow_by_scope(dataset, rids, facets, scope):
    for field in facets:
        if field.name in scope:
            rids = narrow_by_value(
                dataset, rids, field,
                lambda values, key=scope[field.name]: key in values)
    return rids


def describe_facet(dataset, rids, field, scope, env):
    values = facet_values(dataset, rids, field, env)
    picked = scope.get(field.name)
    if len(values) < 2 and picked is None:
        return None
    return {
        "name": field.name,
        "title": field.describe()["title"],
        "picked": picked,
        "values": values,
    }


# Rows

def sort_key(value):
    """Objects without a value go last."""
    return (value is None, value)


def sort_rids(dataset, rids):
    index, order = dataset.sort
    values = {rid: get_index_value(dataset.catalog, index, rid)
              for rid in rids}
    ordered = sorted(rids, key=lambda rid: sort_key(values[rid]))
    if order == "descending":
        present = [rid for rid in ordered if values[rid] is not None]
        missing = [rid for rid in ordered if values[rid] is None]
        ordered = present[::-1] + missing
    return ordered


def get_brain(dataset, rid):
    """The catalog record of a record id, without a search."""
    return api.get_tool(dataset.catalog)._catalog[rid]


def to_slot(brain, column, dataset, env):
    return {"kind": column.kind,
            "value": to_cell(brain, column, dataset, env)}


def card_slots(brain, names, dataset, env):
    return [to_slot(brain, column, dataset, env)
            for column in dataset.find_columns(names, env)]


def get_state(brain, dataset):
    """The workflow state of the object, for its color."""
    state = getattr(brain, "review_state", None)
    return state if isinstance(state, basestring) else None


def opens(dataset, below=None):
    """Whether a row of the dataset opens in the tile.

    :param below: the dataset of the object the rows are shown below;
        a row that would open that object again does not open
    """
    if dataset.children:
        return True
    parent = dataset.parent
    return bool(parent) and (below is None or parent.dataset != below)


def to_row(brain, dataset, env, below=None):
    card = dataset.get_card(env)
    title = card_slots(brain, [card.title], dataset, env) \
        if card.title else []
    note = card_slots(brain, [card.note], dataset, env) \
        if card.note else []
    return {
        "uid": brain.UID,
        "dataset": dataset.name,
        "url": dataset.get_url(brain),
        "state": get_state(brain, dataset),
        "title": title[0]["value"] if title else brain.getId,
        "subtitle": card_slots(brain, card.subtitle, dataset, env),
        "detail": card_slots(brain, card.detail, dataset, env),
        "note": note[0] if note else None,
        "opens": opens(dataset, below),
    }


def to_fact(brain, column, dataset, env):
    fact = to_slot(brain, column, dataset, env)
    fact["title"] = column.describe()["title"]
    return fact


def describe_object(brain, dataset, env):
    row = to_row(brain, dataset, env)
    row["facts"] = [to_fact(brain, column, dataset, env)
                    for column in dataset.get_facts(env)]
    return row


def get_offset(body):
    offset = body.get("offset", 0)
    if not is_number(offset) or offset < 0:
        raise ValidationError(_("Invalid parameter ${name}",
                                mapping={"name": "offset"}))
    return offset


def narrow(dataset, rids, split_field, body, env):
    """The objects narrowed by the facets picked, with the facets and
    what was picked."""
    facets = get_facets(dataset, split_field, env)
    scope = clean_scope(body.get("scope") or {}, facets)
    return narrow_by_scope(dataset, rids, facets, scope), facets, scope


def listing_url(dataset, body, env):
    """The page that lists exactly the objects of a part of a tile.

    The request of the tile goes along in the URL; the page searches
    again with it, as the user who opens it.
    """
    request = {key: body[key] for key in ("tile", "pick", "scope")
               if body.get(key)}
    query = urlencode({"drill": json.dumps(request, sort_keys=True)})
    portal_url = api.get_url(env.portal)
    return "{}/{}?{}".format(portal_url, dataset.drill_view, query)


def list_answer(dataset, rids, split_field, body, env, below=None):
    """The rows of a page of the objects, with the facets to narrow by."""
    narrowed, facets, scope = narrow(dataset, rids, split_field, body, env)
    offset = get_offset(body)
    page = sort_rids(dataset, narrowed)[offset:offset + PAGE_SIZE]
    described = [describe_facet(dataset, narrowed, field, scope, env)
                 for field in facets]
    return {
        "dataset": dataset.name,
        "total": len(narrowed),
        "offset": offset,
        "facets": [facet for facet in described if facet],
        "rows": [to_row(get_brain(dataset, rid), dataset, env, below)
                 for rid in page],
    }


def open_object(body, env):
    """An object opened in a tile, with the objects below it."""
    target = body.get("object")
    if not isinstance(target, dict) or not is_name(target.get("dataset")):
        raise ValidationError(_("Invalid parameter ${name}",
                                mapping={"name": "object"}))
    uid = target.get("uid")
    if not isinstance(uid, basestring) or not uid:
        raise ValidationError(_("Invalid parameter ${name}",
                                mapping={"name": "object"}))
    dataset = get_dataset(target["dataset"], env)
    brain = find_brain(dataset, uid, env)
    if dataset.parent and not dataset.children:
        dataset, brain = follow_parent(dataset, brain, env)
    answer = {"object": describe_object(brain, dataset, env)}
    if dataset.children:
        children, rids = select_children(dataset, brain, env)
        answer.update(list_answer(children, rids, None, body, env,
                                  below=dataset.name))
        title = dataset.children.title
        answer["section"] = display_title(title) if title else None
    return answer


def check_tile_request(body):
    """The tile and the part of it a request asks for."""
    tile = body.get("tile")
    pick = body.get("pick") or {}
    if not isinstance(tile, dict) or not isinstance(pick, dict):
        raise ValidationError(_("Invalid parameter ${name}",
                                mapping={"name": "tile"}))
    for name in ("key", "bucket"):
        value = pick.get(name)
        if value is not None and not isinstance(value, basestring):
            raise ValidationError(_("Invalid parameter ${name}",
                                    mapping={"name": name}))
    return tile, pick


def select(body, env):
    """The dataset and the UIDs of the objects of a part of a tile,
    narrowed by the facets picked; for the page that lists them."""
    if not isinstance(body, dict):
        raise ValidationError(_("Invalid parameter ${name}",
                                mapping={"name": "drill"}))
    tile, pick = check_tile_request(body)
    dataset, rids, field = select_tile(tile, pick, env)
    narrowed, facets, scope = narrow(dataset, rids, field, body, env)
    uids = [get_index_value(dataset.catalog, "UID", rid)
            for rid in sort_rids(dataset, narrowed)]
    return dataset, [uid for uid in uids if uid]


def drill(body, env):
    """The objects behind a part of a tile, or an object opened in it.

    Body: {"tile": {"source", "params"}, "pick": {"key", "bucket"}} or
    {"object": {"dataset", "uid"}}, and in both cases "scope": {facet
    name: value} and "offset".
    """
    if "object" in body:
        return open_object(body, env)
    tile, pick = check_tile_request(body)
    dataset, rids, field = select_tile(tile, pick, env)
    answer = list_answer(dataset, rids, field, body, env)
    answer["listing"] = listing_url(dataset, body, env)
    return answer
