#!/usr/bin/env python3
"""Phase 2 goal-tree schema migration — idempotent CREATE TABLE IF NOT EXISTS.

Creates:
  - ystar_goal_tree: hierarchical goal decomposition
  - cieu_goal_contribution: event-to-goal contribution scores
  - 4 indexes for query performance

Usage:
    python3 scripts/phase2_goal_tree_schema.py [--db PATH]
"""

import argparse
import os
import sqlite3
import sys
import time

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS ystar_goal_tree (
    goal_id TEXT PRIMARY KEY,
    parent_goal_id TEXT,
    goal_text TEXT NOT NULL,
    y_star_definition TEXT,
    owner_role TEXT,
    created_at REAL,
    created_by TEXT,
    status TEXT DEFAULT 'active',
    weight REAL DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS cieu_goal_contribution (
    event_id TEXT,
    goal_id TEXT,
    role_alignment_score REAL,
    goal_contribution_score REAL,
    inference_basis TEXT,
    created_at REAL
);

CREATE INDEX IF NOT EXISTS idx_cgc_goal ON cieu_goal_contribution(goal_id);
CREATE INDEX IF NOT EXISTS idx_cgc_event ON cieu_goal_contribution(event_id);
CREATE INDEX IF NOT EXISTS idx_gt_parent ON ystar_goal_tree(parent_goal_id);
CREATE INDEX IF NOT EXISTS idx_gt_status ON ystar_goal_tree(status);
"""


def run_migration(db_path: str) -> None:
    """Execute idempotent schema migration."""
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        # Verify
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('ystar_goal_tree','cieu_goal_contribution') ORDER BY name")
        tables = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%' ORDER BY name")
        indexes = [r[0] for r in cur.fetchall()]
        print(f"[phase2] Migration OK — tables: {tables}, indexes: {indexes}")
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 2 goal-tree schema migration")
    parser.add_argument("--db", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".ystar_cieu.db"),
                        help="Path to CIEU database")
    args = parser.parse_args()
    if not os.path.exists(args.db):
        print(f"[phase2] ERROR: DB not found at {args.db}", file=sys.stderr)
        sys.exit(1)
    run_migration(args.db)


if __name__ == "__main__":
    main()
