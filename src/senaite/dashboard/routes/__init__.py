# -*- coding: utf-8 -*-
"""JSON API routes.

Importing this package registers the route modules with the
senaite.jsonapi router (via the add_route decorator).
"""

from senaite.dashboard.routes import dashboard  # noqa: F401
from senaite.dashboard.routes import data  # noqa: F401
from senaite.dashboard.routes import datasets  # noqa: F401
from senaite.dashboard.routes import library  # noqa: F401
