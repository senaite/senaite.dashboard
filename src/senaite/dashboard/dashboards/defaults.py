# -*- coding: utf-8 -*-
"""The global dashboards a fresh installation starts with.

Each default has a key that its record keeps, so that the ones a
manager deleted can be told apart and restored, whatever the others
are called by now.
"""

from bika.lims import api
from senaite.dashboard import messagefactory as _
from senaite.dashboard import storage
from senaite.dashboard.access import check_manage
from senaite.dashboard.dashboards import shared
from senaite.dashboard.env import LAB_ROLES
from senaite.dashboard.library.builders import translate_tile
from senaite.dashboard.library.builders import translate_title
from senaite.dashboard.library.builtin import PRESET_GROUPS
from senaite.dashboard.titles import new_id

# Stored titles always carry English, the language a title falls back to
FALLBACK_LANGUAGE = "en"

# (preset, x, y, w, h)
LABORATORY = [
    ("samples-to-receive", 0, 0, 3, 2),
    ("samples-results-pending", 3, 0, 3, 2),
    ("samples-to-verify", 6, 0, 3, 2),
    ("samples-to-publish", 9, 0, 3, 2),
    ("samples-registered-weekly", 0, 2, 8, 5),
    ("samples-open-by-status", 8, 2, 4, 5),
    ("samples-due-soon", 0, 7, 6, 5),
    ("analyses-by-analyst", 6, 7, 6, 5),
    ("samples-overdue", 0, 12, 3, 2),
    ("samples-turnaround", 3, 12, 3, 2),
    ("worksheets-open", 6, 12, 3, 2),
    ("samples-this-week", 9, 12, 3, 2),
]

MY_WORK = [
    ("analyses-mine", 0, 0, 4, 2),
    ("worksheets-mine", 4, 0, 4, 2),
    ("analyses-to-verify", 8, 0, 4, 2),
    ("analyses-due-mine", 0, 2, 7, 5),
    ("analyses-to-verify-by-service", 7, 2, 5, 5),
    ("analyses-captured-daily", 0, 7, 12, 4),
]

CLIENT = [
    ("samples-to-receive", 0, 0, 4, 2),
    ("samples-results-pending", 4, 0, 4, 2),
    ("samples-published-30d", 8, 0, 4, 2),
    ("samples-recently-published", 0, 2, 7, 5),
    ("samples-open-by-status", 7, 2, 5, 5),
    ("samples-registered-weekly", 0, 7, 12, 4),
]

# (key, title, roles, tiles)
DEFAULTS = [
    ("laboratory", _("Laboratory"), sorted(LAB_ROLES), LABORATORY),
    ("my-work", _("My work"), ["Analyst", "LabManager", "Manager"],
     MY_WORK),
    ("overview", _("Overview"), ["Client"], CLIENT),
]


def find_preset(preset_id):
    """The tile of a preset senaite.dashboard ships with."""
    for category, entries in PRESET_GROUPS:
        for entry_id, description, tile in entries:
            if entry_id == preset_id:
                return tile
    raise KeyError(preset_id)


def make_tile(preset_id, x, y, w, h, languages):
    """A new tile from a preset, placed on the grid."""
    tile = translate_tile(find_preset(preset_id), languages)
    tile["id"] = new_id()
    tile["layout"] = {"x": x, "y": y, "w": w, "h": h}
    return tile


def get_languages():
    """The languages the titles of the defaults are stored in.

    Those the site offers, so that each user reads the titles in their
    language; the page shows the one in use.
    """
    languages = api.get_registry_record("plone.available_languages") or []
    return sorted(set(languages) | {FALLBACK_LANGUAGE})


def make_tiles(entries, languages):
    return [make_tile(preset_id, x, y, w, h, languages)
            for preset_id, x, y, w, h in entries]


def get_default_key(record):
    """The default a global dashboard was made from.

    Records of installations before the key was kept go by their id,
    which was made from the same English title.
    """
    return record.get("default", record["id"])


def is_missing(default, records):
    key = default[0]
    return all(get_default_key(record) != key for record in records)


def create_default(default, env):
    """Create one default dashboard as a draft and return its id."""
    key, title, roles, entries = default
    languages = get_languages()
    record = shared.create(translate_title(title, languages),
                           make_tiles(entries, languages), roles, env,
                           default=key)
    return record["id"]


def restore_defaults(env):
    """Create the default dashboards that are missing, as drafts.

    Dashboards that are there stay as they are, and so do the changes
    users made to them. Returns the ids of the dashboards created.
    """
    check_manage(env)
    records = storage.list_globals()
    return [create_default(default, env) for default in DEFAULTS
            if is_missing(default, records)]


def install_defaults(env):
    """Create and publish the default dashboards, once.

    Does nothing when there are global dashboards already, so a
    reinstall never overwrites what an administrator changed.
    """
    if storage.list_globals():
        return
    for dashboard_id in restore_defaults(env):
        shared.publish(dashboard_id, env)
