"""
Test: mint_agent_brain — 9-agent brain template parity + idempotent.

Milestone 8b 2026-04-21: verify all 9 agent brains have schema parity +
seed operation is idempotent (re-run doesn't duplicate anchor nodes).

M-tag: M-1 Survivability (全 9 agent persistent brain, 无 schema drift).
"""
import os
import sys
import tempfile
import sqlite3
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mint_agent_brain import AGENTS, mint, db_path_for, init_schema, seed_minimal


def test_all_9_agents_have_brain_db_in_production():
    """All 10 agents (aiden + 9) must have brain.db in production workspace."""
    W = "/Users/haotianliu/.openclaw/workspace/ystar-company"
    for name in ["aiden", "ethan", "leo", "maya", "ryan", "jordan",
                 "sofia", "zara", "marco", "samantha"]:
        path = f"{W}/{name}_brain.db"
        assert os.path.exists(path), f"{name}_brain.db MISSING"


def test_schema_parity_across_all_9_production_brains():
    """All 10 brain.db must have identical nodes schema (21 cols)."""
    W = "/Users/haotianliu/.openclaw/workspace/ystar-company"
    baseline = None
    for name in ["aiden", "ethan", "leo", "maya", "ryan", "jordan",
                 "sofia", "zara", "marco", "samantha"]:
        path = f"{W}/{name}_brain.db"
        if not os.path.exists(path):
            continue
        conn = sqlite3.connect(path)
        cols = sorted(r[1] for r in conn.execute("PRAGMA table_info(nodes)").fetchall())
        conn.close()
        if baseline is None:
            baseline = cols
        else:
            assert cols == baseline, f"{name}_brain.db schema drift vs baseline"


def test_mint_creates_db_with_seed_nodes():
    """mint() on a fresh path creates db and seeds 4 anchor nodes."""
    with tempfile.TemporaryDirectory() as td:
        # Override db path within test
        import mint_agent_brain
        original = mint_agent_brain.WORKSPACE
        mint_agent_brain.WORKSPACE = __import__("pathlib").Path(td)
        try:
            r = mint("testagent", "Test Agent", "Test Role", "test-role")
            assert r["action"] == "CREATED"
            assert r["seeded"] == 4
            assert r["nodes_total"] == 4
        finally:
            mint_agent_brain.WORKSPACE = original


def test_mint_is_idempotent():
    """Re-running mint on existing db doesn't duplicate seed nodes."""
    with tempfile.TemporaryDirectory() as td:
        import mint_agent_brain
        original = mint_agent_brain.WORKSPACE
        mint_agent_brain.WORKSPACE = __import__("pathlib").Path(td)
        try:
            r1 = mint("testagent", "Test Agent", "Test Role", "test-role")
            r2 = mint("testagent", "Test Agent", "Test Role", "test-role")
            assert r2["nodes_total"] == 4, "second mint must not duplicate anchor nodes"
            assert r2["action"] == "UPDATED"
        finally:
            mint_agent_brain.WORKSPACE = original


def test_seed_creates_identity_edges_to_charter():
    """Each agent's identity node must have edges to charter anchor nodes."""
    with tempfile.TemporaryDirectory() as td:
        conn = sqlite3.connect(f"{td}/test.db")
        init_schema(conn)
        seed_minimal(conn, "testkey", "Test Name", "Test Role", "test-tag")

        # Identity → M_TRIANGLE + WORK_METHODOLOGY + AGENTS_MD
        edges = conn.execute(
            "SELECT target_id FROM edges WHERE source_id=?",
            ("testkey/identity/self",)
        ).fetchall()
        conn.close()

        targets = {e[0] for e in edges}
        assert "testkey/charter/M_TRIANGLE" in targets
        assert "testkey/charter/WORK_METHODOLOGY" in targets
        assert "testkey/role/AGENTS_MD" in targets


def test_agent_registry_has_8_non_aiden_non_ethan():
    """AGENTS list must cover exactly the 8 agents missing brain before Milestone 8b."""
    keys = {a[0] for a in AGENTS}
    expected = {"leo", "maya", "ryan", "jordan", "sofia", "zara", "marco", "samantha"}
    assert keys == expected, f"expected {expected}, got {keys}"
