#!/usr/bin/env python3
"""
CIEU Emit Helpers — F2 emit-side agent_id enforcement
All CIEU emit points MUST import emit_cieu() or _get_canonical_agent().
Never hardcode agent_id to 'agent'/'unknown'/''.
"""
import json
import sqlite3
import sys
import time
import uuid
from pathlib import Path
from typing import Optional

ACTIVE_AGENT_PATH = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_active_agent")
CANONICAL_REGISTRY_PATH = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/governance/agent_id_canonical.json")
CIEU_DB_PATH = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db")


def _load_canonical_registry() -> set[str]:
    """Load canonical agent_id whitelist from registry."""
    try:
        if not CANONICAL_REGISTRY_PATH.exists():
            return {"system"}

        with open(CANONICAL_REGISTRY_PATH, 'r') as f:
            registry = json.load(f)

            # Extract canonical roles from registry structure
            canonical = set()

            # Add primary roles
            if "roles" in registry:
                canonical.update(registry["roles"].keys())

            # Add system components (prefixed)
            if "system_components" in registry:
                for component in registry["system_components"]:
                    canonical.add(f"system:{component}")

            # Add "system" as fallback
            canonical.add("system")

            return canonical
    except Exception:
        return {"system"}


def _get_current_agent() -> str:
    """
    Read current agent identity from .ystar_active_agent.
    NEVER fallback to "unknown" — if file missing/empty, return "system".

    Returns:
        str: Active agent ID (e.g., "Marco-CFO", "ceo", "eng-governance")
    """
    if not ACTIVE_AGENT_PATH.exists():
        return "system"

    agent_id = ACTIVE_AGENT_PATH.read_text().strip()
    return agent_id if agent_id else "system"


def _get_canonical_agent() -> str:
    """
    Get current agent_id with canonical validation.
    If agent_id not in canonical registry → return 'unidentified' + emit warning.

    Returns:
        str: Canonical agent_id or 'unidentified'
    """
    agent_id = _get_current_agent()
    canonical_roles = _load_canonical_registry()

    if agent_id in canonical_roles:
        return agent_id

    # Not canonical → emit AGENT_ID_UNIDENTIFIED_EMIT warning
    try:
        _emit_unidentified_warning(agent_id, caller_context=_get_caller_context())
    except Exception:
        pass  # Fail-open

    return "unidentified"


def _get_caller_context() -> dict:
    """Extract caller script path + line for debugging."""
    import traceback
    stack = traceback.extract_stack()
    if len(stack) >= 3:
        caller = stack[-3]
        return {
            "script": caller.filename,
            "line": caller.lineno,
            "function": caller.name
        }
    return {}


def _emit_unidentified_warning(agent_id: str, caller_context: dict):
    """Emit AGENT_ID_UNIDENTIFIED_EMIT warning to CIEU."""
    try:
        conn = sqlite3.connect(str(CIEU_DB_PATH))
        cursor = conn.cursor()

        event_id = str(uuid.uuid4())
        seq_global = int(time.time() * 1_000_000)

        cursor.execute("""
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, session_id, agent_id,
                event_type, decision, passed, task_description, params_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            seq_global,
            time.time(),
            "emit_helper",
            "system",  # Meta-event uses system
            "AGENT_ID_UNIDENTIFIED_EMIT",
            "warn",
            0,  # Failed validation
            f"Agent '{agent_id}' not in canonical registry",
            json.dumps(caller_context)
        ))

        conn.commit()
        conn.close()

        # Also log to stderr
        sys.stderr.write(f"[AGENT_ID_UNIDENTIFIED_EMIT] agent='{agent_id}' caller={caller_context.get('script', 'unknown')}\n")

    except Exception as e:
        # Fail-open
        sys.stderr.write(f"[AGENT_ID_UNIDENTIFIED_EMIT] failed to emit: {e}\n")


def emit_rt_measurement(
    task_id: str,
    y_star: str,
    xt: str,
    u: list,
    yt_plus_1: str,
    rt_plus_1: float,
    producer: str = "",
    executor: str = ""
) -> bool:
    """
    Emit RT_MEASUREMENT event to production CIEU DB (events table).

    Args:
        task_id: Unique task identifier
        y_star: Y* ideal predicate
        xt: Current state
        u: Action sequence
        yt_plus_1: Predicted end state
        rt_plus_1: Residual gap (0.0 = clean closure)
        producer: Producer agent (e.g., "ceo", "cto")
        executor: Executor agent (e.g., "eng-platform")

    Returns:
        bool: True if emission succeeded, False otherwise
    """
    try:
        conn = sqlite3.connect(str(CIEU_DB_PATH))
        cursor = conn.cursor()

        agent_id = _get_canonical_agent()
        timestamp = time.time()

        metadata = {
            "task_id": task_id,
            "y_star": y_star,
            "xt": xt,
            "u": u,
            "yt_plus_1": yt_plus_1,
            "rt_plus_1": rt_plus_1,
            "producer": producer or agent_id,
            "executor": executor or agent_id,
            "timestamp": timestamp
        }

        cursor.execute(
            """
            INSERT INTO events (timestamp, event_type, agent, metadata)
            VALUES (?, ?, ?, ?)
            """,
            (timestamp, "RT_MEASUREMENT", agent_id, json.dumps(metadata))
        )

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        sys.stderr.write(f"[RT_MEASUREMENT] emit failed: {e}\n")
        return False


def emit_cieu(
    event_type: str,
    decision: str = "info",
    passed: int = 1,
    task_description: str = "",
    **kwargs
) -> bool:
    """
    Central CIEU event emitter with canonical agent_id validation.

    Args:
        event_type: CIEU event type (e.g., "SESSION_HEALTH_CHECK")
        decision: Decision type ("allow"/"deny"/"warn"/"info")
        passed: 1=passed, 0=failed
        task_description: Human-readable description
        **kwargs: Additional fields (params_json, drift_details, etc.)

    Returns:
        bool: True if emission succeeded, False otherwise (fail-open)
    """
    try:
        conn = sqlite3.connect(str(CIEU_DB_PATH))
        cursor = conn.cursor()

        event_id = str(uuid.uuid4())
        seq_global = int(time.time() * 1_000_000)
        agent_id = _get_canonical_agent()

        # Build column list + values dynamically based on kwargs
        columns = [
            "event_id", "seq_global", "created_at", "session_id",
            "agent_id", "event_type", "decision", "passed", "task_description"
        ]
        values = [
            event_id,
            seq_global,
            time.time(),
            kwargs.get("session_id", "emit_helper"),
            agent_id,
            event_type,
            decision,
            passed,
            task_description
        ]

        # Add optional fields if present
        optional_fields = [
            "params_json", "drift_detected", "drift_details", "drift_category",
            "file_path", "command", "evidence_grade"
        ]
        for field in optional_fields:
            if field in kwargs:
                columns.append(field)
                values.append(kwargs[field])

        placeholders = ", ".join(["?"] * len(columns))
        columns_str = ", ".join(columns)

        cursor.execute(
            f"INSERT INTO cieu_events ({columns_str}) VALUES ({placeholders})",
            values
        )

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        # Fail-open
        sys.stderr.write(f"[CIEU_EMIT_ERROR] {event_type}: {e}\n")
        return False
