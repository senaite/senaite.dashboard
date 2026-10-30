# -*- coding: utf-8 -*-
"""Tiles a manager saved to the tile library, for everybody.

A manager who made a tile worth having keeps it in the library; every
user can then add it like the tiles senaite.dashboard ships with. Only
the tile is kept, not where it sat: it gets its place when added.
"""

from senaite.dashboard import messagefactory as _
from senaite.dashboard import storage
from senaite.dashboard.access import can_manage
from senaite.dashboard.access import check_manage
from senaite.dashboard.dashboards import model
from senaite.dashboard.exceptions import NotFound
from senaite.dashboard.exceptions import check_limit
from senaite.dashboard.interfaces import IDashboardPresetProvider
from senaite.dashboard.titles import clean_text_title
from senaite.dashboard.titles import new_id
from senaite.dashboard.titles import title_text
from zope.interface import implementer

# Category of the saved tiles in the library
CATEGORY = "saved"
MAX_SAVED_TILES = 100
ID_PREFIX = "saved-"


def check_room():
    check_limit(len(storage.list_library_tiles()), MAX_SAVED_TILES,
                _("The library keeps at most ${count} saved tiles",
                  mapping={"count": MAX_SAVED_TILES}))


def to_library_tile(tile):
    """The tile without its id and its place on a dashboard."""
    tile = model.clean_tile(tile)
    del tile["id"]
    tile["layout"] = {"w": tile["layout"]["w"], "h": tile["layout"]["h"]}
    return tile


def save(tile, description, env):
    """Keep a tile in the library."""
    check_manage(env)
    check_room()
    record = {
        "id": ID_PREFIX + new_id(),
        "description": clean_text_title(description),
        "tile": to_library_tile(tile),
        "created": env.now.ISO8601(),
        "by": env.user_id,
    }
    storage.set_library_tile(record)
    return record


def remove(preset_id, env):
    check_manage(env)
    if storage.get_library_tile(preset_id) is None:
        raise NotFound(_("There is no such tile in the library"))
    storage.delete_library_tile(preset_id)


def to_preset(record, env):
    """A saved tile as the library shows it.

    Its title and description are what the manager wrote, so they are
    shown as they are, not translated.
    """
    tile = record["tile"]
    description = record["description"] or title_text(
        tile["title"], env.language)
    return {
        "id": record["id"],
        "category": CATEGORY,
        "description": description,
        "tile": tile,
        "removable": can_manage(env),
    }


@implementer(IDashboardPresetProvider)
class SavedPresets(object):
    """The tiles managers saved to the library."""

    categories = [(CATEGORY, _("Saved by your laboratory"))]

    def __call__(self, env):
        records = sorted(storage.list_library_tiles(),
                         key=lambda record: record["created"])
        return [to_preset(record, env) for record in records]
