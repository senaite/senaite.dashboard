# -*- coding: utf-8 -*-
"""What the catalogs of SENAITE offer to datasets defined in the browser.

Three rules decide what a manager may pick:

- Only types with a catalog of their own are offered: those of
  SENAITE and its add-ons. Types the generic catalogs keep are types
  of the CMS underneath, and are left out; so is every type that is
  personal data as a whole.
- Only indexes whose kind of values a field understands are offered,
  and only metadata a table can show.
- What the catalog needs for itself, who may see an object, personal
  data and results are never offered. The catalog knows no permission
  per field, so a dataset could not keep such values from a user who
  may see the object.
"""

from Acquisition import aq_base
from bika.lims import api
from bika.lims import senaiteMessageFactory as _c
from senaite.core.i18n import translate
from senaite.dashboard import messagefactory as _
from senaite.dashboard.exceptions import QueryError
from senaite.dashboard.query import fields as kinds

# Catalogs that are not SENAITE's own: a type kept only there is a
# type of the CMS underneath, not of the laboratory
GENERIC_CATALOGS = ("portal_catalog", "uid_catalog")

# Types that are personal data as a whole, and the site itself, which
# is a single object and nothing to count
EXCLUDED_TYPES = ("Patient", "Plone Site")

# Indexes and metadata that are never offered: results, the roles
# and users that may see an object, and parts of names that stand for
# personal data
BLOCKED_NAMES = ("getResult", "getFormattedResult", "getResultsRange",
                 "allowedRolesAndUsers")
BLOCKED_PARTS = ("patient", "medicalrecord", "email", "phone", "fax",
                 "mobile", "password", "birth")

# Indexes and metadata the catalog needs for itself; they mean nothing
# on a tile
INTERNAL_NAMES = ("object_provides", "path", "portal_type", "Type",
                  "meta_type", "UID", "sortable_title", "SearchableText",
                  "listing_searchable_text", "getObjPositionInParent",
                  "is_folderish", "exclude_from_nav", "getIcon",
                  "cmf_uid", "in_reply_to", "total_comments", "sync_uid")

# Kinds of fields, by the type of index they fit
FIELD_KINDS = {
    "DateIndex": (kinds.DATE,),
    "BooleanIndex": (kinds.BOOLEAN,),
    "FieldIndex": (kinds.TEXT, kinds.STATE, kinds.REFERENCE, kinds.USER),
    "KeywordIndex": (kinds.TEXT, kinds.REFERENCE, kinds.USER),
}


def is_blocked(name):
    """Whether an index or column must never be offered."""
    lowered = name.lower()
    return name in BLOCKED_NAMES or any(
        part in lowered for part in BLOCKED_PARTS)


def is_offered(name):
    """Whether a manager may pick an index or column at all."""
    return name not in INTERNAL_NAMES and not is_blocked(name)


def get_own_catalog(portal_type):
    """The catalog SENAITE keeps the type in, or None for CMS types."""
    for catalog in api.get_catalogs_for(portal_type):
        if catalog.getId() not in GENERIC_CATALOGS:
            return catalog.getId()
    return None


def get_type_title(fti):
    return translate(_c(fti.Title()), to_utf8=False)


def is_content_type(fti):
    """Whether the type is an Archetypes or Dexterity type.

    Older type informations of the CMS have neither; looking up their
    catalogs would fail, and they are not SENAITE's anyway.
    """
    fti = aq_base(fti)
    return bool(getattr(fti, "product", None) or getattr(fti, "klass", None))


def to_candidate(fti):
    """A type a dataset may be made of, or None."""
    portal_type = fti.getId()
    if portal_type in EXCLUDED_TYPES or not is_content_type(fti):
        return None
    catalog = get_own_catalog(portal_type)
    if catalog is None:
        return None
    return {"portal_type": portal_type, "title": get_type_title(fti),
            "catalog": catalog}


def get_candidates():
    """The types a dataset may be made of, by title."""
    tool = api.get_tool("portal_types")
    candidates = filter(None, map(to_candidate, tool.listTypeInfo()))
    return sorted(candidates, key=lambda item: item["title"].lower())


def get_candidate(portal_type, candidates):
    """The candidate of the type, out of `get_candidates()`."""
    for candidate in candidates:
        if candidate["portal_type"] == portal_type:
            return candidate
    raise QueryError(_("A dataset cannot be made of ${type}",
                       mapping={"type": portal_type}))


def get_offered_indexes(catalog_id):
    """{name: index} of the indexes a field may stand for."""
    catalog = api.get_tool(catalog_id)
    return {index.getId(): index for index in catalog.getIndexObjects()
            if index.meta_type in FIELD_KINDS and is_offered(index.getId())}


def is_uid_name(name):
    """Whether an index or column holds UIDs, e.g. getClientUID."""
    return name.lower().endswith(("uid", "uids"))


def get_offered_columns(catalog_id):
    """The metadata columns a table may show.

    Columns of UIDs are left out: a UID in a table means nothing to a
    user, and a field shows the title of what it points to instead.
    """
    catalog = api.get_tool(catalog_id)
    return sorted(name for name in catalog.schema()
                  if is_offered(name) and not is_uid_name(name))


def get_date_indexes(indexes):
    """The names of the date indexes among {name: index}."""
    return {name for name, index in indexes.items()
            if index.meta_type == "DateIndex"}


def index_date_text(value):
    """The date a DateIndex keeps as minutes, as YYYY-MM-DD (UTC).

    The index stores (((year * 12 + month) * 31 + day) * 24 + hour) *
    60 + minute, with months and days counted from 1.
    """
    days = value // 60 // 24
    day = (days - 1) % 31 + 1
    months = (days - day) // 31
    month = (months - 1) % 12 + 1
    year = (months - month) // 12
    return u"{:04d}-{:02d}-{:02d}".format(year, month, day)
