# -*- coding: utf-8 -*-
"""Permissions of senaite.dashboard.

The ids match the titles registered in configure.zcml; rolemap.xml
grants them.
"""

# See the dashboard at all
ViewDashboard = "senaite.dashboard: View Dashboard"

# Arrange, add and remove tiles for oneself, and keep personal
# dashboards. Nobody else sees the result.
CustomizeDashboard = "senaite.dashboard: Customize Dashboard"

# Edit, publish and delete the dashboards every user starts from
ManageDashboards = "senaite.dashboard: Manage Global Dashboards"
