#!/usr/bin/env python3
"""
K9 Event Trigger — Event-Driven Real-Time Audit Gateway
Board 2026-04-16 architecture transformation: K9 audit 从 cron polling 改 event-driven 实时督查.

Design:
  - Lightweight per-event violation scan (subset of k9_audit_v3 logic for performance)
  - Routing table: violation_type → target_module + action
  - Emits CIEU K9_AUDIT_TRIGGERED event with routing_target field
  - Emits K9_VIOLATION_DETECTED event when violations found
  - Called from PostToolUse hook chain (hook_prompt_gate.py)
  - Fail-open on all exceptions

Integration:
  hook_prompt_gate.py → k9_audit_on_event() → routing_target dispatch → ForgetGuard/StopHook/CZL
"""
import json
import os
import sys
import sqlite3
import time
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

REPO_ROOT = Path(__file__).parent.parent
CIEU_DB = REPO_ROOT / ".ystar_cieu.db"
ACTIVE_AGENT_PATH = REPO_ROOT / ".ystar_active_agent"
CANONICAL_REGISTRY_PATH = REPO_ROOT / "governance" / "agent_id_canonical.json"

# Y-star-gov path fix (Board 2026-04-16: PYTHONPATH resolution)
sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/Y-star-gov")

# ═══ VIOLATION ROUTING TABLE ═══
# Maps violation_type → (target_module, action)
# target_module: component responsible for handling this violation class
# action: "warn" (emit CIEU only) | "deny" (block via hook) | "escalate" (notify Board)

VIOLATION_ROUTING = {
    # CEO engineering boundary violations
    "ceo_engineering_boundary": ("forget_guard", "warn"),
    "ceo_direct_code_write": ("forget_guard", "warn"),

    # Sub-agent unauthorized operations
    "subagent_unauthorized_git_op": ("stop_hook_inject", "deny"),
    "subagent_scope_violation": ("stop_hook_inject", "warn"),

    # CZL protocol violations
    "dispatch_missing_5tuple": ("czl_protocol", "warn"),
    "receipt_missing_5tuple": ("czl_protocol", "warn"),
    "receipt_tool_use_mismatch": ("czl_protocol", "warn"),

    # Agent identity violations
    "agent_id_unidentified": ("agent_registry", "warn"),
    "agent_id_drift": ("agent_registry", "escalate"),

    # Governance component liveness
    "hook_chain_missing": ("hook_health", "escalate"),
    "forget_guard_stale": ("hook_health", "warn"),

    # 3D audit violations (Producer/Executor/Governed)
    "producer_executor_mismatch": ("three_dim_audit", "warn"),
    "governed_missing": ("three_dim_audit", "warn"),

    # ForgetGuard pattern violations
    "defer_language": ("forget_guard", "warn"),
# retired AMENDMENT-021 2026-04-20:     # "choice_question_to_board": ("forget_guard", "deny"),  # retired per AMENDMENT-021 2026-04-20
    "state_undefined_drift": ("stop_hook_inject", "warn"),
}


# ═══ HELPER FUNCTIONS ═══

def get_cieu_conn() -> sqlite3.Connection:
    """Return connection to CIEU database."""
    if not CIEU_DB.exists():
        # Fallback to gov-mcp/cieu.db
        fallback = Path.home() / ".openclaw" / "workspace" / "gov-mcp" / "cieu.db"
        if fallback.exists():
            return sqlite3.connect(str(fallback), timeout=2.0)
        raise FileNotFoundError(f"CIEU DB not found: {CIEU_DB}")
    return sqlite3.connect(str(CIEU_DB), timeout=2.0)


def get_active_agent() -> str:
    """Read current agent from .ystar_active_agent."""
    if not ACTIVE_AGENT_PATH.exists():
        return "system"
    agent_id = ACTIVE_AGENT_PATH.read_text().strip()
    return agent_id if agent_id else "system"


def load_canonical_registry() -> set:
    """Load canonical agent_id whitelist."""
    try:
        if not CANONICAL_REGISTRY_PATH.exists():
            return {"system", "ceo", "cto", "cmo", "cso", "cfo"}

        with open(CANONICAL_REGISTRY_PATH, 'r') as f:
            registry = json.load(f)
            canonical = set()
            if "roles" in registry:
                canonical.update(registry["roles"].keys())
            if "system_components" in registry:
                for component in registry["system_components"]:
                    canonical.add(f"system:{component}")
            canonical.add("system")
            return canonical
    except Exception:
        return {"system", "ceo", "cto", "cmo", "cso", "cfo"}


def emit_cieu_event(event_type: str, metadata: dict) -> None:
    """Emit CIEU event to database."""
    try:
        conn = get_cieu_conn()
        cursor = conn.cursor()

        # Get next seq_global
        cursor.execute("SELECT COALESCE(MAX(seq_global), 0) + 1 FROM cieu_events")
        seq_global = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, session_id, agent_id,
                event_type, decision, passed, task_description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                seq_global,
                time.time(),
                metadata.get("session_id", "k9_event"),
                metadata.get("agent_id", get_active_agent()),
                event_type,
                metadata.get("decision", "warn"),
                metadata.get("passed", 1),
                json.dumps(metadata, ensure_ascii=False)[:1000],
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        # Fail-open: log to stderr but don't crash
        print(f"[K9_EVENT] CIEU emit failed: {e}", file=sys.stderr)


# ═══ LIGHTWEIGHT VIOLATION CHECKS ═══

def check_agent_identity_violation(agent_id: str) -> Optional[str]:
    """Check if agent_id is in canonical registry."""
    canonical = load_canonical_registry()
    if agent_id not in canonical and agent_id not in ["unidentified", "unknown"]:
        return "agent_id_unidentified"
    return None


def check_ceo_engineering_boundary(agent_id: str, event_type: str, payload: dict) -> Optional[str]:
    """Check if CEO is writing code directly (violates AGENTS.md charter)."""
    if agent_id != "ceo":
        return None

    # Only check Edit/Write/MultiEdit tools (not Read/Grep/Bash)
    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Edit", "Write", "MultiEdit"):
        return None

    # CEO should NOT directly Edit/Write to src/, ystar/, tests/ (engineering scope)
    # Exception: .claude/tasks/ (task assignment is CEO's job)
    file_path = payload.get("file_path", "")
    if not file_path:
        return None

    engineering_scopes = ["src/", "ystar/", "tests/", "Y-star-gov/"]
    task_scope = ".claude/tasks/"

    if any(scope in file_path for scope in engineering_scopes):
        if task_scope not in file_path:
            return "ceo_engineering_boundary"

    return None


def check_dispatch_5tuple(event_type: str, payload: dict) -> Optional[str]:
    """Check if CTO dispatch contains required 5-tuple (Y*/Xt/U/Yt+1/Rt+1)."""
    # Only check events that are dispatch-like
    if event_type not in ["SUBAGENT_DISPATCH", "TASK_ASSIGNED", "CTO_DISPATCH"]:
        return None

    task_description = payload.get("task_description", "")
    if not task_description:
        return None

    # Quick check: all 5 markers present
    required_markers = ["Y*", "Xt", "U", "Yt+1", "Rt+1"]
    missing = [m for m in required_markers if m not in task_description]

    if len(missing) >= 2:  # Allow 1 typo/variation, but 2+ missing = violation
        return "dispatch_missing_5tuple"

    return None


def check_hook_liveness() -> Optional[str]:
    """Check if hook chain has fired recently (10min window)."""
    try:
        conn = get_cieu_conn()
        cursor = conn.cursor()

        cutoff = datetime.now() - timedelta(seconds=600)
        cutoff_str = cutoff.isoformat()

        cursor.execute(
            """
            SELECT COUNT(*) FROM cieu_events
            WHERE event_type IN ('HOOK_PRE_CALL', 'HOOK_POST_CALL')
            AND created_at >= ?
            """,
            (cutoff_str,),
        )
        count = cursor.fetchone()[0]
        conn.close()

        if count == 0:
            return "hook_chain_missing"
    except Exception:
        pass  # fail-open

    return None


def check_3d_role_integrity(agent_id: str, event_type: str, payload: dict) -> Optional[str]:
    """
    Check 3D audit compliance: Producer/Executor/Governed roles match.

    E.g., if agent_id="ceo" but event_type="CODE_COMMITTED", producer/executor mismatch
    (CEO should dispatch to CTO, not commit code directly).
    """
    # Producer = who initiated (agent_id)
    # Executor = who performed (tool_use metadata)
    # Governed = who was subject to governance (payload governed_agent_id)

    # Map event_type → expected producer role
    expected_producer = {
        "CODE_COMMITTED": ["cto", "eng-kernel", "eng-governance", "eng-platform", "eng-domains"],
        "MARKETING_CONTENT_PUBLISHED": ["cmo"],
        "SALES_OUTREACH_SENT": ["cso"],
        "FINANCIAL_MODEL_UPDATED": ["cfo"],
    }

    for event_pattern, allowed_roles in expected_producer.items():
        if event_pattern in event_type:
            if agent_id not in allowed_roles:
                return "producer_executor_mismatch"

    return None


# ═══ MAIN AUDIT ENTRY POINT ═══

def k9_audit_on_event(
    event_type: str,
    agent_id: str,
    payload: dict,
    file_path: Optional[str] = None
) -> dict:
    """
    Run lightweight K9 audit on a single event.

    Args:
        event_type: Event type (e.g., "TOOL_USE_BASH", "SUBAGENT_DISPATCH")
        agent_id: Agent ID who triggered the event
        payload: Event payload dict (from hook stdin or CIEU event)
        file_path: Optional file path for Edit/Write events

    Returns:
        dict: {
            "violations": List[str],  # violation_type strings
            "routing_targets": List[tuple],  # (target_module, action)
            "metadata": dict  # for CIEU event
        }
    """
    violations = []
    routing_targets = []

    # Add file_path to payload if provided
    if file_path:
        payload["file_path"] = file_path

    # Run lightweight checks (fast, subset of k9_audit_v3)
    checks = [
        check_agent_identity_violation(agent_id),
        check_ceo_engineering_boundary(agent_id, event_type, payload),
        check_dispatch_5tuple(event_type, payload),
        check_hook_liveness(),
        check_3d_role_integrity(agent_id, event_type, payload),
    ]

    for violation_type in checks:
        if violation_type:
            violations.append(violation_type)
            # Lookup routing target
            if violation_type in VIOLATION_ROUTING:
                target_module, action = VIOLATION_ROUTING[violation_type]
                routing_targets.append((target_module, action))

    # Emit K9_AUDIT_TRIGGERED event
    metadata = {
        "event_type": event_type,
        "agent_id": agent_id,
        "violations_found": len(violations),
        "violations": violations,
        "routing_targets": [f"{t[0]}:{t[1]}" for t in routing_targets],
        "session_id": "k9_event",
    }

    emit_cieu_event("K9_AUDIT_TRIGGERED", metadata)

    # Emit K9_VIOLATION_DETECTED for each violation
    for violation_type in violations:
        violation_meta = {
            "violation_type": violation_type,
            "agent_id": agent_id,
            "event_type": event_type,
            "routing_target": VIOLATION_ROUTING.get(violation_type, ("unknown", "warn"))[0],
            "action": VIOLATION_ROUTING.get(violation_type, ("unknown", "warn"))[1],
        }
        emit_cieu_event("K9_VIOLATION_DETECTED", violation_meta)

    return {
        "violations": violations,
        "routing_targets": routing_targets,
        "metadata": metadata,
    }


# ═══ STANDALONE CLI (for testing) ═══

def main():
    """CLI entry point for manual testing."""
    if len(sys.argv) < 3:
        print("Usage: k9_event_trigger.py <event_type> <agent_id> [payload_json]")
        sys.exit(1)

    event_type = sys.argv[1]
    agent_id = sys.argv[2]
    payload = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}

    result = k9_audit_on_event(event_type, agent_id, payload)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
