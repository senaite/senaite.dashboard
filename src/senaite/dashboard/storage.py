# -*- coding: utf-8 -*-
"""Where the add-on keeps what it keeps: an annotation on the site.

Trees for global dashboards, for tiles saved to the library and for
datasets defined in the browser, each by id, and one tree per user id
with what that user keeps: one entry per personal dashboard, per
overlay on a global dashboard and for the dashboard they looked at
last. A save writes one small entry, not everything a user has.

Entries are plain mappings that are copied on read and replaced as a
whole on write, so a change is always persisted and a caller never
edits stored data in place.

Users are keyed by id, not by a member property, so that LDAP users
work like local ones.
"""

import copy

from bika.lims import api
from BTrees.OOBTree import OOBTree
from zope.annotation.interfaces import IAnnotations

ANNOTATION_KEY = "senaite.dashboard"
GLOBALS = "globals"
USERS = "users"
LIBRARY = "library"
DATASETS = "datasets"

# Keys of what a user keeps
DASHBOARD = "dashboard:"
OVERLAY = "overlay:"
ACTIVE = "active"


def get_root(create=False):
    """Return the storage root, or None when there is none yet.

    Reading never creates it: a GET must not write to the database.
    """
    annotations = IAnnotations(api.get_portal())
    root = annotations.get(ANNOTATION_KEY)
    if root is None and create:
        root = OOBTree()
        root[GLOBALS] = OOBTree()
        root[USERS] = OOBTree()
        annotations[ANNOTATION_KEY] = root
    return root


def get_tree(name, create=False):
    """A tree of the root; trees added in later versions on demand."""
    root = get_root(create=create)
    if root is None:
        return {}
    if create and name not in root:
        root[name] = OOBTree()
    return root.get(name, {})


# Records by id

def get_record(tree_name, key):
    """A copy of the record, or None."""
    record = get_tree(tree_name).get(key)
    return copy.deepcopy(record) if record is not None else None


def list_records(tree_name):
    return [copy.deepcopy(record)
            for record in get_tree(tree_name).values()]


def set_record(tree_name, key, record):
    get_tree(tree_name, create=True)[key] = copy.deepcopy(record)


def delete_record(tree_name, key):
    tree = get_tree(tree_name)
    if key in tree:
        del tree[key]


# Global dashboards, by id

def get_global(dashboard_id):
    return get_record(GLOBALS, dashboard_id)


def list_globals():
    return list_records(GLOBALS)


def set_global(record):
    set_record(GLOBALS, record["id"], record)


def delete_global(dashboard_id):
    delete_record(GLOBALS, dashboard_id)


# Tiles saved to the library, by id

def get_library_tile(preset_id):
    return get_record(LIBRARY, preset_id)


def list_library_tiles():
    return list_records(LIBRARY)


def set_library_tile(record):
    set_record(LIBRARY, record["id"], record)


def delete_library_tile(preset_id):
    delete_record(LIBRARY, preset_id)


# Datasets defined in the browser, by name

def get_dataset(name):
    return get_record(DATASETS, name)


def list_datasets():
    return list_records(DATASETS)


def set_dataset(record):
    set_record(DATASETS, record["name"], record)


def delete_dataset(name):
    delete_record(DATASETS, name)


# What a user keeps

def dashboard_key(dashboard_id):
    """Key of a personal dashboard."""
    return DASHBOARD + dashboard_id


def overlay_key(dashboard_id):
    """Key of a user's changes to a global dashboard."""
    return OVERLAY + dashboard_id


def get_user_tree(user_id, create=False):
    users = get_tree(USERS, create=create)
    tree = users.get(user_id)
    if tree is None and create:
        tree = users[user_id] = OOBTree()
    return tree if tree is not None else {}


def get_user_value(user_id, key, default=None):
    value = get_user_tree(user_id).get(key)
    return copy.deepcopy(value) if value is not None else default


def set_user_value(user_id, key, value):
    get_user_tree(user_id, create=True)[key] = copy.deepcopy(value)


def delete_user_value(user_id, key):
    tree = get_user_tree(user_id)
    if key in tree:
        del tree[key]


def list_user_values(user_id, prefix):
    """The values of a user whose keys start with the prefix."""
    tree = get_user_tree(user_id)
    keys = [key for key in tree.keys() if key.startswith(prefix)]
    return [copy.deepcopy(tree[key]) for key in keys]


def list_user_ids():
    return list(get_tree(USERS).keys())


def delete_overlays(dashboard_id):
    """Drop every user's changes to a global dashboard."""
    key = overlay_key(dashboard_id)
    for user_id in list_user_ids():
        delete_user_value(user_id, key)
