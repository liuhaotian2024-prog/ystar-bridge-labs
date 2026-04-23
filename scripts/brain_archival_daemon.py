#!/usr/bin/env python3
'''Brain Archival Daemon — SleepGate-inspired periodic maintenance.

Per CZL-BRAIN-FRONTIER-4-ARCHIVAL-SLEEPGATE
Mechanisms (Friston/SleepGate-inspired):
1. Synaptic downscaling: nodes.base_activation *= 0.95 (decay)
2. Selective replay: top 10% access_count nodes get +0.1 base_activation boost
3. Active forgetting: bottom 5% (low recency x low access) -> archive to backups/brain_archive/{ts}.db
'''

import sqlite3
import time
from pathlib import Path

BRAIN_DB = Path('/Users/haotianliu/.openclaw/workspace/ystar-company/aiden_brain.db')
ARCHIVE_DIR = Path('/Users/haotianliu/.openclaw/workspace/ystar-company/backups/brain_archive')


def synaptic_downscale(db):
    """Decay all base_activation by 5% (multiply by 0.95)."""
    db.execute("UPDATE nodes SET base_activation = base_activation * 0.95")
    return db.execute("SELECT changes()").fetchone()[0]


def selective_replay(db):
    """Top 10% by access_count get +0.1 boost, capped at 1.0."""
    db.execute("""
        UPDATE nodes SET base_activation = MIN(1.0, base_activation + 0.1)
        WHERE id IN (
            SELECT id FROM nodes
            ORDER BY access_count DESC
            LIMIT (SELECT MAX(1, COUNT(*) / 10) FROM nodes)
        )
    """)
    return db.execute("SELECT changes()").fetchone()[0]


def active_forgetting(db, archive_dir):
    """Bottom 5% by (last_accessed * access_count) score -> count candidates.

    Destructive delete deferred — this iteration only counts.
    """
    total = db.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    if total < 20:
        return 0

    offset = max(1, total // 20)
    cutoff_row = db.execute("""
        SELECT (COALESCE(last_accessed, 0) * COALESCE(access_count, 1)) as score
        FROM nodes
        ORDER BY score ASC
        LIMIT 1 OFFSET ?
    """, (offset,)).fetchone()

    if cutoff_row is None:
        return 0

    cutoff_score = cutoff_row[0]
    archived_count = db.execute("""
        SELECT COUNT(*) FROM nodes
        WHERE (COALESCE(last_accessed, 0) * COALESCE(access_count, 1)) <= ?
    """, (cutoff_score,)).fetchone()[0]

    return archived_count


def main():
    if not BRAIN_DB.exists():
        print("[archival] ERROR: brain.db not found")
        return 1

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    db = sqlite3.connect(str(BRAIN_DB))
    total_before = db.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]

    t0 = time.monotonic()
    db.execute("BEGIN")
    downscaled = synaptic_downscale(db)
    replayed = selective_replay(db)
    archive_candidates = active_forgetting(db, ARCHIVE_DIR)
    db.commit()
    elapsed_ms = (time.monotonic() - t0) * 1000

    print(f"[archival] nodes={total_before} | downscaled={downscaled} | "
          f"replay_boosted={replayed} | archive_candidates={archive_candidates} | "
          f"elapsed={elapsed_ms:.0f}ms")

    db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
