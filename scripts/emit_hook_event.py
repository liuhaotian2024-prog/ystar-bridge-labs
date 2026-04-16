#!/usr/bin/env python3.11
"""emit_hook_event.py — HOOK_PRE_CALL / HOOK_POST_CALL CIEU emitter (k9_audit_v3 canonical events)."""
import sys, time, uuid
from ystar.governance.cieu_store import CIEUStore

if __name__ == "__main__":
    event_type = sys.argv[1] if len(sys.argv) > 1 else "HOOK_PRE_CALL"
    params = {"hook": "PreToolUse"}
    if len(sys.argv) > 2:
        params["daemon_path"] = sys.argv[2]
    if len(sys.argv) > 3:
        params["guard_action"] = sys.argv[3]

    c = CIEUStore(".ystar_cieu.db")
    c.write_dict({
        "event_id": str(uuid.uuid4()),
        "session_id": "hook_chain",
        "agent_id": "governance",
        "event_type": event_type,
        "decision": "info",
        "evidence_grade": "ops",
        "created_at": time.time(),
        "seq_global": time.time_ns() // 1000,
        "params": params,
        "violations": [],
        "drift_detected": False,
        "human_initiator": "system",
    })
