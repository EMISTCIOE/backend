#!/usr/bin/env bash
set -euo pipefail

# Run a command in the uv virtual environment
# Usage: ./scripts/uv_run.sh <command>
# Example: ./scripts/uv_run.sh python manage.py runserver

if [ $# -eq 0 ]; then
    echo "Usage: $0 <command>"
    echo "Example: $0 python manage.py runserver"
    exit 1
fi

uv run "$@"
