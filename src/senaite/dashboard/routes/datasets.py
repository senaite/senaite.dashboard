# -*- coding: utf-8 -*-
"""JSON API routes for datasets defined in the browser.

Below @@API/senaite/v1/dashboard/datasets; managers only. The checks
of `route` apply as for every dashboard route.
"""

from senaite.dashboard.dashboards import usage
from senaite.dashboard.query import custom
from senaite.dashboard.query import inspection
from senaite.dashboard.routes.base import get_body
from senaite.dashboard.routes.base import route


def definitions_answer(env):
    return {"datasets": custom.list_definitions(env)}


@route("/datasets", ["GET"])
def list_datasets(env, request):
    return definitions_answer(env)


@route("/datasets/inspect/<string:portal_type>", ["GET"])
def inspect_type(env, request, portal_type):
    """What a dataset of the type may offer, with examples."""
    return inspection.inspect(portal_type, env)


@route("/datasets/usage/<string:name>", ["GET"])
def dataset_usage(env, request, name):
    return usage.count_usage(name, env)


@route("/datasets/save", ["POST"])
def save_dataset(env, request):
    """Create a dataset, or change the one the body names.

    Body: {"name"?, "title", "portal_type", "lab_only", "fields",
    "columns", "spans"}
    """
    record = custom.save(get_body(), env)
    answer = definitions_answer(env)
    answer["saved"] = record["name"]
    return answer


@route("/datasets/remove/<string:name>", ["POST"])
def remove_dataset(env, request, name):
    custom.remove(name, env)
    return definitions_answer(env)
