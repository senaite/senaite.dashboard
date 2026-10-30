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


def exc_text(exc):
    """The message id or text an exception was raised with."""
    return exc.args[0] if exc.args else u""


def message(exc):
    """The text of an exception, in the language of the user."""
    return translate(exc_text(exc), to_utf8=False)


def error_text(text):
    """The text for an error of senaite.jsonapi, as UTF-8.

    Its error handler calls `str()` on the error, which fails on text
    that is not ASCII and turns the answer into a server error.
    """
    return translate(text, to_utf8=True)


def origin_of(url):
    parts = urlparse(url or "")
    return (parts.scheme, parts.netloc)


def check_post(request):
    """Refuse a change that is no JSON or comes from another site."""
    content_type = (request.getHeader("Content-Type") or "").split(";")[0]
    if content_type.strip().lower() != "application/json":
        raise BadRequestError(error_text(
            _("Send the request as application/json")))
    origin = request.getHeader("Origin")
    if origin and origin_of(origin) != origin_of(
            api.get_url(api.get_portal())):
        raise ForbiddenError(error_text(
            _("Changes from another site are refused")))


def check_dashboard_id(kwargs):
    dashboard_id = kwargs.get("dashboard_id")
    if dashboard_id is not None and not ids.is_dashboard_id(dashboard_id):
        raise NotFoundError(error_text(_("No such dashboard")))


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
                raise NotFoundError(error_text(
                    _("senaite.dashboard is not installed")))
            check_permission(ViewDashboard)
            check_dashboard_id(kwargs)
            if "POST" in methods:
                check_post(request)
                req.disable_csrf_protection()
            try:
                return func(Environment(), request, **kwargs)
            except QueryError as exc:
                raise BadRequestError(error_text(exc_text(exc)))
            except NotFound as exc:
                raise NotFoundError(error_text(exc_text(exc)))
            except Forbidden as exc:
                raise ForbiddenError(error_text(exc_text(exc)))
        return wrapper
    return decorator


def parse_body(text):
    """The JSON object of a request body, or {} for an empty one."""
    try:
        body = json.loads(text or "{}")
    except ValueError:
        raise BadRequestError(error_text(
            _("The request is no valid JSON")))
    if not isinstance(body, dict):
        raise BadRequestError(error_text(_("Send a JSON object")))
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
