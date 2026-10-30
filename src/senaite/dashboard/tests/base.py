# -*- coding: utf-8 -*-
"""What the integration tests share: a site and users with roles."""

import unittest

from bika.lims import api
from plone.app.testing import login
from senaite.dashboard.env import Environment
from senaite.dashboard.tests.layers import DASHBOARD_TESTING

# The users every test may act as, with their roles on the site
USERS = {
    "manager": ["LabManager"],
    "analyst": ["Analyst"],
    "contact": ["Client"],
}


def add_user(user_id, roles):
    acl = api.get_tool("acl_users")
    acl.userFolderAddUser(user_id, "secret-" + user_id, roles, [])


class DashboardTestCase(unittest.TestCase):
    """A site with senaite.dashboard and the users of `USERS`."""
    layer = DASHBOARD_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        for user_id, roles in USERS.items():
            add_user(user_id, roles)

    def as_user(self, user_id):
        """Log the user in and return the environment of a request."""
        login(self.portal, user_id)
        return Environment()
