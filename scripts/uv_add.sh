#!/usr/bin/env bash
set -euo pipefail

# Add a package using uv
# Usage: ./scripts/uv_add.sh package-name

if [ $# -eq 0 ]; then
    echo "Usage: $0 <package-name>"
    echo "Example: $0 django-debug-toolbar"
    exit 1
fi

PACKAGE=$1

echo " Adding package: $PACKAGE"
uv add "$PACKAGE"

echo " Package added and dependencies synced!"
