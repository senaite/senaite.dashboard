# -*- coding: utf-8 -*-
"""SENAITE.DASHBOARD: configurable dashboards for SENAITE.

Three parts, each listing its modules in reading order:

`dashboards`
    What users see and change: global and personal dashboards, and
    who may change what.
`query`
    How a tile gets its numbers: data sources searching datasets in
    the catalog, as the current user.
`library`
    The tile library: ready-made tiles and the ones managers saved.

`routes` and `browser` are the web layer on top; `app` is what the
pages start from. See the README for the whole picture.
"""

import logging

from zope.i18nmessageid import MessageFactory

PRODUCT_NAME = "senaite.dashboard"

logger = logging.getLogger(PRODUCT_NAME)
messagefactory = MessageFactory(PRODUCT_NAME)
