#!/usr/bin/env python3
"""Session memory boot — load top-N YML memory events into boot pack on session start."""
import os, sys, json, sqlite3
from pathlib import Path

WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
Y_STAR_GOV = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
sys.path.insert(0, str(Y_STAR_GOV))

from ystar.memory.store import MemoryStore  # 顾问 verified 存在

def main(agent_id: str, top_n: int = 20):
    memory_db = WORKSPACE / ".ystar_memory.db"
    store = MemoryStore(db_path=str(memory_db))

    # Clean up bad timestamps (defensive - fail-open)
    import time
    now = time.time()
    with store._conn() as conn:
        conn.execute("DELETE FROM memories WHERE created_at > ? OR created_at < 1000000000", (now + 86400,))
        conn.commit()

    # Recall top-N memory events for this agent, ordered by relevance (decay-aware)
    try:
        events = store.recall(agent_id=agent_id, limit=top_n, sort_by="relevance_desc", min_relevance=0.0)
    except (OverflowError, ValueError) as e:
        print(f"[session_memory_boot] Warning: recall failed ({e}), returning empty")
        events = []

    # Write to boot_pack as Category 0.5 "yml_memory_recall"
    boot_pack_path = WORKSPACE / f"memory/boot_packages/{agent_id}.json"
    if boot_pack_path.exists():
        with open(boot_pack_path) as f:
            pack = json.load(f)
    else:
        pack = {}

    pack["category_0_5_yml_memory_recall"] = {
        "generated_at": __import__("time").time(),
        "agent_id": agent_id,
        "top_n": top_n,
        "events": [{"id": e.memory_id, "content": e.content, "initial_score": e.initial_score, "created_at": e.created_at, "type": e.memory_type} for e in events]
    }

    with open(boot_pack_path, "w") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)

    print(f"[session_memory_boot] Loaded {len(events)} top memories for {agent_id}")
    return 0

if __name__ == "__main__":
    agent_id = sys.argv[1] if len(sys.argv) > 1 else "ceo"
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    sys.exit(main(agent_id, top_n))
