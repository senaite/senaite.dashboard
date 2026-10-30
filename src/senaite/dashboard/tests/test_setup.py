# -*- coding: utf-8 -*-
"""Install, uninstall and the storage on the site."""

import unittest

from bika.lims import api
from plone.app.testing import applyProfile
from plone.browserlayer.utils import registered_layers
from senaite.dashboard import storage
from senaite.dashboard.interfaces import ISenaiteDashboardLayer
from senaite.dashboard.tests.layers import DASHBOARD_TESTING
from zope.annotation.interfaces import IAnnotations


class SetupTestCase(unittest.TestCase):
    layer = DASHBOARD_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

    def test_the_layer_is_registered(self):
        self.assertIn(ISenaiteDashboardLayer, registered_layers())

    def test_the_storage_knows_its_version(self):
        self.assertEqual(storage.get_version(), storage.VERSION)

    def test_uninstall_removes_the_layer_and_keeps_the_dashboards(self):
        dashboards = storage.list_globals()
        applyProfile(self.portal, "senaite.dashboard:uninstall")
        self.assertNotIn(ISenaiteDashboardLayer, registered_layers())
        self.assertEqual(storage.list_globals(), dashboards)

    def test_reinstall_keeps_the_dashboards(self):
        before = sorted(r["id"] for r in storage.list_globals())
        applyProfile(self.portal, "senaite.dashboard:uninstall")
        applyProfile(self.portal, "senaite.dashboard:default")
        after = sorted(r["id"] for r in storage.list_globals())
        self.assertEqual(after, before)


class StorageTestCase(unittest.TestCase):
    layer = DASHBOARD_TESTING

    def setUp(self):
        self.annotations = IAnnotations(api.get_portal())
        self.root = self.annotations.pop(storage.ANNOTATION_KEY)

    def tearDown(self):
        self.annotations[storage.ANNOTATION_KEY] = self.root

    def test_reading_never_creates_the_storage(self):
        self.assertEqual(storage.list_globals(), [])
        self.assertIsNone(storage.get_global("anything"))
        self.assertIsNone(storage.get_version())
        self.assertNotIn(storage.ANNOTATION_KEY, self.annotations)

    def test_a_record_is_copied_on_read_and_write(self):
        record = {"id": "a", "tiles": []}
        storage.set_global(record)
        record["tiles"].append("changed")
        stored = storage.get_global("a")
        self.assertEqual(stored["tiles"], [])
        stored["tiles"].append("changed")
        self.assertEqual(storage.get_global("a")["tiles"], [])
