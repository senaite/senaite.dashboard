# -*- coding: utf-8 -*-
"""The dashboard page."""

import json
import os

from bika.lims import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.dashboard import app
from senaite.dashboard.env import Environment

STATIC = os.path.join(os.path.dirname(__file__), "static")


class DashboardView(BrowserView):
    """Renders the page the dashboard script mounts on.

    The page carries what the script starts from, so the first paint
    does not wait for a request.
    """

    template = ViewPageTemplateFile("templates/dashboard.pt")
    # The element the script mounts on; it tells the script which page
    # it is on
    mount_id = "senaite-dashboard"

    def __call__(self):
        self.request.set("disable_border", 1)
        return self.template()

    def get_bootstrap(self):
        return app.bootstrap(Environment())

    def get_bootstrap_json(self):
        data = json.dumps(self.get_bootstrap())
        # No "<" at all, so that no text in the data can end or confuse
        # the script element; JSON reads the escape as the same letter
        return data.replace("<", "\\u003c")

    def get_resource_url(self, name):
        """URL of a static file that changes with the file.

        Browsers cache resources; the modification time in the query
        makes a rebuilt bundle a new URL.
        """
        version = int(os.path.getmtime(os.path.join(STATIC, name)))
        return "{}/++resource++senaite.dashboard/{}?v={}".format(
            api.get_url(api.get_portal()), name, version)


class DatasetsView(DashboardView):
    """The page where managers define datasets."""

    mount_id = "senaite-dashboard-datasets"

    def get_bootstrap(self):
        return app.bootstrap_datasets(Environment())
