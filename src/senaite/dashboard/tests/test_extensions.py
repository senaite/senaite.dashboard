# -*- coding: utf-8 -*-
"""Integration tests: what add-ons add to datasets and the library."""

import unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import login
from plone.app.testing import setRoles
from senaite.dashboard.env import Environment
from senaite.dashboard.exceptions import QueryError
from senaite.dashboard.interfaces import IDashboardDatasetExtension
from senaite.dashboard.interfaces import IDashboardPresetProvider
from senaite.dashboard.library.presets import get_categories
from senaite.dashboard.query.datasets import Column
from senaite.dashboard.query.datasets import DatasetExtension
from senaite.dashboard.query.datasets import choice_getter
from senaite.dashboard.query.fields import CHOICE
from senaite.dashboard.query.fields import TEXT
from senaite.dashboard.query.fields import Field
from senaite.dashboard.query.labels import get_labels
from senaite.dashboard.query.registry import get_dataset
from senaite.dashboard.query.sources import order_keys
from senaite.dashboard.query.vocabularies import get_choices
from senaite.dashboard.tests.layers import DASHBOARD_TESTING
from zope.component import getGlobalSiteManager

PRIORITY = Field("getPriority", u"Priority", CHOICE,
                 choices=[("1", u"Highest"), ("3", u"Medium"),
                          ("5", u"Lowest")])

EXTENSION = DatasetExtension(
    "samples",
    fields=[PRIORITY, Field("getProject", u"Project", TEXT)],
    columns=[Column("project", u"Project",
                    getter=lambda brain: u"P-" + brain.getId)],
)


class Presets(object):
    categories = [("projects", u"Projects")]

    def __call__(self, env):
        return []


class FakeBrain(object):
    getId = "W-0001"
    getPriority = "1"


class ExtensionsTestCase(unittest.TestCase):
    layer = DASHBOARD_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["LabManager"])
        login(self.portal, "test-user")
        self.env = Environment()
        gsm = getGlobalSiteManager()
        gsm.registerUtility(EXTENSION, IDashboardDatasetExtension,
                            name="test")
        gsm.registerUtility(Presets(), IDashboardPresetProvider,
                            name="test")

    def tearDown(self):
        gsm = getGlobalSiteManager()
        gsm.unregisterUtility(EXTENSION, IDashboardDatasetExtension,
                              name="test")
        gsm.unregisterUtility(provided=IDashboardPresetProvider,
                              name="test")

    def samples(self):
        return get_dataset("samples", self.env)

    def test_extension_adds_fields_and_columns(self):
        samples = self.samples()
        self.assertIs(samples.get_field("getPriority", self.env), PRIORITY)
        column = samples.get_column("project", self.env)
        self.assertEqual(column.name, "project")
        names = [f["name"] for f in samples.describe(self.env)["fields"]]
        self.assertIn("getProject", names)
        self.assertIn("review_state", names)

    def test_extension_leaves_other_datasets_alone(self):
        worksheets = get_dataset("worksheets", self.env)
        self.assertNotIn("getPriority", worksheets.fields)

    def test_column_getter(self):
        column = self.samples().get_column("project", self.env)
        self.assertEqual(column.get_value(FakeBrain()), u"P-W-0001")

    def test_choices_keep_their_order(self):
        choices = get_choices(PRIORITY, self.samples(), self.env)
        self.assertEqual([c["value"] for c in choices], ["1", "3", "5"])
        self.assertEqual(choices[0]["title"], u"Highest")

    def test_choice_labels(self):
        labels = get_labels(["5", "9"], PRIORITY, self.samples(), self.env)
        self.assertEqual(labels, {"5": u"Lowest", "9": u"9"})

    def test_choices_group_in_their_order(self):
        counts = {"5": 10, "1": 2, "3": 7}
        self.assertEqual(order_keys(counts, PRIORITY, self.samples()),
                         ["1", "3", "5"])

    def test_choice_getter_shows_the_title(self):
        self.assertEqual(choice_getter(PRIORITY)(FakeBrain()), u"Highest")

    def test_choice_getter_reads_with_a_getter(self):
        getter = choice_getter(PRIORITY, getter=lambda brain: "5")
        self.assertEqual(getter(FakeBrain()), u"Lowest")
        empty = choice_getter(PRIORITY, getter=lambda brain: None)
        self.assertIsNone(empty(FakeBrain()))

    def test_fields_of_an_unknown_kind_are_refused(self):
        field = Field("getPriority", u"Priority", "colour")
        self.assertRaises(QueryError, get_choices, field, self.samples(),
                          self.env)
        self.assertRaises(QueryError, get_labels, ["1"], field,
                          self.samples(), self.env)

    def test_provider_categories_come_before_general(self):
        ids = [c["id"] for c in get_categories()]
        self.assertEqual(ids[-2:], ["projects", "general"])
