#!/usr/bin/env python3
"""UserPromptSubmit hook — Voyager-style skill retrieval.

For each user prompt, query SkillLibrary for top 3 matching scripts
and inject as context. Helps agent remember it has scripts/ tools
before building new ones (anti P-12 先查后造 violation).

Reads from scripts/skill_library.db.
Fail-open: if library missing or empty, exit 0 silently.

Output format (to stdout, Claude Code captures as context):
  [SKILL HINTS]
  1. scripts/X.py — <trigger excerpt>
  2. scripts/Y.py — <trigger excerpt>
  3. scripts/Z.py — <trigger excerpt>

If zero matches, prints nothing (fail-open, don't spam context).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SCRIPTS_DIR = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/scripts")

sys.path.insert(0, str(SCRIPTS_DIR))


def main() -> int:
    # UserPromptSubmit hook receives JSON on stdin
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        payload = {}

    prompt = payload.get("prompt", "") or payload.get("user_prompt", "")
    if not prompt or len(prompt) < 4:
        return 0  # too short, skip

    try:
        from skill_library import SkillLibrary
        lib = SkillLibrary()
        results = lib.retrieve(prompt, limit=3)
    except Exception as e:
        # Fail-open — hook must never block
        return 0

    if not results:
        return 0

    # Emit to stdout (Claude Code injects as UserPromptSubmit context)
    print("[SKILL HINTS] relevant local scripts:")
    for i, r in enumerate(results, 1):
        trigger = (r.get("trigger") or "")[:80]
        path = r.get("path", "")
        rel = path.replace(str(SCRIPTS_DIR.parent) + "/", "")
        print(f"  {i}. {rel} — {trigger}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
