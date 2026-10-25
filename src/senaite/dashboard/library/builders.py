# -*- coding: utf-8 -*-
"""What tiles of the library are built with.

A preset is a complete tile with a title and a description; the user
adds it with one click and may change it afterwards. The builders here
make the tile of each kind of preset (a number, groups, a chart, a
table, a duration), the parameters on a dataset, and turn
(id, description, tile) entries into presets. Add-ons build their
presets with them too.
"""

import copy

from senaite.core.i18n import translate
from senaite.dashboard.query import timeline

WEEKLY_TREND = timeline.DEFAULT_TREND
LAST_30_DAYS = {"created": {"min": "$today-30d"}}


def tile_params(dataset, filters, **kwargs):
    """Parameters of a tile on a dataset."""
    kwargs.update({"dataset": dataset, "filters": dict(filters)})
    return kwargs


def samples(filters, **kwargs):
    """Samples of the user's client; a laboratory user sees all."""
    filters = dict(filters, getClientUID="$client")
    return tile_params("samples", filters, **kwargs)


def analyses(filters, **kwargs):
    return tile_params("analyses", filters, **kwargs)


def worksheets(filters, **kwargs):
    return tile_params("worksheets", filters, **kwargs)


def make_preset_tile(tile_type, source, title, params, options, size):
    """A tile of the library; it gets its id and place when added.

    :param size: (width, height) in grid cells
    """
    width, height = size
    return {
        "type": tile_type,
        "title": title,
        "source": source,
        "params": params,
        "options": options,
        "layout": {"w": width, "h": height},
    }


def kpi(title, params, link=None, color=None, icon=None):
    """A number, optionally with its course over the last weeks."""
    options = {"link": link, "color": color, "icon": icon}
    options = {key: value for key, value in options.items() if value}
    return make_preset_tile("kpi", "count", title, params, options, (3, 2))


def group(tile_type, title, params, h=4):
    """Numbers per value of a field, as bars or a donut."""
    width = 4 if tile_type == "donut" else 6
    return make_preset_tile(tile_type, "group", title, params, {},
                            (width, h))


def chart(title, params, style="bars"):
    """Numbers per period."""
    return make_preset_tile("chart", "timeseries", title, params,
                            {"style": style}, (8, 4))


def table(title, params):
    """The first objects of a search."""
    return make_preset_tile("table", "list", title, params, {}, (6, 4))


def span(title, params):
    """How long it takes between two dates."""
    return make_preset_tile("kpi", "span", title, params, {"icon": "clock"},
                            (3, 2))


def translate_title(title, languages=None):
    """Translate a title, into several languages for a stored tile."""
    if not languages:
        return translate(title, to_utf8=False)
    return {lang: translate(title, to_utf8=False, target_language=lang)
            for lang in languages}


def translate_tile(tile, languages=None):
    """Return a complete tile with its title translated."""
    tile = dict({"source": None, "params": {}, "options": {}},
                **copy.deepcopy(tile))
    tile["title"] = translate_title(tile["title"], languages)
    return tile


def to_preset(preset_id, category, description, tile, configure=False):
    """A preset as the library shows it.

    :param configure: open the settings of the tile once it is added,
        for tiles that show nothing before they are filled in
    """
    return {
        "id": preset_id,
        "category": category,
        "description": translate(description, to_utf8=False),
        "tile": translate_tile(tile),
        "configure": configure,
    }


def to_presets(category, entries, configure=False):
    """The presets of a category, from (id, description, tile)."""
    return [to_preset(preset_id, category, description, tile, configure)
            for preset_id, description, tile in entries]
