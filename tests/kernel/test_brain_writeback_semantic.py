# Audience: CTO Ethan (review) + Leo-Kernel (author) + CI pipeline
# Research basis: CTO ruling CZL-BRAIN-3LOOP-FINAL Points 6,9,10; CEO v2 Section 3.3; Ethan Q6 self-ref guard
# Synthesis: 7 test cases covering positive Hebbian, negative (CROBA) Hebbian with asymmetric lr, warmup gate, provenance tagging, error path, relevance tiers, and smoke integration
# Purpose: Validate L2 writeback semantic correctness before Ryan wires into hook chain
"""
Tests for hook_ceo_post_output_brain_writeback.py -- L2 outcome-weighted Hebbian write-back.

Covers:
  1. Positive outcome -> positive Hebbian + access_count incremented
  2. CROBA event -> negative Hebbian (lr=0.15)
  3. Warmup gate < 5000 rows -> BRAIN_WARMUP_PENDING + no Hebbian
  4. Provenance='system:brain' on all activation_log rows
  5. Error path: hebbian_update raises -> BRAIN_WRITEBACK_FAILED + no crash
  6. Relevance tiers: cited=1.0, keyword=0.6, background=0.3
  7. Smoke: synthetic data -> brain weight delta observed
"""

import os
import sys
import sqlite3
import time
import pytest

# Add scripts/ to path so we can import the writeback module
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_SCRIPTS_DIR = os.path.join(_REPO_ROOT, "scripts")
sys.path.insert(0, _SCRIPTS_DIR)

from hook_ceo_post_output_brain_writeback import (
    writeback,
    _compute_node_relevance,
    _determine_outcome_sign,
    _check_warmup,
    POSITIVE_LR,
    NEGATIVE_LR,
    WARMUP_THRESHOLD,
    OUTCOME_WINDOW_SECONDS,
    RELEVANCE_CITED,
    RELEVANCE_KEYWORD,
    RELEVANCE_BACKGROUND,
)


# ── Fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
def brain_db(tmp_path):
    """Create a minimal brain DB with nodes, edges, and activation_log tables."""
    db_path = str(tmp_path / "test_brain.db")
    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE nodes (
            id TEXT PRIMARY KEY,
            name TEXT,
            file_path TEXT,
            summary TEXT,
            dim_y REAL DEFAULT 0.5,
            dim_x REAL DEFAULT 0.5,
            dim_z REAL DEFAULT 0.5,
            dim_t REAL DEFAULT 0.5,
            dim_phi REAL DEFAULT 0.5,
            dim_c REAL DEFAULT 0.5,
            access_count INTEGER DEFAULT 0,
            last_accessed REAL DEFAULT 0,
            triggers TEXT DEFAULT '',
            created_at REAL,
            updated_at REAL
        );
        CREATE TABLE edges (
            source_id TEXT,
            target_id TEXT,
            edge_type TEXT DEFAULT 'explicit',
            weight REAL DEFAULT 0.5,
            created_at REAL,
            updated_at REAL,
            co_activations INTEGER DEFAULT 0,
            PRIMARY KEY (source_id, target_id)
        );
        CREATE TABLE activation_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT,
            query_text TEXT,
            activation_score REAL,
            timestamp REAL,
            provenance TEXT DEFAULT ''
        );
    """)
    now = time.time()
    # Insert 3 test nodes
    for nid, name in [("n1", "governance-core"), ("n2", "identity-values"),
                      ("n3", "brain-architecture")]:
        conn.execute(
            "INSERT INTO nodes (id, name, access_count, created_at, updated_at) "
            "VALUES (?, ?, 0, ?, ?)",
            (nid, name, now, now)
        )
    # Insert existing edge between n1 and n2
    for src, tgt in [("n1", "n2"), ("n2", "n1")]:
        conn.execute(
            "INSERT INTO edges (source_id, target_id, edge_type, weight, "
            "created_at, updated_at, co_activations) "
            "VALUES (?, ?, 'hebbian', 0.5, ?, ?, 3)",
            (src, tgt, now, now)
        )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def cieu_db(tmp_path):
    """Create a minimal CIEU DB for event emission."""
    db_path = str(tmp_path / "test_cieu.db")
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE cieu_events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT,
            agent_id TEXT,
            decision TEXT,
            details TEXT,
            created_at REAL,
            provenance TEXT
        )
    """)
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def warmed_brain_db(brain_db):
    """Brain DB with >= WARMUP_THRESHOLD activation_log rows."""
    conn = sqlite3.connect(brain_db)
    now = time.time()
    # Insert WARMUP_THRESHOLD + 1 rows to pass warmup gate
    rows = [(f"n{(i % 3) + 1}", "warmup_seed", 0.5, now - i, "seed")
            for i in range(WARMUP_THRESHOLD + 1)]
    conn.executemany(
        "INSERT INTO activation_log (node_id, query_text, activation_score, "
        "timestamp, provenance) VALUES (?, ?, ?, ?, ?)",
        rows
    )
    conn.commit()
    conn.close()
    return brain_db


def _make_l1_cache(nodes=None):
    """Build a synthetic L1 cache entry."""
    if nodes is None:
        nodes = [
            {"node_id": "n1", "distance": 0.15, "hint": "governance core principles"},
            {"node_id": "n2", "distance": 0.22, "hint": "identity and values alignment"},
            {"node_id": "n3", "distance": 0.35, "hint": "brain architecture design"},
        ]
    return {
        "query_id": "test_q_001",
        "timestamp": time.time(),
        "top_k": nodes,
    }


# ── Test 1: Positive outcome -> positive Hebbian + access_count ──────

def test_positive_outcome_hebbian_and_access_count(warmed_brain_db, cieu_db):
    """Positive outcome events should strengthen co-activated edges and
    increment access_count for each fired node."""
    l1_cache = _make_l1_cache()
    # Outcome events that cite n1 and have keyword match for n2
    outcome_events = [
        {"event_type": "PostToolUse", "decision": "allow",
         "tool_results": "Node n1 provided good governance insight",
         "details": "identity values alignment confirmed"},
    ]

    result = writeback(l1_cache, outcome_events,
                       brain_db_path=warmed_brain_db, cieu_db_path=cieu_db)

    assert result["error"] is None
    assert result["outcome_sign"] == 1
    assert len(result["nodes_accessed"]) == 3

    # Verify access_count incremented
    conn = sqlite3.connect(warmed_brain_db)
    for nid in ["n1", "n2", "n3"]:
        row = conn.execute(
            "SELECT access_count FROM nodes WHERE id = ?", (nid,)
        ).fetchone()
        assert row[0] >= 1, f"access_count for {nid} should be >= 1"

    # Verify edge weight increased (n1-n2 had 0.5, should be higher now)
    row = conn.execute(
        "SELECT weight FROM edges WHERE source_id='n1' AND target_id='n2'"
    ).fetchone()
    assert row[0] > 0.5, f"Edge n1->n2 weight should have increased from 0.5, got {row[0]}"
    conn.close()

    # Verify CIEU event emitted
    conn = sqlite3.connect(cieu_db)
    events = conn.execute(
        "SELECT event_type FROM cieu_events"
    ).fetchall()
    conn.close()
    event_types = [e[0] for e in events]
    assert "BRAIN_HEBBIAN_UPDATE_POSITIVE" in event_types


# ── Test 2: CROBA event -> negative Hebbian (lr=0.15) ────────────────

def test_croba_negative_hebbian(warmed_brain_db, cieu_db):
    """CROBA/violation events should decay co-activated edges using lr=0.15.
    Outcome events must contain keyword matches for >= 2 nodes to trigger
    co-activation Hebbian (relevance must be > 0.3 background threshold)."""
    l1_cache = _make_l1_cache()
    # Outcome events that cite n1 explicitly AND keyword-match n2 (identity/values)
    # so that both nodes exceed RELEVANCE_BACKGROUND and form a co-activated pair
    outcome_events = [
        {"event_type": "CROBA_VIOLATION", "decision": "deny",
         "details": "CROBA boundary violation detected in n1 scope; "
                    "identity values alignment breach confirmed",
         "agent_id": "ceo"},
    ]

    result = writeback(l1_cache, outcome_events,
                       brain_db_path=warmed_brain_db, cieu_db_path=cieu_db)

    assert result["error"] is None
    assert result["outcome_sign"] == -1

    # Verify lr used is NEGATIVE_LR (0.15)
    assert len(result["applied_updates"]) >= 1, \
        "Should have at least 1 co-activated pair update"
    assert result["applied_updates"][0]["lr_used"] == NEGATIVE_LR

    # Verify edge weight decreased (n1-n2 had 0.5, should be lower now)
    conn = sqlite3.connect(warmed_brain_db)
    row = conn.execute(
        "SELECT weight FROM edges WHERE source_id='n1' AND target_id='n2'"
    ).fetchone()
    assert row[0] < 0.5, f"Edge n1->n2 weight should have decreased from 0.5, got {row[0]}"
    conn.close()

    # Verify CIEU event is DECAY
    conn = sqlite3.connect(cieu_db)
    events = conn.execute(
        "SELECT event_type FROM cieu_events"
    ).fetchall()
    conn.close()
    event_types = [e[0] for e in events]
    assert "BRAIN_HEBBIAN_DECAY" in event_types


# ── Test 3: Warmup gate < 5000 -> BRAIN_WARMUP_PENDING ───────────────

def test_warmup_gate_pending(brain_db, cieu_db):
    """When activation_log < WARMUP_THRESHOLD, Hebbian should be skipped
    but activation_log should still be written (bootstrap)."""
    l1_cache = _make_l1_cache()
    outcome_events = [
        {"event_type": "PostToolUse", "decision": "allow",
         "details": "normal operation"},
    ]

    result = writeback(l1_cache, outcome_events,
                       brain_db_path=brain_db, cieu_db_path=cieu_db)

    assert result["error"] is None
    assert result["warmup_pending"] is True
    assert len(result["applied_updates"]) == 0  # No Hebbian updates

    # Verify activation_log WAS written (bootstrap data)
    conn = sqlite3.connect(brain_db)
    count = conn.execute("SELECT count(*) FROM activation_log").fetchone()[0]
    conn.close()
    assert count >= 3  # One per top-k node

    # Verify BRAIN_WARMUP_PENDING CIEU event emitted
    conn = sqlite3.connect(cieu_db)
    events = conn.execute(
        "SELECT event_type FROM cieu_events"
    ).fetchall()
    conn.close()
    event_types = [e[0] for e in events]
    assert "BRAIN_WARMUP_PENDING" in event_types


# ── Test 4: Provenance='system:brain' on all activation_log rows ─────

def test_provenance_system_brain(brain_db, cieu_db):
    """All activation_log entries from writeback must have provenance='system:brain'."""
    l1_cache = _make_l1_cache()
    outcome_events = [
        {"event_type": "PostToolUse", "decision": "allow", "details": "ok"},
    ]

    writeback(l1_cache, outcome_events,
              brain_db_path=brain_db, cieu_db_path=cieu_db)

    conn = sqlite3.connect(brain_db)
    rows = conn.execute(
        "SELECT provenance FROM activation_log WHERE query_text LIKE 'L2_writeback:%'"
    ).fetchall()
    conn.close()

    assert len(rows) >= 3  # One per top-k node
    for row in rows:
        assert row[0] == 'system:brain', \
            f"activation_log provenance must be 'system:brain', got '{row[0]}'"


# ── Test 5: Error path -> BRAIN_WRITEBACK_FAILED + no crash ──────────

def test_error_path_no_crash(tmp_path, cieu_db):
    """When brain DB is corrupted (missing table), writeback should not raise
    but should emit BRAIN_WRITEBACK_FAILED and return error in result dict."""
    # Create a DB without the expected tables
    bad_db = str(tmp_path / "bad_brain.db")
    conn = sqlite3.connect(bad_db)
    conn.execute("CREATE TABLE dummy (id TEXT)")
    conn.commit()
    conn.close()

    l1_cache = _make_l1_cache()
    outcome_events = [
        {"event_type": "PostToolUse", "decision": "allow", "details": "ok"},
    ]

    # This should NOT raise
    result = writeback(l1_cache, outcome_events,
                       brain_db_path=bad_db, cieu_db_path=cieu_db)

    assert result["error"] is not None

    # Verify BRAIN_WRITEBACK_FAILED CIEU event emitted
    conn = sqlite3.connect(cieu_db)
    events = conn.execute(
        "SELECT event_type FROM cieu_events WHERE event_type = 'BRAIN_WRITEBACK_FAILED'"
    ).fetchall()
    conn.close()
    assert len(events) >= 1


# ── Test 6: Relevance tiers ─────────────────────────────────────────

def test_relevance_tiers():
    """Test the 3-tier relevance scoring: cited=1.0, keyword=0.6, background=0.3."""
    # Cited: node_id appears in event text
    node_cited = {"node_id": "n1", "hint": "governance core"}
    events_cite = [{"tool_results": "Used node n1 for decision"}]
    assert _compute_node_relevance(node_cited, events_cite) == RELEVANCE_CITED

    # Keyword: hint terms appear in event text
    node_kw = {"node_id": "n_other", "hint": "governance core principles"}
    events_kw = [{"details": "governance principles were applied correctly"}]
    assert _compute_node_relevance(node_kw, events_kw) == RELEVANCE_KEYWORD

    # Background: no match
    node_bg = {"node_id": "n_unrelated", "hint": "quantum physics theory"}
    events_bg = [{"details": "deployed new hook wiring"}]
    assert _compute_node_relevance(node_bg, events_bg) == RELEVANCE_BACKGROUND


# ── Test 7: Smoke integration -- synthetic data -> weight delta ──────

def test_smoke_synthetic_weight_delta(warmed_brain_db, cieu_db):
    """End-to-end: call writeback with synthetic data, verify brain weight changed."""
    conn_before = sqlite3.connect(warmed_brain_db)
    weight_before = conn_before.execute(
        "SELECT weight FROM edges WHERE source_id='n1' AND target_id='n2'"
    ).fetchone()[0]
    access_before = conn_before.execute(
        "SELECT access_count FROM nodes WHERE id='n1'"
    ).fetchone()[0]
    conn_before.close()

    l1_cache = _make_l1_cache()
    # Positive outcome citing n1
    outcome_events = [
        {"event_type": "PostToolUse", "decision": "allow",
         "tool_results": "Node n1 wisdom applied successfully",
         "details": "identity values alignment was key insight"},
    ]

    result = writeback(l1_cache, outcome_events,
                       brain_db_path=warmed_brain_db, cieu_db_path=cieu_db)

    assert result["error"] is None
    assert result["outcome_sign"] == 1

    conn_after = sqlite3.connect(warmed_brain_db)
    weight_after = conn_after.execute(
        "SELECT weight FROM edges WHERE source_id='n1' AND target_id='n2'"
    ).fetchone()[0]
    access_after = conn_after.execute(
        "SELECT access_count FROM nodes WHERE id='n1'"
    ).fetchone()[0]
    conn_after.close()

    assert weight_after > weight_before, \
        f"Weight should increase: before={weight_before}, after={weight_after}"
    assert access_after > access_before, \
        f"Access count should increase: before={access_before}, after={access_after}"

    # Verify at least one CIEU event was emitted
    assert len(result["cieu_event_ids"]) >= 1
