# -*- coding: utf-8 -*-
"""Opening a tile to the objects behind its numbers."""

import unittest

from bika.lims import api as lims_api
from DateTime import DateTime
from plone.app.testing import TEST_USER_ID
from plone.app.testing import login
from plone.app.testing import setRoles
from senaite.core.catalog import CONTACT_CATALOG
from senaite.dashboard import api
from senaite.dashboard.exceptions import NotFound
from senaite.dashboard.interfaces import IDashboardDataset
from senaite.dashboard.query import builtin
from senaite.dashboard.query import drill
from senaite.dashboard.query.datasets import COL_DATE
from senaite.dashboard.query.datasets import COL_DUE
from senaite.dashboard.query.datasets import Column
from senaite.dashboard.query.datasets import default_card
from senaite.dashboard.tests.layers import DASHBOARD_TESTING
from zope.component import getGlobalSiteManager

CONTACTS = api.Dataset(
    name="drill-contacts",
    title=u"Lab contacts",
    catalog=CONTACT_CATALOG,
    portal_type="LabContact",
    fields=[api.Field("created", u"Created", api.DATE)],
    columns=[api.Column("Title", u"Name")],
)

PERIODS = [
    (DateTime("2026/11/09 00:00:00 GMT+1"), DateTime("2026/11/16 00:00:00 "
                                                     "GMT+1")),
    (DateTime("2026/11/16 00:00:00 GMT+1"), DateTime("2026/11/23 00:00:00 "
                                                     "GMT+1")),
]


class SelectionTestCase(unittest.TestCase):
    """What decides which objects a part of a tile stands for."""

    def test_a_group_is_the_objects_with_its_value(self):
        self.assertTrue(drill.has_value(["a", "b"], "b"))
        self.assertFalse(drill.has_value(["a"], "b"))

    def test_other_is_the_objects_with_a_value_not_shown(self):
        shown = {"a", "b"}
        self.assertTrue(drill.has_other_value(["a", "c"], shown))
        self.assertFalse(drill.has_other_value(["a", "b"], shown))

    def test_the_period_of_a_bucket(self):
        start, end = drill.find_period(PERIODS, PERIODS[1][0].ISO8601())
        self.assertEqual(start, PERIODS[1][0])

    def test_a_period_no_longer_shown(self):
        self.assertRaises(api.ValidationError, drill.find_period, PERIODS,
                          "2020-01-06T00:00:00+01:00")

    def test_objects_without_a_value_sort_last(self):
        values = [3, None, 1]
        self.assertEqual(sorted(values, key=drill.sort_key), [1, 3, None])


class RowsTestCase(unittest.TestCase):
    """How a dataset shows its objects in an opened tile."""

    def test_a_card_from_the_columns(self):
        card = default_card([
            Column("getId", u"ID"),
            Column("created", u"Created", COL_DATE),
            Column("getClientTitle", u"Client"),
            Column("getDueDate", u"Due", COL_DUE),
            Column("getSampleTypeTitle", u"Type"),
        ])
        self.assertEqual(card.title, "getId")
        self.assertEqual(card.subtitle, ["getClientTitle",
                                         "getSampleTypeTitle"])
        self.assertEqual(card.detail, ["created"])

    def test_a_sample_opens_to_its_analyses(self):
        self.assertTrue(drill.opens(builtin.SAMPLES))

    def test_an_analysis_opens_its_sample(self):
        self.assertTrue(drill.opens(builtin.ANALYSES))

    def test_below_its_sample_an_analysis_does_not_open_it_again(self):
        self.assertFalse(drill.opens(builtin.ANALYSES, below="samples"))

    def test_a_dataset_without_links_does_not_open(self):
        self.assertFalse(drill.opens(CONTACTS))


class DrillTestCase(unittest.TestCase):
    layer = DASHBOARD_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["LabManager"])
        login(self.portal, "test-user")
        self.env = api.Environment()
        getGlobalSiteManager().registerUtility(
            CONTACTS, IDashboardDataset, name="drill-contacts")
        container = self.portal.bika_setup.bika_labcontacts
        for first, last in ((u"Tomas", u"Weber"), (u"Marta", u"Ruiz")):
            lims_api.create(container, "LabContact", Firstname=first,
                            Lastname=last)

    def tearDown(self):
        getGlobalSiteManager().unregisterUtility(
            CONTACTS, IDashboardDataset, name="drill-contacts")

    def tile(self, source="count"):
        return {"source": source, "params": {"dataset": "drill-contacts"}}

    def test_a_count_opens_to_the_objects_it_counts(self):
        answer = drill.drill({"tile": self.tile()}, self.env)
        self.assertEqual(answer["total"], 2)
        names = sorted(row["title"].split()[0] for row in answer["rows"])
        self.assertEqual(names, [u"Marta", u"Tomas"])

    def test_a_row_leads_to_its_object(self):
        answer = drill.drill({"tile": self.tile()}, self.env)
        row = answer["rows"][0]
        self.assertTrue(row["url"].startswith(self.portal.absolute_url()))
        self.assertFalse(row["opens"])

    def test_pages_of_rows(self):
        answer = drill.drill({"tile": self.tile(), "offset": 1}, self.env)
        self.assertEqual((answer["total"], len(answer["rows"])), (2, 1))

    def test_a_list_tile_does_not_open(self):
        self.assertRaises(api.ValidationError, drill.drill,
                          {"tile": self.tile("list")}, self.env)

    def test_only_offered_facets_narrow(self):
        body = {"tile": self.tile(), "scope": {"review_state": "active"}}
        self.assertRaises(api.ValidationError, drill.drill, body, self.env)

    def test_an_object_of_another_user_is_not_found(self):
        body = {"object": {"dataset": "samples", "uid": "0" * 32}}
        self.assertRaises(NotFound, drill.drill, body, self.env)
