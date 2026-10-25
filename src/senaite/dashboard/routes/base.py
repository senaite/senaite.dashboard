# -*- coding: utf-8 -*-
"""What every route of the dashboard API has in common.

Reads are GET, changes are POST with a JSON body. A JSON body is what
a page on another site cannot make a browser send without asking
first, and a browser that sends one from another site says so in the
Origin header; changes from another origin are refused. So the routes
may switch off the CSRF token check that a form post would need.
"""

import functools
import json
from urlparse import urlparse

from bika.lims import api
from senaite.core.i18n import translate
from senaite.dashboard import messagefactory as _
from senaite.dashboard.dashboards import ids
from senaite.dashboard.env import Environment
from senaite.dashboard.exceptions import Forbidden
from senaite.dashboard.exceptions import NotFound
from senaite.dashboard.exceptions import QueryError
from senaite.dashboard.interfaces import ISenaiteDashboardLayer
from senaite.dashboard.permissions import ViewDashboard
from senaite.jsonapi import request as req
from senaite.jsonapi.api import check_permission
from senaite.jsonapi.exceptions import BadRequestError
from senaite.jsonapi.exceptions import ForbiddenError
from senaite.jsonapi.exceptions import NotFoundError
from senaite.jsonapi.v1 import add_route

PREFIX = "/dashboard"


def message(exc):
    """The text of an exception, in the language of the user."""
    return translate(exc.args[0], to_utf8=False) if exc.args else u""


def origin_of(url):
    parts = urlparse(url or "")
    return (parts.scheme, parts.netloc)


def check_post(request):
    """Refuse a change that is no JSON or comes from another site."""
    content_type = (request.getHeader("Content-Type") or "").split(";")[0]
    if content_type.strip().lower() != "application/json":
        raise BadRequestError("Send the request as application/json")
    origin = request.getHeader("Origin")
    if origin and origin_of(origin) != origin_of(
            api.get_url(api.get_portal())):
        raise ForbiddenError("Changes from another site are refused")


def check_dashboard_id(kwargs):
    dashboard_id = kwargs.get("dashboard_id")
    if dashboard_id is not None and not ids.is_dashboard_id(dashboard_id):
        raise NotFoundError("No such dashboard")


def route(path, methods):
    """Register a dashboard route that answers with JSON.

    Checks that the add-on is installed and that the user may see the
    dashboard, and turns dashboard errors into HTTP errors.
    """
    def decorator(func):
        @add_route(PREFIX + path, "senaite.dashboard." + func.__name__,
                   methods=methods)
        @functools.wraps(func)
        def wrapper(context, request, **kwargs):
            if not ISenaiteDashboardLayer.providedBy(request):
                raise NotFoundError("senaite.dashboard is not installed")
            check_permission(ViewDashboard)
            check_dashboard_id(kwargs)
            if "POST" in methods:
                check_post(request)
                req.disable_csrf_protection()
            try:
                return func(Environment(), request, **kwargs)
            except QueryError as exc:
                raise BadRequestError(message(exc))
            except NotFound as exc:
                raise NotFoundError(message(exc))
            except Forbidden as exc:
                raise ForbiddenError(message(exc))
        return wrapper
    return decorator


def parse_body(text):
    """The JSON object of a request body, or {} for an empty one."""
    try:
        body = json.loads(text or "{}")
    except ValueError:
        raise BadRequestError("The request is no valid JSON")
    if not isinstance(body, dict):
        raise BadRequestError("Send a JSON object")
    return body


def get_body():
    """The JSON object the page sent.

    Read here rather than with senaite.jsonapi, which fails with a
    server error on a body that is no object.
    """
    return parse_body(req.get_request().get("BODY"))


def get_tiles(body):
    tiles = body.get("tiles")
    if not isinstance(tiles, list):
        raise QueryError(_("The request needs a list of tiles"))
    return tiles


def ok(**kwargs):
    kwargs.setdefault("ok", True)
    return kwargs
