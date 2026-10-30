# -*- coding: utf-8 -*-
"""Replace the global dashboards with the defaults, for development.

Deletes every global dashboard and every user's changes to them, then
installs the defaults again. Personal dashboards stay. Managers can
also restore missing defaults in the browser; this script is for
starting over.

Usage, with the instance stopped::

    bin/instance run path/to/scripts/reset_defaults.py <site-id> [<user>]

The user runs the reset and must be a manager of the Zope root; it is
`admin` by default.
"""

from __future__ import print_function

import sys

import transaction
from AccessControl.SecurityManagement import newSecurityManager
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


def find_user(portal, user_id):
    """A user of the Zope root, in the user folder it lives in."""
    folder = portal.getPhysicalRoot().acl_users
    user = folder.getUserById(user_id)
    if user is None:
        raise SystemExit("No user {} in the Zope root".format(user_id))
    return user.__of__(folder)


def main(app, argv):
    args = script_args(argv)
    if not args:
        print(__doc__)
        return 2
    portal = enter_site(app, args[0])
    user_id = args[1] if len(args) > 1 else "admin"
    newSecurityManager(None, find_user(portal, user_id))
    env = Environment()
    for record in storage.list_globals():
        shared.delete(record["id"], env)
    install_defaults(env)
    transaction.commit()
    print("Installed {} global dashboards".format(
        len(storage.list_globals())))
    return 0


if "app" in globals():
    sys.exit(main(app, sys.argv))  # noqa: F821
