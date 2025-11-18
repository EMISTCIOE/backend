#!/usr/bin/env bash
# Wrapper script to prevent accidental pip usage in uv-managed projects

set -euo pipefail

echo "  ERROR: Direct pip usage is disabled in this project!"
echo ""
echo "This project uses uv for package management."
echo ""
echo "Instead of pip commands, use:"
echo ""
echo "  pip install <package>    →  uv add <package>"
echo "  pip install -r requirements.txt  →  uv sync"
echo "  pip uninstall <package>  →  uv remove <package>"
echo "  pip list                 →  uv pip list"
echo "  pip freeze               →  uv pip freeze"
echo ""
echo "For more help, see: https://docs.astral.sh/uv/"
echo ""
exit 1
