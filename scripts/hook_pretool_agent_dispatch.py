#!/usr/bin/env python3
"""
PreToolUse Hook — Agent Dispatch Validator

**Authority**: Platform Engineer Ryan Park per CEO directive CZL-136
**Spec**: governance/action_model_v2.md Phase A enforcement
**Purpose**: Block Agent tool calls with missing BOOT CONTEXT (5-step Phase A)

Called by: ~/.claude/settings.json hooks.PreToolUse entry
Emits CIEU: DISPATCH_BLOCKED_MISSING_PHASE_A (deny mode) or DISPATCH_PHASE_A_CHECK (warn mode)

Usage:
    echo '{"tool":"Agent","params":{"task":"..."}}' | python3 hook_pretool_agent_dispatch.py
"""

import sys
import json
from pathlib import Path

# Import Phase A validator from action_model_validator
COMPANY_ROOT = Path.home() / ".openclaw/workspace/ystar-company"
sys.path.insert(0, str(COMPANY_ROOT / "scripts"))

from action_model_validator import validate_dispatch_phase_a


def main():
    """PreToolUse hook for Agent tool calls."""
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        # Not valid JSON, allow (not an Agent call)
        print(json.dumps({"action": "allow", "message": "Not JSON, skip Agent validator"}))
        return 0

    tool_name = payload.get("tool", "")

    # Only validate Agent tool calls
    if tool_name != "Agent":
        print(json.dumps({"action": "allow", "message": f"Tool {tool_name} not Agent, skip"}))
        return 0

    # Extract task/prompt from Agent tool params
    params = payload.get("params", {})
    prompt_text = params.get("task", "") or params.get("prompt", "")

    # Run Phase A validation
    result = validate_dispatch_phase_a(prompt_text)

    # Emit CIEU event
    event_type = "DISPATCH_BLOCKED_MISSING_PHASE_A" if not result["allow"] else "DISPATCH_PHASE_A_CHECK"
    emit_cieu(event_type, result)

    # Current mode: WARN only (not deny) per CZL-136 gradual rollout
    # After 48h baseline, promote to deny mode
    if not result["allow"]:
        # WARN mode: log violation but allow through
        print(json.dumps({
            "action": "allow",
            "message": f"[WARN] {result['reason']} (bitmap: {result['phase_bitmap']})"
        }))
    else:
        print(json.dumps({
            "action": "allow",
            "message": f"Phase A complete: {result['phase_bitmap']}"
        }))

    return 0


def emit_cieu(event_type: str, validation_result: dict):
    """Emit CIEU event to sqlite database."""
    try:
        import sqlite3
        from datetime import datetime
        import uuid as uuid_lib
        import time

        db_path = Path.home() / ".openclaw/workspace/ystar-company/.ystar_cieu.db"
        conn = sqlite3.connect(str(db_path), timeout=5.0)
        cursor = conn.cursor()

        # Generate event fields per schema
        event_id = str(uuid_lib.uuid4())
        now = time.time()
        seq_global = int(now * 1_000_000)  # microsecond timestamp

        cursor.execute("""
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, session_id, agent_id, event_type,
                decision, passed, violations, drift_detected
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            seq_global,
            now,
            "current",  # session_id placeholder
            "hook_pretool_agent_dispatch",
            event_type,
            "allow" if validation_result["allow"] else "warn",
            1 if validation_result["allow"] else 0,
            json.dumps(validation_result["missing_steps"]),
            0  # No drift detected
        ))

        conn.commit()
        conn.close()
    except Exception as e:
        # Fail-open for CIEU logging (don't block hook if DB error)
        sys.stderr.write(f"CIEU emit error: {e}\n")


if __name__ == "__main__":
    sys.exit(main())
