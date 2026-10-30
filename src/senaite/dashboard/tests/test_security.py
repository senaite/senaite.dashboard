# -*- coding: utf-8 -*-
"""What a dashboard keeps from users who may not see it in SENAITE."""

import unittest

from bika.lims import api
from plone.app.testing import login
from senaite.dashboard.env import Environment
from senaite.dashboard.query import catalogs
from senaite.dashboard.query import custom
from senaite.dashboard.query.builtin import ANALYSES
from senaite.dashboard.query.builtin import SAMPLES
from senaite.dashboard.query.compute import compute
from senaite.dashboard.query.search import INTERNAL_USE
from senaite.dashboard.query.search import NONE
from senaite.dashboard.query.search import RETRACTED
from senaite.dashboard.query.search import build_query
from senaite.dashboard.query.search import exclude_value
from senaite.dashboard.routes.base import error_text
from senaite.dashboard.tests.layers import DASHBOARD_TESTING


class ExcludeValueTestCase(unittest.TestCase):

    def test_without_a_query_of_the_index(self):
        self.assertEqual(exclude_value({}, "state", "a"),
                         {"state": {"not": ["a"]}})

    def test_adds_to_an_exclusion(self):
        query = {"state": {"not": ["b"]}}
        self.assertEqual(exclude_value(query, "state", "a"),
                         {"state": {"not": ["b", "a"]}})

    def test_narrows_a_list_of_values(self):
        query = {"state": {"query": ["a", "b"]}}
        self.assertEqual(exclude_value(query, "state", "a"),
                         {"state": {"query": ["b"], "not": ["a"]}})

    def test_an_emptied_list_matches_nothing(self):
        query = {"state": {"query": ["a"]}}
        self.assertEqual(exclude_value(query, "state", "a"),
                         {"state": {"query": [NONE], "not": ["a"]}})

    def test_a_plain_value_becomes_a_query(self):
        self.assertEqual(exclude_value({"state": "b"}, "state", "a"),
                         {"state": {"query": ["b"], "not": ["a"]}})

    def test_leaves_the_query_passed_in_alone(self):
        query = {"state": {"query": ["a"]}}
        exclude_value(query, "state", "a")
        self.assertEqual(query, {"state": {"query": ["a"]}})


class RestrictTestCase(unittest.TestCase):
    layer = DASHBOARD_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        acl = api.get_tool("acl_users")
        acl.userFolderAddUser("manager", "secret", ["LabManager"], [])
        acl.userFolderAddUser("contact", "secret", ["Client"], [])

    def as_user(self, user_id):
        login(self.portal, user_id)
        return Environment()

    def test_internal_use_is_kept_from_client_contacts(self):
        query = build_query(SAMPLES, {}, self.as_user("contact"))
        self.assertEqual(query["object_provides"], {"not": [INTERNAL_USE]})

    def test_internal_use_is_shown_to_the_laboratory(self):
        query = build_query(SAMPLES, {}, self.as_user("manager"))
        self.assertNotIn("object_provides", query)

    def test_retracted_analyses_are_kept_from_client_contacts(self):
        env = self.as_user("contact")
        query = build_query(ANALYSES, {}, env)
        self.assertEqual(query["review_state"], {"not": [RETRACTED]})

    def test_a_state_filter_cannot_ask_for_retracted_analyses(self):
        env = self.as_user("contact")
        filters = {"review_state": [RETRACTED, "verified"]}
        query = build_query(ANALYSES, filters, env)
        self.assertEqual(query["review_state"],
                         {"query": ["verified"], "not": [RETRACTED]})

    def test_the_catalog_runs_the_narrowed_queries(self):
        env = self.as_user("contact")
        filters = {"review_state": ["verified", RETRACTED]}
        for dataset in ("samples", "analyses"):
            for params in ({}, {"filters": filters}):
                params = dict(params, dataset=dataset)
                result = compute("count", params, env)
                self.assertEqual(result["value"], 0)

    def test_the_laboratory_sees_retracted_analyses(self):
        query = build_query(ANALYSES, {}, self.as_user("manager"))
        self.assertNotIn("review_state", query)


class CustomDatasetTestCase(unittest.TestCase):
    layer = DASHBOARD_TESTING

    def test_only_secured_catalogs_are_offered(self):
        names = [c["catalog"] for c in catalogs.get_candidates()]
        self.assertTrue(names)
        for name in names:
            self.assertTrue(catalogs.is_secured(api.get_tool(name)))

    def test_a_column_is_lab_only_unless_opened(self):
        column = custom.to_column(
            {"name": "getId", "title": "ID", "kind": "text"}, set())
        self.assertTrue(column.lab_only)

    def test_an_opened_column_of_a_lab_only_field_stays_lab_only(self):
        item = {"name": "getId", "title": "ID", "kind": "text",
                "lab_only": False}
        self.assertFalse(custom.to_column(item, set()).lab_only)
        self.assertTrue(custom.to_column(item, {"getId"}).lab_only)


class ErrorTextTestCase(unittest.TestCase):
    layer = DASHBOARD_TESTING

    def test_error_text_survives_str(self):
        # The error handler of senaite.jsonapi calls str() on it
        text = error_text(u"F\xfcr Sie nicht bestimmt")
        self.assertEqual(str(text), "F\xc3\xbcr Sie nicht bestimmt")
