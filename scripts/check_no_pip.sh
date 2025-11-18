#!/usr/bin/env bash
# Pre-commit hook to prevent pip commands in code and documentation

set -e

files=("$@")
issues_found=0

for file in "${files[@]}"; do
    # Skip files that are allowed to mention pip
    if [[ "$file" =~ (pip-wrapper|post_venv_setup|check_no_pip|uv_setup|UV_PACKAGE_MANAGEMENT|README|UV_SETUP_COMPLETE|PRECOMMIT_EMOJI_SETUP|UV_EMOJI_COMPLETE) ]]; then
        continue
    fi

    # Check for problematic pip usage patterns
    if grep -n -E '\bpip\s+(install|uninstall)\b' "$file" 2>/dev/null; then
        echo "❌ Found 'pip install/uninstall' in $file"
        echo "   Use 'uv add' or 'uv remove' instead"
        issues_found=1
    fi

    # Check for pip freeze in new code
    if grep -n -E '\bpip\s+freeze\b' "$file" 2>/dev/null; then
        echo "⚠️  Found 'pip freeze' in $file"
        echo "   Consider using 'uv pip freeze' or 'uv.lock' instead"
        issues_found=1
    fi
done

if [ $issues_found -eq 1 ]; then
    echo ""
    echo "💡 This project uses uv for package management."
    echo "   See docs/UV_PACKAGE_MANAGEMENT.md for migration guide."
    exit 1
fi

exit 0
