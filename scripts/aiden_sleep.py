#!/usr/bin/env python3
"""
Aiden Sleep — Session close consolidation.

Like biological sleep: consolidate short-term → long-term, then clear short-term.

1. Verify this session's insights are in brain (nodes exist)
2. Apply Hebbian decay (forget unused connections)
3. Write FRESH handoff (overwrite, not append)
4. Report consolidation stats

Usage:
    aiden_sleep.py "one-line summary of what this session was about"
"""

import os
import sys
import time
import json

sys.path.insert(0, os.path.dirname(__file__))
from aiden_brain import get_db, apply_decay, stats, DB_PATH

COMPANY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def consolidation_check(db_path: str = DB_PATH) -> dict:
    """Check what's in the brain from this session (created recently)."""
    conn = get_db(db_path)
    now = time.time()
    one_hour_ago = now - 3600

    recent_nodes = conn.execute(
        "SELECT id, name FROM nodes WHERE created_at > ?",
        (one_hour_ago,)).fetchall()

    recent_hebbian = conn.execute(
        "SELECT source_id, target_id, weight FROM edges "
        "WHERE edge_type='hebbian' AND updated_at > ?",
        (one_hour_ago,)).fetchall()

    total_stats = stats(db_path)
    conn.close()

    return {
        "recent_nodes": [(r["id"], r["name"]) for r in recent_nodes],
        "recent_hebbian": len(recent_hebbian),
        "total": total_stats,
    }


def sleep_cycle(session_summary: str = "", decay_rate: float = 0.005,
                db_path: str = DB_PATH):
    """Full sleep cycle: consolidate → decay → report."""

    print("=== Aiden Sleep Cycle ===\n")

    # Phase 1: Check consolidation
    print("Phase 1: Consolidation check...")
    report = consolidation_check(db_path)
    print(f"  This session added {len(report['recent_nodes'])} nodes to long-term memory")
    for nid, name in report["recent_nodes"]:
        print(f"    + {name[:60]}")
    print(f"  {report['recent_hebbian']} Hebbian connections strengthened")
    print(f"  Brain total: {report['total']['nodes']}n / "
          f"{report['total']['edges']}e / {report['total']['hebbian_edges']}h")

    # Phase 2: Decay (forgetting curve)
    print(f"\nPhase 2: Hebbian decay (rate={decay_rate})...")
    apply_decay(decay_rate, db_path)
    post_stats = stats(db_path)
    print(f"  Post-decay: avg_weight={post_stats['avg_weight']}")

    # Phase 3: Summarize for wake-up
    print(f"\nPhase 3: Sleep summary")
    print(f"  Session: {session_summary or '(no summary)'}")
    print(f"  Consolidated: {len(report['recent_nodes'])} insights → long-term memory")
    print(f"  Decayed: unused Hebbian edges weakened by {decay_rate}")
    print(f"  Brain health: {post_stats['nodes']}n / {post_stats['edges']}e")
    print(f"\n  Next wake-up: run `aiden_recall.py --boot`")
    print("  Brain will activate from long-term memory, not from old handoffs.\n")

    return report


if __name__ == "__main__":
    summary = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    sleep_cycle(summary)
