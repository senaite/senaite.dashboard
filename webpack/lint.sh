#!/usr/bin/env bash
# Lint the script: ESLint with the rules of React hooks, then names the
# script uses but never defines or imports, and imports of names a
# module does not export. Webpack builds such a bundle without a word;
# it fails only in the browser.
#
# TypeScript reads the plain JavaScript for the second check; its other
# findings are about types this code does not declare, and are left
# out.
set -uo pipefail
cd "$(dirname "$0")"

npx --no-install eslint --max-warnings 0 --ext .js,.jsx app || exit 1

FOUND=$(npx --no-install tsc -p jsconfig.json 2>&1 |
        grep -E "TS2304|TS2552|TS2305|TS2614|TS2724")
if [ -n "$FOUND" ]; then
    echo "$FOUND"
    exit 1
fi
echo "No undefined names"
