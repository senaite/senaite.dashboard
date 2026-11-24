# -*- coding: utf-8 -*-
"""Listings of exactly the objects behind a part of a tile.

"Open list" in an opened tile leads here. The page carries the request
of the tile in its URL (see `drill.listing_url`); it searches again
with it, as the user who opens the page, and lists the objects found
and nothing else. Samples get the listing of SENAITE with its actions,
other datasets a plain listing of their columns.
"""

import json
from cgi import escape
from urlparse import parse_qs
from collections import OrderedDict

from bika.lims import api
from bika.lims.utils import get_link
from senaite.app.listing.view import ListingView
from senaite.core.api import dtime
from senaite.core.browser.samples.view import SamplesView
from senaite.core.i18n import translate
from senaite.dashboard import messagefactory as _
from senaite.dashboard.env import Environment
from senaite.dashboard.exceptions import NotFound
from senaite.dashboard.exceptions import ValidationError
from senaite.dashboard.query.datasets import COL_DATE
from senaite.dashboard.query.datasets import COL_DUE
from senaite.dashboard.query.datasets import COL_NUMBER
from senaite.dashboard.query.datasets import COL_PERCENT
from senaite.dashboard.query.datasets import COL_STATE
from senaite.dashboard.query.drill import select
from senaite.dashboard.query.labels import get_state_title
from senaite.dashboard.query.search import NONE
from senaite.dashboard.titles import display_title
from zExceptions import BadRequest

# Text of the request of a tile in the URL, at most
MAX_REQUEST = 8000


def parse_request(text):
    """The request of a tile from the URL."""
    if not text or len(text) > MAX_REQUEST:
        raise ValidationError(_("Invalid parameter ${name}",
                                mapping={"name": "drill"}))
    try:
        return json.loads(text)
    except ValueError:
        raise ValidationError(_("Invalid parameter ${name}",
                                mapping={"name": "drill"}))


def get_param(request, name):
    """A parameter of the URL of the page.

    The listing asks for its rows with a POST to the same URL, whose
    query string Zope does not read into the form.
    """
    value = request.form.get(name)
    if value is None:
        values = parse_qs(request.get("QUERY_STRING") or "").get(name)
        value = values[0] if values else None
    return value


def get_selection(request):
    """The dataset and the UIDs of the objects the page lists.

    :raises BadRequest: when the request of the tile is not valid
    """
    env = Environment()
    try:
        return env, select(parse_request(get_param(request, "drill")), env)
    except (ValidationError, NotFound) as exc:
        text = translate(exc.args[0], to_utf8=True) if exc.args else ""
        raise BadRequest(text)


def uid_query(uids):
    """A catalog query for exactly the UIDs; none matches nothing."""
    return {"query": uids or [NONE]}


def get_title(request, dataset):
    """What the tile called the part, or the title of the dataset."""
    title = get_param(request, "title")
    if isinstance(title, basestring) and title.strip():
        return api.safe_unicode(title.strip())[:200]
    return display_title(dataset.title)


def format_date(value):
    if not dtime.is_date(value):
        return u""
    return dtime.to_localized_time(value, long_format=True) or u""


def format_value(value, column, dataset):
    """The text of a value of a column, as the listing shows it."""
    if value in (None, ""):
        return u""
    if column.kind in (COL_DATE, COL_DUE):
        return format_date(value)
    if column.kind == COL_STATE:
        return get_state_title(value, dataset.portal_type)
    if column.kind == COL_PERCENT:
        return u"{}%".format(value)
    if column.kind == COL_NUMBER:
        return api.safe_unicode(value)
    if isinstance(value, basestring):
        return api.safe_unicode(value)
    return u""


class DrillSamplesView(SamplesView):
    """The samples listing of SENAITE, of the samples of a tile only.

    The samples are searched in `update`, not on construction: the view
    is made while the request is traversed, before the user is known.
    """

    def update(self):
        super(DrillSamplesView, self).update()
        env, (dataset, uids) = get_selection(self.request)
        self.contentFilter["UID"] = uid_query(uids)
        self.title = get_title(self.request, dataset)
        # The samples of a tile may be in any state: the first button
        # shows them all, the buttons of the states still narrow them
        self.review_states = [
            dict(review_state, contentFilter={}, title=_("All"))
            if review_state.get("id") == "default" else review_state
            for review_state in self.review_states
            if review_state.get("id") != "all"]


class DrillObjectsView(ListingView):
    """A plain listing of the objects of a tile, by the columns of its
    dataset. Like the samples, they are searched in `update`."""

    def __init__(self, context, request):
        super(DrillObjectsView, self).__init__(context, request)
        self.show_select_column = False
        self.form_id = "dashboard_objects"

    def update(self):
        super(DrillObjectsView, self).update()
        self.env, (dataset, uids) = get_selection(self.request)
        self.dataset = dataset
        self.catalog = dataset.catalog
        index, order = dataset.sort
        self.contentFilter = {
            "UID": uid_query(uids),
            "sort_on": index,
            "sort_order": order,
        }
        self.title = get_title(self.request, dataset)
        self.dataset_columns = dataset.get_columns(self.env)
        # What the tile shows of an object is shown at first, the other
        # columns can be switched on
        shown = set(dataset.get_card(self.env).names())
        shown.update(column.name for column in dataset.get_facts(self.env))
        self.columns = OrderedDict(
            (column.name, {"title": display_title(column.title),
                           "toggle": column.name in shown})
            for column in self.dataset_columns)
        self.review_states = [{
            "id": "default",
            "title": _("All"),
            "contentFilter": {},
            "columns": list(self.columns.keys()),
        }]

    def folderitem(self, obj, item, index):
        """The cells of a row; the first leads to the object."""
        for position, column in enumerate(self.dataset_columns):
            text = u""
            if column.is_readable(obj, self.env):
                text = format_value(column.get_value(obj), column,
                                    self.dataset)
            item[column.name] = text
            if position == 0:
                url = self.dataset.get_url(obj)
                item["replace"][column.name] = get_link(
                    url, value=escape(text or obj.getId, quote=True))
        return item
