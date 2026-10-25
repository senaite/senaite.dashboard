# -*- coding: utf-8 -*-
"""Routes for the tiles managers save to the library.

Below @@API/senaite/v1/dashboard/library. Both answer with the library
as it is after the change, so the page shows it at once.
"""

from senaite.dashboard.library import saved
from senaite.dashboard.library.presets import get_categories
from senaite.dashboard.library.presets import get_presets
from senaite.dashboard.routes.base import get_body
from senaite.dashboard.routes.base import route


def library_answer(env):
    """The tile library as it is now, after a change to it."""
    return {"presets": get_presets(env), "categories": get_categories()}


@route("/library/save", ["POST"])
def save_to_library(env, request):
    """Keep a tile in the library.

    Body: {"tile": {...}, "description": text}
    """
    body = get_body()
    saved.save(body.get("tile"), body.get("description"), env)
    return library_answer(env)


@route("/library/remove/<string:preset_id>", ["POST"])
def remove_from_library(env, request, preset_id):
    saved.remove(preset_id, env)
    return library_answer(env)
