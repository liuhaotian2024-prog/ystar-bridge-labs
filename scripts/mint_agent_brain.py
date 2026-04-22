#!/usr/bin/env python3
"""
Mint Agent Brain — batch-create per-agent brain.db for all 9 agents.

Milestone 8b (2026-04-21): scale Ethan brain pilot template to
Leo / Maya / Ryan / Jordan / Sofia / Zara / Marco / Samantha.
Aiden + Ethan brain already LIVE, this mints the remaining 8.

Reuses ethan_brain schema (CZL-PARITY: schema drift 0 across 9 agents).
Seed from AGENTS.md 对应 role section if present, else minimal 1-node seed
of the agent's role identity. Can re-run idempotent (INSERT OR REPLACE).

M-tag: M-1 Survivability (9 agent 空脑 → 全持久).

Usage:
    python3.11 scripts/mint_agent_brain.py                # mint all 8
    python3.11 scripts/mint_agent_brain.py --agent leo    # one only
    python3.11 scripts/mint_agent_brain.py --stats        # no mint, report
"""

import argparse
import hashlib
import re
import sqlite3
import sys
import time
from pathlib import Path

WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
AGENTS_MD = WORKSPACE / "AGENTS.md"

# 8 agents missing brain (Aiden + Ethan already LIVE)
AGENTS = [
    ("leo", "Leo Chen", "Kernel Engineer", "eng-kernel"),
    ("maya", "Maya Patel", "Governance Engineer", "eng-governance"),
    ("ryan", "Ryan Park", "Platform Engineer", "eng-platform"),
    ("jordan", "Jordan Lee", "Domains Engineer", "eng-domains"),
    ("sofia", "Sofia Reyes", "CMO", "cmo"),
    ("zara", "Zara Ahmed", "CSO", "cso"),
    ("marco", "Marco Ricci", "CFO", "cfo"),
    ("samantha", "Samantha Lin", "Secretary", "secretary"),
]


SCHEMA_NODES = """
CREATE TABLE IF NOT EXISTS nodes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    file_path TEXT,
    node_type TEXT,
    depth_label TEXT,
    content_hash TEXT,
    dim_y REAL DEFAULT 0.5, dim_x REAL DEFAULT 0.5, dim_z REAL DEFAULT 0.5,
    dim_t REAL DEFAULT 0.5, dim_phi REAL DEFAULT 0.5, dim_c REAL DEFAULT 0.5,
    base_activation REAL DEFAULT 0.0,
    last_accessed REAL DEFAULT 0.0, access_count INTEGER DEFAULT 0,
    created_at REAL DEFAULT 0.0, updated_at REAL DEFAULT 0.0,
    principles TEXT, triggers TEXT, summary TEXT, embedding BLOB
)
"""
SCHEMA_EDGES = """
CREATE TABLE IF NOT EXISTS edges (
    source_id TEXT NOT NULL, target_id TEXT NOT NULL,
    edge_type TEXT DEFAULT 'explicit', weight REAL DEFAULT 0.5,
    created_at REAL DEFAULT 0.0, updated_at REAL DEFAULT 0.0,
    co_activations INTEGER DEFAULT 0,
    PRIMARY KEY (source_id, target_id),
    FOREIGN KEY (source_id) REFERENCES nodes(id),
    FOREIGN KEY (target_id) REFERENCES nodes(id)
)
"""
SCHEMA_ACTIVATION = """
CREATE TABLE IF NOT EXISTS activation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT, activated_nodes TEXT, session_id TEXT, timestamp REAL
)
"""


def db_path_for(agent_key: str) -> Path:
    return WORKSPACE / f"{agent_key}_brain.db"


def init_schema(conn: sqlite3.Connection) -> None:
    conn.execute(SCHEMA_NODES)
    conn.execute(SCHEMA_EDGES)
    conn.execute(SCHEMA_ACTIVATION)
    conn.commit()


def seed_minimal(conn: sqlite3.Connection, agent_key: str, display_name: str,
                 role: str, agents_md_role: str) -> int:
    """Seed identity + role + M Triangle + WORK_METHODOLOGY anchor nodes."""
    now = time.time()
    seeds = [
        (f"{agent_key}/identity/self",
         f"{display_name} — {role}",
         "agent_identity", "kernel",
         f"Y* Bridge Labs {role} ({display_name}), M Triangle + WORK_METHODOLOGY 必遵守"),
        (f"{agent_key}/charter/M_TRIANGLE",
         "M Triangle — 最高对齐目标",
         "charter_anchor", "kernel",
         "M-1 Survivability + M-2a 防做错 + M-2b 防不作为 + M-3 Value Production"),
        (f"{agent_key}/charter/WORK_METHODOLOGY",
         "WORK METHODOLOGY — 14 原则 + 2 checklist",
         "charter_anchor", "kernel",
         "P-1 对齐 M Triangle / P-4 真实测试 / P-9 plan ≠ done / ..."),
        (f"{agent_key}/role/AGENTS_MD",
         f"AGENTS.md role: {agents_md_role}",
         "role_contract", "foundational",
         f"scope + write boundaries + collaboration rules per AGENTS.md"),
    ]
    count = 0
    for node_id, name, ntype, depth, summary in seeds:
        content_hash = hashlib.sha256(name.encode()).hexdigest()[:16]
        conn.execute("""
            INSERT OR REPLACE INTO nodes
            (id, name, node_type, depth_label, content_hash,
             created_at, updated_at, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (node_id, name, ntype, depth, content_hash, now, now, summary))
        count += 1
    # Wire identity → charter edges (agent must know M Triangle + METHODOLOGY)
    for tgt_suffix in ["charter/M_TRIANGLE", "charter/WORK_METHODOLOGY", "role/AGENTS_MD"]:
        conn.execute("""
            INSERT OR IGNORE INTO edges
            (source_id, target_id, edge_type, weight, created_at, updated_at)
            VALUES (?, ?, 'identity_anchor', 1.0, ?, ?)
        """, (f"{agent_key}/identity/self",
              f"{agent_key}/{tgt_suffix}",
              now, now))
    conn.commit()
    return count


def mint(agent_key: str, display_name: str, role: str, role_tag: str,
         dry_run: bool = False) -> dict:
    """Create + seed one agent brain."""
    path = db_path_for(agent_key)
    if dry_run:
        return {"agent": agent_key, "path": str(path), "action": "DRY-RUN"}

    existed = path.exists()
    conn = sqlite3.connect(path)
    init_schema(conn)
    seeded = seed_minimal(conn, agent_key, display_name, role, role_tag)
    n = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    e = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    conn.close()
    return {
        "agent": agent_key, "path": str(path),
        "action": "UPDATED" if existed else "CREATED",
        "seeded": seeded, "nodes_total": n, "edges_total": e,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", default=None,
                    help="mint only this agent (key: leo/maya/...). Default: all 8.")
    ap.add_argument("--stats", action="store_true",
                    help="report existing brain.db state, no mint")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    targets = AGENTS
    if args.agent:
        targets = [a for a in AGENTS if a[0] == args.agent]
        if not targets:
            print(f"[mint] unknown agent: {args.agent}")
            return 2

    if args.stats:
        for key, name, role, role_tag in targets:
            p = db_path_for(key)
            if not p.exists():
                print(f"  {key}: MISSING")
                continue
            conn = sqlite3.connect(p)
            n = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
            conn.close()
            print(f"  {key}: nodes={n}, db={p.name}")
        return 0

    for key, name, role, role_tag in targets:
        result = mint(key, name, role, role_tag, dry_run=args.dry_run)
        print(f"[mint] {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
