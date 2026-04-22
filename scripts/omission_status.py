#!/usr/bin/env python3
"""Inspect OmissionEngine status for a given agent — close path + Board visibility.

Usage:
  python3.11 omission_status.py --agent ceo
  python3.11 omission_status.py --agent all --overdue-only
  python3.11 omission_status.py --close <obligation_id> --reason "explanation"
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
import time
import uuid
from pathlib import Path

WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
OMISSION_DB = WORKSPACE / ".ystar_cieu_omission.db"


def list_obligations(agent: str = "all", overdue_only: bool = False) -> None:
    if not OMISSION_DB.exists():
        print("[omission_status] DB not found")
        return
    conn = sqlite3.connect(str(OMISSION_DB), timeout=5)
    now = time.time()
    clauses = ["status = 'pending'"]
    params = []
    if agent != "all":
        clauses.append("actor_id = ?")
        params.append(agent)
    if overdue_only:
        clauses.append("(due_at + COALESCE(hard_overdue_secs, 0)) < ?")
        params.append(now)
    q = f"""
        SELECT obligation_id, actor_id, obligation_type, due_at, hard_overdue_secs, notes
        FROM obligations WHERE {' AND '.join(clauses)}
        ORDER BY due_at ASC LIMIT 30
    """
    rows = conn.execute(q, params).fetchall()

    if not rows:
        print(f"[omission_status] no pending obligations for agent={agent} overdue_only={overdue_only}")
        return

    print(f"[omission_status] {len(rows)} pending obligation(s) for agent={agent}:")
    for obl_id, actor, otype, due_at, hard_overdue, notes in rows:
        age_sec = now - (due_at + (hard_overdue or 0))
        status = "OVERDUE" if age_sec > 0 else "pending"
        age_min = int(abs(age_sec) / 60)
        print(f"  [{status}] {obl_id[:8]}... actor={actor} type={otype} "
              f"{'+' if age_sec > 0 else '-'}{age_min}min notes={(notes or '')[:60]}")
    conn.close()


def close_obligation(obl_id: str, reason: str) -> int:
    if not OMISSION_DB.exists():
        print("[omission_status] DB not found")
        return 1
    conn = sqlite3.connect(str(OMISSION_DB), timeout=5)
    # Mark as fulfilled with explicit reason
    conn.execute(
        "UPDATE obligations SET status = 'fulfilled', updated_at = ?, notes = ? "
        "WHERE obligation_id = ?",
        (time.time(), f"manually_closed: {reason}", obl_id)
    )
    changed = conn.total_changes
    conn.commit()
    conn.close()
    if changed:
        print(f"[omission_status] closed obligation {obl_id} — reason: {reason}")
        return 0
    print(f"[omission_status] obligation {obl_id} not found")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", default="all")
    ap.add_argument("--overdue-only", action="store_true")
    ap.add_argument("--close", help="obligation_id to close")
    ap.add_argument("--reason", default="manually_closed_via_cli")
    args = ap.parse_args()

    if args.close:
        return close_obligation(args.close, args.reason)

    list_obligations(args.agent, args.overdue_only)
    return 0


if __name__ == "__main__":
    sys.exit(main())
