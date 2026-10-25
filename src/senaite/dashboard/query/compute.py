# -*- coding: utf-8 -*-
"""Data sources: what computes the data of a tile.

`compute` is the one entry point. It looks the source up, checks the
parameters against what the source declares, runs it with the
permissions of the current user and caches the answer per user.
"""

import json
from time import time

from bika.lims import api
from plone.memoize import ram
from senaite.core.i18n import translate
from senaite.dashboard import messagefactory as _
from senaite.dashboard.exceptions import QueryError
from senaite.dashboard.interfaces import IDashboardDataSource
from senaite.dashboard.query.params import clean_params
from senaite.dashboard.query.registry import find_dataset
from zope.component import getUtilitiesFor
from zope.component import queryUtility

# Answers are cached at most this long, in seconds. Within that time a
# change to the catalog of the dataset still invalidates them at once.
CACHE_TTL = 300


def find_source(name):
    """The source of the name, or None; a tile may send anything."""
    if not isinstance(name, basestring):
        return None
    return queryUtility(IDashboardDataSource, name=name)


def get_source(name):
    source = find_source(name)
    if source is None:
        raise QueryError(_("Unknown data source ${name}",
                           mapping={"name": name}))
    return source


def describe_sources():
    return [{
        "name": name,
        "title": translate(source.title, to_utf8=False),
        "output": source.output,
        "params": sorted(source.params),
    } for name, source in getUtilitiesFor(IDashboardDataSource)]


def get_data_version(dataset_name):
    """What changes when the answers on a dataset may change.

    The change counter of its catalog, and the version of a dataset
    defined in the browser, which a manager may change at any time.
    """
    dataset = find_dataset(dataset_name)
    if dataset is None:
        return None
    counter = api.get_tool(dataset.catalog).getCounter()
    return counter, getattr(dataset, "version", None)


def get_security_key(env):
    """What decides which objects the user's searches return."""
    catalog = api.get_tool("portal_catalog")
    return tuple(catalog._listAllowedRolesAndUsers(env.user))


def _compute_cachekey(func, name, params_json, dataset_name, env):
    return (
        name,
        params_json,
        get_security_key(env),
        # Lab-only fields and the names of users depend on the roles
        # on the site, local ones included, which the key above misses
        env.is_lab,
        env.client_uid,
        get_data_version(dataset_name),
        env.language,
        time() // CACHE_TTL,
    )


@ram.cache(_compute_cachekey)
def _compute(name, params_json, dataset_name, env):
    return get_source(name)(json.loads(params_json), env)


def clean_source_params(source, params):
    """The parameters the source declares, checked."""
    params = clean_params(params, source.params)
    clean = getattr(source, "clean", None)
    return clean(params) if clean else params


def compute(name, params, env):
    """Return the data of a source for the parameters of a tile.

    :raises QueryError: for an unknown source or invalid parameters
    """
    params = clean_source_params(get_source(name), params)
    params_json = json.dumps(params, sort_keys=True)
    return _compute(name, params_json, params.get("dataset"), env)


def get_cost(name, params):
    """How many catalog searches a tile asks for, roughly."""
    cost = getattr(find_source(name), "cost", None)
    if cost is None or not isinstance(params, dict):
        return 1
    return cost(params)
