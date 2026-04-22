"""
Test: ethan_brain pilot — schema parity + seed + stats.

Milestone 8 2026-04-21: Ethan brain pilot, prove 9-agent brain template.
Verifies schema match with aiden_brain (prevent drift across 9 agents).

M-tag: M-1 Survivability (per-agent persistent brain, 9 agent 空脑 gap).
"""
import os
import sys
import tempfile
import sqlite3
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ethan_brain import init_db, add_node, seed_from_who_i_am, stats


def test_init_db_creates_3_tables():
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, "test_ethan.db")
        conn = init_db(db)
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()]
        conn.close()

        assert "nodes" in tables
        assert "edges" in tables
        assert "activation_log" in tables


def test_schema_matches_aiden_brain():
    """Ethan brain schema must match aiden_brain for daemon reusability."""
    aiden_db = "/Users/haotianliu/.openclaw/workspace/ystar-company/aiden_brain.db"
    if not os.path.exists(aiden_db):
        pytest.skip("aiden_brain.db not present in test env")

    with tempfile.TemporaryDirectory() as td:
        ethan_db = os.path.join(td, "ethan.db")
        conn_e = init_db(ethan_db)
        conn_a = sqlite3.connect(aiden_db)

        for table in ["nodes", "edges", "activation_log"]:
            e_cols = sorted(r[1] for r in conn_e.execute(f"PRAGMA table_info({table})").fetchall())
            a_cols = sorted(r[1] for r in conn_a.execute(f"PRAGMA table_info({table})").fetchall())
            assert e_cols == a_cols, f"{table} schema drift: ethan={e_cols} vs aiden={a_cols}"

        conn_e.close()
        conn_a.close()


def test_add_node_persists():
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, "test.db")
        conn = init_db(db)
        add_node(conn, "ethan/test/abc123", "Test Ethan Node",
                 node_type="ethan_test", summary="for test")
        conn.commit()

        r = conn.execute(
            "SELECT id, name, node_type FROM nodes WHERE id=?",
            ("ethan/test/abc123",)
        ).fetchone()
        conn.close()

        assert r is not None
        assert r[0] == "ethan/test/abc123"
        assert r[1] == "Test Ethan Node"
        assert r[2] == "ethan_test"


def test_seed_from_who_i_am_returns_count():
    """Seeder returns node count from WHO_I_AM sections."""
    from pathlib import Path

    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, "test.db")
        conn = init_db(db)

        # Create a minimal WHO_I_AM mock with 2 sections
        mock_md = Path(td) / "mock_who_i_am.md"
        mock_md.write_text("# Top Title\n\n## Section 1 — First\n\ntext\n\n## Section 2 — Second\n\ntext\n")

        count = seed_from_who_i_am(conn, md_path=mock_md)
        assert count == 2

        # Verify nodes created
        n = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        assert n == 2
        conn.close()


def test_stats_reports_counts():
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, "test.db")
        conn = init_db(db)
        add_node(conn, "ethan/x/1", "Node1")
        add_node(conn, "ethan/x/2", "Node2")
        conn.commit()

        s = stats(conn)
        assert s["nodes"] == 2
        assert s["edges"] == 0
        assert s["activations"] == 0
        conn.close()
