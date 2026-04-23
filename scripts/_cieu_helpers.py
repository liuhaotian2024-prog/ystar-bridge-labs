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
from typing import Optional, Tuple

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


def _infer_m_functor(event_type: str, task_description: str = "", file_path: str = "", command: str = "") -> Tuple[Optional[str], Optional[float]]:
    """Infer (m_functor, m_weight) from event_type prefix + context.
    Explicit caller-supplied m_functor ALWAYS wins (this is fallback only).
    """
    et = (event_type or "").upper()
    td = (task_description or "").lower() + " " + (file_path or "").lower() + " " + (command or "").lower()

    # M-1 Survivability: session / identity / restart / brain / dream / handoff / seal / backup
    if any(k in et for k in ['SESSION_SEALED', 'BACKFILL_MERKLE', 'SESSION_SEAL', 'BRAIN_DREAM', 'BRAIN_AUTO', 'HANDOFF', 'SESSION_CLOSE', 'CIEU_TO_BRAIN']):
        return 'M-1', 0.7
    if any(k in td for k in ['session close', 'brain', 'handoff', 'merkle', 'seal', 'backup', 'restart']):
        return 'M-1', 0.5

    # M-2a Commission: forget_guard / boundary / router / iron rule / enforce / deny / block
    if any(k in et for k in ['FORGET_GUARD', 'BOUNDARY', 'ROUTER', 'K9_ROUTING', 'VIOLATION_DETECTED', 'DENY', 'BLOCK', 'PRETOOL', 'HOOK', 'INTERVENTION_GATE']):
        return 'M-2a', 0.8

    # M-2b Omission: tracked / overdue / P0 / alarm / timeout / escalate / scan
    if any(k in et for k in ['OMISSION', 'OVERDUE', 'OBLIGATION', 'ESCALATE', 'ALARM', 'TIMEOUT', 'COVERAGE_SCAN', 'HOOK_HEALTH']):
        return 'M-2b', 0.8

    # M-3 Value: customer / revenue / demo / pipeline / product / ship / whitepaper / sale
    if any(k in et for k in ['SHIPPED', 'LANDED', 'DEPLOY', 'RELEASE']):
        return 'M-3', 0.6
    if any(k in td for k in ['customer', 'revenue', 'demo', 'pipeline', 'whitepaper', 'sale', 'enterprise']):
        return 'M-3', 0.7

    # Governance infra (M-2a by default)
    if any(k in et for k in ['GOVERNANCE', 'WAVE2', 'WAVE_', 'VALIDATOR', 'AUDIT', 'RECEIPT']):
        return 'M-2a', 0.5

    # Unknown — skip (let later taggers fix)
    return None, None


def emit_cieu(
    event_type: str,
    decision: str = "info",
    passed: int = 1,
    task_description: str = "",
    m_functor: Optional[str] = None,
    m_weight: Optional[float] = None,
    **kwargs
) -> Optional[str]:
    """
    Central CIEU event emitter with canonical agent_id validation.

    Args:
        event_type: CIEU event type (e.g., "SESSION_HEALTH_CHECK")
        decision: Decision type ("allow"/"deny"/"warn"/"info")
        passed: 1=passed, 0=failed
        task_description: Human-readable description
        m_functor: M-triangle functor tag (e.g., "M-1", "M-2a", "M-3")
        m_weight: Weight/priority of this event's M-triangle contribution (0.0-1.0)
        **kwargs: Additional fields (params_json, drift_details, etc.)

    Returns:
        str: event_id if emission succeeded, None otherwise (fail-open)
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

        # Infer m_functor/m_weight when caller did not supply them
        if m_functor is None:
            inferred_f, inferred_w = _infer_m_functor(event_type=event_type, task_description=task_description, file_path=kwargs.get("file_path", ""), command=kwargs.get("command", ""))
            m_functor = inferred_f
            if m_weight is None:
                m_weight = inferred_w

        # Add M-triangle fields if provided
        if m_functor is not None:
            columns.append("m_functor")
            values.append(m_functor)
        if m_weight is not None:
            columns.append("m_weight")
            values.append(m_weight)

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
        return event_id

    except Exception as e:
        # Fail-open
        sys.stderr.write(f"[CIEU_EMIT_ERROR] {event_type}: {e}\n")
        return None
