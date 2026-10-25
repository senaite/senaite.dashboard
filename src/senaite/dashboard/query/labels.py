# -*- coding: utf-8 -*-
"""Turn raw index values into what the user reads.

A grouped tile gets index values: state ids, UIDs, user ids. Each kind
of field has a labeller that maps them to titles. A labeller returns
None for a value the user may not see; the caller leaves it out or
counts it under "Other", so a title never leaks through a label.
"""

from bika.lims import api
from bika.lims import senaiteMessageFactory as _c
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.i18n import translate
from senaite.dashboard import messagefactory as _
from senaite.dashboard.query import fields


def get_state_title(state, portal_type):
    """Return the translated title of a workflow state."""
    wf_tool = api.get_tool("portal_workflow")
    title = wf_tool.getTitleForStateOnType(state, portal_type) or state
    return translate(_c(title), to_utf8=False)


def label_states(values, field, dataset, env):
    return {value: get_state_title(value, dataset.portal_type)
            for value in values}


def label_references(values, field, dataset, env):
    """Titles of the referenced objects the user may view."""
    labels = {}
    for uid in values:
        obj = api.get_object_by_uid(uid, default=None)
        if obj is None or not api.security.check_permission("View", obj):
            labels[uid] = None
            continue
        labels[uid] = api.safe_unicode(api.get_title(obj))
    return labels


def label_users(values, field, dataset, env):
    """Full names of users; hidden from users outside the laboratory."""
    if not env.is_lab:
        return dict.fromkeys(values)
    return {value: api.safe_unicode(api.get_user_fullname(value) or value)
            for value in values}


def label_keywords(values, field, dataset, env):
    """Titles of the analysis services with the given keywords."""
    if not values:
        # An empty list does not narrow a search: it finds every service
        return {}
    brains = api.search({
        "portal_type": "AnalysisService",
        "getKeyword": list(values),
    }, SETUP_CATALOG)
    titles = {brain.getKeyword: api.safe_unicode(brain.Title)
              for brain in brains}
    return {value: titles.get(value, value) for value in values}


def label_booleans(values, field, dataset, env):
    yes = translate(_("Yes"), to_utf8=False)
    no = translate(_("No"), to_utf8=False)
    return {value: yes if value else no for value in values}


def label_texts(values, field, dataset, env):
    return {value: api.safe_unicode(value) for value in values}


def label_choices(values, field, dataset, env):
    return {value: field.get_choice_title(value) for value in values}


LABELLERS = {
    fields.STATE: label_states,
    fields.REFERENCE: label_references,
    fields.USER: label_users,
    fields.KEYWORD: label_keywords,
    fields.BOOLEAN: label_booleans,
    fields.TEXT: label_texts,
    fields.CHOICE: label_choices,
}


def get_labels(values, field, dataset, env):
    """Return {value: label or None} for the values of the field."""
    labeller = fields.get_by_kind(LABELLERS, field)
    values = [value for value in values if value not in (None, "")]
    return labeller(values, field, dataset, env)
