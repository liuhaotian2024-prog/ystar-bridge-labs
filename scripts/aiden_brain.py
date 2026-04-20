#!/usr/bin/env python3
"""
Aiden Neural Network v0.1 — Personal Cognitive Graph Engine

Not a file system. A brain.

Nodes = knowledge items (wisdom files, principles, experiences)
Edges = connections with continuous weights (not binary)
Activation = spreading activation (Collins & Loftus 1975)
Learning = Hebbian (fire together, wire together)
Dimensions = 6D coordinates (Y/X/Z/T/Φ/C)

Storage: SQLite (aiden_brain.db)
"""

import sqlite3
import json
import math
import time
import os
from pathlib import Path
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "aiden_brain.db")


def get_db(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db(db_path: str = DB_PATH):
    conn = get_db(db_path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS nodes (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            file_path   TEXT,
            node_type   TEXT,    -- ceo_learning, meta, paradigm, self_knowledge, strategic, hub
            depth_label TEXT,    -- kernel, foundational, operational, tactical
            content_hash TEXT,
            -- 6D coordinates (0.0 to 1.0)
            dim_y       REAL DEFAULT 0.5,  -- depth/identity
            dim_x       REAL DEFAULT 0.5,  -- breadth/knowledge
            dim_z       REAL DEFAULT 0.5,  -- impact/transcendence
            dim_t       REAL DEFAULT 0.5,  -- evolution/direction
            dim_phi     REAL DEFAULT 0.5,  -- metacognition/counterfactual
            dim_c       REAL DEFAULT 0.5,  -- courage/action
            -- activation state
            base_activation REAL DEFAULT 0.0,
            last_accessed   REAL DEFAULT 0.0,
            access_count    INTEGER DEFAULT 0,
            created_at      REAL DEFAULT 0.0,
            updated_at      REAL DEFAULT 0.0,
            -- metadata
            principles  TEXT,   -- JSON list of linked principles
            triggers    TEXT,   -- JSON list of discovery triggers
            summary     TEXT    -- one-line summary for activation display
        );

        CREATE TABLE IF NOT EXISTS edges (
            source_id   TEXT NOT NULL,
            target_id   TEXT NOT NULL,
            edge_type   TEXT DEFAULT 'explicit',  -- explicit, implicit, hebbian
            weight      REAL DEFAULT 0.5,
            created_at  REAL DEFAULT 0.0,
            updated_at  REAL DEFAULT 0.0,
            co_activations INTEGER DEFAULT 0,
            PRIMARY KEY (source_id, target_id),
            FOREIGN KEY (source_id) REFERENCES nodes(id),
            FOREIGN KEY (target_id) REFERENCES nodes(id)
        );

        CREATE TABLE IF NOT EXISTS activation_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            query       TEXT,
            activated_nodes TEXT,  -- JSON list of {node_id, activation_level}
            session_id  TEXT,
            timestamp   REAL
        );

        CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);
        CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
        CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(node_type);
    """)
    conn.commit()
    conn.close()


# ── Node Operations ─────────────────────────────────────────────────

def add_node(node_id: str, name: str, file_path: str = "",
             node_type: str = "", depth_label: str = "",
             dims: Optional[dict] = None, principles: list = None,
             summary: str = "", content_hash: str = "",
             db_path: str = DB_PATH):
    """Add or update a node. Preserves access_count, last_accessed, created_at
    on conflict (existing node). Only content-derived fields are updated."""
    conn = get_db(db_path)
    now = time.time()
    d = dims or {}
    conn.execute("""
        INSERT INTO nodes
        (id, name, file_path, node_type, depth_label,
         dim_y, dim_x, dim_z, dim_t, dim_phi, dim_c,
         base_activation, last_accessed, access_count,
         created_at, updated_at, principles, summary, content_hash)
        VALUES (?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                0.0, 0.0, 0,
                ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name = excluded.name,
            file_path = excluded.file_path,
            node_type = excluded.node_type,
            depth_label = excluded.depth_label,
            dim_y = excluded.dim_y,
            dim_x = excluded.dim_x,
            dim_z = excluded.dim_z,
            dim_t = excluded.dim_t,
            dim_phi = excluded.dim_phi,
            dim_c = excluded.dim_c,
            updated_at = excluded.updated_at,
            principles = excluded.principles,
            summary = excluded.summary,
            content_hash = excluded.content_hash
    """, (node_id, name, file_path, node_type, depth_label,
          d.get("y", 0.5), d.get("x", 0.5), d.get("z", 0.5),
          d.get("t", 0.5), d.get("phi", 0.5), d.get("c", 0.5),
          now, now,
          json.dumps(principles or []), summary, content_hash))
    conn.commit()
    conn.close()


def touch_node(node_id: str, db_path: str = DB_PATH):
    conn = get_db(db_path)
    conn.execute("""
        UPDATE nodes SET last_accessed = ?, access_count = access_count + 1
        WHERE id = ?
    """, (time.time(), node_id))
    conn.commit()
    conn.close()


def increment_access_count(node_id: str, db_path: str = DB_PATH):
    """Atomically increment access_count and update last_accessed.

    Fixes the gap where activation_log writes never updated nodes table,
    causing access_count to remain 0 despite repeated activations.
    Per CTO ruling CZL-BRAIN-AUTO-INGEST Q8.
    """
    conn = get_db(db_path)
    conn.execute(
        "UPDATE nodes SET access_count = access_count + 1, last_accessed = ? WHERE id = ?",
        (time.time(), node_id),
    )
    conn.commit()
    conn.close()


# ── Edge Operations ─────────────────────────────────────────────────

def add_edge(source_id: str, target_id: str, weight: float = 0.5,
             edge_type: str = "explicit", db_path: str = DB_PATH):
    """Add or update a bidirectional edge. Preserves co_activations and
    created_at on conflict (existing edge). Only updates weight, edge_type,
    updated_at."""
    conn = get_db(db_path)
    now = time.time()
    for src, tgt in [(source_id, target_id), (target_id, source_id)]:
        conn.execute("""
            INSERT INTO edges
            (source_id, target_id, edge_type, weight, created_at, updated_at, co_activations)
            VALUES (?, ?, ?, ?, ?, ?, 0)
            ON CONFLICT(source_id, target_id) DO UPDATE SET
                edge_type = excluded.edge_type,
                weight = excluded.weight,
                updated_at = excluded.updated_at
        """, (src, tgt, edge_type, weight, now, now))
    conn.commit()
    conn.close()


def hebbian_update(node_a: str, node_b: str, learning_rate: float = 0.1,
                   db_path: str = DB_PATH):
    """Strengthen connection between co-activated nodes."""
    conn = get_db(db_path)
    now = time.time()
    for src, tgt in [(node_a, node_b), (node_b, node_a)]:
        existing = conn.execute(
            "SELECT weight, co_activations FROM edges WHERE source_id=? AND target_id=?",
            (src, tgt)).fetchone()
        if existing:
            old_w = existing["weight"]
            new_w = min(1.0, old_w + learning_rate * (1.0 - old_w))
            conn.execute("""
                UPDATE edges SET weight=?, updated_at=?, co_activations=co_activations+1
                WHERE source_id=? AND target_id=?
            """, (new_w, now, src, tgt))
        else:
            conn.execute("""
                INSERT INTO edges (source_id, target_id, edge_type, weight,
                                   created_at, updated_at, co_activations)
                VALUES (?, ?, 'hebbian', ?, ?, ?, 1)
            """, (src, tgt, learning_rate, now, now))
    conn.commit()
    conn.close()


# ── Activation Engine ───────────────────────────────────────────────

def _base_activation(node: dict, now: float) -> float:
    """ACT-R inspired: activation = ln(access_count) - decay * time_since_last."""
    count = max(node["access_count"], 1)
    time_since = max(now - node["last_accessed"], 1.0)
    decay = 0.5
    return math.log(count) - decay * math.log(time_since)


def _text_similarity(query: str, node: dict) -> float:
    """Substring + token overlap for both English and Chinese."""
    q = query.lower()
    score = 0.0
    searchable = " ".join(filter(None, [
        node.get("name", ""), node.get("summary", ""),
        node.get("node_type", ""), node.get("depth_label", ""),
        node.get("id", ""),
    ]))
    try:
        principles = json.loads(node.get("principles", "[]") or "[]")
        searchable += " " + " ".join(principles)
    except (json.JSONDecodeError, TypeError):
        pass
    searchable_lower = searchable.lower()
    # Whole-word/phrase match (min 3 chars for English to avoid noise)
    for term in q.split():
        if len(term) >= 3 and term in searchable_lower:
            score += 2.0
        elif len(term) < 3 and ord(term[0]) > 127 and term in searchable_lower:
            score += 2.0
    # Chinese character matching (each CJK char is meaningful)
    cjk_chars = [c for c in q if ord(c) > 0x4E00]
    for ch in cjk_chars:
        if ch in searchable_lower:
            score += 1.0
    return score / max(len(q.split()), 1)


def activate(query: str, max_hops: int = 3, top_n: int = 10,
             decay_per_hop: float = 0.5, db_path: str = DB_PATH) -> list:
    """
    Spreading activation: query → match nodes → spread along edges → return top-N.

    Returns list of (node_id, name, activation_level, file_path, hop_distance).
    """
    conn = get_db(db_path)
    now = time.time()
    all_nodes = [dict(r) for r in conn.execute("SELECT * FROM nodes").fetchall()]

    # Phase 1: Initial activation from query match
    activations = {}
    for node in all_nodes:
        sim = _text_similarity(query, node)
        base = _base_activation(node, now)
        initial = sim * 2.0 + max(base, 0) * 0.3
        if initial > 0.01:
            activations[node["id"]] = {"level": initial, "hop": 0,
                                        "name": node["name"],
                                        "file_path": node.get("file_path", ""),
                                        "summary": node.get("summary", "")}

    # Phase 2: Spreading activation
    for hop in range(1, max_hops + 1):
        new_activations = {}
        for node_id, info in list(activations.items()):
            if info["hop"] != hop - 1:
                continue
            edges = conn.execute(
                "SELECT target_id, weight FROM edges WHERE source_id=?",
                (node_id,)).fetchall()
            for edge in edges:
                target_id = edge["target_id"]
                spread = info["level"] * edge["weight"] * (decay_per_hop ** hop)
                if spread > 0.01:
                    if target_id in activations:
                        if spread > activations[target_id]["level"] * 0.5:
                            activations[target_id]["level"] += spread * 0.5
                    elif target_id in new_activations:
                        new_activations[target_id]["level"] = max(
                            new_activations[target_id]["level"], spread)
                    else:
                        target_node = conn.execute(
                            "SELECT name, file_path, summary FROM nodes WHERE id=?",
                            (target_id,)).fetchone()
                        if target_node:
                            new_activations[target_id] = {
                                "level": spread, "hop": hop,
                                "name": target_node["name"],
                                "file_path": target_node["file_path"] or "",
                                "summary": target_node["summary"] or ""}
        activations.update(new_activations)

    conn.close()

    # Sort by activation level, return top-N
    results = sorted(activations.items(), key=lambda x: x[1]["level"], reverse=True)
    return [(nid, info["name"], round(info["level"], 3),
             info["file_path"], info["hop"])
            for nid, info in results[:top_n]]


def record_co_activation(node_ids: list, db_path: str = DB_PATH):
    """Record that these nodes were used together → Hebbian strengthen all pairs."""
    for i, a in enumerate(node_ids):
        touch_node(a, db_path)
        for b in node_ids[i+1:]:
            hebbian_update(a, b, db_path=db_path)


# ── Decay ───────────────────────────────────────────────────────────

def apply_decay(decay_rate: float = 0.01, db_path: str = DB_PATH):
    """Decay all edge weights slightly. Call periodically (e.g., session close)."""
    conn = get_db(db_path)
    conn.execute("""
        UPDATE edges SET weight = MAX(0.01, weight - ?)
        WHERE edge_type = 'hebbian'
    """, (decay_rate,))
    conn.commit()
    conn.close()


# ── Stats ───────────────────────────────────────────────────────────

def stats(db_path: str = DB_PATH) -> dict:
    conn = get_db(db_path)
    n_nodes = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    n_edges = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    n_hebbian = conn.execute(
        "SELECT COUNT(*) FROM edges WHERE edge_type='hebbian'").fetchone()[0]
    avg_weight = conn.execute(
        "SELECT AVG(weight) FROM edges").fetchone()[0] or 0
    conn.close()
    return {"nodes": n_nodes, "edges": n_edges, "hebbian_edges": n_hebbian,
            "avg_weight": round(avg_weight, 3)}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: aiden_brain.py [init|stats|activate <query>|decay]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "init":
        init_db()
        print(f"Brain initialized at {DB_PATH}")
    elif cmd == "stats":
        init_db()
        s = stats()
        print(json.dumps(s, indent=2))
    elif cmd == "activate":
        query = " ".join(sys.argv[2:])
        results = activate(query)
        for nid, name, level, fpath, hop in results:
            print(f"  [{level:.3f}] (hop {hop}) {name}")
            if fpath:
                print(f"         → {fpath}")
    elif cmd == "decay":
        apply_decay()
        print("Decay applied to hebbian edges")
