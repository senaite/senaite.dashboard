# -*- coding: utf-8 -*-
"""The texts of the pages, by the key the script asks for them by.

They are translated on the server and handed to the script with the
data it starts from, so the script needs no translation machinery of
its own. A key the script asks for but this table lacks shows as the
key itself.
"""

from collections import OrderedDict

from senaite.core.i18n import translate
from senaite.dashboard import messagefactory as _

UI_STRINGS = OrderedDict([
    ("add_filter", _("Add filter")),
    ("add_link", _("Add link")),
    ("add_span", _("Add span")),
    ("add_tile", _("Add tile")),
    ("add_to_dashboard", _("Add")),
    ("advanced", _("Advanced")),
    ("after_now", _("From now on")),
    ("all", _("All")),
    ("appearance", _("Appearance")),
    ("ascending", _("Oldest first")),
    ("back_to_dashboard", _("Back to the dashboard")),
    ("before_now", _("Before now")),
    ("cancel", _("Cancel")),
    ("close", _("Close")),
    ("color", _("Color")),
    ("column", _("Column")),
    ("columns", _("Columns")),
    ("create", _("Create")),
    ("create_dashboard", _("New dashboard")),
    ("current_day", _("Today")),
    ("current_month", _("This month")),
    ("current_week", _("This week")),
    ("custom", _("Custom")),
    ("customize", _("Customize")),
    ("customized", _("Customized for you")),
    ("dashboard_title", _("Title")),
    ("dashboards", _("Dashboards")),
    ("data", _("Data")),
    ("dataset", _("Show")),
    ("dataset_columns", _("Columns of tables")),
    ("dataset_columns_hint", _("What a table may show of each object. The "
                               "values come from the catalog, not from the "
                               "objects.")),
    ("dataset_fields", _("Fields")),
    ("dataset_fields_hint", _("What a tile may filter and group by. Fields "
                              "only for the laboratory are not offered to "
                              "client contacts.")),
    ("dataset_general", _("Dataset")),
    ("dataset_lab_only", _("Only for the laboratory")),
    ("dataset_spans", _("Spans of time")),
    ("dataset_spans_hint", _("How long it takes from one date to another, "
                             "e.g. from reception to release.")),
    ("dataset_type", _("Made of")),
    ("dataset_type_fixed", _("The type of a saved dataset stays as it is.")),
    ("dataset_unused", _("No global dashboard and no tile of the library "
                         "uses it.")),
    ("dataset_usage", _("Used by {dashboards} global dashboards and "
                        "{library} tiles of the library.")),
    ("dataset_warning", _("Everybody who may see an object sees what you "
                          "offer of it here. Personal data and results are "
                          "never offered.")),
    ("datasets", _("Datasets")),
    ("datasets_hint", _("Make types of SENAITE and its add-ons available to "
                        "tiles.")),
    ("date_field", _("Date")),
    ("days", _("d")),
    ("delete", _("Delete")),
    ("delete_confirm", _("Delete this dashboard? This cannot be undone.")),
    ("delete_dashboard", _("Delete dashboard")),
    ("delete_dataset", _("Delete dataset")),
    ("delete_dataset_confirm", _("Their tiles will show that the dataset is "
                                 "gone.")),
    ("descending", _("Newest first")),
    ("description", _("Description")),
    ("discard_draft", _("Discard changes")),
    ("done", _("Done")),
    ("draft", _("Draft")),
    ("draft_hint", _("You are editing the draft. Users see the published "
                     "version until you publish.")),
    ("draft_hint_published", _("Everything is published. What you "
                               "change here stays in the draft until "
                               "you publish again.")),
    ("edit_draft", _("Edit for everybody")),
    ("pending_hint", _("The draft has changes that are not published "
                       "yet. Everybody else sees this version.")),
    ("open_draft", _("Open the draft")),
    ("edit_draft_hint", _("Change the dashboard every user starts from")),
    ("edit_hint", _("Drag tiles by their title to move them, drag the "
                    "corner to resize. Changes are saved automatically.")),
    ("edit_mine", _("Customize for me")),
    ("edit_mine_hint", _("Arrange the tiles the way you like; nobody else is "
                         "affected")),
    ("empty_dashboard", _("This dashboard has no tiles yet.")),
    ("empty_tile", _("Nothing to show")),
    ("error", _("Not saved")),
    ("examples", _("Examples")),
    ("filters", _("Filters")),
    ("for_everybody", _("Nobody selected: visible for everybody")),
    ("for_roles", _("Visible for")),
    ("global", _("For everybody")),
    ("good_afternoon", _("Good afternoon")),
    ("good_evening", _("Good evening")),
    ("good_morning", _("Good morning")),
    ("group_by", _("Group by")),
    ("hide", _("Remove")),
    ("hours", _("h")),
    ("index", _("Index")),
    ("interval", _("Interval")),
    ("interval_day", _("Daily")),
    ("interval_month", _("Monthly")),
    ("interval_week", _("Weekly")),
    ("invalid_json", _("This is not valid JSON; nothing was changed.")),
    ("keyboard_hint", _("Arrow keys move the tile, with Shift they "
                        "resize it")),
    ("kind", _("Kind")),
    ("kind_boolean", _("Yes or no")),
    ("kind_date", _("Date")),
    ("kind_number", _("Number")),
    ("kind_reference", _("Reference")),
    ("kind_state", _("Status")),
    ("kind_text", _("Text")),
    ("kind_user", _("User")),
    ("lab_only", _("Lab only")),
    ("last_30d", _("Last 30 days")),
    ("last_365d", _("Last 12 months")),
    ("last_7d", _("Last 7 days")),
    ("last_90d", _("Last 90 days")),
    ("last_updated", _("Updated")),
    ("library", _("Add a tile")),
    ("library_hint", _("Pick a tile to add it to the dashboard. You can "
                       "change it afterwards.")),
    ("limit", _("Entries")),
    ("link", _("Link")),
    ("link_hint", _("Page the title leads to, e.g. samples")),
    ("loading", _("Loading")),
    ("manage_datasets", _("Manage datasets")),
    ("manage_datasets_hint", _("Make more types available to tiles")),
    ("markdown_hint", _("**bold**, *italic*, # heading, - list, "
                        "[text](samples) for a link")),
    ("me", _("Me")),
    ("measured", _("Measured")),
    ("median", _("Median")),
    ("more", _("More actions")),
    ("my_client", _("My client")),
    ("my_client_hint", _("Client contacts see their own client, the "
                         "laboratory sees all")),
    ("new_dashboard_hint", _("Start with")),
    ("new_dataset", _("New dataset")),
    ("new_global", _("For everybody (draft)")),
    ("new_personal", _("Only for me")),
    ("no", _("No")),
    ("no_dashboards", _("There is no dashboard for you yet. Make one "
                        "of your own.")),
    ("no_data", _("No data")),
    ("no_datasets", _("There are no datasets of your own yet.")),
    ("none", _("None")),
    ("not_published", _("Not published")),
    ("note_info", _("Notice")),
    ("note_placeholder", _("Write a note")),
    ("note_plain", _("Plain")),
    ("note_warning", _("Important")),
    ("notice_dataset_removed", _("Dataset deleted")),
    ("notice_dataset_saved", _("Saved. Load the dashboard again to use it.")),
    ("notice_defaults_complete", _("All default dashboards are there "
                                   "already.")),
    ("notice_defaults_restored", _("Default dashboards added as drafts. "
                                   "Publish them to show them to users.")),
    ("notice_discarded", _("Changes discarded. The draft is the "
                           "published version again.")),
    ("notice_published", _("Published. Everybody now sees this "
                           "version.")),
    ("notice_removed_from_library", _("Removed from the library")),
    ("notice_saved_to_library", _("Saved to the library. Everybody can "
                                  "add it now.")),
    ("notice_tile_removed", _("Tile removed")),
    ("notice_was_reset", _("Your changes are undone. You see the "
                           "dashboard as everybody else.")),
    ("objects_visible", _("objects you may see")),
    ("of_total", _("of")),
    ("open_list", _("Open list")),
    ("or", _("or ...")),
    ("p90", _("90% within")),
    ("periods", _("Periods")),
    ("personal", _("Only for you")),
    ("pick_dataset", _("Pick a dataset on the left, or make a new one.")),
    ("points_to", _("Points to")),
    ("publish", _("Publish")),
    ("refresh", _("Refresh")),
    ("refreshing", _("Refreshing")),
    ("remove_from_library", _("Remove from the library")),
    ("reset", _("Reset to default")),
    ("reset_confirm", _("Undo all your changes to this dashboard?")),
    ("restore", _("Restore")),
    ("restore_defaults", _("Restore default dashboards")),
    ("restore_defaults_hint", _("Add the default dashboards that are "
                                "missing")),
    ("restore_defaults_confirm", _("Default dashboards that are missing "
                                   "are added as drafts. Dashboards that "
                                   "are there stay as they are. Users see "
                                   "the new ones once you publish them.")),
    ("save", _("Save")),
    ("save_to_library", _("Save to library")),
    ("save_to_library_hint", _("Everybody can add the tile from the "
                               "library afterwards. Say in a few words "
                               "what it shows.")),
    ("saved", _("Saved")),
    ("saving", _("Saving")),
    ("search_tiles", _("Search tiles")),
    ("settings", _("Settings")),
    ("sort_on", _("Sort by")),
    ("source", _("Kind of data")),
    ("span", _("Measure")),
    ("span_from", _("From")),
    ("span_to", _("To")),
    ("stack_by", _("Split by")),
    ("start_empty", _("An empty dashboard")),
    ("start_from_copy", _("A copy of this one")),
    ("style", _("Style")),
    ("style_area", _("Area")),
    ("style_bars", _("Columns")),
    ("style_line", _("Line")),
    ("this_month", _("This month")),
    ("this_week", _("This week")),
    ("this_year", _("This year")),
    ("tile_failed", _("This tile cannot be shown. Check its settings "
                      "or remove it.")),
    ("tile_settings", _("Tile settings")),
    ("tile_title", _("Title")),
    ("tile_type", _("Display")),
    ("total", _("Total")),
    ("trend", _("Show the course")),
    ("type_bar", _("Bars")),
    ("type_chart", _("Over time")),
    ("type_donut", _("Donut")),
    ("type_kpi", _("Number")),
    ("type_links", _("Links")),
    ("type_note", _("Note")),
    ("type_table", _("Table")),
    ("undo", _("Undo")),
    ("unpublished_changes", _("Unpublished changes")),
    ("url", _("Address")),
    ("use", _("Use")),
    ("value_any", _("Any")),
    ("view_as_user", _("Back to my view")),
    ("week_of", _("Week of")),
    ("yes", _("Yes")),
])


def get_ui_strings():
    return OrderedDict((key, translate(msg, to_utf8=False))
                       for key, msg in UI_STRINGS.items())
