# -*- coding: utf-8 -*-
"""The query language: how a tile gets its numbers.

A tile names a data source and its parameters. Everything runs as the
current user, through the catalog. Read in this order:

`compute`
    The one entry point: looks the source up, checks the parameters
    and caches the answer per user.
`sources`
    The data sources: count, group, timeseries, list and span, and the
    shape of what each answers.
`registry`
    Where a tile finds its dataset.
`datasets`
    What a dataset is made of: the fields a tile may filter and group
    by, the columns and spans it may show.
`builtin`
    The datasets senaite.dashboard ships with.
`fields`
    Kinds of fields, and how a filter becomes a catalog query.
`search`
    Catalog searches, and values read straight from the indexes.
`labels`
    Index values (states, UIDs, user ids) to what the user reads.

Datasets managers define in the browser: `custom` keeps their
definitions, `catalogs` decides what the catalogs offer to them,
`inspection` proposes fields and columns with examples.

`params` checks the parameters before anything runs, `variables`
resolves placeholders such as `$client` or `$today-30d`, `timeline`
and `calendar_dates` cut time into periods, and `vocabularies`
gives the tile editor the choices of a filter.
"""
