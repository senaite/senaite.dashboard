# -*- coding: utf-8 -*-
"""Dashboards: what users see and change, and who may change what.

A dashboard is a list of tiles. Nothing here computes any data; that
is the business of `senaite.dashboard.query`. Where it is all kept is
`senaite.dashboard.storage`, who may do what `senaite.dashboard.access`.
Read in this order:

`model`
    Tiles and overlays as plain mappings, pure functions only. An
    overlay is what a user changed on a global dashboard.
`shared`
    Global dashboards: a draft for managers, a published version for
    everybody else.
`personal`
    What a user keeps for themselves: personal dashboards, overlays
    and the dashboard they looked at last.
`views`
    A dashboard as the page shows it to the current user.

`ids` makes the ids of dashboards, `defaults` the dashboards a new
site starts with.
"""
