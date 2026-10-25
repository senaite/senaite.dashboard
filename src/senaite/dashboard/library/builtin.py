# -*- coding: utf-8 -*-
"""The presets senaite.dashboard ships with, by category.

Nobody should have to write a query to get a useful tile: these cover
what a laboratory looks at every day. The default dashboards of a new
site are made of them (see dashboards/defaults.py).
"""

from bika.lims import senaiteMessageFactory as _c
from senaite.dashboard import messagefactory as _
from senaite.dashboard.dashboards.model import new_id
from senaite.dashboard.interfaces import IDashboardPresetProvider
from senaite.dashboard.library.builders import LAST_30_DAYS
from senaite.dashboard.library.builders import WEEKLY_TREND
from senaite.dashboard.library.builders import analyses
from senaite.dashboard.library.builders import chart
from senaite.dashboard.library.builders import group
from senaite.dashboard.library.builders import kpi
from senaite.dashboard.library.builders import make_preset_tile
from senaite.dashboard.library.builders import samples
from senaite.dashboard.library.builders import span
from senaite.dashboard.library.builders import table
from senaite.dashboard.library.builders import tile_params
from senaite.dashboard.library.builders import to_presets
from senaite.dashboard.library.builders import translate_tile
from senaite.dashboard.library.builders import worksheets
from zope.interface import implementer

# Categories of the library, in the order it shows them; those of
# add-ons go before "General"
CATEGORIES = [
    ("samples", _("Samples")),
    ("analyses", _("Analyses")),
    ("worksheets", _c("Worksheets")),
]
GENERAL = "general"
GENERAL_CATEGORY = (GENERAL, _("General"))


OPEN_SAMPLE_STATES = [
    "to_be_sampled", "scheduled_sampling", "to_be_preserved",
    "sample_due", "sample_received", "to_be_verified", "verified",
]
OPEN_ANALYSIS_STATES = ["unassigned", "assigned", "to_be_verified"]


def samples_link(review_state):
    return "samples?samples_review_state={}".format(review_state)


# Each preset: (id, what it shows, the tile)
SAMPLE_PRESETS = [
    ("samples-to-receive",
     _("Samples waiting for reception"),
     kpi(_("Samples to receive"),
         samples({"review_state": ["sample_due"]}, trend=WEEKLY_TREND),
         link=samples_link("sample_due"), color="yellow", icon="inbox")),
    ("samples-results-pending",
     _("Received samples without all results"),
     kpi(_("Results pending"),
         samples({"review_state": ["sample_received"]},
                 trend=WEEKLY_TREND),
         link=samples_link("sample_received"), color="blue",
         icon="flask")),
    ("samples-to-verify",
     _("Samples with all results, waiting for verification"),
     kpi(_("To be verified"),
         samples({"review_state": ["to_be_verified"]}, trend=WEEKLY_TREND),
         link=samples_link("to_be_verified"), color="orange",
         icon="check")),
    ("samples-to-publish",
     _("Verified samples, waiting for publication"),
     kpi(_("To be published"),
         samples({"review_state": ["verified"]}, trend=WEEKLY_TREND),
         link=samples_link("verified"), color="aqua", icon="send")),
    ("samples-overdue",
     _("Open samples past their due date"),
     kpi(_("Overdue samples"),
         samples({"review_state": ["sample_due", "sample_received"],
                  "getDueDate": {"max": "$now"}}),
         link="samples", color="red", icon="alert")),
    ("samples-this-week",
     _("Samples registered since Monday"),
     kpi(_("Registered this week"),
         samples({"created": {"min": "$week"}}, trend=WEEKLY_TREND),
         link="samples", color="violet", icon="plus")),
    ("samples-published-30d",
     _("Samples published in the last 30 days"),
     kpi(_("Published (30 days)"),
         samples({"getDatePublished": {"min": "$today-30d"}},
                 trend=dict(WEEKLY_TREND, date_field="getDatePublished")),
         link=samples_link("published"), color="green", icon="file")),
    ("samples-turnaround",
     _("Average time from reception to verification, last 90 days"),
     span(_("Turnaround time"),
          samples({"getDateVerified": {"min": "$today-90d"}},
                  span="turnaround"))),
    ("samples-open-by-status",
     _("Open samples per status"),
     group("donut", _("Open samples by status"),
           samples({"review_state": OPEN_SAMPLE_STATES},
                   group_by="review_state"))),
    ("samples-by-type",
     _("Samples of the last 30 days per sample type"),
     group("bar", _("Samples by sample type"),
           samples(LAST_30_DAYS, group_by="getSampleTypeUID", limit=8))),
    ("samples-by-client",
     _("Samples of the last 30 days per client"),
     group("bar", _("Samples by client"),
           samples(LAST_30_DAYS, group_by="getClientUID", limit=8))),
    ("samples-by-point",
     _("Samples of the last 30 days per sample point"),
     group("bar", _("Samples by sample point"),
           samples(LAST_30_DAYS, group_by="getSamplePointUID", limit=8))),
    ("samples-registered-weekly",
     _("Registered samples per week, by their current status"),
     chart(_("Registered samples"),
           samples({}, date_field="created", interval="week",
                   periods=12, stack_by="review_state"))),
    ("samples-received-daily",
     _("Samples received per day, last 30 days"),
     chart(_("Received samples"),
           samples({}, date_field="getDateReceived", interval="day",
                   periods=30),
           style="area")),
    ("samples-latest",
     _("The most recently registered samples"),
     table(_("Latest samples"),
           samples({}, sort_on="created", limit=8,
                   columns=["getId", "getClientTitle",
                            "getSampleTypeTitle", "review_state"]))),
    ("samples-due-soon",
     _("Received samples, the earliest due date first"),
     table(_("Due next"),
           samples({"review_state": ["sample_received"]},
                   sort_on="getDueDate", sort_order="ascending", limit=8,
                   columns=["getId", "getClientTitle",
                            "getSampleTypeTitle", "getDueDate"]))),
    ("samples-recently-published",
     _("Samples published most recently"),
     table(_("Recently published"),
           samples({"review_state": ["published"]},
                   sort_on="getDatePublished", limit=8,
                   columns=["getId", "getClientSampleID",
                            "getSampleTypeTitle", "getDatePublished"]))),
]


ANALYSIS_PRESETS = [
    ("analyses-mine",
     _("Analyses assigned to me, waiting for a result"),
     kpi(_("My assigned analyses"),
         analyses({"getAnalyst": "$user", "review_state": ["assigned"]}),
         link="worksheets", color="blue", icon="user")),
    ("analyses-unassigned",
     _("Analyses not yet on a worksheet"),
     kpi(_("Unassigned analyses"),
         analyses({"review_state": ["unassigned"]}, trend=WEEKLY_TREND),
         link=samples_link("unassigned"), color="yellow", icon="list")),
    ("analyses-to-verify",
     _("Results waiting for verification"),
     kpi(_("Results to verify"),
         analyses({"review_state": ["to_be_verified"]},
                  trend=WEEKLY_TREND),
         link=samples_link("to_be_verified"), color="orange",
         icon="check")),
    ("analyses-by-analyst",
     _("Open analyses per analyst"),
     group("bar", _("Open analyses by analyst"),
           analyses({"review_state": OPEN_ANALYSIS_STATES},
                    group_by="getAnalyst", limit=8))),
    ("analyses-to-verify-by-service",
     _("Results waiting for verification per analysis"),
     group("bar", _("To verify by analysis"),
           analyses({"review_state": ["to_be_verified"]},
                    group_by="getKeyword", limit=8))),
    ("analyses-by-instrument",
     _("Open analyses per instrument"),
     group("bar", _("Open analyses by instrument"),
           analyses({"review_state": OPEN_ANALYSIS_STATES},
                    group_by="getInstrumentUID", limit=8))),
    ("analyses-by-status",
     _("Analyses of the last 30 days per status"),
     group("donut", _("Analyses by status"),
           analyses(LAST_30_DAYS, group_by="review_state"))),
    ("analyses-captured-daily",
     _("Results captured per day, last 30 days"),
     chart(_("Results captured"),
           analyses({}, date_field="getResultCaptureDate",
                    interval="day", periods=30),
           style="area")),
    ("analyses-due-mine",
     _("My open analyses, the earliest due date first"),
     table(_("My analyses due next"),
           analyses({"getAnalyst": "$user", "review_state": ["assigned"]},
                    sort_on="getDueDate", sort_order="ascending", limit=8,
                    columns=["Title", "getRequestID", "getDueDate",
                             "review_state"]))),
]


WORKSHEET_PRESETS = [
    ("worksheets-open",
     _("Worksheets waiting for results"),
     kpi(_("Open worksheets"),
         worksheets({"review_state": ["open"]}, trend=WEEKLY_TREND),
         link="worksheets?worksheets_review_state=open", color="blue",
         icon="grid")),
    ("worksheets-mine",
     _("Open worksheets assigned to me"),
     kpi(_("My worksheets"),
         worksheets({"getAnalyst": "$user", "review_state": ["open"]}),
         link="worksheets?worksheets_review_state=mine", color="blue",
         icon="grid")),
    ("worksheets-by-analyst",
     _("Open worksheets per analyst"),
     group("bar", _("Worksheets by analyst"),
           worksheets({"review_state": ["open", "to_be_verified"]},
                      group_by="getAnalyst"))),
]


GENERAL_PRESETS = [
    ("custom", _("Choose yourself what the tile shows and how"),
     make_preset_tile("kpi", "count", _("New tile"),
                      tile_params("samples", {}), {}, (3, 2))),
    ("links", _("Shortcuts to the pages you use most"), {
        "type": "links",
        "title": _("Quick links"),
        "options": {"links": []},
        "layout": {"w": 4, "h": 3},
    }),
    ("note", _("A text of your own, e.g. a notice for the team"), {
        "type": "note",
        "title": _("Note"),
        "options": {"text": ""},
        "layout": {"w": 4, "h": 3},
    }),
]


# The presets of each category
PRESET_GROUPS = [
    ("samples", SAMPLE_PRESETS),
    ("analyses", ANALYSIS_PRESETS),
    ("worksheets", WORKSHEET_PRESETS),
    (GENERAL, GENERAL_PRESETS),
]


@implementer(IDashboardPresetProvider)
class CorePresets(object):
    """The presets senaite.dashboard ships with."""

    def __call__(self, env):
        presets = []
        for category, entries in PRESET_GROUPS:
            presets.extend(to_presets(
                category, entries, configure=category == GENERAL))
        return presets


def find_preset(preset_id):
    """The tile of a preset senaite.dashboard ships with."""
    for category, entries in PRESET_GROUPS:
        for entry_id, description, tile in entries:
            if entry_id == preset_id:
                return tile
    raise KeyError(preset_id)


def make_tile(preset_id, x, y, w=None, h=None, languages=None):
    """Return a new tile from a preset, placed on the grid."""
    tile = translate_tile(find_preset(preset_id), languages)
    tile["id"] = new_id()
    tile["layout"] = {
        "x": x,
        "y": y,
        "w": w or tile["layout"]["w"],
        "h": h or tile["layout"]["h"],
    }
    return tile
