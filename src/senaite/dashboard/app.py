# -*- coding: utf-8 -*-
"""What the pages of the add-on start from, each in one mapping.

The page carries it in a script element, so the first paint does not
wait for a request (see browser/view.py). Both pages share addresses,
language and texts; the dashboard adds the dashboards, the datasets,
the tile library and what the user may do, the page of the datasets
what a manager may define datasets of.
"""

from collections import OrderedDict

from bika.lims import api
from senaite.core.i18n import translate
from senaite.dashboard import messagefactory as _
from senaite.dashboard.access import can_customize
from senaite.dashboard.access import can_manage
from senaite.dashboard.dashboards import views
from senaite.dashboard.library.presets import get_categories
from senaite.dashboard.library.presets import get_presets
from senaite.dashboard.query import catalogs
from senaite.dashboard.query import custom
from senaite.dashboard.query import timeline
from senaite.dashboard.query.compute import describe_sources
from senaite.dashboard.query.registry import get_datasets
from senaite.dashboard.query.sources import MAX_GROUPS
from senaite.dashboard.query.sources import MAX_ROWS
from senaite.dashboard.strings import get_ui_strings

# Roles a manager may give a global dashboard to, with the names users
# know them by
ASSIGNABLE_ROLES = OrderedDict([
    ("LabManager", _("Lab managers")),
    ("LabClerk", _("Lab clerks")),
    ("Analyst", _("Analysts")),
    ("Verifier", _("Verifiers")),
    ("Publisher", _("Publishers")),
    ("Sampler", _("Samplers")),
    ("Preserver", _("Preservers")),
    ("SamplingCoordinator", _("Sampling coordinators")),
    ("RegulatoryInspector", _("Regulatory inspectors")),
    ("Client", _("Client contacts")),
    ("Manager", _("Site administrators")),
])


def get_page_data(env):
    """What every page of the add-on needs: addresses, language, texts."""
    portal_url = api.get_url(env.portal)
    return {
        "portal_url": portal_url,
        "api_url": "{}/@@API/senaite/v1/dashboard".format(portal_url),
        "dashboard_url": "{}/senaite-dashboard".format(portal_url),
        "datasets_url": "{}/@@dashboard-datasets".format(portal_url),
        "language": env.language,
        "strings": get_ui_strings(),
    }


def get_limits():
    """What the tile editor offers at most; the sources hold to it."""
    return {
        "periods": timeline.MAX_PERIODS,
        "groups": MAX_GROUPS,
        "rows": MAX_ROWS,
    }


def get_assignable_roles():
    valid = set(api.get_portal().validRoles())
    return [{"id": role, "title": translate(title, to_utf8=False)}
            for role, title in ASSIGNABLE_ROLES.items() if role in valid]


def bootstrap(env):
    """Return what the dashboard page starts from."""
    dashboards = views.list_dashboards(env)
    manage = can_manage(env)
    data = get_page_data(env)
    data.update({
        "now": env.now.ISO8601(),
        "user": {"id": env.user_id, "fullname": env.fullname,
                 "is_lab": env.is_lab},
        "permissions": {
            "customize": can_customize(env),
            "manage": manage,
        },
        "dashboards": dashboards,
        "active": views.get_active_id(env, dashboards),
        "datasets": [dataset.describe(env) for dataset in get_datasets(env)],
        "sources": describe_sources(),
        "presets": get_presets(env),
        "categories": get_categories(),
        "limits": get_limits(),
        "default_trend": timeline.DEFAULT_TREND,
        "roles": get_assignable_roles() if manage else [],
    })
    return data


def bootstrap_datasets(env):
    """Return what the page of the datasets starts from."""
    data = get_page_data(env)
    data.update({
        "types": catalogs.get_candidates(),
        "datasets": custom.list_definitions(env),
    })
    return data
