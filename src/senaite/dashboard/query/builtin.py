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
from senaite.dashboard.query.datasets import Card
from senaite.dashboard.query.datasets import Column
from senaite.dashboard.query.datasets import Dataset
from senaite.dashboard.query.datasets import Link
from senaite.dashboard.query.datasets import Span
from senaite.dashboard.query.fields import BOOLEAN
from senaite.dashboard.query.fields import DATE
from senaite.dashboard.query.fields import KEYWORD
from senaite.dashboard.query.fields import REFERENCE
from senaite.dashboard.query.fields import STATE
from senaite.dashboard.query.fields import TEXT
from senaite.dashboard.query.fields import USER
from senaite.dashboard.query.fields import Field
from senaite.dashboard.query.search import get_index_value


def can_view_result(brain, env):
    """Whether the user may read the result of an analysis.

    Seeing an analysis is not seeing its result: the workflow shows a
    client contact the result only once it is verified.
    """
    return env.can(ViewResults, api.get_object(brain))


# HTML of a result as SENAITE formats it, and the text that stands for
# it in a line of text
RESULT_MARKUP = (
    ("<br/>", u", "),
    ("\n", u" "),
)

# Scientific notations with a superscript, and the same in plain text
PLAIN_NOTATIONS = {3: 2, 5: 4}


def get_result_format():
    """The decimal mark and the scientific notation of the laboratory,
    in a notation that needs no markup."""
    setup = api.get_bika_setup()
    notation = api.to_int(setup.getScientificNotationResults(), 1)
    return {
        "decimalmark": setup.getResultsDecimalMark(),
        "sciformat": PLAIN_NOTATIONS.get(notation, notation),
    }


def to_line(text):
    """The formatted result on one line of text."""
    for markup, plain in RESULT_MARKUP:
        text = text.replace(markup, plain)
    return text.strip()


def get_formatted_result(analysis):
    """The result as the sample shows it, for every type of result: the
    text of the options chosen, a date in the format of the language, a
    number with its precision, a detection limit or "Not detected"."""
    text = analysis.getFormattedResult(html=False, **get_result_format())
    return to_line(api.safe_unicode(text or u""))


def result_text(brain):
    """The result of an analysis as the sample shows it, or None."""
    if brain.getResult in (None, ""):
        return None
    return get_formatted_result(api.get_object(brain)) or None


def has_digit(text):
    return any(char.isdigit() for char in text)


def result_with_unit(brain):
    """The result of an analysis with its unit, or None without one.

    Only a number has a unit: the text of an option, a date or a text
    stands for itself, and so does "Not detected".
    """
    text = result_text(brain)
    if text is None:
        return None
    analysis = api.get_object(brain)
    unit = brain.getUnit
    if analysis.getResultType() != "numeric" or not unit \
            or not has_digit(text):
        return text
    return u"{} {}".format(text, api.safe_unicode(unit))


def own_uid(brain, dataset):
    return brain.UID


def root_sample_uid(brain, dataset):
    """The UID of the sample an analysis belongs to, through partitions.

    The index holds the sample of the analysis and its ancestors, the
    root last; the samples dataset holds root samples only.
    """
    uids = get_index_value(dataset.catalog, "getAncestorsUIDs",
                           brain.getRID())
    return uids[-1] if uids else None


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
    card=Card("getId", subtitle=["getClientTitle", "getSampleTypeTitle"],
              detail=["getDueDate"], note="getProgress"),
    facts=["getClientTitle", "getSampleTypeTitle", "review_state",
           "getDateReceived", "getDueDate", "getProgress"],
    facets=["getClientUID", "getSampleTypeUID"],
    sort=("getDueDate", "ascending"),
    children=Link("analyses", "getAncestorsUIDs", own_uid,
                  title=_("Analyses")),
    # The listing of SENAITE, with its actions, of the samples alone
    drill_view="samples/dashboard-samples",
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
        Column("getResult", _c("Result"), guard=can_view_result,
               getter=result_text),
        Column("result_with_unit", _("Result with unit"),
               guard=can_view_result, getter=result_with_unit),
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
    card=Card("Title", subtitle=["getRequestID", "getClientTitle"],
              detail=["result_with_unit", "getDueDate"], note="review_state"),
    facets=["getKeyword", "getClientUID", "getAnalyst"],
    sort=("getDueDate", "ascending"),
    parent=Link("samples", "UID", root_sample_uid),
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
    card=Card("getId", subtitle=["getWorksheetTemplateTitle"],
              detail=["created"], note="getProgressPercentage"),
    children=Link("analyses", "getWorksheetUID", own_uid,
                  title=_c("Analyses")),
)
