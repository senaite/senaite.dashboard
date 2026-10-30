# -*- coding: utf-8 -*-
"""What an add-on builds with senaite.dashboard.api alone."""

import unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import login
from plone.app.testing import setRoles
from senaite.core.catalog import SETUP_CATALOG
from senaite.dashboard import api
from senaite.dashboard import app
from senaite.dashboard.interfaces import IDashboardDataSource
from senaite.dashboard.interfaces import IDashboardDataset
from senaite.dashboard.query.compute import compute
from senaite.dashboard.query.compute import get_cost
from senaite.dashboard.tests.layers import DASHBOARD_TESTING
from zope.component import getGlobalSiteManager

CONTACTS = api.Dataset(
    name="lab-contacts",
    title=u"Lab contacts",
    catalog=SETUP_CATALOG,
    portal_type="LabContact",
    fields=[api.Field("created", u"Created", api.DATE)],
    columns=[api.Column("Title", u"Name")],
)


class TwiceSource(api.DataSource):
    """Twice the number of objects of a dataset."""
    title = u"Twice"
    output = "scalar"
    params = api.with_dataset({"factor": api.NUMBER})

    def clean(self, params):
        if params.get("factor", 2) < 1:
            raise api.ValidationError(u"The factor must be positive")
        return params

    def cost(self, params):
        return 2

    def __call__(self, params, env):
        dataset = CONTACTS
        query = api.build_query(dataset, params.get("filters"), env)
        count = len(api.search(dataset, query))
        return {"value": count * params.get("factor", 2)}


class BareSource(object):
    """A source that declares nothing but what it must."""
    title = u"Bare"
    output = "scalar"

    def __call__(self, params, env):
        return {"value": 1}


class ApiTestCase(unittest.TestCase):
    layer = DASHBOARD_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["LabManager"])
        login(self.portal, "test-user")
        self.env = api.Environment()
        self.registrations = [
            (CONTACTS, IDashboardDataset, "lab-contacts"),
            (TwiceSource(), IDashboardDataSource, "twice"),
            (BareSource(), IDashboardDataSource, "bare"),
        ]
        gsm = getGlobalSiteManager()
        for component, provided, name in self.registrations:
            gsm.registerUtility(component, provided, name=name)

    def tearDown(self):
        gsm = getGlobalSiteManager()
        for component, provided, name in self.registrations:
            gsm.unregisterUtility(component, provided, name=name)

    def test_a_dataset_of_an_addon(self):
        result = compute("count", {"dataset": "lab-contacts"}, self.env)
        self.assertEqual(result["value"], 0)

    def test_a_source_of_an_addon(self):
        params = {"dataset": "lab-contacts", "factor": 3}
        self.assertEqual(compute("twice", params, self.env), {"value": 0})
        self.assertEqual(get_cost("twice", params), 2)

    def test_the_source_checks_its_parameters(self):
        self.assertRaises(api.ValidationError, compute, "twice",
                          {"dataset": "lab-contacts", "factor": 0},
                          self.env)

    def test_a_bare_source_does_not_break_the_page(self):
        data = app.bootstrap(self.env)
        bare = [s for s in data["sources"] if s["name"] == "bare"]
        self.assertEqual(bare[0]["params"], [])
        self.assertEqual(compute("bare", {}, self.env), {"value": 1})
        self.assertEqual(get_cost("bare", {}), 1)

    def test_the_dataset_is_offered_in_the_tile_editor(self):
        data = app.bootstrap(self.env)
        names = [dataset["name"] for dataset in data["datasets"]]
        self.assertIn("lab-contacts", names)
