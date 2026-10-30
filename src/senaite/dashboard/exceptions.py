# -*- coding: utf-8 -*-
"""Exceptions of senaite.dashboard."""


class DashboardError(Exception):
    """Base of all dashboard errors."""


class ValidationError(DashboardError):
    """What a request sent is not valid: a tile asks for something its
    dataset or source does not offer, a title is missing, a limit is
    reached.

    The message is shown to the user, so it is written for them.
    """


class NotFound(DashboardError):
    """There is no dashboard with the requested id."""


class Forbidden(DashboardError):
    """The current user may not do this."""


def check_limit(count, maximum, message):
    """Refuse one more of what there are `count` of already.

    :raises ValidationError: with the message when the maximum is reached
    """
    if count >= maximum:
        raise ValidationError(message)
