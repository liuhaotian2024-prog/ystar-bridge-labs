#!/usr/bin/env python3
"""
Regression tests for CZL-BRAIN-ADD-NODE-PRESERVE:
Verify that add_node() and add_edge() use ON CONFLICT upsert
and never reset access_count, last_accessed, created_at, or co_activations.
"""
import os
import sys
import time
import tempfile
import sqlite3
import json
import pytest

# Ensure scripts/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
from aiden_brain import init_db, add_node, add_edge, get_db, touch_node, hebbian_update


@pytest.fixture
def tmp_db():
    """Create a temporary database for each test.
    Also adds the 'embedding' column which exists in production DB
    (added via ALTER TABLE migration) but is not in init_db() schema."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    conn = sqlite3.connect(path)
    try:
        conn.execute("ALTER TABLE nodes ADD COLUMN embedding BLOB")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # column already exists
    conn.close()
    yield path
    os.unlink(path)


class TestAddNodePreservesState:
    """Case 1+2: re-adding a node must not reset access_count, last_accessed, created_at."""

    def test_access_count_preserved_on_re_add(self, tmp_db):
        """Case 1: create node, set access_count=5, re-add -> access_count stays 5."""
        add_node("WHO_I_AM", "Who I Am", file_path="WHO_I_AM.md",
                 node_type="hub", db_path=tmp_db)

        # Manually set access_count to 5 (simulating real usage)
        conn = get_db(tmp_db)
        conn.execute("UPDATE nodes SET access_count = 5 WHERE id = 'WHO_I_AM'")
        conn.commit()
        conn.close()

        # Re-add the same node (as aiden_import would)
        add_node("WHO_I_AM", "Who I Am v2", file_path="WHO_I_AM.md",
                 node_type="hub", summary="updated summary", db_path=tmp_db)

        conn = get_db(tmp_db)
        row = conn.execute("SELECT access_count, name, summary FROM nodes WHERE id='WHO_I_AM'").fetchone()
        conn.close()
        assert row["access_count"] == 5, f"access_count was reset to {row['access_count']}"
        assert row["name"] == "Who I Am v2", "name should be updated"
        assert row["summary"] == "updated summary", "summary should be updated"

    def test_last_accessed_preserved_on_re_add(self, tmp_db):
        """Case 2: last_accessed must not be reset on re-add."""
        add_node("TEST_NODE", "Test", db_path=tmp_db)

        # Simulate a touch (sets last_accessed to a known time)
        known_time = 1700000000.0
        conn = get_db(tmp_db)
        conn.execute("UPDATE nodes SET last_accessed = ? WHERE id = 'TEST_NODE'", (known_time,))
        conn.commit()
        conn.close()

        # Re-add
        add_node("TEST_NODE", "Test Updated", db_path=tmp_db)

        conn = get_db(tmp_db)
        row = conn.execute("SELECT last_accessed FROM nodes WHERE id='TEST_NODE'").fetchone()
        conn.close()
        assert row["last_accessed"] == known_time, \
            f"last_accessed was reset to {row['last_accessed']}, expected {known_time}"

    def test_created_at_preserved_on_re_add(self, tmp_db):
        """Case 2: created_at must never change on re-add."""
        add_node("TEST_NODE", "Test", db_path=tmp_db)

        conn = get_db(tmp_db)
        row = conn.execute("SELECT created_at FROM nodes WHERE id='TEST_NODE'").fetchone()
        original_created = row["created_at"]
        conn.close()

        time.sleep(0.05)  # ensure time progresses

        # Re-add
        add_node("TEST_NODE", "Test Updated", db_path=tmp_db)

        conn = get_db(tmp_db)
        row = conn.execute("SELECT created_at FROM nodes WHERE id='TEST_NODE'").fetchone()
        conn.close()
        assert row["created_at"] == original_created, \
            f"created_at was reset from {original_created} to {row['created_at']}"

    def test_base_activation_preserved_on_re_add(self, tmp_db):
        """base_activation must not be reset on re-add."""
        add_node("TEST_NODE", "Test", db_path=tmp_db)

        conn = get_db(tmp_db)
        conn.execute("UPDATE nodes SET base_activation = 0.75 WHERE id = 'TEST_NODE'")
        conn.commit()
        conn.close()

        add_node("TEST_NODE", "Test Updated", db_path=tmp_db)

        conn = get_db(tmp_db)
        row = conn.execute("SELECT base_activation FROM nodes WHERE id='TEST_NODE'").fetchone()
        conn.close()
        assert row["base_activation"] == 0.75, \
            f"base_activation was reset to {row['base_activation']}"

    def test_embedding_preserved_on_re_add(self, tmp_db):
        """embedding blob must not be destroyed on re-add."""
        add_node("TEST_NODE", "Test", db_path=tmp_db)

        fake_embedding = b'\x00\x01\x02\x03'
        conn = get_db(tmp_db)
        conn.execute("UPDATE nodes SET embedding = ? WHERE id = 'TEST_NODE'", (fake_embedding,))
        conn.commit()
        conn.close()

        add_node("TEST_NODE", "Test Updated", db_path=tmp_db)

        conn = get_db(tmp_db)
        row = conn.execute("SELECT embedding FROM nodes WHERE id='TEST_NODE'").fetchone()
        conn.close()
        assert row["embedding"] == fake_embedding, "embedding was destroyed on re-add"

    def test_triggers_preserved_on_re_add(self, tmp_db):
        """triggers field must not be destroyed on re-add."""
        add_node("TEST_NODE", "Test", db_path=tmp_db)

        triggers_json = json.dumps(["morning_review", "crisis_mode"])
        conn = get_db(tmp_db)
        conn.execute("UPDATE nodes SET triggers = ? WHERE id = 'TEST_NODE'", (triggers_json,))
        conn.commit()
        conn.close()

        add_node("TEST_NODE", "Test Updated", db_path=tmp_db)

        conn = get_db(tmp_db)
        row = conn.execute("SELECT triggers FROM nodes WHERE id='TEST_NODE'").fetchone()
        conn.close()
        assert row["triggers"] == triggers_json, "triggers was destroyed on re-add"


class TestAddNodeNewInsert:
    """Case 4: new node (no conflict) -> INSERT path works normally."""

    def test_new_node_insert(self, tmp_db):
        add_node("BRAND_NEW", "Brand New Node", file_path="test.md",
                 node_type="meta", depth_label="operational",
                 dims={"y": 0.8, "x": 0.6}, principles=["test_principle"],
                 summary="A new node", content_hash="abc123", db_path=tmp_db)

        conn = get_db(tmp_db)
        row = conn.execute("SELECT * FROM nodes WHERE id='BRAND_NEW'").fetchone()
        conn.close()
        assert row is not None
        assert row["name"] == "Brand New Node"
        assert row["file_path"] == "test.md"
        assert row["access_count"] == 0
        assert row["content_hash"] == "abc123"
        assert row["dim_y"] == 0.8

    def test_content_hash_updated_on_re_add(self, tmp_db):
        """content_hash should update when node content changes."""
        add_node("TEST_NODE", "Test", content_hash="hash_v1", db_path=tmp_db)
        add_node("TEST_NODE", "Test", content_hash="hash_v2", db_path=tmp_db)

        conn = get_db(tmp_db)
        row = conn.execute("SELECT content_hash FROM nodes WHERE id='TEST_NODE'").fetchone()
        conn.close()
        assert row["content_hash"] == "hash_v2"


class TestAddEdgePreservesState:
    """Verify add_edge() preserves co_activations and created_at."""

    def test_co_activations_preserved_on_re_add(self, tmp_db):
        add_node("A", "Node A", db_path=tmp_db)
        add_node("B", "Node B", db_path=tmp_db)
        add_edge("A", "B", weight=0.5, db_path=tmp_db)

        # Simulate hebbian learning increments
        conn = get_db(tmp_db)
        conn.execute("UPDATE edges SET co_activations = 10 WHERE source_id='A' AND target_id='B'")
        conn.execute("UPDATE edges SET co_activations = 10 WHERE source_id='B' AND target_id='A'")
        conn.commit()
        conn.close()

        # Re-add same edge (as aiden_import would)
        add_edge("A", "B", weight=0.7, db_path=tmp_db)

        conn = get_db(tmp_db)
        row = conn.execute(
            "SELECT co_activations, weight FROM edges WHERE source_id='A' AND target_id='B'"
        ).fetchone()
        conn.close()
        assert row["co_activations"] == 10, \
            f"co_activations was reset to {row['co_activations']}"
        assert row["weight"] == 0.7, "weight should be updated"

    def test_edge_created_at_preserved(self, tmp_db):
        add_node("A", "Node A", db_path=tmp_db)
        add_node("B", "Node B", db_path=tmp_db)
        add_edge("A", "B", weight=0.5, db_path=tmp_db)

        conn = get_db(tmp_db)
        row = conn.execute(
            "SELECT created_at FROM edges WHERE source_id='A' AND target_id='B'"
        ).fetchone()
        original_created = row["created_at"]
        conn.close()

        time.sleep(0.05)
        add_edge("A", "B", weight=0.8, db_path=tmp_db)

        conn = get_db(tmp_db)
        row = conn.execute(
            "SELECT created_at FROM edges WHERE source_id='A' AND target_id='B'"
        ).fetchone()
        conn.close()
        assert row["created_at"] == original_created


class TestBatchImportPreservation:
    """Case 5: simulate batch aiden_import on existing DB -> no access_count drop."""

    def test_batch_import_preserves_counts(self, tmp_db):
        """Simulate what aiden_import does: add_node for many nodes, some pre-existing."""
        # Create some nodes with accumulated access_counts
        nodes_with_counts = {
            "WHO_I_AM": 15,
            "team/ceo": 42,
            "meta/courage": 7,
        }
        for nid, count in nodes_with_counts.items():
            add_node(nid, f"Node {nid}", db_path=tmp_db)
            conn = get_db(tmp_db)
            conn.execute("UPDATE nodes SET access_count = ? WHERE id = ?", (count, nid))
            conn.commit()
            conn.close()

        # Simulate aiden_import re-adding all nodes
        for nid in nodes_with_counts:
            add_node(nid, f"Node {nid} reimported", content_hash="new_hash",
                     db_path=tmp_db)

        # Verify all access_counts preserved
        conn = get_db(tmp_db)
        for nid, expected_count in nodes_with_counts.items():
            row = conn.execute(
                "SELECT access_count FROM nodes WHERE id=?", (nid,)
            ).fetchone()
            assert row["access_count"] == expected_count, \
                f"{nid}: access_count was {row['access_count']}, expected {expected_count}"
        conn.close()


class TestNoInsertOrReplace:
    """Structural test: ensure INSERT OR REPLACE is not in aiden_brain.py."""

    def test_no_insert_or_replace_in_source(self):
        brain_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "scripts", "aiden_brain.py"
        )
        with open(brain_path, "r") as f:
            source = f.read()
        assert "INSERT OR REPLACE" not in source, \
            "aiden_brain.py still contains INSERT OR REPLACE -- the self-destruct pattern"
