#!/usr/bin/env bash
# Rebuild the .pot from the sources and sync the .po files with it.
# Run from the package root; needs bin/i18ndude of the buildout.
set -euo pipefail

I18NDUDE="${I18NDUDE:-../../bin/i18ndude}"
LOCALES="src/senaite/dashboard/locales"
POT="$LOCALES/senaite.dashboard.pot"

"$I18NDUDE" rebuild-pot --pot "$POT" --create senaite.dashboard \
    src/senaite/dashboard
for po in "$LOCALES"/*/LC_MESSAGES/senaite.dashboard.po; do
    "$I18NDUDE" sync --pot "$POT" "$po"
done
