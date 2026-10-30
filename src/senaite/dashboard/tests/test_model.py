# -*- coding: utf-8 -*-
"""Unit tests for tiles and overlays."""

import unittest

from senaite.dashboard.dashboards import model
from senaite.dashboard.exceptions import ValidationError
from senaite.dashboard.titles import title_text


def tile(tile_id, x=0, y=0, w=3, h=2, **kwargs):
    data = {"id": tile_id, "type": "kpi", "title": tile_id,
            "source": "count", "params": {"dataset": "samples"},
            "options": {}, "layout": {"x": x, "y": y, "w": w, "h": h}}
    data.update(kwargs)
    return data


class LayoutTestCase(unittest.TestCase):

    def test_snaps_onto_the_grid(self):
        self.assertEqual(
            model.clean_layout({"x": 11, "y": -3, "w": 4, "h": 99}),
            {"x": 8, "y": 0, "w": 4, "h": model.MAX_TILE_HEIGHT})

    def test_defaults(self):
        self.assertEqual(model.clean_layout(None),
                         {"x": 0, "y": 0, "w": 4, "h": 2})

    def test_refuses_text(self):
        self.assertRaises(ValidationError, model.clean_layout, {"w": "wide"})


class TileTestCase(unittest.TestCase):

    def test_keeps_known_fields_only(self):
        cleaned = model.clean_tile(dict(tile("a"), script="alert(1)"))
        self.assertNotIn("script", cleaned)

    def test_needs_a_type(self):
        self.assertRaises(ValidationError, model.clean_tile, {"id": "a"})

    def test_gets_an_id(self):
        self.assertTrue(model.clean_tile({"type": "note"})["id"])

    def test_duplicate_ids_are_renamed(self):
        tiles = model.clean_tiles([tile("a"), tile("a")])
        self.assertNotEqual(tiles[0]["id"], tiles[1]["id"])

    def test_too_many_tiles(self):
        tiles = [tile(str(i)) for i in range(model.MAX_TILES + 1)]
        self.assertRaises(ValidationError, model.clean_tiles, tiles)

    def test_too_large(self):
        big = tile("a", options={"text": "x" * model.MAX_TILE_SIZE})
        self.assertRaises(ValidationError, model.clean_tile, big)

    def test_title_in_several_languages(self):
        title = {"en": "Samples", "de": u"Proben"}
        self.assertEqual(model.clean_tile(tile("a", title=title))["title"],
                         title)
        self.assertEqual(title_text(title, "de"), u"Proben")
        self.assertEqual(title_text(title, "fr"), u"Samples")


class OverlayTestCase(unittest.TestCase):

    def setUp(self):
        self.base = [tile("a"), tile("b", x=3), tile("c", x=6)]

    def roundtrip(self, tiles):
        overlay = model.make_overlay(self.base, tiles)
        return overlay, model.apply_overlay(self.base, overlay)

    def test_unchanged_is_empty(self):
        overlay, tiles = self.roundtrip(self.base)
        self.assertTrue(model.is_empty_overlay(overlay))
        self.assertEqual(tiles, self.base)

    def test_moved_tile(self):
        moved = [tile("a", y=4), tile("b", x=3), tile("c", x=6)]
        overlay, tiles = self.roundtrip(moved)
        self.assertEqual(overlay["overrides"],
                         {"a": {"layout": moved[0]["layout"]}})
        self.assertEqual(tiles, moved)

    def test_hidden_and_added(self):
        changed = [tile("a"), tile("c", x=6), tile("mine", type="note")]
        overlay, tiles = self.roundtrip(changed)
        self.assertEqual(overlay["hidden"], ["b"])
        self.assertEqual([t["id"] for t in overlay["tiles"]], ["mine"])
        self.assertEqual(tiles, changed)

    def test_new_base_tiles_show_up(self):
        overlay = model.make_overlay(self.base, self.base[:2])
        newer = self.base + [tile("d", y=2)]
        ids = [t["id"] for t in model.apply_overlay(newer, overlay)]
        self.assertEqual(ids, ["a", "b", "d"])

    def test_overrides_of_removed_base_tiles_are_ignored(self):
        overlay = {"overrides": {"gone": {"title": "x"}}}
        self.assertEqual(model.apply_overlay(self.base, overlay), self.base)

    def test_does_not_change_the_base(self):
        overlay = {"overrides": {"a": {"title": "changed"}}}
        model.apply_overlay(self.base, overlay)
        self.assertEqual(self.base[0]["title"], "a")
