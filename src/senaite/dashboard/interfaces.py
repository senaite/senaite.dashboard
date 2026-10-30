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
    utility; the name is what a tile refers to. Names starting with
    `custom-` belong to datasets managers define in the browser.

    Register an instance of `senaite.dashboard.api.Dataset` rather than
    implementing this interface yourself: the sources use all of it.
    """

    name = Attribute("Name a tile refers to the dataset by")
    title = Attribute("Title, a message id")
    catalog = Attribute("Id of the catalog to search")
    portal_type = Attribute("Portal type of the objects")
    base_query = Attribute("Query every search starts from")

    def is_available(env):
        """Whether the user may use the dataset."""

    def get_fields(env):
        """The fields the user may filter and group by."""

    def get_field(name, env):
        """The field of the name.

        :raises ValidationError: when the user may not use it
        """

    def get_columns(env):
        """The columns the user may show in a table."""

    def get_column(name, env):
        """The column of the name.

        :raises ValidationError: when the user may not show it
        """

    def get_span(name):
        """The span of the name.

        :raises ValidationError: when there is none
        """

    def get_states():
        """The workflow states of the objects, in the order to show."""

    def get_url(brain):
        """Where a row of a table leads."""

    def describe(env):
        """Return a JSON-able description for the tile editor.

        :param env: the `Environment` of the current request
        """


class IDashboardDatasetExtension(Interface):
    """Fields, columns and spans an add-on adds to a dataset.

    Register an instance of `senaite.dashboard.api.DatasetExtension` as
    a named utility. An add-on that indexes more about samples, for
    example, makes it available to the tiles on samples without
    defining a dataset of its own. A field or column of the same name
    as one of the dataset replaces it.
    """

    dataset = Attribute("Name of the dataset it extends")
    fields = Attribute("Fields to add")
    columns = Attribute("Columns to add")
    spans = Attribute("Spans to add")


class IDashboardDataSource(Interface):
    """Computes the data of a tile.

    Register one as a named utility; the name is what a tile refers to
    as its `source`. Subclass `senaite.dashboard.api.DataSource`, which
    has defaults for everything but `__call__`. A source never trusts
    its parameters: it validates them and searches with the permissions
    of the current user.
    """

    title = Attribute("Title, a message id")
    output = Attribute("Shape of the result: scalar, items, series, rows")
    params = Attribute("The parameters it takes: {name: kind}")

    def clean(params):
        """Return the parameters checked further than by their kinds.

        :raises ValidationError: when they are not valid
        """

    def cost(params):
        """Return how many catalog searches the tile causes, roughly."""

    def __call__(params, env):
        """Return the data for the given parameters.

        :param params: the `params` of the tile, checked
        :param env: the `Environment` of the current request
        :raises ValidationError: when the parameters are not valid
        """


class IDashboardPresetProvider(Interface):
    """Contributes ready-made tiles to the tile library.

    A provider may have `categories`, [(id, title)], for categories
    of its own; they show before "General".
    """

    def __call__(env):
        """Return the presets: [{"id", "category", "description",
        "tile"}], optionally with "configure": true to open the settings
        of the tile once it is added. `to_presets` of
        `senaite.dashboard.api` builds them.
        """
