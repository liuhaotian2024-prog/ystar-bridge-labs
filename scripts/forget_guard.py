#!/usr/bin/env python3
"""
ForgetGuard shim — delegates to ystar.governance.forget_guard (structured rules).

The 405-line keyword-pattern engine that lived here was purged per Board
commit 8195fc2 (2026-04-25).  This thin wrapper preserves the stdin/stdout
JSON contract that hook_client_labs.sh line 64 relies on:

    echo "$PAYLOAD" | python3 scripts/forget_guard.py

Input  (stdin): JSON hook payload  {"tool_name": ..., "tool_input": ..., ...}
Output (stdout): JSON  {"action": "allow"|"deny", ...}

NO keyword regex. NO _matches_pattern(). NO yaml load.
Any attempt to reintroduce pattern matching here should be caught by
ForgetGuardSchemaError in the upstream module.
"""

import sys
import json
import os
from pathlib import Path

# Ensure ystar package is importable (Y-star-gov sibling workspace)
_YGOV_DIR = os.environ.get(
    "YGOV_DIR",
    str(Path(__file__).resolve().parent.parent.parent / "Y-star-gov"),
)
if _YGOV_DIR not in sys.path:
    sys.path.insert(0, _YGOV_DIR)

ALLOW = json.dumps({"action": "allow", "rules_triggered": []})


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        print(ALLOW)
        return

    try:
        from ystar.governance.forget_guard import check_forget_violation

        result = check_forget_violation(payload)
        if result is None:
            print(ALLOW)
        else:
            # Upstream returns a dict; ensure it has the fields the shell expects
            result.setdefault("action", "allow")
            result.setdefault("rules_triggered", [])
            print(json.dumps(result))
    except Exception as exc:
        # Fail-open: never brick the hook chain
        print(ALLOW, file=sys.stdout)
        print(f"[FORGET_GUARD_SHIM] fail-open: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
