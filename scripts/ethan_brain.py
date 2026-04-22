#!/usr/bin/env python3
"""
Ethan Brain — CTO's 6D persistent brain (pilot).

Milestone 8 (2026-04-21): Prove 9-agent brain template by landing Ethan's
brain.db first. Same 6D schema as aiden_brain.db. On success, scale
template to Leo / Maya / Ryan / Jordan / Sofia / Zara / Marco / Samantha.

Seed from `knowledge/cto/wisdom/WHO_I_AM_ETHAN.md` section headings
→ initial nodes. Subsequent CIEU ingest + dialogue ingest via shared
daemons (cieu_brain_daemon + dialogue_to_brain_feeder) with role filter.

M-tag: M-1 Survivability (Ethan cross-session memory persistence).
Board 2026-04-21 asked "其他 agent 也要持续存在 — 大家的大脑" — this is
the first per-agent brain fulfilling that. Aiden brain pattern reused (P-12).

Usage:
    python3.11 scripts/ethan_brain.py --init      # create schema
    python3.11 scripts/ethan_brain.py --seed      # ingest WHO_I_AM_ETHAN.md sections
    python3.11 scripts/ethan_brain.py --stats     # report counts
"""

import argparse
import hashlib
import os
import re
import sqlite3
import sys
import time
from pathlib import Path

WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
DB_PATH = WORKSPACE / "ethan_brain.db"
WHO_I_AM = WORKSPACE / "knowledge/cto/wisdom/WHO_I_AM_ETHAN.md"

# Reuse aiden_brain schema (verified 2026-04-21 via PRAGMA table_info)
SCHEMA_NODES = """
CREATE TABLE IF NOT EXISTS nodes (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    file_path   TEXT,
    node_type   TEXT,
    depth_label TEXT,
    content_hash TEXT,
    dim_y       REAL DEFAULT 0.5,
    dim_x       REAL DEFAULT 0.5,
    dim_z       REAL DEFAULT 0.5,
    dim_t       REAL DEFAULT 0.5,
    dim_phi     REAL DEFAULT 0.5,
    dim_c       REAL DEFAULT 0.5,
    base_activation REAL DEFAULT 0.0,
    last_accessed   REAL DEFAULT 0.0,
    access_count    INTEGER DEFAULT 0,
    created_at      REAL DEFAULT 0.0,
    updated_at      REAL DEFAULT 0.0,
    principles  TEXT,
    triggers    TEXT,
    summary     TEXT,
    embedding   BLOB
)
"""

SCHEMA_EDGES = """
CREATE TABLE IF NOT EXISTS edges (
    source_id   TEXT NOT NULL,
    target_id   TEXT NOT NULL,
    edge_type   TEXT DEFAULT 'explicit',
    weight      REAL DEFAULT 0.5,
    created_at  REAL DEFAULT 0.0,
    updated_at  REAL DEFAULT 0.0,
    co_activations INTEGER DEFAULT 0,
    PRIMARY KEY (source_id, target_id),
    FOREIGN KEY (source_id) REFERENCES nodes(id),
    FOREIGN KEY (target_id) REFERENCES nodes(id)
)
"""

SCHEMA_ACTIVATION = """
CREATE TABLE IF NOT EXISTS activation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT,
    activated_nodes TEXT,
    session_id TEXT,
    timestamp REAL
)
"""


def init_db(db_path: str = None) -> sqlite3.Connection:
    p = db_path or str(DB_PATH)
    conn = sqlite3.connect(p)
    conn.execute(SCHEMA_NODES)
    conn.execute(SCHEMA_EDGES)
    conn.execute(SCHEMA_ACTIVATION)
    conn.commit()
    return conn


def add_node(conn: sqlite3.Connection, node_id: str, name: str,
             node_type: str = "ethan_identity", depth_label: str = "foundational",
             summary: str = "") -> None:
    now = time.time()
    content_hash = hashlib.sha256(name.encode()).hexdigest()[:16]
    conn.execute("""
        INSERT OR REPLACE INTO nodes
        (id, name, node_type, depth_label, content_hash,
         created_at, updated_at, summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (node_id, name, node_type, depth_label, content_hash, now, now, summary))


def seed_from_who_i_am(conn: sqlite3.Connection, md_path: Path = None) -> int:
    """Parse WHO_I_AM_ETHAN.md section headings as seed nodes."""
    path = md_path or WHO_I_AM
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8", errors="replace")
    # Match "## Section N — Title" style headers
    pattern = re.compile(r"^##\s+(.+)$", re.MULTILINE)
    sections = pattern.findall(text)
    count = 0
    for section in sections:
        title = section.strip()
        node_id = f"ethan/wisdom/{hashlib.sha256(title.encode()).hexdigest()[:12]}"
        add_node(conn, node_id, title,
                 node_type="ethan_wisdom_section",
                 depth_label="foundational",
                 summary=title[:120])
        count += 1
    conn.commit()
    return count


def stats(conn: sqlite3.Connection) -> dict:
    nodes = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    edges = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    activations = conn.execute("SELECT COUNT(*) FROM activation_log").fetchone()[0]
    return {"nodes": nodes, "edges": edges, "activations": activations,
            "db_path": conn.execute("PRAGMA database_list").fetchall()[0][2]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--seed", action="store_true")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--db-path", default=str(DB_PATH))
    args = ap.parse_args()

    conn = init_db(args.db_path)

    if args.init:
        print(f"[ethan_brain] schema ready at {args.db_path}")

    if args.seed:
        n = seed_from_who_i_am(conn)
        print(f"[ethan_brain] seeded {n} nodes from WHO_I_AM_ETHAN.md")

    if args.stats or not (args.init or args.seed):
        s = stats(conn)
        print(f"[ethan_brain] {s}")

    conn.close()


if __name__ == "__main__":
    sys.exit(main() or 0)
