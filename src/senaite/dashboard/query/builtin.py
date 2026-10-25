# -*- coding: utf-8 -*-
"""The datasets senaite.dashboard ships with: samples, analyses and
worksheets.

Each names its catalog, the fields a tile may filter and group by, the
columns a table may show and the spans of time a tile may measure.
Add-ons extend them with a DatasetExtension, or bring datasets of their
own the same way (see configure.zcml).
"""

from bika.lims import api
from bika.lims import senaiteMessageFactory as _c
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.catalog import WORKSHEET_CATALOG
from senaite.core.permissions import ViewResults
from senaite.dashboard import messagefactory as _
from senaite.dashboard.query.datasets import COL_DATE
from senaite.dashboard.query.datasets import COL_DUE
from senaite.dashboard.query.datasets import COL_NUMBER
from senaite.dashboard.query.datasets import COL_PERCENT
from senaite.dashboard.query.datasets import COL_STATE
from senaite.dashboard.query.datasets import Column
from senaite.dashboard.query.datasets import Dataset
from senaite.dashboard.query.datasets import Span
from senaite.dashboard.query.fields import BOOLEAN
from senaite.dashboard.query.fields import DATE
from senaite.dashboard.query.fields import KEYWORD
from senaite.dashboard.query.fields import REFERENCE
from senaite.dashboard.query.fields import STATE
from senaite.dashboard.query.fields import TEXT
from senaite.dashboard.query.fields import USER
from senaite.dashboard.query.fields import Field


def can_view_result(brain, env):
    """Whether the user may read the result of an analysis.

    Seeing an analysis is not seeing its result: the workflow shows a
    client contact the result only once it is verified.
    """
    return env.can(ViewResults, api.get_object(brain))


SAMPLES = Dataset(
    name="samples",
    title=_("Samples"),
    catalog=SAMPLE_CATALOG,
    portal_type="AnalysisRequest",
    icon="sample",
    listing="samples",
    # Partitions are counted through their root sample
    base_query={"isRootAncestor": True},
    states=[
        "to_be_sampled", "scheduled_sampling", "to_be_preserved",
        "sample_due", "sample_received", "to_be_verified", "verified",
        "published", "rejected", "invalid", "cancelled",
    ],
    fields=[
        Field("review_state", _c("Status"), STATE),
        Field("getClientUID", _c("Client"), REFERENCE, "Client"),
        Field("getSampleTypeUID", _c("Sample Type"), REFERENCE,
              "SampleType"),
        Field("getSamplePointUID", _c("Sample Point"), REFERENCE,
              "SamplePoint"),
        Field("getBatchUID", _c("Batch"), REFERENCE, "Batch"),
        Field("Creator", _("Registered by"), USER, lab_only=True),
        Field("getReceivedBy", _("Received by"), USER, lab_only=True),
        Field("is_received", _("Received"), BOOLEAN, groupable=False),
        Field("created", _("Registered"), DATE),
        Field("getDateSampled", _c("Date Sampled"), DATE),
        Field("getDateReceived", _c("Date Received"), DATE),
        Field("getDueDate", _c("Due Date"), DATE),
        Field("getDateVerified", _c("Date Verified"), DATE),
        Field("getDatePublished", _c("Date Published"), DATE),
    ],
    columns=[
        Column("getId", _c("Sample ID")),
        Column("getClientTitle", _c("Client")),
        Column("getClientSampleID", _c("Client SID")),
        Column("getSampleTypeTitle", _c("Sample Type")),
        Column("getSamplePointTitle", _c("Sample Point")),
        Column("review_state", _c("Status"), COL_STATE),
        Column("getProgress", _c("Progress"), COL_PERCENT),
        Column("getAnalysesNum", _("Analyses"), COL_NUMBER),
        Column("created", _("Registered"), COL_DATE),
        Column("getDateSampled", _c("Date Sampled"), COL_DATE),
        Column("getDateReceived", _c("Date Received"), COL_DATE),
        Column("getDueDate", _c("Due Date"), COL_DUE),
        Column("getDateVerified", _c("Date Verified"), COL_DATE),
        Column("getDatePublished", _c("Date Published"), COL_DATE),
    ],
    spans=[
        Span("turnaround", _("Turnaround (received to verified)"),
             "getDateReceived", "getDateVerified"),
        Span("to_publication", _("Received to published"),
             "getDateReceived", "getDatePublished"),
        Span("to_reception", _("Sampled to received"),
             "getDateSampled", "getDateReceived"),
    ],
)

ANALYSES = Dataset(
    name="analyses",
    title=_("Analyses"),
    catalog=ANALYSIS_CATALOG,
    portal_type="Analysis",
    icon="analysis",
    listing="samples",
    url_column="getRequestURL",
    base_query={"is_active": True},
    states=[
        "registered", "unassigned", "assigned", "to_be_verified",
        "verified", "published", "retracted", "rejected", "cancelled",
    ],
    fields=[
        Field("review_state", _c("Status"), STATE),
        Field("getKeyword", _c("Analysis"), KEYWORD),
        Field("getCategoryUID", _c("Category"), REFERENCE,
              "AnalysisCategory"),
        Field("getClientUID", _c("Client"), REFERENCE, "Client"),
        Field("getSampleTypeUID", _c("Sample Type"), REFERENCE,
              "SampleType"),
        Field("getInstrumentUID", _c("Instrument"), REFERENCE,
              "Instrument", lab_only=True),
        Field("getAnalyst", _c("Analyst"), USER, lab_only=True),
        Field("getPointOfCapture", _("Point of capture"), TEXT,
              lab_only=True),
        Field("created", _("Registered"), DATE),
        Field("getDateReceived", _c("Date Received"), DATE),
        Field("getDueDate", _c("Due Date"), DATE),
        Field("getResultCaptureDate", _("Result captured"), DATE),
    ],
    columns=[
        Column("Title", _c("Analysis")),
        Column("getRequestID", _c("Sample ID")),
        Column("getClientTitle", _c("Client")),
        Column("getResult", _c("Result"), guard=can_view_result),
        Column("getUnit", _c("Unit")),
        Column("review_state", _c("Status"), COL_STATE),
        Column("getMethodTitle", _c("Method")),
        Column("getDateReceived", _c("Date Received"), COL_DATE),
        Column("getDueDate", _c("Due Date"), COL_DUE),
        Column("getResultCaptureDate", _("Result captured"), COL_DATE),
    ],
    spans=[
        Span("to_result", _("Received to result"),
             "getDateReceived", "getResultCaptureDate"),
    ],
)

WORKSHEETS = Dataset(
    name="worksheets",
    title=_c("Worksheets"),
    catalog=WORKSHEET_CATALOG,
    portal_type="Worksheet",
    icon="worksheet",
    listing="worksheets",
    lab_only=True,
    states=["open", "attachment_due", "to_be_verified", "verified"],
    fields=[
        Field("review_state", _c("Status"), STATE),
        Field("getAnalyst", _c("Analyst"), USER),
        Field("getWorksheetTemplateTitle", _c("Template"), TEXT),
        Field("created", _("Created"), DATE),
    ],
    columns=[
        Column("getId", _("Worksheet")),
        Column("getWorksheetTemplateTitle", _c("Template")),
        Column("review_state", _c("Status"), COL_STATE),
        Column("getNumberOfRegularSamples", _c("Samples"), COL_NUMBER),
        Column("getNumberOfRegularAnalyses", _c("Analyses"), COL_NUMBER),
        Column("getProgressPercentage", _c("Progress"), COL_PERCENT),
        Column("created", _("Created"), COL_DATE),
    ],
)
