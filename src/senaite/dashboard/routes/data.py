# -*- coding: utf-8 -*-
"""Routes for the data of tiles and the choices of the tile editor.

Below @@API/senaite/v1/dashboard. The page asks for the data of all
tiles of a dashboard in one request; a request may cause only so many
catalog searches.
"""

from senaite.dashboard import messagefactory as _
from senaite.dashboard.exceptions import QueryError
from senaite.dashboard.query.compute import compute
from senaite.dashboard.query.compute import get_cost
from senaite.dashboard.query.registry import get_dataset
from senaite.dashboard.query.vocabularies import get_choices
from senaite.dashboard.routes.base import get_body
from senaite.dashboard.routes.base import get_tiles
from senaite.dashboard.routes.base import message
from senaite.dashboard.routes.base import route

# A dashboard holds at most this many tiles, and asks for all at once
MAX_TILES_PER_REQUEST = 60
# Catalog searches one request may cause, roughly: a dashboard of
# charts over long periods is fine, sixty of them are not
MAX_COST_PER_REQUEST = 1000


def compute_tile(tile, env):
    """Return the data of one tile, or the reason there is none."""
    try:
        return compute(tile.get("source"), tile.get("params") or {}, env)
    except QueryError as exc:
        return {"error": message(exc)}


def answer_key(tile):
    """The id of a tile as a key of the answer."""
    tile_id = tile.get("id")
    return tile_id if isinstance(tile_id, basestring) else repr(tile_id)


def data_tiles(body):
    """The tiles of a data request that have a data source."""
    tiles = [tile for tile in get_tiles(body)
             if isinstance(tile, dict) and tile.get("source")]
    if len(tiles) > MAX_TILES_PER_REQUEST:
        raise QueryError(_("Too many tiles in one request"))
    cost = sum(get_cost(tile.get("source"), tile.get("params"))
               for tile in tiles)
    if cost > MAX_COST_PER_REQUEST:
        raise QueryError(_("This asks for too much at once; use fewer "
                           "or shorter charts"))
    return tiles


@route("/data", ["POST"])
def data(env, request):
    """The data of many tiles, in one request.

    Body: {"tiles": [{"id", "source", "params"}, ...]}
    Answer: {"results": {tile id: data or {"error": text}}}
    """
    results = {answer_key(tile): compute_tile(tile, env)
               for tile in data_tiles(get_body())}
    # senaite.jsonapi errors set the response status when they are
    # constructed; one caught for a single tile must not turn the
    # answer for all of them into an error
    request.response.setStatus(200)
    return {"results": results, "now": env.now.ISO8601()}


@route("/choices/<string:dataset>/<string:field>", ["GET"])
def choices(env, request, dataset, field):
    dataset = get_dataset(dataset, env)
    field = dataset.get_field(field, env)
    return {"choices": get_choices(field, dataset, env)}
