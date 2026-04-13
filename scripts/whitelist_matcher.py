#!/usr/bin/env python3
"""
[L3] Whitelist Matcher — Find matching whitelist patterns for user message

Used by hook_user_prompt_tracker.py to inject context hints
"""

import sys
import re
from pathlib import Path

WORKSPACE_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
WHITELIST_DIR = WORKSPACE_ROOT / "governance/whitelist"


def load_whitelist_patterns():
    """Load all whitelist YAML patterns"""
    patterns = []
    if not WHITELIST_DIR.exists():
        return patterns

    for yaml_file in WHITELIST_DIR.glob("*.yaml"):
        try:
            content = yaml_file.read_text()
            # Extract pattern lines (simplified YAML parser)
            for line in content.split('\n'):
                if 'pattern:' in line or 'action:' in line:
                    # Extract quoted string or bare word
                    match = re.search(r'["\'](.+?)["\']|:\s*(\S+)', line)
                    if match:
                        pattern = match.group(1) or match.group(2)
                        patterns.append((yaml_file.stem, pattern))
        except Exception:
            pass
    return patterns


def match_message(user_msg, patterns):
    """Find top 3 matching patterns"""
    user_lower = user_msg.lower()
    matches = []

    for rule_name, pattern in patterns:
        # Simple substring match (can upgrade to regex/fuzzy later)
        if pattern.lower() in user_lower or user_lower in pattern.lower():
            matches.append(f"{rule_name}: {pattern[:60]}")

    return matches[:3]


def main():
    if len(sys.argv) < 2:
        return

    user_msg = sys.argv[1]
    patterns = load_whitelist_patterns()
    matches = match_message(user_msg, patterns)

    for match in matches:
        print(match)


if __name__ == "__main__":
    main()
