#!/usr/bin/env bash
# Activate virtual environment with pip protection

set -euo pipefail

VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
    echo " Virtual environment not found at $VENV_DIR"
    echo "Run './scripts/uv_setup.sh' or 'make setup' first"
    exit 1
fi

# Source the venv activation
source "$VENV_DIR/bin/activate"

# Create pip wrapper aliases
alias pip='echo " Use uv instead of pip. Run: uv add <package>" && false'
alias pip3='echo " Use uv instead of pip. Run: uv add <package>" && false'

echo " Virtual environment activated with pip protection enabled"
echo " Use 'uv add <package>' to install packages"
echo " Use 'make help' to see all available commands"
echo ""
echo "To activate in your current shell, run:"
echo "  source $VENV_DIR/bin/activate"
