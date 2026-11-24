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
from senaite.dashboard.browser import listing
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

    def test_the_list_of_a_part_carries_its_request(self):
        answer = drill.drill({"tile": self.tile(), "offset": 1}, self.env)
        self.assertIn("/dashboard-objects?drill=", answer["listing"])
        self.assertNotIn("offset", answer["listing"])

    def test_the_list_finds_what_the_tile_counts(self):
        dataset, uids = drill.select({"tile": self.tile()}, self.env)
        self.assertEqual((dataset.name, len(uids)), ("drill-contacts", 2))

    def test_an_object_of_another_user_is_not_found(self):
        body = {"object": {"dataset": "samples", "uid": "0" * 32}}
        self.assertRaises(NotFound, drill.drill, body, self.env)


class ListingTestCase(unittest.TestCase):
    """The page that lists exactly the objects of a part of a tile."""

    def test_the_request_is_read_from_the_query_string_of_a_post(self):
        class FakeRequest(dict):
            form = {}
        request = FakeRequest(QUERY_STRING="drill=%7B%7D&title=Due")
        self.assertEqual(listing.get_param(request, "drill"), "{}")
        self.assertEqual(listing.get_param(request, "title"), "Due")

    def test_a_request_that_is_no_json(self):
        self.assertRaises(api.ValidationError, listing.parse_request, "{")
        self.assertRaises(api.ValidationError, listing.parse_request, "")

    def test_a_request_that_is_too_long(self):
        self.assertRaises(api.ValidationError, listing.parse_request,
                          "[" + "1," * listing.MAX_REQUEST + "1]")

    def test_no_objects_match_nothing(self):
        self.assertEqual(listing.uid_query([]), {"query": ["__none__"]})


class ResultTextTestCase(unittest.TestCase):
    """A result on a line of a row, as the sample shows it."""

    def test_the_options_of_a_multiple_choice_on_one_line(self):
        self.assertEqual(builtin.to_line(u"Positive<br/>Negative"),
                         u"Positive, Negative")

    def test_a_text_of_many_lines_on_one(self):
        self.assertEqual(builtin.to_line(u"line one\nline two"),
                         u"line one line two")

    def test_a_unit_with_a_superscript(self):
        self.assertEqual(builtin.to_supsub(u"cm^2"), u"cm\xb2")
        self.assertEqual(builtin.to_supsub(u"kg^(-1)"), u"kg\u207b\xb9")

    def test_a_scientific_notation_with_a_superscript(self):
        self.assertEqual(builtin.to_supsub(u"1.2x10<sup>-5</sup>"),
                         u"1.2x10\u207b\u2075")

    def test_only_a_number_takes_the_unit(self):
        self.assertTrue(builtin.has_digit(u"< 0.50"))
        self.assertFalse(builtin.has_digit(u"Not detected"))
