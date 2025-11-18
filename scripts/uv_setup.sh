#!/usr/bin/env bash
set -euo pipefail

# Setup script for uv package manager
# This script checks if uv is installed and creates a virtual environment

echo " Checking for uv installation..."

if ! command -v uv &> /dev/null; then
    echo " uv is not installed."
    echo ""
    echo "To install uv, run one of the following commands:"
    echo ""
    echo "  # macOS/Linux:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    echo "  # Or with pip:"
    echo "  pip install uv"
    echo ""
    exit 1
fi

echo " uv is installed: $(uv --version)"
echo ""
echo " Creating virtual environment with uv..."

# Create venv using uv
uv venv

echo ""
echo " Virtual environment created in .venv"
echo ""
echo " Syncing dependencies from pyproject.toml..."

# Sync dependencies
uv sync

echo ""
echo " All dependencies installed!"
echo ""
echo " Installing pip protection..."

# Run post-setup script to lock pip
./scripts/post_venv_setup.sh

echo ""
echo " Setup complete! Activate the virtual environment with:"
echo "   source .venv/bin/activate"
echo ""
echo "  Note: Direct pip commands are now locked. Use 'uv' instead."
echo ""
