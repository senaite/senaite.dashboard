# -*- coding: utf-8 -*-
"""Replace the global dashboards with the defaults, for development.

Deletes every global dashboard and every user's changes to them, then
installs the defaults again. Personal dashboards stay.

Usage, with the instance stopped::

    bin/instance run \\
        src/senaite.dashboard/src/senaite/dashboard/devtools/\\
reset_defaults.py <site-id>
"""

from __future__ import print_function

import sys

import transaction
from AccessControl.SecurityManagement import newSecurityManager
from BTrees.OOBTree import OOBTree
from senaite.dashboard import storage
from senaite.dashboard.dashboards import shared
from senaite.dashboard.dashboards.defaults import install_defaults
from senaite.dashboard.env import Environment
from Testing.makerequest import makerequest
from zope.component.hooks import setSite
from zope.globalrequest import setRequest


def script_args(argv):
    for index, arg in enumerate(argv):
        if arg.endswith("reset_defaults.py"):
            return argv[index + 1:]
    return argv[1:]


def enter_site(app, site_id):
    """The site, set up the way a request to it would find it."""
    app = makerequest(app)
    setRequest(app.REQUEST)
    portal = app[site_id]
    setSite(portal)
    portal.setupCurrentSkin(app.REQUEST)
    return portal


def find_admin(portal):
    """The `admin` of the server, in the user folder it lives in."""
    folder = portal.getPhysicalRoot().acl_users
    return folder.getUserById("admin").__of__(folder)


def drop_legacy_user_records():
    """Records of the first prototype were plain mappings per user."""
    users = storage.get_tree(storage.USERS, create=True)
    for user_id in list(users.keys()):
        if not isinstance(users[user_id], OOBTree):
            del users[user_id]


def main(app, argv):
    args = script_args(argv)
    if not args:
        print(__doc__)
        return 2
    portal = enter_site(app, args[0])
    newSecurityManager(None, find_admin(portal))
    env = Environment()
    drop_legacy_user_records()
    for record in storage.list_globals():
        shared.delete(record["id"], env)
    install_defaults(env)
    transaction.commit()
    print("Installed {} global dashboards".format(
        len(storage.list_globals())))
    return 0


if "app" in globals():
    sys.exit(main(app, sys.argv))  # noqa: F821
