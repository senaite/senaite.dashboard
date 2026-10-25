# -*- coding: utf-8 -*-
"""Routes to see and change dashboards.

Below @@API/senaite/v1/dashboard. A change answers with the dashboard
as the page shows it afterwards.
"""

from senaite.dashboard import app
from senaite.dashboard.dashboards import defaults
from senaite.dashboard.dashboards import ids
from senaite.dashboard.dashboards import personal
from senaite.dashboard.dashboards import shared
from senaite.dashboard.dashboards import views
from senaite.dashboard.routes.base import get_body
from senaite.dashboard.routes.base import get_tiles
from senaite.dashboard.routes.base import ok
from senaite.dashboard.routes.base import route


@route("/bootstrap", ["GET"])
def bootstrap(env, request):
    return app.bootstrap(env)


@route("/view/<string:dashboard_id>", ["GET"])
def view(env, request, dashboard_id):
    draft = request.form.get("draft") in ("1", "true")
    return views.get_view(dashboard_id, env, draft=draft)


@route("/list", ["GET"])
def list_dashboards(env, request):
    items = views.list_dashboards(env)
    return {"dashboards": items,
            "active": views.get_active_id(env, items)}


@route("/defaults/restore", ["POST"])
def restore_defaults(env, request):
    """Create the default dashboards that are missing, as drafts."""
    created = defaults.restore_defaults(env)
    items = views.list_dashboards(env)
    return {"created": created, "dashboards": items,
            "active": views.get_active_id(env, items)}


@route("/save/<string:dashboard_id>", ["POST"])
def save(env, request, dashboard_id):
    personal.save_tiles(dashboard_id, get_tiles(get_body()), env)
    return views.get_view(dashboard_id, env)


@route("/reset/<string:dashboard_id>", ["POST"])
def reset(env, request, dashboard_id):
    personal.reset(dashboard_id, env)
    return views.get_view(dashboard_id, env)


@route("/activate/<string:dashboard_id>", ["POST"])
def activate(env, request, dashboard_id):
    personal.set_active(dashboard_id, env)
    return ok()


@route("/new", ["POST"])
def new(env, request):
    """Create a dashboard.

    Body: {"title", "scope": "personal" | "global", "tiles", "roles"}
    """
    body = get_body()
    tiles = body.get("tiles") or []
    if body.get("scope") == views.GLOBAL:
        record = shared.create(
            body.get("title"), tiles, body.get("roles"), env)
        personal.set_active(record["id"], env)
        return views.get_view(record["id"], env, draft=True)
    dashboard = personal.create(body.get("title"), tiles, env)
    return views.get_view(dashboard["id"], env)


@route("/settings/<string:dashboard_id>", ["POST"])
def settings(env, request, dashboard_id):
    """Rename a dashboard, or give a global one to other roles."""
    body = get_body()
    if ids.is_personal(dashboard_id):
        personal.rename(dashboard_id, body.get("title"), env)
        return views.get_view(dashboard_id, env)
    shared.save_draft(dashboard_id, env, title=body.get("title"),
                      roles=body.get("roles"))
    return views.get_view(dashboard_id, env, draft=True)


@route("/remove/<string:dashboard_id>", ["POST"])
def remove(env, request, dashboard_id):
    if ids.is_personal(dashboard_id):
        personal.delete(dashboard_id, env)
    else:
        shared.delete(dashboard_id, env)
    return ok()


@route("/draft/<string:dashboard_id>", ["POST"])
def draft(env, request, dashboard_id):
    shared.save_draft(dashboard_id, env, tiles=get_tiles(get_body()))
    return views.get_view(dashboard_id, env, draft=True)


@route("/publish/<string:dashboard_id>", ["POST"])
def publish(env, request, dashboard_id):
    shared.publish(dashboard_id, env)
    return views.get_view(dashboard_id, env, draft=True)


@route("/discard/<string:dashboard_id>", ["POST"])
def discard(env, request, dashboard_id):
    shared.discard_draft(dashboard_id, env)
    return views.get_view(dashboard_id, env, draft=True)


@route("/unpublish/<string:dashboard_id>", ["POST"])
def unpublish(env, request, dashboard_id):
    shared.unpublish(dashboard_id, env)
    return views.get_view(dashboard_id, env, draft=True)
