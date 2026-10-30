# -*- coding: utf-8 -*-
"""What a data source knows about the request it answers."""

from collections import OrderedDict

from bika.lims import api
from DateTime import DateTime
from plone.memoize.instance import memoize
from senaite.dashboard import messagefactory as _
from senaite.dashboard.titles import get_language

# The roles of SENAITE, with the names users know them by, in the order
# a manager picks them for a global dashboard
ROLES = OrderedDict([
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

# Roles of client contacts
CLIENT_ROLES = frozenset(["Client"])

# Roles that mark a member of the laboratory staff. A user without any
# of them is treated like a client contact: fields that only make
# sense inside the laboratory are not offered.
LAB_ROLES = frozenset(ROLES) - CLIENT_ROLES


class LabOnly(object):
    """Something that may be kept from users outside the laboratory.

    A dataset, a field or a column sets `lab_only` to hide itself from
    client contacts.
    """
    lab_only = False

    def is_available(self, env):
        """Whether the user may use it."""
        return env.is_lab or not self.lab_only


class Environment(object):
    """The current user, site and time, resolved once per request."""

    def __init__(self, portal=None, user=None, now=None):
        self.portal = portal or api.get_portal()
        self.user = user or api.get_current_user()
        self.now = now or DateTime()

    @property
    def user_id(self):
        return self.user.getId()

    @property
    @memoize
    def roles(self):
        return frozenset(self.user.getRolesInContext(self.portal))

    @property
    def is_lab(self):
        return bool(self.roles & LAB_ROLES)

    @property
    @memoize
    def client_uid(self):
        """UID of the client the user belongs to, or None."""
        client = api.get_user_client(self.user)
        return api.get_uid(client) if client else None

    @property
    @memoize
    def fullname(self):
        return api.get_user_fullname(self.user) or self.user_id

    @property
    def language(self):
        return get_language()

    def can(self, permission, obj=None):
        """Whether the user has the permission, on the site by default."""
        return bool(self.user.has_permission(permission, obj or self.portal))
