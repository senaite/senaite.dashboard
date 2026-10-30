# -*- coding: utf-8 -*-
"""Unit tests for placeholders, periods and filter values."""

import unittest

from DateTime import DateTime
from senaite.dashboard.exceptions import ValidationError
from senaite.dashboard.query import fields
from senaite.dashboard.query import timeline
from senaite.dashboard.query import variables
from senaite.dashboard.query.variables import UNSET

# A Thursday
NOW = DateTime("2026/10/22 14:30:00 GMT+2")


class FakeEnv(object):
    user_id = "tweber"
    client_uid = None
    now = NOW


class VariablesTestCase(unittest.TestCase):

    def resolve(self, value, **env):
        fake = FakeEnv()
        fake.__dict__.update(env)
        return variables.resolve(value, fake)

    def test_user(self):
        self.assertEqual(self.resolve("$user"), "tweber")

    def test_client_of_a_lab_user_is_unset(self):
        self.assertIs(self.resolve("$client"), UNSET)

    def test_client_of_a_client_contact(self):
        self.assertEqual(self.resolve("$client", client_uid="abc"), "abc")

    def test_today_minus_days(self):
        self.assertEqual(self.resolve("$today-30d").Date(), "2026/09/22")

    def test_start_of_week_is_monday(self):
        week = self.resolve("$week")
        self.assertEqual((week.Date(), week.dow()), ("2026/10/19", 1))

    def test_month_and_year(self):
        self.assertEqual(self.resolve("$month").Date(), "2026/10/01")
        self.assertEqual(self.resolve("$year").Date(), "2026/01/01")

    def test_nested(self):
        self.assertEqual(self.resolve({"a": ["$user", 1]}),
                         {"a": ["tweber", 1]})

    def test_unknown(self):
        self.assertRaises(ValidationError, self.resolve, "$password")

    def test_offset_on_text(self):
        self.assertRaises(ValidationError, self.resolve, "$user-1d")

    def test_months_are_calendar_months(self):
        self.assertEqual(self.resolve("$month-1m").Date(), "2026/09/01")
        self.assertEqual(self.resolve("$year+1y").Date(), "2027/01/01")

    def test_huge_offsets_are_invalid(self):
        self.assertRaises(ValidationError, self.resolve, "$today-99999d")

    def test_offsets_beyond_the_calendar_are_invalid(self):
        for token in ("$today+9999y", "$year-9999y", "$now+9999y"):
            self.assertRaises(ValidationError, self.resolve, token)

    def test_a_trailing_newline_is_invalid(self):
        self.assertRaises(ValidationError, self.resolve, "$user\n")

    def test_unicode_placeholder(self):
        self.assertRaises(ValidationError, self.resolve, u"$\xfcser")

    def test_plain_text_stays(self):
        self.assertEqual(self.resolve("published"), "published")


class TimelineTestCase(unittest.TestCase):

    def test_weeks_end_with_the_current_one(self):
        periods = timeline.get_periods("week", 3, NOW)
        self.assertEqual([start.Date() for start, end in periods],
                         ["2026/10/05", "2026/10/12", "2026/10/19"])
        self.assertEqual(periods[-1][1].Date(), "2026/10/26")

    def test_months_across_a_year(self):
        periods = timeline.get_periods("month", 12, NOW)
        self.assertEqual(periods[0][0].Date(), "2025/11/01")
        self.assertEqual(periods[-1][1].Date(), "2026/11/01")

    def test_days(self):
        periods = timeline.get_periods("day", 2, NOW)
        self.assertEqual([start.Date() for start, end in periods],
                         ["2026/10/21", "2026/10/22"])

    def test_limits(self):
        self.assertRaises(ValidationError, timeline.get_periods, "week", 0,
                          NOW)
        self.assertRaises(ValidationError, timeline.get_periods, "week",
                          timeline.MAX_PERIODS["week"] + 1, NOW)
        self.assertRaises(ValidationError, timeline.get_periods, "hour", 3,
                          NOW)

    def test_periods_start_at_local_midnight_across_dst(self):
        # Europe/Berlin leaves summer time on 2026-10-25
        periods = timeline.get_periods("week", 3, NOW)
        hours = [start.hour() for start, end in periods]
        self.assertEqual(hours, [0, 0, 0])

    def test_ranges_do_not_overlap(self):
        (start, end), = timeline.get_periods("day", 1, NOW)
        low, high = timeline.to_range(start, end)["query"]
        self.assertTrue(high < end)


class FieldQueryTestCase(unittest.TestCase):

    def field(self, kind):
        return fields.Field("index", u"Title", kind)

    def test_values(self):
        self.assertEqual(fields.to_query(self.field(fields.STATE),
                                         ["a", "b"]),
                         {"query": ["a", "b"]})

    def test_single_value(self):
        self.assertEqual(fields.to_query(self.field(fields.USER), "me"),
                         {"query": ["me"]})

    def test_not(self):
        self.assertEqual(fields.to_query(self.field(fields.STATE),
                                         {"not": ["a"]}),
                         {"not": ["a"]})

    def test_unset_values_drop_out(self):
        self.assertIs(fields.to_query(self.field(fields.REFERENCE),
                                      [UNSET]), UNSET)

    def test_values_must_be_text(self):
        self.assertRaises(ValidationError, fields.to_query,
                          self.field(fields.STATE), [{"$ne": 1}])

    def test_too_many_values(self):
        values = ["v%d" % i for i in range(fields.MAX_FILTER_VALUES + 1)]
        self.assertRaises(ValidationError, fields.to_query,
                          self.field(fields.STATE), values)

    def test_date_range(self):
        query = fields.to_query(self.field(fields.DATE),
                                {"min": NOW - 1, "max": NOW})
        self.assertEqual(query["range"], "min:max")

    def test_date_needs_a_mapping(self):
        self.assertRaises(ValidationError, fields.to_query,
                          self.field(fields.DATE), "yesterday")

    def test_boolean(self):
        field = self.field(fields.BOOLEAN)
        self.assertIs(fields.to_query(field, True), True)
        self.assertIs(fields.to_query(field, False), False)
        for value in ("false", 1, {"not": [True]}):
            self.assertRaises(ValidationError, fields.to_query, field, value)
