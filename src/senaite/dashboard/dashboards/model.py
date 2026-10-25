# -*- coding: utf-8 -*-
"""Tiles and how a user's changes sit on top of a global dashboard.

A tile is a plain mapping:

    {"id": "a1b2c3d4", "type": "kpi", "title": "To receive",
     "source": "count", "params": {...}, "options": {...},
     "layout": {"x": 0, "y": 0, "w": 3, "h": 2}}

A user who rearranges a global dashboard does not get a copy of it.
What they changed is kept as an overlay: tiles they hid, the fields
they changed per tile, and tiles they added. Tiles the administrator
publishes later still show up for them.

Everything here is pure: tiles in, tiles out.
"""

import copy
import json
import re
import uuid

from senaite.dashboard import messagefactory as _
from senaite.dashboard.exceptions import QueryError
from senaite.dashboard.titles import clean_title

GRID_COLUMNS = 12
MAX_ROWS = 400
MAX_TILE_HEIGHT = 24
MAX_TILES = 60
MAX_TILE_SIZE = 16 * 1024

# Ids of tiles: short, and safe in a URL, a key and a CSS selector.
# `\Z`, as `$` also matches before a newline at the end.
TILE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,31}\Z")

# The fields of a tile an overlay may change
TILE_FIELDS = ("type", "title", "source", "params", "options", "layout")


def new_id():
    return uuid.uuid4().hex[:8]


def parse_layout_int(value, minimum, maximum):
    try:
        value = int(value)
    except (TypeError, ValueError):
        raise QueryError(_("Tile layout must be numbers"))
    return max(minimum, min(maximum, value))


def clean_layout(layout):
    """Return the layout snapped onto the grid."""
    layout = layout if isinstance(layout, dict) else {}
    width = parse_layout_int(layout.get("w", 4), 1, GRID_COLUMNS)
    return {
        "x": parse_layout_int(layout.get("x", 0), 0, GRID_COLUMNS - width),
        "y": parse_layout_int(layout.get("y", 0), 0, MAX_ROWS),
        "w": width,
        "h": parse_layout_int(layout.get("h", 2), 1, MAX_TILE_HEIGHT),
    }


def clean_dashboard_title(title):
    """The title of a dashboard, which it cannot be without."""
    title = clean_title(title)
    if not title:
        raise QueryError(_("A dashboard needs a title"))
    return title


def clean_tile_id(tile_id):
    """The id of a tile, or a new one when it is not a valid id."""
    if isinstance(tile_id, basestring) and TILE_ID_RE.match(tile_id):
        return str(tile_id)
    return new_id()


def clean_tile(tile):
    """Return the tile with known fields only, or raise QueryError."""
    if not isinstance(tile, dict):
        raise QueryError(_("A tile must be a mapping"))
    tile_type = tile.get("type")
    if not isinstance(tile_type, basestring) or not tile_type:
        raise QueryError(_("A tile needs a type"))
    params = tile.get("params") or {}
    options = tile.get("options") or {}
    if not isinstance(params, dict) or not isinstance(options, dict):
        raise QueryError(_("Tile settings must be mappings"))
    source = tile.get("source") or None
    if source is not None and not isinstance(source, basestring):
        raise QueryError(_("A tile source must be a name"))
    clean = {
        "id": clean_tile_id(tile.get("id")),
        "type": tile_type,
        "title": clean_title(tile.get("title")),
        "source": source,
        "params": params,
        "options": options,
        "layout": clean_layout(tile.get("layout")),
    }
    if len(json.dumps(clean)) > MAX_TILE_SIZE:
        raise QueryError(_("The tile is too large"))
    return clean


def clean_tiles(tiles):
    """Return the tiles cleaned, with unique ids."""
    if not isinstance(tiles, (list, tuple)):
        raise QueryError(_("Tiles must be a list"))
    if len(tiles) > MAX_TILES:
        raise QueryError(_("A dashboard holds at most ${count} tiles",
                           mapping={"count": MAX_TILES}))
    cleaned = []
    seen = set()
    for tile in tiles:
        tile = clean_tile(tile)
        if tile["id"] in seen:
            tile["id"] = new_id()
        seen.add(tile["id"])
        cleaned.append(tile)
    return cleaned


def tile_changes(base, tile):
    """Return the fields of the tile that differ from the base tile."""
    return {field: copy.deepcopy(tile.get(field)) for field in TILE_FIELDS
            if tile.get(field) != base.get(field)}


def make_overlay(base_tiles, tiles):
    """Return what a user changed on top of the base tiles."""
    base = {tile["id"]: tile for tile in base_tiles}
    ids = {tile["id"] for tile in tiles}
    overrides = {}
    added = []
    for tile in tiles:
        if tile["id"] not in base:
            added.append(copy.deepcopy(tile))
            continue
        changes = tile_changes(base[tile["id"]], tile)
        if changes:
            overrides[tile["id"]] = changes
    return {
        "hidden": sorted(set(base) - ids),
        "overrides": overrides,
        "tiles": added,
    }


def is_empty_overlay(overlay):
    return not overlay or not any(
        overlay.get(key) for key in ("hidden", "overrides", "tiles"))


def apply_overlay(base_tiles, overlay):
    """Return the base tiles with a user's changes applied."""
    overlay = overlay or {}
    hidden = set(overlay.get("hidden") or [])
    overrides = overlay.get("overrides") or {}
    tiles = []
    for base in base_tiles:
        if base["id"] in hidden:
            continue
        tile = copy.deepcopy(base)
        tile.update(copy.deepcopy(overrides.get(base["id"], {})))
        tiles.append(tile)
    taken = {tile["id"] for tile in tiles}
    for tile in overlay.get("tiles") or []:
        if tile["id"] not in taken:
            tiles.append(copy.deepcopy(tile))
    return tiles
