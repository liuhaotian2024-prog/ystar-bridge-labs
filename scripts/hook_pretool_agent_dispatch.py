#!/usr/bin/env python3
"""
PreToolUse Hook — Agent Dispatch Validator

**Authority**: Platform Engineer Ryan Park per CEO directive CZL-136
**Spec**: governance/action_model_v2.md Phase A enforcement
         + Y* Field Theory Spec Section 14.4-bis Phase 1 pre-flight
**Purpose**: Block Agent tool calls with missing BOOT CONTEXT (5-step Phase A)
             + Y* m_functor pre-flight validation (Phase 1 cognitive-governance)

Called by: ~/.claude/settings.json hooks.PreToolUse entry
Emits CIEU: DISPATCH_BLOCKED_MISSING_PHASE_A (deny mode) or DISPATCH_PHASE_A_CHECK (warn mode)
            Y_STAR_PREFLIGHT_FAIL (deny on m_functor mismatch) or Y_STAR_PREFLIGHT_PASS (continue)

Usage:
    echo '{"tool":"Agent","params":{"task":"..."}}' | python3 hook_pretool_agent_dispatch.py
"""

import sys
import json
import re
from pathlib import Path

# Import Phase A validator from action_model_validator
COMPANY_ROOT = Path.home() / ".openclaw/workspace/ystar-company"
sys.path.insert(0, str(COMPANY_ROOT / "scripts"))

from action_model_validator import validate_dispatch_phase_a


# ---------------------------------------------------------------------------
# Y* pre-flight: m_functor extraction from Agent prompt
# ---------------------------------------------------------------------------

# Patterns to detect Y* navigation markers in prompt text
_YSTAR_MARKER_RE = re.compile(
    r"(?:Y\*\s*[:=]|m_functor\s*[:=]|Y_star\s*[:=])",
    re.IGNORECASE,
)

# Extract m_functor value: "m_functor: M-2a" or "m_functor=M-1+M-2"
_MFUNCTOR_VALUE_RE = re.compile(
    r"m_functor\s*[:=]\s*(M[\-\d\w+]+)",
    re.IGNORECASE,
)

# Extract artifacts from prompt (comma-separated paths after "artifacts:" line)
_ARTIFACTS_RE = re.compile(
    r"artifacts?\s*[:=]\s*([^\n]+)",
    re.IGNORECASE,
)

# Extract parent CZL from prompt
_PARENT_CZL_RE = re.compile(
    r"(?:parent[_\-]?czl|czl[_\-]?parent|parent)\s*[:=]\s*(\S+)",
    re.IGNORECASE,
)


def _extract_ystar_fields(prompt_text: str) -> dict:
    """
    Extract Y* pre-flight fields from an Agent dispatch prompt.
    Returns dict with keys: has_markers, m_functor, task_description, artifacts, parent_czl.
    """
    has_markers = bool(_YSTAR_MARKER_RE.search(prompt_text))

    m_functor = None
    m_match = _MFUNCTOR_VALUE_RE.search(prompt_text)
    if m_match:
        m_functor = m_match.group(1).strip().rstrip(",;.)")

    # Task description: use the full prompt as task_description for KH matching
    task_description = prompt_text

    # Artifacts
    artifacts = []
    art_match = _ARTIFACTS_RE.search(prompt_text)
    if art_match:
        raw = art_match.group(1)
        artifacts = [a.strip().strip('"\'') for a in raw.split(",") if a.strip()]

    # Parent CZL
    parent_czl = None
    czl_match = _PARENT_CZL_RE.search(prompt_text)
    if czl_match:
        parent_czl = czl_match.group(1).strip().rstrip(",;.)")

    return {
        "has_markers": has_markers,
        "m_functor": m_functor,
        "task_description": task_description,
        "artifacts": artifacts,
        "parent_czl": parent_czl,
    }


def _run_ystar_preflight(prompt_text: str) -> dict:
    """
    Run Y* pre-flight self-check on an Agent dispatch prompt.
    Returns dict: {preflight_ran, passed, result_or_none, deny_message_or_none}.
    """
    fields = _extract_ystar_fields(prompt_text)

    # No Y* markers in prompt → skip pre-flight (not a Y*-annotated dispatch)
    if not fields["has_markers"] or not fields["m_functor"]:
        return {"preflight_ran": False, "passed": True, "result": None, "deny_message": None}

    # Import y_star_self_check (same scripts/ directory)
    try:
        from y_star_self_check import run_self_check
    except ImportError as e:
        # Fail-open: if self_check module unavailable, allow through with warning
        sys.stderr.write(f"Y* preflight import error: {e}\n")
        return {"preflight_ran": False, "passed": True, "result": None, "deny_message": None}

    workspace_root = str(COMPANY_ROOT)

    result = run_self_check(
        task_description=fields["task_description"],
        m_functor=fields["m_functor"],
        parent_czl=fields["parent_czl"],
        artifacts=fields["artifacts"],
        workspace_root=workspace_root,
        emit_cieu=False,  # We emit our own CIEU below, not the advisory one
    )

    verdict = result.get("overall_verdict", "FAIL")
    passed = verdict == "PASS"

    deny_message = None
    if not passed:
        suggestion = result.get("suggestion", "")
        deny_message = (
            f"Y* pre-flight FAIL: m_functor={fields['m_functor']} "
            f"inconsistent with deterministic paths. {suggestion}"
        )

    return {
        "preflight_ran": True,
        "passed": passed,
        "result": result,
        "deny_message": deny_message,
    }


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

    # --- Gate 1: Phase A validation (BOOT CONTEXT 5-step) ---
    result = validate_dispatch_phase_a(prompt_text)

    # Emit CIEU event for Phase A
    event_type = "DISPATCH_BLOCKED_MISSING_PHASE_A" if not result["allow"] else "DISPATCH_PHASE_A_CHECK"
    emit_cieu(event_type, result)

    # Current mode: WARN only (not deny) per CZL-136 gradual rollout
    if not result["allow"]:
        # WARN mode: log violation but allow through
        print(json.dumps({
            "action": "allow",
            "message": f"[WARN] {result['reason']} (bitmap: {result['phase_bitmap']})"
        }))
        # Still continue to Y* pre-flight even if Phase A warn
        # (Phase A is warn-only; Y* pre-flight is deny-mode)

    # --- Gate 2: Y* pre-flight (Phase 1 cognitive-governance per Section 14.4-bis) ---
    preflight = _run_ystar_preflight(prompt_text)

    if preflight["preflight_ran"]:
        if preflight["passed"]:
            # Y* pre-flight PASS
            emit_cieu_ystar("Y_STAR_PREFLIGHT_PASS", preflight["result"])
            if result["allow"]:
                print(json.dumps({
                    "action": "allow",
                    "message": (
                        f"Phase A complete: {result['phase_bitmap']} | "
                        f"Y* pre-flight PASS: m_functor={preflight['result']['input']['m_functor']}"
                    ),
                }))
        else:
            # Y* pre-flight FAIL → DENY with recipe
            emit_cieu_ystar("Y_STAR_PREFLIGHT_FAIL", preflight["result"])
            suggestion = preflight["result"].get("suggestion", "")
            m_functor = preflight["result"]["input"]["m_functor"]
            kh = preflight["result"]["kh_check"]["recovered"]
            ag = preflight["result"]["ag_check"]["recovered"]
            print(json.dumps({
                "action": "deny",
                "message": (
                    f"Y* pre-flight FAIL: claimed m_functor={m_functor} "
                    f"inconsistent with KH={kh}, AG={ag}. "
                    f"{suggestion}"
                ),
            }))
            return 0
    else:
        # No Y* markers → normal Phase A result already printed above
        if result["allow"]:
            print(json.dumps({
                "action": "allow",
                "message": f"Phase A complete: {result['phase_bitmap']}",
            }))

    return 0


def emit_cieu(event_type: str, validation_result: dict):
    """Emit CIEU event to sqlite database (Phase A validation)."""
    try:
        import sqlite3
        import uuid as uuid_lib
        import time

        db_path = Path.home() / ".openclaw/workspace/ystar-company/.ystar_cieu.db"
        conn = sqlite3.connect(str(db_path), timeout=5.0)
        cursor = conn.cursor()

        event_id = str(uuid_lib.uuid4())
        now = time.time()
        seq_global = int(now * 1_000_000)

        cursor.execute("""
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, session_id, agent_id, event_type,
                decision, passed, violations, drift_detected
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            seq_global,
            now,
            "current",
            "hook_pretool_agent_dispatch",
            event_type,
            "allow" if validation_result["allow"] else "warn",
            1 if validation_result["allow"] else 0,
            json.dumps(validation_result["missing_steps"]),
            0
        ))

        conn.commit()
        conn.close()
    except Exception as e:
        # Fail-open for CIEU logging (don't block hook if DB error)
        sys.stderr.write(f"CIEU emit error: {e}\n")


def emit_cieu_ystar(event_type: str, self_check_result: dict):
    """Emit CIEU event for Y* pre-flight validation (Phase 1 cognitive-governance)."""
    try:
        import sqlite3
        import uuid as uuid_lib
        import time

        db_path = Path.home() / ".openclaw/workspace/ystar-company/.ystar_cieu.db"
        conn = sqlite3.connect(str(db_path), timeout=5.0)
        cursor = conn.cursor()

        event_id = str(uuid_lib.uuid4())
        now = time.time()
        seq_global = int(now * 1_000_000)

        verdict = self_check_result.get("overall_verdict", "FAIL")
        m_functor = self_check_result.get("input", {}).get("m_functor", "unknown")
        suggestion = self_check_result.get("suggestion", "")

        description = (
            f"Y* pre-flight {verdict}: m_functor={m_functor}, "
            f"KH={self_check_result.get('kh_check', {}).get('recovered', [])}, "
            f"AG={self_check_result.get('ag_check', {}).get('recovered', [])}"
        )

        violations_data = []
        if verdict == "FAIL":
            violations_data.append({
                "type": "m_functor_mismatch",
                "claimed": m_functor,
                "kh_recovered": self_check_result.get("kh_check", {}).get("recovered", []),
                "ag_recovered": self_check_result.get("ag_check", {}).get("recovered", []),
                "suggestion": suggestion,
            })

        cursor.execute("""
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, session_id, agent_id, event_type,
                decision, passed, violations, drift_detected,
                task_description, params_json, result_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            seq_global,
            now,
            "current",
            "hook_pretool_ystar_preflight",
            event_type,
            "allow" if verdict == "PASS" else "deny",
            1 if verdict == "PASS" else 0,
            json.dumps(violations_data),
            0,
            description,
            json.dumps({"m_functor": m_functor}),
            json.dumps(self_check_result),
        ))

        conn.commit()
        conn.close()
    except Exception as e:
        sys.stderr.write(f"CIEU Y* preflight emit error: {e}\n")


if __name__ == "__main__":
    sys.exit(main())
