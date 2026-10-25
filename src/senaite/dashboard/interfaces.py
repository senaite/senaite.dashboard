# -*- coding: utf-8 -*-
"""Interfaces of senaite.dashboard."""

from senaite.core.interfaces import ISenaiteCore
from zope.interface import Attribute
from zope.interface import Interface


class ISenaiteDashboardLayer(ISenaiteCore):
    """Request layer, active when senaite.dashboard is installed.

    It extends the layer of senaite.core, so that the dashboard page
    registered for it takes the place of the one of senaite.core.
    """


class IDashboardDataset(Interface):
    """A set of objects a tile may count, group or list.

    A dataset is the whitelist the dashboard query language works in:
    the catalog it searches, the filters it accepts, the fields it can
    group by and the columns it can show. Register one as a named
    utility; the name is what a tile refers to.
    """

    title = Attribute("Title, a message id")
    catalog = Attribute("Id of the catalog to search")
    base_query = Attribute("Query every search starts from")

    def describe(env):
        """Return a JSON-able description for the tile editor.

        :param env: the `Environment` of the current request
        """


class IDashboardDatasetExtension(Interface):
    """Fields, columns and spans an add-on adds to a dataset.

    Register one as a named utility. An add-on that indexes more about
    samples, for example, makes it available to the tiles on samples
    without defining a dataset of its own.
    """

    dataset = Attribute("Name of the dataset it extends")
    fields = Attribute("Fields to add")
    columns = Attribute("Columns to add")
    spans = Attribute("Spans to add")


class IDashboardDataSource(Interface):
    """Computes the data of a tile.

    Register one as a named utility; the name is what a tile refers to
    as its `source`. A source never trusts its parameters: it validates
    them and searches with the permissions of the current user.
    """

    title = Attribute("Title, a message id")
    output = Attribute("Shape of the result: scalar, items, series, rows")

    def __call__(params, env):
        """Return the data for the given parameters.

        :param params: the `params` of the tile
        :param env: the `Environment` of the current request
        :raises QueryError: when the parameters are not valid
        """


class IDashboardPresetProvider(Interface):
    """Contributes ready-made tiles to the tile library.

    A provider may have `categories`, [(id, title)], for categories
    of its own; they show before "General".
    """

    def __call__(env):
        """Return [{id, category, description, tile}]."""
