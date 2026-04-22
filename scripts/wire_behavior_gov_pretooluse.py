#!/usr/bin/env python3
"""Wire behavior_gov_engine into PreToolUse hook chain.

Per Board 2026-04-22 methodology directive: YAML-driven rule engine replaces
ad-hoc hook accumulation. Idempotent: checks existing chain before append.
"""
import json
import sys
from pathlib import Path

SETTINGS = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/.claude/settings.json")

NEW_HOOK = {
    "matcher": ".*",
    "hooks": [
        {
            "type": "command",
            "command": "python3.11 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/behavior_gov_engine.py",
            "timeout": 3000,
        }
    ],
}


def main() -> int:
    data = json.loads(SETTINGS.read_text(encoding="utf-8"))
    ptu_chain = data.get("hooks", {}).get("PreToolUse", [])
    target_cmd = NEW_HOOK["hooks"][0]["command"]

    # Idempotent
    for entry in ptu_chain:
        for h in entry.get("hooks", []):
            if h.get("command") == target_cmd:
                print(f"[wire] already wired: behavior_gov_engine in PreToolUse")
                return 0

    ptu_chain.append(NEW_HOOK)
    data["hooks"]["PreToolUse"] = ptu_chain

    SETTINGS.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"[wire] appended behavior_gov_engine to PreToolUse")
    print(f"[wire] PreToolUse chain length: {len(ptu_chain)}")

    # Verify JSON valid
    try:
        json.loads(SETTINGS.read_text())
        print("[wire] JSON valid")
    except Exception as e:
        print(f"[wire] JSON INVALID: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
