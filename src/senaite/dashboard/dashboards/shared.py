# -*- coding: utf-8 -*-
"""Global dashboards: made by managers for everybody, or some roles.

A global dashboard has a draft, which only managers see, and a
published version, which everybody else sees. Publishing copies the
draft over.
"""

import copy

from bika.lims import api
from senaite.dashboard import messagefactory as _
from senaite.dashboard import storage
from senaite.dashboard.access import can_manage
from senaite.dashboard.access import check_manage
from senaite.dashboard.dashboards import ids
from senaite.dashboard.dashboards import model
from senaite.dashboard.exceptions import NotFound
from senaite.dashboard.exceptions import QueryError


def not_found(dashboard_id):
    return NotFound(_("There is no dashboard ${id}, or it is not meant "
                      "for you", mapping={"id": dashboard_id}))


def clean_roles(roles):
    if not isinstance(roles, (list, tuple)):
        return []
    valid = set(api.get_portal().validRoles())
    return sorted({role for role in roles if role in valid})


def is_for(record, env):
    """Whether a global dashboard is meant for the user."""
    roles = set(record.get("roles") or [])
    return not roles or bool(roles & env.roles)


def is_published(record):
    return record.get("published") is not None


def is_visible(record, env):
    """Whether the user sees the dashboard; managers see drafts too."""
    if can_manage(env):
        return True
    return is_published(record) and is_for(record, env)


def has_changes(record):
    """Whether the draft differs from what is published."""
    published = record.get("published") or {}
    return record["draft"]["tiles"] != published.get("tiles")


def get_visible(env):
    """Global dashboards the user sees, in their order."""
    records = [record for record in storage.list_globals()
               if is_visible(record, env)]
    return sorted(records, key=lambda r: (r.get("order", 0), r["id"]))


def get(dashboard_id, env):
    """The global dashboard, if the user may see it."""
    record = storage.get_global(dashboard_id)
    if record is None or not is_visible(record, env):
        raise not_found(dashboard_id)
    return record


def touch(record, env):
    record["modified"] = env.now.ISO8601()
    record["modified_by"] = env.user_id


def create(title, tiles, roles, env, default=None):
    """Create a global dashboard with a draft only.

    `default` is the key of the default dashboard it is made from.
    """
    check_manage(env)
    title = model.clean_dashboard_title(title)
    record = {
        "id": ids.new_global_id(title, storage.get_global),
        "title": title,
        "roles": clean_roles(roles),
        "order": len(storage.list_globals()),
        "draft": {"tiles": model.clean_tiles(tiles)},
        "published": None,
        "revision": 0,
    }
    if default:
        record["default"] = default
    touch(record, env)
    storage.set_global(record)
    return record


def save_draft(dashboard_id, env, tiles=None, title=None, roles=None):
    """Change the draft of a global dashboard, or its title or roles."""
    check_manage(env)
    record = get(dashboard_id, env)
    if tiles is not None:
        record["draft"] = {"tiles": model.clean_tiles(tiles)}
    if title is not None:
        record["title"] = model.clean_dashboard_title(title)
    if roles is not None:
        record["roles"] = clean_roles(roles)
    touch(record, env)
    storage.set_global(record)
    return record


def publish(dashboard_id, env):
    """Make the draft what everybody sees."""
    check_manage(env)
    record = get(dashboard_id, env)
    record["published"] = {
        "tiles": copy.deepcopy(record["draft"]["tiles"]),
        "date": env.now.ISO8601(),
        "by": env.user_id,
    }
    record["revision"] = record.get("revision", 0) + 1
    storage.set_global(record)
    return record


def discard_draft(dashboard_id, env):
    """Throw the draft away and start again from what is published."""
    check_manage(env)
    record = get(dashboard_id, env)
    if not is_published(record):
        raise QueryError(_("There is nothing published to go back to"))
    record["draft"] = {"tiles": copy.deepcopy(record["published"]["tiles"])}
    storage.set_global(record)
    return record


def unpublish(dashboard_id, env):
    check_manage(env)
    record = get(dashboard_id, env)
    record["published"] = None
    storage.set_global(record)
    return record


def delete(dashboard_id, env):
    """Delete a global dashboard and every user's changes to it."""
    check_manage(env)
    get(dashboard_id, env)
    storage.delete_global(dashboard_id)
    storage.delete_overlays(dashboard_id)
