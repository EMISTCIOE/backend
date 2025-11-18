#!/usr/bin/env bash
# Post-setup script to lock pip in the virtual environment

set -euo pipefail

VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
    echo " Virtual environment not found at $VENV_DIR"
    exit 1
fi

echo " Installing pip protection in virtual environment..."

# Backup original pip if it exists
if [ -f "$VENV_DIR/bin/pip" ]; then
    mv "$VENV_DIR/bin/pip" "$VENV_DIR/bin/pip.real"
fi
if [ -f "$VENV_DIR/bin/pip3" ]; then
    mv "$VENV_DIR/bin/pip3" "$VENV_DIR/bin/pip3.real"
fi

# Create pip wrapper
cat > "$VENV_DIR/bin/pip" << 'EOF'
#!/usr/bin/env bash
echo "  ERROR: Direct pip usage is disabled in this project!"
echo ""
echo "This project uses uv for package management."
echo ""
echo "Instead of pip commands, use:"
echo ""
echo "  pip install <package>    →  uv add <package>"
echo "  pip install -r ...       →  uv sync"
echo "  pip uninstall <package>  →  uv remove <package>"
echo "  pip list                 →  uv pip list"
echo "  pip freeze               →  uv pip freeze"
echo ""
echo "To bypass this protection (not recommended):"
echo "  $(dirname "$0")/pip.real \"$@\""
echo ""
exit 1
EOF

# Make it executable
chmod +x "$VENV_DIR/bin/pip"

# Create pip3 symlink
ln -sf pip "$VENV_DIR/bin/pip3"

echo " Pip protection installed successfully!"
echo ""
echo "  Note: Direct pip commands will now show an error message."
echo "Use 'uv' commands instead for package management."
