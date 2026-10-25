# -*- coding: utf-8 -*-
"""Install the dashboards a fresh site starts with."""

from senaite.dashboard import logger
from senaite.dashboard.dashboards.defaults import install_defaults
from senaite.dashboard.env import Environment
from senaite.dashboard.storage import get_root


def post_install(context):
    """Create the storage and the default global dashboards."""
    get_root(create=True)
    install_defaults(Environment())
    logger.info("senaite.dashboard installed")
