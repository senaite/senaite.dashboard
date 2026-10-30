# -*- coding: utf-8 -*-
"""Datasets managers define in the browser.

A definition names a type, the indexes of its catalog a tile may
filter and group by, the metadata a table may show and the spans of
time a tile may measure. It is kept on the site (see storage.py) and
checked against the catalog whenever it is saved (see catalogs.py).
At runtime it becomes a `Dataset` like the ones of the code, so every
source, filter and label works with it unchanged.

New datasets and their fields are for the laboratory only, unless the
manager opens them to client contacts.
"""

import uuid

from senaite.dashboard import messagefactory as _
from senaite.dashboard import storage
from senaite.dashboard.access import check_manage
from senaite.dashboard.exceptions import NotFound
from senaite.dashboard.exceptions import QueryError
from senaite.dashboard.query import catalogs
from senaite.dashboard.query import fields as kinds
from senaite.dashboard.query.datasets import COL_DATE
from senaite.dashboard.query.datasets import COL_NUMBER
from senaite.dashboard.query.datasets import COL_STATE
from senaite.dashboard.query.datasets import COL_TEXT
from senaite.dashboard.query.datasets import Column
from senaite.dashboard.query.datasets import Dataset
from senaite.dashboard.query.datasets import Span
from senaite.dashboard.query.fields import Field
from senaite.dashboard.titles import clean_title
from senaite.dashboard.titles import slugify
from senaite.dashboard.titles import title_text

# Names of datasets defined in the browser start with it, so that they
# never stand in for a dataset of the code
PREFIX = "custom-"

MAX_DATASETS = 50
MAX_FIELDS = 40
MAX_COLUMNS = 40
MAX_SPANS = 10

# Kinds of columns a table may show the values of a dataset as
COLUMN_KINDS = (COL_TEXT, COL_DATE, COL_NUMBER, COL_STATE)


def is_custom(name):
    return isinstance(name, basestring) and name.startswith(PREFIX)


def is_lab_only(item):
    """Only for the laboratory, unless the item says otherwise."""
    return item.get("lab_only", True) is not False


def required_title(title, message):
    title = clean_title(title)
    if not title:
        raise QueryError(message)
    return title


def clean_name(value, message):
    """The name of an index or a column; catalogs name them in ASCII."""
    if not isinstance(value, basestring) or not value:
        raise QueryError(message)
    try:
        return str(value)
    except UnicodeEncodeError:
        raise QueryError(message)


def clean_field(item, indexes, candidates):
    """A field of a definition, checked against the catalog."""
    if not isinstance(item, dict):
        raise QueryError(_("A field must be a mapping"))
    name = clean_name(item.get("index"), _("A field needs an index"))
    index = indexes.get(name)
    if index is None:
        raise QueryError(_("The index ${name} cannot be used",
                           mapping={"name": name}))
    kind = item.get("kind")
    if kind not in catalogs.FIELD_KINDS[index.meta_type]:
        raise QueryError(_("${name} cannot be a field of kind ${kind}",
                           mapping={"name": name, "kind": kind}))
    target = None
    if kind == kinds.REFERENCE:
        target = item.get("portal_type")
        if target not in [c["portal_type"] for c in candidates]:
            raise QueryError(_("${name} needs the type it points to",
                               mapping={"name": name}))
    return {
        "index": name,
        "title": clean_title(item.get("title")) or name,
        "kind": kind,
        "portal_type": target,
        "lab_only": is_lab_only(item),
    }


def clean_column(item, offered):
    if not isinstance(item, dict):
        raise QueryError(_("A column must be a mapping"))
    name = clean_name(item.get("name"), _("A column needs a name"))
    if name not in offered:
        raise QueryError(_("The column ${name} cannot be shown",
                           mapping={"name": name}))
    kind = item.get("kind")
    if kind not in COLUMN_KINDS:
        kind = COL_TEXT
    return {"name": name, "title": clean_title(item.get("title")) or name,
            "kind": kind, "lab_only": is_lab_only(item)}


def span_name(title):
    """A name for a span; a tile only names one starting with a letter."""
    name = slugify(title, "span")
    return name if name[0].isalpha() else "span-" + name


def clean_span(item, offered, date_indexes):
    """A span: from one date to another, the end also an index.

    The source sorts by the end, so it must be an index; both dates are
    read from the metadata.
    """
    if not isinstance(item, dict):
        raise QueryError(_("A span must be a mapping"))
    title = required_title(item.get("title"), _("A span needs a title"))
    start, end = item.get("start"), item.get("end")
    dates = start in offered and end in offered
    if not dates or end not in date_indexes:
        raise QueryError(_("A span needs two dates of the type"))
    return {"name": span_name(title), "title": title,
            "start": start, "end": end}


def clean_items(items, maximum, clean):
    """Checked items, the first of each name only."""
    if not isinstance(items, list) or len(items) > maximum:
        raise QueryError(_("At most ${count} entries",
                           mapping={"count": maximum}))
    seen = set()
    cleaned = []
    for item in map(clean, items):
        key = item.get("index") or item["name"]
        if key not in seen:
            seen.add(key)
            cleaned.append(item)
    return cleaned


def clean_definition(body):
    """A definition as it is kept, every part checked."""
    if not isinstance(body, dict):
        raise QueryError(_("A dataset must be a mapping"))
    candidates = catalogs.get_candidates()
    candidate = catalogs.get_candidate(body.get("portal_type"), candidates)
    catalog_id = candidate["catalog"]
    indexes = catalogs.get_offered_indexes(catalog_id)
    offered = set(catalogs.get_offered_columns(catalog_id))
    date_indexes = catalogs.get_date_indexes(indexes)
    return {
        "title": required_title(body.get("title"),
                                _("A dataset needs a title")),
        "portal_type": candidate["portal_type"],
        "catalog": catalog_id,
        "lab_only": is_lab_only(body),
        "fields": clean_items(
            body.get("fields") or [], MAX_FIELDS,
            lambda item: clean_field(item, indexes, candidates)),
        "columns": clean_items(
            body.get("columns") or [], MAX_COLUMNS,
            lambda item: clean_column(item, offered)),
        "spans": clean_items(
            body.get("spans") or [], MAX_SPANS,
            lambda item: clean_span(item, offered, date_indexes)),
    }


def new_name(title):
    """A name for a new dataset that is not taken yet."""
    base = PREFIX + slugify(title, "dataset")
    name = base
    number = 1
    while storage.get_dataset(name) is not None:
        number += 1
        name = "{}-{}".format(base, number)
    return name


def save(body, env):
    """Create a dataset, or change the one the body names."""
    check_manage(env)
    record = clean_definition(body)
    name = body.get("name")
    existing = storage.get_dataset(name) if is_custom(name) else None
    if existing is None:
        if len(storage.list_datasets()) >= MAX_DATASETS:
            raise QueryError(_("There can be at most ${count} datasets",
                               mapping={"count": MAX_DATASETS}))
        name = new_name(record["title"])
    record.update({
        "name": name,
        "revision": (existing or {}).get("revision", 0) + 1,
        # Unique per save, also when a removed dataset's name comes
        # back: cached answers are keyed by it
        "version": uuid.uuid4().hex,
        "modified": env.now.ISO8601(),
        "modified_by": env.user_id,
    })
    storage.set_dataset(record)
    return record


def remove(name, env):
    check_manage(env)
    if not is_custom(name) or storage.get_dataset(name) is None:
        raise NotFound(_("There is no dataset ${name}",
                         mapping={"name": name}))
    storage.delete_dataset(name)


def list_definitions(env):
    check_manage(env)
    records = storage.list_datasets()
    return sorted(records, key=lambda record: title_text(
        record["title"], env.language).lower())


def is_offered_field(item):
    return catalogs.is_offered(item["index"])


def is_offered_column(item):
    return catalogs.is_offered(item["name"])


def is_offered_span(item):
    return catalogs.is_offered(item["start"]) and catalogs.is_offered(
        item["end"])


def get_lab_only_indexes(record):
    """The indexes of the fields only the laboratory may use."""
    return {item["index"] for item in record["fields"] if is_lab_only(item)}


def to_field(item):
    return Field(item["index"], item["title"], item["kind"],
                 portal_type=item.get("portal_type"),
                 lab_only=is_lab_only(item))


def to_column(item, lab_only_indexes):
    """A column; lab-only unless it is opened to client contacts, and
    always when it shows the values of a lab-only field."""
    lab_only = is_lab_only(item) or item["name"] in lab_only_indexes
    return Column(item["name"], item["title"], item["kind"],
                  lab_only=lab_only)


def to_span(item):
    return Span(item["name"], item["title"], item["start"], item["end"])


def to_dataset(record):
    """The dataset a definition stands for.

    What the catalogs must never offer is left out here too, so that a
    definition saved before a name was blocked does not offer it.
    """
    lab_only_indexes = get_lab_only_indexes(record)
    dataset = Dataset(
        name=record["name"],
        title=record["title"],
        catalog=record["catalog"],
        portal_type=record["portal_type"],
        icon="list",
        lab_only=record["lab_only"],
        fields=[to_field(item) for item in record["fields"]
                if is_offered_field(item)],
        columns=[to_column(item, lab_only_indexes)
                 for item in record["columns"] if is_offered_column(item)],
        spans=[to_span(item) for item in record["spans"]
               if is_offered_span(item)],
    )
    dataset.version = (record["revision"], record.get("version"))
    return dataset


def get_dataset(name):
    """The dataset of a definition, or None."""
    record = storage.get_dataset(name) if is_custom(name) else None
    return to_dataset(record) if record is not None else None


def get_datasets():
    return [to_dataset(record) for record in storage.list_datasets()]


def uses_dataset(tile, name):
    return (tile.get("params") or {}).get("dataset") == name


def is_used_by(record, name):
    """Whether a draft or the published version of a global dashboard
    has a tile on the dataset."""
    tiles = list(record["draft"]["tiles"])
    tiles.extend((record.get("published") or {}).get("tiles") or [])
    return any(uses_dataset(tile, name) for tile in tiles)


def count_usage(name, env):
    """How many global dashboards and saved tiles use the dataset.

    Personal dashboards are not searched: they are many, and only their
    owner sees the tile that has no dataset any more.
    """
    check_manage(env)
    return {
        "dashboards": len([record for record in storage.list_globals()
                           if is_used_by(record, name)]),
        "library": len([record for record in storage.list_library_tiles()
                        if uses_dataset(record["tile"], name)]),
    }
