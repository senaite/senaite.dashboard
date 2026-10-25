# -*- coding: utf-8 -*-
"""Dashboards as the page shows them."""

from senaite.dashboard.access import can_manage
from senaite.dashboard.access import check_manage
from senaite.dashboard.dashboards import ids
from senaite.dashboard.dashboards import model
from senaite.dashboard.dashboards import personal
from senaite.dashboard.dashboards import shared

# Kinds of dashboards
GLOBAL = "global"
PERSONAL = "personal"

# What a view of a dashboard shows
MODE_PERSONAL = "personal"
MODE_DRAFT = "draft"
MODE_PUBLISHED = "published"


def summarize_global(record, env):
    summary = {
        "id": record["id"],
        "kind": GLOBAL,
        "title": record["title"],
        "published": shared.is_published(record),
        "for_me": shared.is_for(record, env),
    }
    # Who a dashboard is for and how far it is concern managers only
    if can_manage(env):
        summary["roles"] = record.get("roles") or []
        summary["has_changes"] = shared.has_changes(record)
    return summary


def summarize_personal(dashboard):
    return {
        "id": dashboard["id"],
        "kind": PERSONAL,
        "title": dashboard["title"],
    }


def list_dashboards(env):
    """The dashboards the user can switch between."""
    dashboards = [summarize_global(record, env)
                  for record in shared.get_visible(env)]
    dashboards.extend(summarize_personal(dashboard)
                      for dashboard in personal.list_dashboards(env))
    return dashboards


def is_startable(summary):
    """Whether a dashboard is a good one to open first."""
    return summary["kind"] == PERSONAL or (
        summary["published"] and summary["for_me"])


def get_active_id(env, dashboards):
    """The dashboard the user looked at last, else the first for them."""
    active = personal.get_active(env)
    known = [summary["id"] for summary in dashboards]
    if active in known:
        return active
    startable = [s["id"] for s in dashboards if is_startable(s)]
    return (startable or known or [None])[0]


def view_personal(dashboard_id, env):
    dashboard = personal.get_dashboard(dashboard_id, env)
    view = summarize_personal(dashboard)
    view.update({"mode": MODE_PERSONAL, "tiles": dashboard["tiles"]})
    return view


def view_draft(record, env):
    check_manage(env)
    view = summarize_global(record, env)
    view.update({
        "mode": MODE_DRAFT,
        "tiles": record["draft"]["tiles"],
        "modified": record.get("modified"),
        "modified_by": record.get("modified_by"),
    })
    return view


def view_published(record, env):
    published = record["published"]
    overlay = personal.get_overlay(record["id"], env)
    view = summarize_global(record, env)
    view.update({
        "mode": MODE_PUBLISHED,
        "tiles": model.apply_overlay(published["tiles"], overlay),
        "customized": not model.is_empty_overlay(overlay),
        "revision": record.get("revision", 0),
        "published_date": published.get("date"),
    })
    return view


def get_view(dashboard_id, env, draft=False):
    """A dashboard as the user sees it, with its tiles."""
    if ids.is_personal(dashboard_id):
        return view_personal(dashboard_id, env)
    record = shared.get(dashboard_id, env)
    if draft or not shared.is_published(record):
        return view_draft(record, env)
    return view_published(record, env)
