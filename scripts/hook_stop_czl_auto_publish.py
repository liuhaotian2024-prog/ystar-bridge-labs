#!/usr/bin/env python3
"""
Stop hook: auto-extract CEO reply commitments and publish to CZL bus.

Milestone 10 (2026-04-21): close "CEO reply 口头派 task 绕过 CZL bus" gap
Board caught at 20:55. Before this: if CEO says "派 Leo 做 X" / "下 reply 开
Milestone Y" / "Milestone N = Z" in a reply, the commitment never landed on
.czl_bus.jsonl, so omission_subscriber never saw it, forget_guard never saw
it, and CEO could silently forget (exactly the "你又被自己骗了" pattern).

Fix (this hook): on every Claude Code Stop event, scan the reply text via
parent_session_commitment_tracker.extract_commitments, auto-generate a
CZLMessageEnvelope per extracted commitment (message_type="reply_commitment"),
publish to czl_bus. Downstream forget_guard_subscribe + omission_subscribe
see it in the next scan.

Runtime wire (Ryan P0 CZL-UNIFIED-BUS-RUNTIME-WIRE): add this script to
.claude/settings.json Stop hooks. POC here is standalone-testable.

M-tag: M-2a (CEO reply 的 dispatch/承诺 走同一治理入口, 无绕过) +
       M-2b (承诺结构级追踪, 不靠 CEO 自觉).
"""
import json
import os
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from parent_session_commitment_tracker import extract_commitments  # noqa: E402
from czl_bus import CZLMessageEnvelope, publish as czl_publish  # noqa: E402


def commitment_to_envelope(commitment: dict,
                           session_id: str = "unknown",
                           reply_id: str = "unknown") -> CZLMessageEnvelope:
    """Convert extracted commitment dict → CZLMessageEnvelope (reply_commitment type)."""
    statement = commitment.get("statement", "")
    ctype = commitment.get("commitment_type", "unknown")
    deadline = commitment.get("deadline", time.time() + 600)
    created_at = commitment.get("created_at", time.time())

    # Map commitment_type → urgency for omission subscriber deadline priority
    urgency_map = {
        "next_reply_commitment": "P0",       # 10 min - fast-expiring
        "immediate_action": "P0",            # 5 min
        "pilot_then_scale": "P1",            # 30 min
        "milestone_scope_declaration": "P1",
        "convergence_claim": "P0",           # 1 min verify window
    }
    urgency = urgency_map.get(ctype, "P2")

    task_id = f"CEO-COMMIT-{int(created_at * 1000)}-{abs(hash(statement)) & 0xfff:03x}"
    env = CZLMessageEnvelope(
        y_star=f"CEO commitment: {statement[:150]}",
        x_t=f"committed at reply ts={created_at}, type={ctype}",
        u=[statement],  # single-step action is the statement itself
        y_t_plus_1=f"commitment {ctype} delivered (matched receipt with Rt+1=0)",
        rt_value=1.0,  # open until matching receipt
        task_id=task_id,
        sender="ceo",
        recipient="ceo_self_commit_track",
        message_type="reply_commitment",
        deadline=deadline,
        urgency=urgency,
        role_tags={
            "producer": "ceo",
            "executor": "ceo",
            "governed": "omission_subscriber+forget_guard_subscriber",
            "commitment_type": ctype,
        },
    )
    return env


def process_reply_text(reply_text: str,
                       session_id: str = "unknown",
                       reply_id: str = "unknown",
                       bus_path: Path = None) -> list:
    """Main entry: extract commitments + publish envelopes. Return published message_ids."""
    commitments = extract_commitments(reply_text)
    published = []
    for c in commitments:
        env = commitment_to_envelope(c, session_id=session_id, reply_id=reply_id)
        mid = czl_publish(env, bus_path=bus_path)
        published.append({
            "message_id": mid,
            "task_id": env.task_id,
            "commitment_type": c["commitment_type"],
            "statement": c["statement"][:80],
            "urgency": env.urgency,
        })
    return published


def main():
    """Hook entry: read Stop event payload from stdin, extract + publish."""
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}

    # Stop hook payload has reply text in "reply" or "content" or "output"
    reply_text = (
        payload.get("reply", "")
        or payload.get("content", "")
        or payload.get("output", "")
        or raw
    )
    session_id = payload.get("session_id", os.environ.get("CLAUDE_SESSION_ID", "unknown"))
    reply_id = payload.get("reply_id", f"reply_{int(time.time())}")

    if not reply_text:
        # nothing to scan — hook is no-op
        return 0

    published = process_reply_text(reply_text, session_id=session_id, reply_id=reply_id)

    # Log to stderr for hook debugging (Stop hook output is not captured by Claude)
    if published:
        print(f"[hook_stop_czl_auto_publish] published {len(published)} commitment envelopes",
              file=sys.stderr)
        for p in published[:5]:
            print(f"  - {p['task_id']} | {p['commitment_type']} | {p['statement']}",
                  file=sys.stderr)

    # CIEU event 记录 (CEO self-commit tracker LIVE)
    try:
        import sqlite3
        cieu_db = "/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db"
        conn = sqlite3.connect(cieu_db)
        conn.execute("""
            INSERT INTO cieu_events (event_id, seq_global, created_at, event_type,
                                     agent_id, result_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            f"stop_hook_{int(time.time() * 1_000_000)}",
            int(time.time() * 1_000_000),
            time.time(),
            "CEO_REPLY_COMMITMENTS_EXTRACTED",
            "ceo",
            json.dumps({"count": len(published), "items": published[:10]}),
        ))
        conn.commit()
        conn.close()
    except Exception:
        pass  # non-fatal

    return 0


if __name__ == "__main__":
    sys.exit(main())
