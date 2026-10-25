# -*- coding: utf-8 -*-
"""Where a tile finds its dataset.

Datasets come from two places: the code registers them as named
utilities, managers define them in the browser (see custom.py). Both
are `Dataset` objects; nothing after this module tells them apart.
"""

from senaite.dashboard import messagefactory as _
from senaite.dashboard.exceptions import QueryError
from senaite.dashboard.interfaces import IDashboardDataset
from senaite.dashboard.query import custom
from zope.component import getUtilitiesFor
from zope.component import queryUtility


def find_dataset(name):
    """The dataset with the name, whoever may use it, or None."""
    if not name or not isinstance(name, basestring):
        return None
    if custom.is_custom(name):
        return custom.get_dataset(name)
    return queryUtility(IDashboardDataset, name=name)


def get_dataset(name, env):
    """Return the dataset with the name if the user may use it."""
    dataset = find_dataset(name)
    if dataset is None or not dataset.is_available(env):
        raise QueryError(_("Unknown dataset ${name}",
                           mapping={"name": name}))
    return dataset


def get_datasets(env):
    """Return the datasets the user may use, those of the code first."""
    datasets = [dataset for name, dataset
                in getUtilitiesFor(IDashboardDataset)]
    datasets.extend(custom.get_datasets())
    return [dataset for dataset in datasets if dataset.is_available(env)]
