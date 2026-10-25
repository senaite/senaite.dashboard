# -*- coding: utf-8 -*-
"""Test layer: a SENAITE site with senaite.dashboard installed."""

import transaction
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from senaite.core.tests.layers import BASE_LAYER_FIXTURE


class DashboardLayer(PloneSandboxLayer):
    defaultBases = (BASE_LAYER_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        import senaite.jsonapi
        import senaite.dashboard
        self.loadZCML(package=senaite.jsonapi)
        self.loadZCML(package=senaite.dashboard)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "senaite.dashboard:default")
        transaction.commit()


DASHBOARD_FIXTURE = DashboardLayer()
DASHBOARD_TESTING = FunctionalTesting(
    bases=(DASHBOARD_FIXTURE, ), name="senaite.dashboard:Functional")
