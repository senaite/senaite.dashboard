# -*- coding: utf-8 -*-
"""Exceptions of senaite.dashboard."""


class DashboardError(Exception):
    """Base of all dashboard errors."""


class QueryError(DashboardError):
    """A tile asks for something its dataset or source does not offer.

    The message is shown in the tile, so it is written for the user.
    """


class NotFound(DashboardError):
    """There is no dashboard with the requested id."""


class Forbidden(DashboardError):
    """The current user may not do this."""
