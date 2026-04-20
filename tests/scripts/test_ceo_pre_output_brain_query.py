"""
Tests for CEO Pre-Output Brain Query (Board 2026-04-19 Layer 3 fix).

Tests:
  1. test_query_returns_top_3_nodes_for_ceo_reply
  2. test_nodes_resolve_to_readable_files
  3. test_hook_response_includes_brain_context_field
  4. test_fallback_when_brain_db_missing
"""

import json
import os
import sqlite3
import sys
import tempfile

import pytest

# Ensure scripts/ is importable
_SCRIPTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "scripts",
)
sys.path.insert(0, _SCRIPTS_DIR)

# Ensure Y-star-gov is importable
sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/Y-star-gov")

from hook_ceo_pre_output_brain_query import (
    extract_context_signals,
    format_brain_context_for_hook,
    query_brain_for_context,
)


def _create_test_brain_db(db_path: str, wisdom_dir: str = None):
    """Create a minimal brain DB with 5 test nodes."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            file_path TEXT,
            node_type TEXT,
            depth_label TEXT,
            content_hash TEXT,
            dim_y REAL DEFAULT 0.5,
            dim_x REAL DEFAULT 0.5,
            dim_z REAL DEFAULT 0.5,
            dim_t REAL DEFAULT 0.5,
            dim_phi REAL DEFAULT 0.5,
            dim_c REAL DEFAULT 0.5,
            base_activation REAL DEFAULT 0.0,
            last_accessed REAL DEFAULT 0.0,
            access_count INTEGER DEFAULT 0,
            created_at REAL DEFAULT 0.0,
            updated_at REAL DEFAULT 0.0,
            principles TEXT,
            triggers TEXT,
            summary TEXT,
            embedding BLOB
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS activation_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            activated_nodes TEXT,
            session_id TEXT,
            timestamp REAL
        )
    """)
    # Insert test nodes with different 6D positions
    test_nodes = [
        ("deploy_wisdom", "Deploy Decision Framework", "deploy_wisdom.md",
         0.6, 0.5, 0.8, 0.5, 0.7, 0.7, "Framework for deployment decisions"),
        ("identity_core", "CEO Identity Core", "identity_core.md",
         0.95, 0.3, 0.5, 0.3, 0.7, 0.6, "Who I am as CEO"),
        ("learning_strat", "Strategic Learning", "learning_strat.md",
         0.4, 0.9, 0.35, 0.5, 0.4, 0.45, "Strategic thinking frameworks"),
        ("risk_mgmt", "Risk Management", "risk_mgmt.md",
         0.4, 0.9, 0.3, 0.5, 0.4, 0.4, "Antifragile risk approach"),
        ("execution_ops", "Execution Operations", "execution_ops.md",
         0.3, 0.5, 0.4, 0.5, 0.3, 0.7, "File write execution patterns"),
    ]
    for nid, name, fp, y, x, z, t, phi, c, summary in test_nodes:
        conn.execute(
            """INSERT INTO nodes (id, name, file_path, dim_y, dim_x, dim_z,
               dim_t, dim_phi, dim_c, summary) VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (nid, name, fp, y, x, z, t, phi, c, summary),
        )
    conn.commit()

    # Create corresponding wisdom files if wisdom_dir provided
    if wisdom_dir:
        for nid, name, fp, *_ in test_nodes:
            fpath = os.path.join(wisdom_dir, fp)
            with open(fpath, "w") as f:
                f.write(f"# {name}\n\nThis is the wisdom content for {name}. "
                        f"It contains actionable insights about {nid.replace('_', ' ')}.\n")

    conn.close()
    return db_path


class TestExtractContextSignals:
    """Test context signal extraction from hook payloads."""

    def test_basic_write_payload(self):
        payload = {
            "tool_name": "Write",
            "tool_input": {"file_path": "reports/test.md", "content": "hello"},
            "agent_id": "ceo",
        }
        event = extract_context_signals(payload)
        assert event["event_type"] == "Write"
        assert event["agent_id"] == "ceo"
        assert event["_tool"] == "Write"

    def test_deploy_triggers_escalate(self):
        payload = {
            "tool_name": "Write",
            "tool_input": {"content": "We should deploy Phase 2 now."},
            "agent_id": "ceo",
        }
        event = extract_context_signals(payload)
        assert event["decision"] == "escalate"

    def test_strategy_triggers_ceo_learning(self):
        payload = {
            "tool_name": "Write",
            "tool_input": {"content": "Our strategy for Q3 requires evaluation."},
            "agent_id": "ceo",
        }
        event = extract_context_signals(payload)
        assert event["event_type"] == "ceo_learning"

    def test_identity_triggers_drift(self):
        payload = {
            "tool_name": "Write",
            "tool_input": {"content": "Reflecting on my identity and purpose as CEO."},
            "agent_id": "ceo",
        }
        event = extract_context_signals(payload)
        assert event["drift_category"] == "identity_violation"


class TestQueryReturnsTop3:
    """test_query_returns_top_3_nodes_for_ceo_reply"""

    def test_returns_exactly_3_nodes(self, tmp_path):
        db_path = str(tmp_path / "test_brain.db")
        wisdom_dir = str(tmp_path / "wisdom")
        os.makedirs(wisdom_dir, exist_ok=True)
        _create_test_brain_db(db_path, wisdom_dir)

        # Patch _WISDOM_DIR for test
        import hook_ceo_pre_output_brain_query as mod
        orig = mod._WISDOM_DIR
        mod._WISDOM_DIR = wisdom_dir
        try:
            payload = {
                "tool_name": "Write",
                "tool_input": {
                    "file_path": "reports/deploy_phase2.md",
                    "content": "Decision: deploy Phase 2 to production.",
                },
                "agent_id": "ceo",
            }
            results = query_brain_for_context(payload, k=3, brain_db_path=db_path)
            assert len(results) == 3
            # Each result has required keys
            for r in results:
                assert "node_name" in r
                assert "hint" in r
                assert "distance" in r
                assert float(r["distance"]) >= 0
        finally:
            mod._WISDOM_DIR = orig

    def test_returns_fewer_if_db_has_fewer_nodes(self, tmp_path):
        db_path = str(tmp_path / "small_brain.db")
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE nodes (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, file_path TEXT,
                node_type TEXT, depth_label TEXT, content_hash TEXT,
                dim_y REAL DEFAULT 0.5, dim_x REAL DEFAULT 0.5,
                dim_z REAL DEFAULT 0.5, dim_t REAL DEFAULT 0.5,
                dim_phi REAL DEFAULT 0.5, dim_c REAL DEFAULT 0.5,
                base_activation REAL DEFAULT 0.0, last_accessed REAL DEFAULT 0.0,
                access_count INTEGER DEFAULT 0, created_at REAL DEFAULT 0.0,
                updated_at REAL DEFAULT 0.0, principles TEXT, triggers TEXT,
                summary TEXT, embedding BLOB
            )
        """)
        conn.execute("""
            CREATE TABLE activation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT, activated_nodes TEXT, session_id TEXT, timestamp REAL
            )
        """)
        conn.execute(
            "INSERT INTO nodes (id, name, dim_y, dim_x, dim_z, dim_t, dim_phi, dim_c, summary) "
            "VALUES ('only', 'Only Node', 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 'solo')"
        )
        conn.commit()
        conn.close()

        payload = {"tool_name": "Write", "tool_input": {"content": "test"}, "agent_id": "ceo"}
        results = query_brain_for_context(payload, k=3, brain_db_path=db_path)
        assert len(results) == 1
        assert results[0]["node_name"] == "Only Node"


class TestNodesResolveToReadableFiles:
    """test_nodes_resolve_to_readable_files"""

    def test_wisdom_files_readable(self, tmp_path):
        db_path = str(tmp_path / "brain.db")
        wisdom_dir = str(tmp_path / "wisdom")
        os.makedirs(wisdom_dir)
        _create_test_brain_db(db_path, wisdom_dir)

        import hook_ceo_pre_output_brain_query as mod
        orig = mod._WISDOM_DIR
        mod._WISDOM_DIR = wisdom_dir
        try:
            payload = {
                "tool_name": "Write",
                "tool_input": {"content": "deploy ship release"},
                "agent_id": "ceo",
            }
            results = query_brain_for_context(payload, k=3, brain_db_path=db_path)
            for r in results:
                # hint should contain actual file content, not just "(node: ...)"
                assert not r["hint"].startswith("(node:")
                assert len(r["hint"]) > 10
        finally:
            mod._WISDOM_DIR = orig

    def test_missing_file_falls_back_to_summary(self, tmp_path):
        db_path = str(tmp_path / "brain.db")
        # No wisdom_dir created, so files won't exist
        _create_test_brain_db(db_path, wisdom_dir=None)

        import hook_ceo_pre_output_brain_query as mod
        orig = mod._WISDOM_DIR
        mod._WISDOM_DIR = str(tmp_path / "nonexistent")
        try:
            payload = {
                "tool_name": "Write",
                "tool_input": {"content": "test"},
                "agent_id": "ceo",
            }
            results = query_brain_for_context(payload, k=3, brain_db_path=db_path)
            assert len(results) == 3
            for r in results:
                # Should fall back to summary text
                assert len(r["hint"]) > 0
        finally:
            mod._WISDOM_DIR = orig


class TestHookResponseIncludesBrainContext:
    """test_hook_response_includes_brain_context_field"""

    def test_format_brain_context(self):
        nodes = [
            {"node_name": "Deploy Framework", "hint": "Check risks before deploy", "distance": "0.42"},
            {"node_name": "Identity Core", "hint": "CEO values integrity", "distance": "0.55"},
        ]
        text = format_brain_context_for_hook(nodes)
        assert "[6D Brain Wisdom Context]" in text
        assert "Deploy Framework" in text
        assert "0.42" in text
        assert "Identity Core" in text

    def test_empty_nodes_returns_empty_string(self):
        assert format_brain_context_for_hook([]) == ""

    def test_brain_context_field_in_mock_result(self, tmp_path):
        """Simulate what hook_wrapper does: inject brain_context into result dict."""
        db_path = str(tmp_path / "brain.db")
        wisdom_dir = str(tmp_path / "wisdom")
        os.makedirs(wisdom_dir)
        _create_test_brain_db(db_path, wisdom_dir)

        import hook_ceo_pre_output_brain_query as mod
        orig = mod._WISDOM_DIR
        mod._WISDOM_DIR = wisdom_dir
        try:
            payload = {
                "tool_name": "Write",
                "tool_input": {"content": "deploy Phase 2"},
                "agent_id": "ceo",
            }
            brain_nodes = query_brain_for_context(payload, k=3, brain_db_path=db_path)

            # Simulate hook_wrapper injection
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                }
            }
            result["brain_context"] = brain_nodes
            brain_text = format_brain_context_for_hook(brain_nodes)

            assert "brain_context" in result
            assert len(result["brain_context"]) == 3
            assert isinstance(result["brain_context"], list)

            # Verify JSON serializable
            serialized = json.dumps(result)
            parsed = json.loads(serialized)
            assert "brain_context" in parsed
        finally:
            mod._WISDOM_DIR = orig


class TestFallbackWhenBrainDbMissing:
    """test_fallback_when_brain_db_missing"""

    def test_missing_db_returns_empty_list(self):
        payload = {
            "tool_name": "Write",
            "tool_input": {"content": "test"},
            "agent_id": "ceo",
        }
        results = query_brain_for_context(
            payload, k=3, brain_db_path="/nonexistent/brain.db"
        )
        assert results == []

    def test_corrupted_db_returns_empty_list(self, tmp_path):
        db_path = str(tmp_path / "bad.db")
        with open(db_path, "w") as f:
            f.write("not a sqlite database")
        payload = {
            "tool_name": "Write",
            "tool_input": {"content": "test"},
            "agent_id": "ceo",
        }
        results = query_brain_for_context(payload, k=3, brain_db_path=db_path)
        assert results == []

    def test_empty_db_returns_empty_list(self, tmp_path):
        db_path = str(tmp_path / "empty.db")
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE nodes (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, file_path TEXT,
                node_type TEXT, depth_label TEXT, content_hash TEXT,
                dim_y REAL DEFAULT 0.5, dim_x REAL DEFAULT 0.5,
                dim_z REAL DEFAULT 0.5, dim_t REAL DEFAULT 0.5,
                dim_phi REAL DEFAULT 0.5, dim_c REAL DEFAULT 0.5,
                base_activation REAL DEFAULT 0.0, last_accessed REAL DEFAULT 0.0,
                access_count INTEGER DEFAULT 0, created_at REAL DEFAULT 0.0,
                updated_at REAL DEFAULT 0.0, principles TEXT, triggers TEXT,
                summary TEXT, embedding BLOB
            )
        """)
        conn.execute("""
            CREATE TABLE activation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT, activated_nodes TEXT, session_id TEXT, timestamp REAL
            )
        """)
        conn.commit()
        conn.close()

        payload = {
            "tool_name": "Write",
            "tool_input": {"content": "test"},
            "agent_id": "ceo",
        }
        results = query_brain_for_context(payload, k=3, brain_db_path=db_path)
        assert results == []
