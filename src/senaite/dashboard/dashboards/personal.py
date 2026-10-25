# -*- coding: utf-8 -*-
"""What a user keeps for themselves.

Personal dashboards, made by a user for themselves only, and overlays:
what a user changed on a global dashboard (see model.py). Nobody else
sees either.
"""

from senaite.dashboard import messagefactory as _
from senaite.dashboard import storage
from senaite.dashboard.access import check_customize
from senaite.dashboard.dashboards import ids
from senaite.dashboard.dashboards import model
from senaite.dashboard.dashboards import shared
from senaite.dashboard.exceptions import QueryError

MAX_PERSONAL_DASHBOARDS = 20


def list_dashboards(env):
    dashboards = storage.list_user_values(env.user_id, storage.DASHBOARD)
    return sorted(dashboards, key=lambda d: d.get("created"))


def get_dashboard(dashboard_id, env):
    dashboard = storage.get_user_value(
        env.user_id, storage.dashboard_key(dashboard_id))
    if dashboard is None:
        raise shared.not_found(dashboard_id)
    return dashboard


def set_dashboard(dashboard, env):
    storage.set_user_value(
        env.user_id, storage.dashboard_key(dashboard["id"]), dashboard)


def check_room(env):
    """Refuse a new dashboard to a user who keeps enough of them."""
    if len(list_dashboards(env)) >= MAX_PERSONAL_DASHBOARDS:
        raise QueryError(_("You can keep at most ${count} dashboards",
                           mapping={"count": MAX_PERSONAL_DASHBOARDS}))


def create(title, tiles, env):
    check_customize(env)
    check_room(env)
    dashboard = {
        "id": ids.new_personal_id(),
        "title": model.clean_dashboard_title(title),
        "tiles": model.clean_tiles(tiles),
        "created": env.now.ISO8601(),
    }
    set_dashboard(dashboard, env)
    set_active(dashboard["id"], env)
    return dashboard


def rename(dashboard_id, title, env):
    check_customize(env)
    dashboard = get_dashboard(dashboard_id, env)
    dashboard["title"] = model.clean_dashboard_title(title)
    set_dashboard(dashboard, env)


def delete(dashboard_id, env):
    check_customize(env)
    get_dashboard(dashboard_id, env)
    storage.delete_user_value(env.user_id, storage.dashboard_key(dashboard_id))


def get_overlay(dashboard_id, env):
    return storage.get_user_value(
        env.user_id, storage.overlay_key(dashboard_id))


def save_personal_tiles(dashboard_id, tiles, env):
    dashboard = get_dashboard(dashboard_id, env)
    dashboard["tiles"] = tiles
    set_dashboard(dashboard, env)


def save_overlay(dashboard_id, tiles, env):
    """Keep what the tiles change on the published global dashboard."""
    published = shared.get(dashboard_id, env)["published"] or {}
    overlay = model.make_overlay(published.get("tiles") or [], tiles)
    storage.set_user_value(
        env.user_id, storage.overlay_key(dashboard_id), overlay)


def save_tiles(dashboard_id, tiles, env):
    """Save the tiles of a dashboard as the user sees them.

    On a personal dashboard that is the dashboard itself; on a global
    one it is the user's overlay.
    """
    check_customize(env)
    tiles = model.clean_tiles(tiles)
    if ids.is_personal(dashboard_id):
        save_personal_tiles(dashboard_id, tiles, env)
    else:
        save_overlay(dashboard_id, tiles, env)


def reset(dashboard_id, env):
    """Drop the user's changes to a global dashboard."""
    check_customize(env)
    storage.delete_user_value(env.user_id, storage.overlay_key(dashboard_id))


def get_active(env):
    return storage.get_user_value(env.user_id, storage.ACTIVE)


def set_active(dashboard_id, env):
    """Remember the dashboard the user looked at last."""
    if not ids.is_dashboard_id(dashboard_id):
        raise QueryError(_("Invalid dashboard id"))
    if get_active(env) != dashboard_id:
        storage.set_user_value(env.user_id, storage.ACTIVE, dashboard_id)
