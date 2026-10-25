# -*- coding: utf-8 -*-
"""Integration tests: tiles managers save to the library."""

import unittest

from bika.lims import api
from plone.app.testing import login
from senaite.dashboard.env import Environment
from senaite.dashboard.exceptions import Forbidden
from senaite.dashboard.exceptions import NotFound
from senaite.dashboard.library import saved
from senaite.dashboard.library.presets import get_categories
from senaite.dashboard.library.presets import get_presets
from senaite.dashboard.tests.layers import DASHBOARD_TESTING

TILE = {"id": "abc", "type": "bar", "title": {"en": u"Mine", "de": u"Meins"},
        "source": "group",
        "params": {"dataset": "samples", "group_by": "review_state"},
        "layout": {"x": 4, "y": 6, "w": 6, "h": 4}}


def add_user(user_id, roles):
    acl = api.get_tool("acl_users")
    acl.userFolderAddUser(user_id, "secret-" + user_id, roles, [])


class LibraryTestCase(unittest.TestCase):
    layer = DASHBOARD_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        add_user("manager", ["LabManager"])
        add_user("analyst", ["Analyst"])

    def as_user(self, user_id):
        login(self.portal, user_id)
        return Environment()

    def saved_presets(self, env):
        return [p for p in get_presets(env)
                if p["category"] == saved.CATEGORY]

    def test_a_saved_tile_is_in_everybodys_library(self):
        manager = self.as_user("manager")
        record = saved.save(TILE, u"Samples per status", manager)
        presets = self.saved_presets(self.as_user("analyst"))
        self.assertEqual([p["id"] for p in presets], [record["id"]])
        self.assertEqual(presets[0]["description"], u"Samples per status")
        self.assertFalse(presets[0]["removable"])

    def test_the_place_on_the_dashboard_is_not_kept(self):
        record = saved.save(TILE, u"", self.as_user("manager"))
        self.assertNotIn("id", record["tile"])
        self.assertEqual(record["tile"]["layout"], {"w": 6, "h": 4})

    def test_without_description_the_title_describes_it(self):
        saved.save(TILE, u" ", self.as_user("manager"))
        preset = self.saved_presets(self.as_user("manager"))[0]
        self.assertEqual(preset["description"], u"Mine")
        self.assertTrue(preset["removable"])

    def test_only_managers_save_and_remove(self):
        analyst = self.as_user("analyst")
        self.assertRaises(Forbidden, saved.save, TILE, u"", analyst)
        record = saved.save(TILE, u"", self.as_user("manager"))
        self.assertRaises(Forbidden, saved.remove, record["id"],
                          self.as_user("analyst"))

    def test_remove(self):
        manager = self.as_user("manager")
        record = saved.save(TILE, u"", manager)
        saved.remove(record["id"], manager)
        self.assertEqual(self.saved_presets(manager), [])
        self.assertRaises(NotFound, saved.remove, record["id"], manager)

    def test_odd_parameters_do_not_break_the_library(self):
        odd = dict(TILE, params={"dataset": "samples", "filters": [1],
                                 "trend": "weekly", "group_by": ["x"]})
        saved.save(odd, None, self.as_user("manager"))
        saved.save(dict(TILE, params={"dataset": ["samples"]}), None,
                   self.as_user("manager"))
        self.assertEqual(len(self.saved_presets(self.as_user("analyst"))), 1)

    def test_saved_tiles_have_a_category_before_general(self):
        ids = [c["id"] for c in get_categories()]
        self.assertEqual(ids[-2:], [saved.CATEGORY, "general"])

    def test_the_custom_tile_opens_its_settings(self):
        env = self.as_user("analyst")
        presets = {p["id"]: p for p in get_presets(env)}
        self.assertTrue(presets["custom"]["configure"])
        self.assertFalse(presets["samples-to-receive"]["configure"])
