#!/usr/bin/env python3
"""
Brain Dream Approve — Human review helper for L3 dream diffs.

Emits BRAIN_DREAM_DIFF_REVIEWED CIEU event after Board/CEO reviews a diff.
This is the manual gate that must be passed before --commit can apply changes.

Usage:
    python3.11 scripts/brain_dream_approve.py --diff <path>
    python3.11 scripts/brain_dream_approve.py --latest

Examples:
    # Approve the latest diff
    python3.11 scripts/brain_dream_approve.py --latest

    # Approve a specific diff
    python3.11 scripts/brain_dream_approve.py --diff reports/ceo/brain_dream_diffs/dream_diff_20260419_234500.md
"""

import os
import sys
import json
import glob
import sqlite3
from datetime import datetime
from pathlib import Path

COMPANY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIFF_DIR = os.path.join(COMPANY_ROOT, "reports", "ceo", "brain_dream_diffs")
CIEU_DB = os.path.join(COMPANY_ROOT, ".ystar_cieu.db")


def _emit_cieu(event_type: str, data: dict, cieu_db: str = None):
    """Emit a CIEU event to the database."""
    db_path = cieu_db or CIEU_DB
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        import uuid
        event_id = str(uuid.uuid4())
        seq_global = int(datetime.now().timestamp() * 1_000_000)
        cursor.execute("""
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, session_id, agent_id,
                event_type, decision, passed, params_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            seq_global,
            datetime.now().timestamp(),
            "board-approve-session",
            data.get("agent_id", "board"),
            event_type,
            "info",
            1,
            json.dumps({
                "action": data.get("action", "review"),
                "context": data.get("context", {}),
                "intent": data.get("intent", ""),
                "result": data.get("result", ""),
            })
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"ERROR: CIEU emit failed: {e}", file=sys.stderr)
        return False


def find_latest_diff() -> str:
    """Find the most recent diff file."""
    if not os.path.isdir(DIFF_DIR):
        return None
    files = sorted(glob.glob(os.path.join(DIFF_DIR, "dream_diff_*.md")))
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def approve_diff(diff_path: str, cieu_db: str = None):
    """Approve a diff file by emitting BRAIN_DREAM_DIFF_REVIEWED event."""
    if not os.path.exists(diff_path):
        print(f"ERROR: Diff file not found: {diff_path}")
        return False

    # Display the diff for human review
    print("=" * 60)
    print("  BRAIN DREAM DIFF REVIEW")
    print("=" * 60)
    print(f"\nDiff file: {diff_path}")
    print(f"File mtime: {datetime.fromtimestamp(os.path.getmtime(diff_path)).isoformat()}")
    print("-" * 60)

    with open(diff_path, "r") as f:
        content = f.read()
    print(content)

    print("-" * 60)
    print("\nApproving this diff and emitting BRAIN_DREAM_DIFF_REVIEWED event...")

    success = _emit_cieu("BRAIN_DREAM_DIFF_REVIEWED", {
        "agent_id": "board",
        "action": "review_approved",
        "intent": "Board/CEO reviewed and approved brain dream diff",
        "context": {
            "diff_path": diff_path,
            "reviewed_at": datetime.now().isoformat(),
        },
        "result": f"approved:{diff_path}",
    }, cieu_db=cieu_db)

    if success:
        print("\nBRAIN_DREAM_DIFF_REVIEWED event emitted.")
        print("You can now run: python3.11 scripts/aiden_dream.py --commit")
        return True
    else:
        print("\nFailed to emit CIEU event. Check database connectivity.")
        return False


if __name__ == "__main__":
    if "--latest" in sys.argv:
        diff_path = find_latest_diff()
        if diff_path:
            approve_diff(diff_path)
        else:
            print("No diff files found. Run --dry-run first.")
            sys.exit(1)
    elif "--diff" in sys.argv:
        idx = sys.argv.index("--diff")
        if idx + 1 < len(sys.argv):
            approve_diff(sys.argv[idx + 1])
        else:
            print("ERROR: --diff requires a path argument")
            sys.exit(1)
    else:
        print(__doc__)
        sys.exit(1)
