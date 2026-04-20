#!/usr/bin/env python3
"""
Patch .claude/settings.json to add brain writeback hooks.

Authority: CZL-BRAIN-L2-HOOK-WIRE-CONTINUATION grant
Engineer: Ryan Park (eng-platform)

This script is idempotent — it checks for existing entries before adding.
Must be run by CEO (Aiden) or an agent with .claude/ write access.

Usage:
    python3 scripts/patch_settings_brain_writeback_hooks.py
"""

import json
import os
import sys

SETTINGS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".claude", "settings.json"
)

BRAIN_ENQUEUE_COMMAND = (
    "python3 /Users/haotianliu/.openclaw/workspace/ystar-company/"
    "scripts/brain_writeback_queue.py enqueue"
)
BRAIN_DRAIN_COMMAND = (
    "python3 /Users/haotianliu/.openclaw/workspace/ystar-company/"
    "scripts/brain_writeback_queue.py drain"
)


def already_has_hook(hooks_list, command_substr):
    """Check if any hook entry already contains the given command substring."""
    for entry in hooks_list:
        for hook in entry.get("hooks", []):
            if command_substr in hook.get("command", ""):
                return True
    return False


def patch():
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        settings = json.load(f)

    hooks = settings.setdefault("hooks", {})
    changed = False

    # 1. PostToolUse: append brain_writeback_queue enqueue (Agent matcher, async)
    post_tool = hooks.setdefault("PostToolUse", [])
    if not already_has_hook(post_tool, "brain_writeback_queue.py enqueue"):
        post_tool.append({
            "matcher": "Agent",
            "hooks": [{
                "type": "command",
                "command": BRAIN_ENQUEUE_COMMAND,
                "timeout": 2000,
                "async": True,
            }]
        })
        changed = True
        print("[PATCH] Added PostToolUse(Agent) -> brain_writeback_queue enqueue")
    else:
        print("[SKIP] PostToolUse brain_writeback_queue enqueue already present")

    # 2. Stop: prepend brain_writeback_queue drain (before existing stop hooks)
    stop = hooks.setdefault("Stop", [])
    if not already_has_hook(stop, "brain_writeback_queue.py drain"):
        stop.insert(0, {
            "matcher": ".*",
            "hooks": [{
                "type": "command",
                "command": BRAIN_DRAIN_COMMAND,
                "timeout": 5000,
            }]
        })
        changed = True
        print("[PATCH] Added Stop -> brain_writeback_queue drain")
    else:
        print("[SKIP] Stop brain_writeback_queue drain already present")

    if changed:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"[OK] settings.json patched at {SETTINGS_PATH}")
    else:
        print("[OK] No changes needed — all hooks already present")

    return changed


if __name__ == "__main__":
    try:
        result = patch()
        sys.exit(0 if result is not None else 1)
    except Exception as e:
        print(f"[ERROR] Patch failed: {e}", file=sys.stderr)
        sys.exit(1)
