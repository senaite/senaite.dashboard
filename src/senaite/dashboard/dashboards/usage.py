# -*- coding: utf-8 -*-
"""Where a dataset defined in the browser is used.

The query part knows nothing about dashboards; a manager who removes a
dataset still wants to know which dashboards and saved tiles show it.
"""

from senaite.dashboard import storage
from senaite.dashboard.access import check_manage


def uses_dataset(tile, name):
    return (tile.get("params") or {}).get("dataset") == name


def is_used_by(record, name):
    """Whether a draft or the published version of a global dashboard
    has a tile on the dataset."""
    tiles = list(record["draft"]["tiles"])
    tiles.extend((record.get("published") or {}).get("tiles") or [])
    return any(uses_dataset(tile, name) for tile in tiles)


def count_usage(name, env):
    """How many global dashboards and saved tiles use the dataset.

    Personal dashboards are not searched: they are many, and only their
    owner sees the tile that has no dataset any more.
    """
    check_manage(env)
    return {
        "dashboards": len([record for record in storage.list_globals()
                           if is_used_by(record, name)]),
        "library": len([record for record in storage.list_library_tiles()
                        if uses_dataset(record["tile"], name)]),
    }
