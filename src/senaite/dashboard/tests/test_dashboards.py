# -*- coding: utf-8 -*-
"""Integration tests: who sees and changes which dashboard."""

import unittest

from bika.lims import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import login
from plone.app.testing import setRoles
from senaite.dashboard import storage
from senaite.dashboard.dashboards import defaults
from senaite.dashboard.dashboards import ids
from senaite.dashboard.dashboards import personal
from senaite.dashboard.dashboards import shared
from senaite.dashboard.dashboards import views
from senaite.dashboard.env import Environment
from senaite.dashboard.exceptions import Forbidden
from senaite.dashboard.exceptions import NotFound
from senaite.dashboard.exceptions import QueryError
from senaite.dashboard.library.presets import get_presets
from senaite.dashboard.query.compute import compute
from senaite.dashboard.query.compute import get_cost
from senaite.dashboard.tests.layers import DASHBOARD_TESTING

NOTE = {"id": "note", "type": "note", "title": "Hello",
        "options": {"text": "Hi"}, "layout": {"x": 0, "y": 0, "w": 4,
                                              "h": 2}}


def add_user(user_id, roles):
    acl = api.get_tool("acl_users")
    acl.userFolderAddUser(user_id, "secret-" + user_id, roles, [])


class DashboardsTestCase(unittest.TestCase):
    layer = DASHBOARD_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        add_user("manager", ["LabManager"])
        add_user("analyst", ["Analyst"])
        add_user("contact", ["Client"])

    def as_user(self, user_id):
        login(self.portal, user_id)
        return Environment()

    def ids(self, env):
        return [d["id"] for d in views.list_dashboards(env)]

    def test_defaults_are_installed_and_published(self):
        records = storage.list_globals()
        self.assertEqual(len(records), 3)
        self.assertTrue(all(shared.is_published(r) for r in records))

    def test_defaults_keep_their_key(self):
        keys = [defaults.get_default_key(record)
                for record in storage.list_globals()]
        self.assertEqual(sorted(keys), ["laboratory", "my-work", "overview"])

    def test_restore_creates_missing_defaults_as_drafts(self):
        manager = self.as_user("manager")
        shared.save_draft("laboratory", manager, title=u"Lab", tiles=[NOTE])
        shared.publish("laboratory", manager)
        shared.delete("my-work", manager)
        self.assertEqual(defaults.restore_defaults(manager), ["my-work"])
        record = storage.get_global("my-work")
        self.assertFalse(shared.is_published(record))
        self.assertTrue(record["draft"]["tiles"])
        # The renamed dashboard was left alone
        self.assertEqual(storage.get_global("laboratory")["title"], u"Lab")
        self.assertEqual(defaults.restore_defaults(manager), [])

    def test_restore_when_all_are_deleted(self):
        manager = self.as_user("manager")
        for record in storage.list_globals():
            shared.delete(record["id"], manager)
        created = defaults.restore_defaults(manager)
        self.assertEqual(created, ["laboratory", "my-work", "overview"])

    def test_only_managers_restore_defaults(self):
        analyst = self.as_user("analyst")
        self.assertRaises(Forbidden, defaults.restore_defaults, analyst)

    def test_global_dashboards_follow_roles(self):
        self.assertEqual(self.ids(self.as_user("analyst")),
                         ["laboratory", "my-work"])
        self.assertEqual(self.ids(self.as_user("contact")), ["overview"])

    def test_a_client_cannot_open_a_lab_dashboard(self):
        env = self.as_user("contact")
        self.assertRaises(NotFound, views.get_view, "laboratory", env)

    def test_only_managers_edit_global_dashboards(self):
        env = self.as_user("analyst")
        self.assertRaises(Forbidden, shared.save_draft, "laboratory",
                          env, tiles=[])
        self.assertRaises(Forbidden, shared.publish, "laboratory", env)

    def test_a_draft_is_not_seen_until_published(self):
        manager = self.as_user("manager")
        shared.save_draft("laboratory", manager, tiles=[NOTE])
        analyst = self.as_user("analyst")
        view = views.get_view("laboratory", analyst)
        self.assertNotIn("note", [t["id"] for t in view["tiles"]])
        self.assertRaises(Forbidden, views.get_view, "laboratory",
                          analyst, draft=True)
        manager = self.as_user("manager")
        self.assertTrue(views.get_view(
            "laboratory", manager, draft=True)["has_changes"])
        shared.publish("laboratory", manager)
        view = views.get_view("laboratory", self.as_user("analyst"))
        self.assertEqual([t["id"] for t in view["tiles"]], ["note"])

    def test_discard_goes_back_to_the_published_version(self):
        manager = self.as_user("manager")
        published = views.get_view("laboratory", manager)["tiles"]
        shared.save_draft("laboratory", manager, tiles=[NOTE])
        shared.discard_draft("laboratory", manager)
        draft = views.get_view("laboratory", manager, draft=True)
        self.assertEqual(draft["tiles"], published)
        self.assertFalse(draft["has_changes"])

    def test_a_user_customizes_for_themselves(self):
        analyst = self.as_user("analyst")
        tiles = views.get_view("laboratory", analyst)["tiles"]
        personal.save_tiles("laboratory", tiles[1:], analyst)
        mine = views.get_view("laboratory", analyst)
        self.assertTrue(mine["customized"])
        self.assertEqual(len(mine["tiles"]), len(tiles) - 1)
        other = views.get_view("laboratory", self.as_user("manager"))
        self.assertEqual(len(other["tiles"]), len(tiles))
        personal.reset("laboratory", self.as_user("analyst"))
        again = views.get_view("laboratory", self.as_user("analyst"))
        self.assertFalse(again["customized"])

    def test_personal_dashboards_are_private(self):
        analyst = self.as_user("analyst")
        mine = personal.create(u"Mine", [NOTE], analyst)
        self.assertIn(mine["id"], self.ids(analyst))
        manager = self.as_user("manager")
        self.assertNotIn(mine["id"], self.ids(manager))
        self.assertRaises(NotFound, views.get_view, mine["id"],
                          manager)

    def test_ids_tell_the_kind(self):
        manager = self.as_user("manager")
        record = shared.create(u"Personal stuff", [], [], manager)
        self.assertFalse(ids.is_personal(record["id"]))
        self.assertFalse(ids.is_personal("my-work"))
        mine = personal.create(u"Mine", [], manager)
        self.assertTrue(ids.is_personal(mine["id"]))

    def test_deleting_a_global_dashboard_drops_overlays(self):
        analyst = self.as_user("analyst")
        tiles = views.get_view("laboratory", analyst)["tiles"]
        personal.save_tiles("laboratory", tiles[1:], analyst)
        key = storage.overlay_key("laboratory")
        self.assertIsNotNone(storage.get_user_value("analyst", key))
        shared.delete("laboratory", self.as_user("manager"))
        self.assertIsNone(storage.get_user_value("analyst", key))

    def test_only_managers_see_roles_and_drafts(self):
        summary = views.list_dashboards(self.as_user("analyst"))[0]
        self.assertNotIn("roles", summary)
        self.assertNotIn("has_changes", summary)
        summary = views.list_dashboards(self.as_user("manager"))[0]
        self.assertIn("roles", summary)

    def test_slug_keeps_accented_letters(self):
        manager = self.as_user("manager")
        record = shared.create({"de": u"\xdcbersicht"}, [], [], manager)
        self.assertTrue(record["id"].startswith("ubersicht"))

    def test_empty_titles_are_refused(self):
        manager = self.as_user("manager")
        self.assertRaises(QueryError, shared.create, {"en": u" "}, [],
                          [], manager)

    def test_new_global_dashboard_starts_as_draft(self):
        manager = self.as_user("manager")
        record = shared.create(u"QC", [NOTE], ["Analyst"], manager)
        self.assertNotIn(record["id"], self.ids(self.as_user("analyst")))
        shared.publish(record["id"], self.as_user("manager"))
        self.assertIn(record["id"], self.ids(self.as_user("analyst")))

    def test_client_contacts_get_no_lab_presets(self):
        ids = [p["id"] for p in get_presets(self.as_user("contact"))]
        self.assertIn("samples-to-receive", ids)
        self.assertNotIn("analyses-by-analyst", ids)
        self.assertNotIn("worksheets-open", ids)

    def test_unknown_parameters_are_dropped(self):
        setRoles(self.portal, TEST_USER_ID, ["LabManager"])
        login(self.portal, "test-user")
        env = Environment()
        self.assertEqual(
            compute("count", {"dataset": "samples", "x": 1}, env),
            compute("count", {"dataset": "samples"}, env))

    def test_parameters_of_the_wrong_kind(self):
        setRoles(self.portal, TEST_USER_ID, ["LabManager"])
        login(self.portal, "test-user")
        env = Environment()
        for params in ({"dataset": ["samples"]},
                       {"dataset": "samples", "trend": "weekly"},
                       {"dataset": "samples", "group_by": {"a": 1}},
                       {"dataset": u"\xfc"}):
            self.assertRaises(QueryError, compute, "group", params, env)

    def test_a_source_must_be_a_name(self):
        setRoles(self.portal, TEST_USER_ID, ["LabManager"])
        login(self.portal, "test-user")
        env = Environment()
        for name in (["count"], {"a": 1}, None):
            self.assertRaises(QueryError, compute, name, {}, env)
            self.assertEqual(get_cost(name, {}), 1)

    def test_sources_answer(self):
        setRoles(self.portal, TEST_USER_ID, ["LabManager"])
        login(self.portal, "test-user")
        env = Environment()
        self.assertEqual(compute("count", {"dataset": "samples"}, env),
                         {"value": 0})
        series = compute("timeseries", {
            "dataset": "samples", "interval": "week", "periods": 4,
            "stack_by": "review_state"}, env)
        self.assertEqual(len(series["buckets"]), 4)
