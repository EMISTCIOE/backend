#!/usr/bin/env bash
# UV Setup Verification Script
# Run this to verify that uv is properly configured

set -euo pipefail

echo " UV Setup Verification"
echo "========================"
echo ""

PASS=0
FAIL=0

# Helper functions
pass() {
    echo " $1"
    PASS=$((PASS + 1))
}

fail() {
    echo " $1"
    FAIL=$((FAIL + 1))
}

warn() {
    echo "  $1"
}

# Test 1: UV installed
echo "Test 1: UV Installation"
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    pass "uv is installed ($UV_VERSION)"
else
    fail "uv is not installed"
fi
echo ""

# Test 2: Configuration files
echo "Test 2: Configuration Files"
[ -f "pyproject.toml" ] && pass "pyproject.toml exists" || fail "pyproject.toml missing"
[ -f ".python-version" ] && pass ".python-version exists" || fail ".python-version missing"
[ -f "uv.toml" ] && pass "uv.toml exists" || fail "uv.toml missing"
[ -f "uv.lock" ] && pass "uv.lock exists" || fail "uv.lock missing"
[ -f "Makefile" ] && pass "Makefile exists" || fail "Makefile missing"
echo ""

# Test 3: Helper scripts
echo "Test 3: Helper Scripts"
[ -x "scripts/uv_setup.sh" ] && pass "uv_setup.sh is executable" || fail "uv_setup.sh not executable"
[ -x "scripts/uv_add.sh" ] && pass "uv_add.sh is executable" || fail "uv_add.sh not executable"
[ -x "scripts/uv_run.sh" ] && pass "uv_run.sh is executable" || fail "uv_run.sh not executable"
[ -x "scripts/post_venv_setup.sh" ] && pass "post_venv_setup.sh is executable" || fail "post_venv_setup.sh not executable"
echo ""

# Test 4: Virtual environment
echo "Test 4: Virtual Environment"
if [ -d ".venv" ]; then
    pass ".venv directory exists"

    if [ -f ".venv/bin/pip.real" ]; then
        pass "pip.real backup exists"
    else
        warn "pip.real backup not found (pip protection may not be active)"
    fi

    if [ -f ".venv/bin/pip" ]; then
        pass "pip wrapper exists"

        # Test pip protection
        if .venv/bin/pip --version 2>&1 | grep -q "ERROR.*disabled"; then
            pass "pip protection is active"
        else
            warn "pip protection may not be working correctly"
        fi
    else
        fail "pip wrapper missing"
    fi
else
    fail ".venv directory not found"
fi
echo ""

# Test 5: Documentation
echo "Test 5: Documentation"
[ -f "README.md" ] && pass "README.md exists" || fail "README.md missing"
[ -f "docs/UV_PACKAGE_MANAGEMENT.md" ] && pass "UV_PACKAGE_MANAGEMENT.md exists" || fail "UV_PACKAGE_MANAGEMENT.md missing"
[ -f "UV_SETUP_COMPLETE.md" ] && pass "UV_SETUP_COMPLETE.md exists" || fail "UV_SETUP_COMPLETE.md missing"
echo ""

# Test 6: Dependencies
echo "Test 6: Dependencies"
if [ -d ".venv" ]; then
    PACKAGE_COUNT=$(uv pip list 2>/dev/null | wc -l)
    if [ "$PACKAGE_COUNT" -gt 5 ]; then
        pass "Dependencies installed ($PACKAGE_COUNT packages)"
    else
        fail "Few or no dependencies installed"
    fi
else
    warn "Cannot check dependencies (no .venv)"
fi
echo ""

# Summary
echo "========================"
echo "Summary:"
echo "   Passed: $PASS"
echo "   Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo " All checks passed! UV setup is complete."
    echo ""
    echo "Next steps:"
    echo "  1. Run 'make help' to see available commands"
    echo "  2. Try 'make run' to start the development server"
    echo "  3. Read 'docs/UV_PACKAGE_MANAGEMENT.md' for more info"
    exit 0
else
    echo "  Some checks failed. Please review the output above."
    exit 1
fi
