#!/usr/bin/env python3
"""
Backfill Merkle sealing for all historical sessions in .ystar_cieu.db.

Iterates distinct session_id values that have no row in sealed_sessions yet,
calls CIEUStore.seal_session(sid) for each, and emits a summary CIEU event.

Usage:
    python3 scripts/backfill_merkle_sealing.py              # seal all
    python3 scripts/backfill_merkle_sealing.py --dry-run     # count only
    python3 scripts/backfill_merkle_sealing.py --help
"""

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

# Add Y-star-gov to path
YSTAR_GOV_PATH = Path(__file__).parent.parent.parent / "Y-star-gov"
if YSTAR_GOV_PATH.exists():
    sys.path.insert(0, str(YSTAR_GOV_PATH))

# Add scripts/ for _cieu_helpers
sys.path.insert(0, str(Path(__file__).parent))

CIEU_DB_PATH = Path(__file__).parent.parent / ".ystar_cieu.db"


def get_unsealed_sessions(db_path: Path) -> list[str]:
    """Return session_ids that exist in cieu_events but not in sealed_sessions."""
    conn = sqlite3.connect(str(db_path))
    rows = conn.execute("""
        SELECT DISTINCT ce.session_id
        FROM cieu_events ce
        LEFT JOIN sealed_sessions ss ON ce.session_id = ss.session_id
        WHERE ss.session_id IS NULL
          AND ce.session_id IS NOT NULL
          AND ce.session_id != ''
        ORDER BY ce.session_id
    """).fetchall()
    conn.close()
    return [r[0] for r in rows]


def main():
    parser = argparse.ArgumentParser(
        description="Backfill Merkle sealing for historical CIEU sessions."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Count unsealed sessions without writing.",
    )
    parser.add_argument(
        "--db",
        type=str,
        default=str(CIEU_DB_PATH),
        help=f"Path to CIEU database (default: {CIEU_DB_PATH})",
    )
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"ERROR: database not found at {db_path}", file=sys.stderr)
        return 1

    unsealed = get_unsealed_sessions(db_path)
    total = len(unsealed)

    if args.dry_run:
        print(f"[dry-run] {total} sessions need sealing in {db_path}")
        return 0

    if total == 0:
        print("All sessions already sealed. Nothing to do.")
        return 0

    print(f"Sealing {total} sessions in {db_path} ...")

    from ystar.governance.cieu_store import CIEUStore

    store = CIEUStore(str(db_path))
    success = 0
    failed = 0
    start_time = time.time()

    for i, sid in enumerate(unsealed, 1):
        try:
            result = store.seal_session(sid)
            ec = result.get("event_count", 0)
            mr = result.get("merkle_root", "")
            mr_short = mr[:16] if mr else "(empty)"
            print(f"[{i}/{total}] sealed session {sid} with merkle_root {mr_short}... ({ec} events)")
            success += 1
        except Exception as e:
            print(f"[{i}/{total}] FAILED session {sid}: {e}", file=sys.stderr)
            failed += 1

    elapsed = time.time() - start_time
    print(f"\nDone in {elapsed:.1f}s: {success} sealed, {failed} failed, {total} total.")

    # Emit summary CIEU event
    try:
        from _cieu_helpers import emit_cieu

        emit_cieu(
            event_type="BACKFILL_MERKLE_SEALING_RUN",
            decision="allow",
            passed=1 if failed == 0 else 0,
            task_description=f"Backfill complete: {success}/{total} sessions sealed, {failed} failed, {elapsed:.1f}s",
            session_id="backfill_merkle",
            params_json=json.dumps({
                "total": total,
                "success": success,
                "failed": failed,
                "elapsed_seconds": round(elapsed, 2),
                "db_path": str(db_path),
            }),
        )
        print("[ok] BACKFILL_MERKLE_SEALING_RUN CIEU event emitted")
    except Exception as e:
        print(f"[warn] CIEU emit failed: {e}", file=sys.stderr)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
