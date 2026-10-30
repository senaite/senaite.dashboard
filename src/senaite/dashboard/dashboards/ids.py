# -*- coding: utf-8 -*-
"""Ids of dashboards.

Personal dashboards get ids with a prefix of their own, and global
ones never start with it, so the id alone tells which kind a dashboard
is.
"""

import re

from senaite.dashboard.titles import new_id
from senaite.dashboard.titles import slugify
from senaite.dashboard.titles import unique_id

PERSONAL_PREFIX = "personal-"
GLOBAL_PREFIX = "global-"

DASHBOARD_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}\Z")


def is_dashboard_id(value):
    return isinstance(value, basestring) and bool(
        DASHBOARD_ID_RE.match(value))


def is_personal(dashboard_id):
    return dashboard_id.startswith(PERSONAL_PREFIX)


def global_slug(title):
    """An id for a global dashboard; never one of a personal one."""
    slug = slugify(title, "dashboard")
    if is_personal(slug):
        slug = GLOBAL_PREFIX + slug
    return slug


def new_global_id(title, exists):
    """An id for a new global dashboard that is not taken yet."""
    return unique_id(global_slug(title), exists)


def new_personal_id():
    return PERSONAL_PREFIX + new_id()
