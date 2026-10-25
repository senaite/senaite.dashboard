# -*- coding: utf-8 -*-
"""Unit tests for checking the parameters of tiles and request bodies."""

import unittest

from senaite.dashboard.dashboards.ids import is_dashboard_id
from senaite.dashboard.dashboards.model import clean_tile_id
from senaite.dashboard.exceptions import QueryError
from senaite.dashboard.query import params
from senaite.dashboard.routes.base import parse_body
from senaite.dashboard.titles import clean_title
from senaite.jsonapi.exceptions import BadRequestError

SPEC = {"dataset": params.NAME, "columns": params.NAMES,
        "filters": params.MAPPING, "limit": params.NUMBER}


class ParamsTestCase(unittest.TestCase):

    def test_keeps_declared_parameters_only(self):
        self.assertEqual(
            params.clean_params({"dataset": "samples", "evil": 1}, SPEC),
            {"dataset": "samples"})

    def test_empty_values_are_left_out(self):
        self.assertEqual(params.clean_params(
            {"dataset": "samples", "filters": {}, "columns": []}, SPEC),
            {"dataset": "samples"})

    def test_wrong_kinds(self):
        for value in ({"dataset": ["x"]}, {"dataset": "a b"},
                      {"columns": "getId"}, {"filters": ["x"]},
                      {"limit": "10"}, {"limit": True},
                      {"dataset": "samples\n"}):
            self.assertRaises(QueryError, params.clean_params, value, SPEC)

    def test_not_a_mapping(self):
        self.assertRaises(QueryError, params.clean_params, [], SPEC)

    def test_trend(self):
        cleaned = params.clean_trend({"trend": {
            "interval": "week", "periods": 8, "other": 1}})
        self.assertEqual(cleaned["trend"], {"interval": "week",
                                            "periods": 8})


class IdsAndTitlesTestCase(unittest.TestCase):

    def test_tile_ids(self):
        self.assertEqual(clean_tile_id("a1b2c3d4"), "a1b2c3d4")
        for bad in (["a"], {"a": 1}, 7, "x" * 40, "<b>", "", "abc\n"):
            new = clean_tile_id(bad)
            self.assertNotEqual(new, bad)
            self.assertEqual(clean_tile_id(new), new)

    def test_dashboard_ids(self):
        self.assertTrue(is_dashboard_id("laboratory"))
        for bad in ("", "Lab", "-lab", "lab\n", "x" * 65, None):
            self.assertFalse(is_dashboard_id(bad))

    def test_titles_drop_empty_and_odd_languages(self):
        self.assertEqual(
            clean_title({"en": u"Lab", "de": u" ", "<x>": u"no",
                         "fr\n": u"no"}),
            {"en": u"Lab"})

    def test_too_many_languages(self):
        title = dict(("l%s" % chr(97 + i) + "x", u"t") for i in range(25))
        self.assertRaises(QueryError, clean_title, title)


class BodyTestCase(unittest.TestCase):

    def test_a_json_object(self):
        self.assertEqual(parse_body('{"tiles": []}'), {"tiles": []})

    def test_an_empty_body_is_an_empty_object(self):
        self.assertEqual(parse_body(""), {})
        self.assertEqual(parse_body(None), {})

    def test_anything_else_is_a_bad_request(self):
        for text in ("[1]", '"text"', "1", "{"):
            self.assertRaises(BadRequestError, parse_body, text)
