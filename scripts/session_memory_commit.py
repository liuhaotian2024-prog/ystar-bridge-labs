#!/usr/bin/env python3
"""Session memory commit — scan session CIEU, persist important events to YML."""
import os, sys, json, sqlite3, time
from pathlib import Path

WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
Y_STAR_GOV = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
sys.path.insert(0, str(Y_STAR_GOV))

from ystar.memory.store import MemoryStore
from ystar.memory.models import Memory

IMPORTANT_EVENT_TYPES = [
    "MATURITY_TRANSITION",
    "WHITELIST_DRIFT",
    "FORGET_GUARD",
    "DEFER_IN_COMMIT_DRIFT",
    "ARTICLE_11_LAYER_%_COMPLETE",
    "CROBA_CONTRACT_INJECT",
    "BREAK_GLASS_CLAIM",
    "LESSON_CAPTURE_DUE",
]

def main(session_id: str, agent_id: str = "ceo"):
    cieu_db = WORKSPACE / ".ystar_cieu.db"
    memory_db = WORKSPACE / ".ystar_memory.db"

    cieu = sqlite3.connect(str(cieu_db))
    memory = MemoryStore(db_path=str(memory_db))

    # Scan session events
    cur = cieu.cursor()
    placeholder = " OR ".join(f"event_type LIKE '{t}'" for t in IMPORTANT_EVENT_TYPES)
    cur.execute(f"SELECT event_type, created_at, decision, violations, drift_details FROM cieu_events WHERE session_id=? AND ({placeholder}) ORDER BY created_at DESC LIMIT 200", (session_id,))

    count = 0
    for row in cur.fetchall():
        event_type, created_at, decision, violations, drift_details = row
        summary = f"[{event_type}] dec={decision} violations={violations[:200] if violations else ''}"
        mem = Memory(
            agent_id=agent_id,
            memory_type="lesson",
            content=summary,
            initial_score=1.0,
            source_cieu_ref=f"cieu:{event_type}:{created_at}"
        )
        memory.remember(mem)
        count += 1

    print(f"[session_memory_commit] Committed {count} important events to YML for {agent_id}")
    return 0

if __name__ == "__main__":
    session_id = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CLAUDE_SESSION_ID", "unknown")
    agent_id = sys.argv[2] if len(sys.argv) > 2 else "ceo"
    sys.exit(main(session_id, agent_id))
