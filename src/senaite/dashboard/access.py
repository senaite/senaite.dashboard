# -*- coding: utf-8 -*-
"""What the user of a request may do with dashboards."""

from senaite.dashboard import messagefactory as _
from senaite.dashboard.exceptions import Forbidden
from senaite.dashboard.permissions import CustomizeDashboard
from senaite.dashboard.permissions import ManageDashboards


def can_customize(env):
    return env.can(CustomizeDashboard)


def can_manage(env):
    return env.can(ManageDashboards)


def check(env, permission):
    if not env.can(permission):
        raise Forbidden(_("You are not allowed to do this"))


def check_customize(env):
    check(env, CustomizeDashboard)


def check_manage(env):
    check(env, ManageDashboards)
