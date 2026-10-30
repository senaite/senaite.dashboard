# -*- coding: utf-8 -*-
"""What add-ons build on: the stable names of senaite.dashboard.

Import from here rather than from the modules the names live in; those
may change, this module keeps its names. See the README for how an
add-on registers datasets, extensions, data sources and presets.
"""

from senaite.dashboard.env import Environment  # noqa: F401
from senaite.dashboard.exceptions import ValidationError  # noqa: F401
from senaite.dashboard.library.builders import LAST_30_DAYS  # noqa: F401
from senaite.dashboard.library.builders import WEEKLY_TREND  # noqa: F401
from senaite.dashboard.library.builders import analyses  # noqa: F401
from senaite.dashboard.library.builders import chart  # noqa: F401
from senaite.dashboard.library.builders import group  # noqa: F401
from senaite.dashboard.library.builders import kpi  # noqa: F401
from senaite.dashboard.library.builders import samples  # noqa: F401
from senaite.dashboard.library.builders import span  # noqa: F401
from senaite.dashboard.library.builders import table  # noqa: F401
from senaite.dashboard.library.builders import tile_params  # noqa: F401
from senaite.dashboard.library.builders import to_presets  # noqa: F401
from senaite.dashboard.library.builders import worksheets  # noqa: F401
from senaite.dashboard.query.datasets import COL_DATE  # noqa: F401
from senaite.dashboard.query.datasets import COL_DUE  # noqa: F401
from senaite.dashboard.query.datasets import COL_NUMBER  # noqa: F401
from senaite.dashboard.query.datasets import COL_PERCENT  # noqa: F401
from senaite.dashboard.query.datasets import COL_STATE  # noqa: F401
from senaite.dashboard.query.datasets import COL_TEXT  # noqa: F401
from senaite.dashboard.query.datasets import Column  # noqa: F401
from senaite.dashboard.query.datasets import Dataset  # noqa: F401
from senaite.dashboard.query.datasets import DatasetExtension  # noqa: F401
from senaite.dashboard.query.datasets import Span  # noqa: F401
from senaite.dashboard.query.datasets import choice_getter  # noqa: F401
from senaite.dashboard.query.datasets import index_getter  # noqa: F401
from senaite.dashboard.query.fields import BOOLEAN  # noqa: F401
from senaite.dashboard.query.fields import CHOICE  # noqa: F401
from senaite.dashboard.query.fields import DATE  # noqa: F401
from senaite.dashboard.query.fields import KEYWORD  # noqa: F401
from senaite.dashboard.query.fields import REFERENCE  # noqa: F401
from senaite.dashboard.query.fields import STATE  # noqa: F401
from senaite.dashboard.query.fields import TEXT  # noqa: F401
from senaite.dashboard.query.fields import USER  # noqa: F401
from senaite.dashboard.query.fields import Field  # noqa: F401
from senaite.dashboard.query.params import MAPPING  # noqa: F401
from senaite.dashboard.query.params import NAME  # noqa: F401
from senaite.dashboard.query.params import NAMES  # noqa: F401
from senaite.dashboard.query.params import NUMBER  # noqa: F401
from senaite.dashboard.query.search import build_query  # noqa: F401
from senaite.dashboard.query.search import search  # noqa: F401
from senaite.dashboard.query.sources import DataSource  # noqa: F401
from senaite.dashboard.query.sources import with_dataset  # noqa: F401
