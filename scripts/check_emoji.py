#!/usr/bin/env python3
"""
Pre-commit hook to check emoji usage in files.

This script ensures:
1. Emojis are used consistently (✅ not ✓, ❌ not ✗)
2. Common emojis follow project standards
3. Shell scripts use consistent emoji patterns
4. Regex patterns for emoji validation
"""

import re
import sys
from pathlib import Path

# Approved emoji mapping (preferred -> alternatives to avoid)
EMOJI_STANDARDS = {
    "✅": ["✓", "√", "☑", "☑️"],  # Use ✅ for success
    "❌": ["✗", "✕", "×", "❎"],  # Use ❌ for errors
    "⚠️": ["⚠"],  # Use ⚠️ with variation selector
    "🔒": ["🔐"],  # Use 🔒 for lock
    "📦": [],  # Use 📦 for packages
    "🚀": [],  # Use 🚀 for launch/start
    "🎉": [],  # Use 🎉 for celebration
    "💡": ["💬"],  # Use 💡 for tips
    "🔍": ["🔎"],  # Use 🔍 for search
    "⚡": [],  # Use ⚡ for speed/fast
    "🛠️": ["🛠"],  # Use 🛠️ with variation selector
    "🎯": [],  # Use 🎯 for target/goal
    "👥": [],  # Use 👥 for team
}

# Build reverse mapping for quick lookup
EMOJI_REPLACEMENTS = {}
for preferred, alternatives in EMOJI_STANDARDS.items():
    for alt in alternatives:
        EMOJI_REPLACEMENTS[alt] = preferred

# Regex patterns for validation
EMOJI_PATTERNS = {
    # Success patterns - should use ✅
    "success": {
        "pattern": re.compile(
            r"\b(pass|success|done|complete|ok|good)\b",
            re.IGNORECASE,
        ),
        "required_emoji": "✅",
        "description": "Success messages should use ✅",
    },
    # Error patterns - should use ❌
    "error": {
        "pattern": re.compile(r"\b(fail|error|wrong|bad|invalid)\b", re.IGNORECASE),
        "required_emoji": "❌",
        "description": "Error messages should use ❌",
    },
    # Warning patterns - should use ⚠️
    "warning": {
        "pattern": re.compile(r"\b(warn|caution|note|attention)\b", re.IGNORECASE),
        "required_emoji": "⚠️",
        "description": "Warning messages should use ⚠️",
    },
}

# Unicode emoji range for detecting any emoji
EMOJI_UNICODE_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U00002702-\U000027B0"  # dingbats
    "\U000024C2-\U0001F251"
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U0001FA00-\U0001FAFF"  # extended symbols
    "\u2600-\u26FF"  # misc symbols
    "\u2700-\u27BF"  # dingbats
    "\uFE00-\uFE0F"  # variation selectors
    "]+",
    flags=re.UNICODE,
)


def check_file(filepath: Path) -> tuple[bool, list[str]]:
    """
    Check a file for emoji usage issues.

    Returns:
        (is_valid, error_messages)
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return True, []  # Skip files we can't read

    errors = []
    warnings = []
    lines = content.split("\n")

    for line_num, line in enumerate(lines, 1):
        # Check for non-standard emojis
        for wrong_emoji, correct_emoji in EMOJI_REPLACEMENTS.items():
            if wrong_emoji in line:
                errors.append(
                    f"{filepath}:{line_num}: Use '{correct_emoji}' instead of '{wrong_emoji}'",
                )

        # Check for common typos in shell scripts
        if filepath.suffix == ".sh":
            # Ensure echo statements with emojis are properly quoted
            emoji_match = EMOJI_UNICODE_PATTERN.search(line)
            if emoji_match and "echo" in line:
                if not re.search(r'echo\s+["\']', line):
                    errors.append(
                        f"{filepath}:{line_num}: Emoji in echo should be quoted",
                    )

        # Regex-based pattern matching for semantic emoji usage
        # Only check lines that contain emojis or emoji keywords
        if EMOJI_UNICODE_PATTERN.search(line) or any(
            pattern_info["pattern"].search(line)
            for pattern_info in EMOJI_PATTERNS.values()
        ):
            for pattern_name, pattern_info in EMOJI_PATTERNS.items():
                if pattern_info["pattern"].search(line):
                    required_emoji = pattern_info["required_emoji"]
                    # Check if the required emoji is present
                    if required_emoji not in line:
                        # Find what emoji (if any) is being used
                        found_emojis = EMOJI_UNICODE_PATTERN.findall(line)
                        if found_emojis:
                            # Only warn if a different emoji is used for this semantic meaning
                            if not any(
                                emoji in EMOJI_STANDARDS for emoji in found_emojis
                            ):
                                pass  # Unknown emoji, ignore
                            else:
                                warnings.append(
                                    f"{filepath}:{line_num}: {pattern_info['description']} (found: {found_emojis[0]})",
                                )

    return len(errors) == 0, errors + warnings


def main():
    """Main entry point for pre-commit hook."""
    if len(sys.argv) < 2:
        print("Usage: check_emoji.py <file> [<file> ...]")
        sys.exit(0)

    all_valid = True
    all_errors = []

    for filepath_str in sys.argv[1:]:
        filepath = Path(filepath_str)

        # Skip certain files
        if any(
            skip in str(filepath)
            for skip in [
                "migrations/",
                "node_modules/",
                ".git/",
                "__pycache__/",
                ".venv/",
                "check_emoji.py",  # Don't check this file
            ]
        ):
            continue

        is_valid, errors = check_file(filepath)

        if not is_valid:
            all_valid = False
            all_errors.extend(errors)

    if not all_valid:
        print("❌ Emoji usage issues found:")
        print()
        for error in all_errors:
            print(f"  {error}")
        print()
        print("💡 Tip: Use the standard emojis defined in scripts/check_emoji.py")
        sys.exit(1)

    # Success - silent output for pre-commit
    sys.exit(0)


if __name__ == "__main__":
    main()
