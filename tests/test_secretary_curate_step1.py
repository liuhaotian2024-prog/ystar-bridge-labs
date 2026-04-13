#!/usr/bin/env python3
"""Unit tests for Secretary Curation Pipeline Step 1 (skill_extract).

Tests:
  - extract_board_corrections: CIEU query for Board corrections
  - identify_skill_patterns: Pattern matching from corrections
  - format_skill_draft: Hermes 4-section formatting
  - step1_skill_extract: End-to-end skill extraction
  - Red-line violation detection
"""
import json
import sqlite3
import tempfile
import time
from pathlib import Path

import pytest

# Import functions from secretary_curate.py
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from secretary_curate import (
    extract_board_corrections,
    identify_skill_patterns,
    format_skill_draft,
    check_redline_violation,
    step1_skill_extract,
    FORBIDDEN_KEYWORDS
)


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace structure."""
    workspace = tmp_path / "ystar-company"
    workspace.mkdir()

    # Create CIEU database
    cieu_db = workspace / ".ystar_cieu.db"
    conn = sqlite3.connect(str(cieu_db))
    conn.execute("""
        CREATE TABLE cieu_events (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT UNIQUE,
            seq_global INTEGER,
            created_at REAL,
            session_id TEXT,
            agent_id TEXT,
            event_type TEXT,
            decision TEXT,
            passed INTEGER,
            task_description TEXT,
            params_json TEXT
        )
    """)
    conn.commit()

    # Create memory and knowledge directories
    (workspace / "memory").mkdir()
    (workspace / "knowledge" / "ceo" / "skills" / "_draft_").mkdir(parents=True)

    # Create session config
    session_cfg = {
        "session_id": "test_session_001",
        "agent_id": "ceo"
    }
    (workspace / ".ystar_session.json").write_text(json.dumps(session_cfg))

    return workspace, cieu_db, conn


def test_extract_board_corrections_empty(temp_workspace):
    """Test extract_board_corrections with empty database."""
    workspace, cieu_db, conn = temp_workspace
    session_start = time.time()

    corrections = extract_board_corrections(cieu_db, session_start)
    assert corrections == []

    conn.close()


def test_extract_board_corrections_with_data(temp_workspace):
    """Test extract_board_corrections with Board correction events."""
    workspace, cieu_db, conn = temp_workspace
    session_start = time.time() - 3600  # 1 hour ago

    # Insert test events
    test_events = [
        ("BOARD_DECISION", "Must use priority_brief over DISPATCH", "{}", session_start + 100),
        ("INTENT_ADJUSTED", "Change approach to X", '{"original": "A", "adjusted": "B"}', session_start + 200),
        ("ALLOW", "Normal operation", "{}", session_start + 300),  # Should not be included
    ]

    for event_type, desc, params, ts in test_events:
        conn.execute("""
            INSERT INTO cieu_events (event_id, seq_global, created_at, session_id, agent_id,
                                    event_type, decision, passed, task_description, params_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (f"evt_{ts}", int(ts * 1e6), ts, "test_session_001", "ceo",
              event_type, "allow", 1, desc, params))
    conn.commit()

    corrections = extract_board_corrections(cieu_db, session_start)

    # Should find 2 events (BOARD_DECISION and INTENT_ADJUSTED, not ALLOW)
    assert len(corrections) == 2
    assert corrections[0]["type"] in ["BOARD_DECISION", "INTENT_ADJUSTED"]
    assert "priority_brief" in corrections[0]["description"] or "approach" in corrections[0]["description"]

    conn.close()


def test_identify_skill_patterns_basic(temp_workspace):
    """Test identify_skill_patterns with simple corrections."""
    workspace, cieu_db, conn = temp_workspace

    corrections = [
        {
            "type": "BOARD_DECISION",
            "description": "Must always check GitHub before reading local files",
            "params": "{}",
            "timestamp": time.time()
        },
        {
            "type": "INTENT_ADJUSTED",
            "description": "Should never fabricate test results",
            "params": "{}",
            "timestamp": time.time()
        }
    ]

    wisdom_path = workspace / "memory" / "wisdom_package_latest.md"
    wisdom_path.write_text("Recent events show emphasis on GitHub-first workflow")

    handoff_path = workspace / "memory" / "session_handoff.md"
    handoff_path.write_text("No fabrication allowed")

    patterns = identify_skill_patterns(corrections, wisdom_path, handoff_path)

    # Should identify at least 1 pattern (MVP limit is 2)
    assert len(patterns) >= 1
    assert len(patterns) <= 2
    assert "source" in patterns[0]
    assert patterns[0]["source"] == "board_correction"

    conn.close()


def test_format_skill_draft_structure(temp_workspace):
    """Test format_skill_draft produces valid Hermes 4-section format."""
    workspace, cieu_db, conn = temp_workspace

    pattern = {
        "trigger_event": "BOARD_DECISION",
        "context": "Always verify external state before making assertions",
        "source": "board_correction",
        "timestamp": time.time()
    }

    draft = format_skill_draft(pattern, "test_session_001")

    # Check Hermes sections present
    assert "## 1. Trigger" in draft
    assert "## 2. Procedure" in draft
    assert "## 3. Principles" in draft
    assert "## 4. Red Lines" in draft

    # Check metadata
    assert "DRAFT" in draft
    assert "test_ses" in draft[:150]  # Session ID truncated in skill name
    assert "BOARD_DECISION" in draft

    conn.close()


def test_check_redline_violation_detect():
    """Test check_redline_violation detects S-4 violations."""
    # Should detect violations
    assert check_redline_violation("You should decide to merge this") == "decide"
    assert check_redline_violation("Approve this charter amendment") == "approve"
    assert check_redline_violation("Commit production code now") == "commit production"

    # Should not trigger on safe content
    assert check_redline_violation("This procedure helps identify issues") is None
    # Note: Simple keyword match intentionally flags "decide" even in safe contexts
    # More sophisticated NLP can refine this, but MVP uses strict keyword matching


def test_check_redline_violation_case_insensitive():
    """Test red-line detection is case-insensitive."""
    assert check_redline_violation("DECIDE NOW") == "decide"
    assert check_redline_violation("Strategy for Launch") == "strategy"


def test_step1_skill_extract_integration(temp_workspace, monkeypatch):
    """Integration test for step1_skill_extract."""
    workspace, cieu_db, conn = temp_workspace

    # Mock YSTAR_DIR to use temp workspace
    import secretary_curate
    monkeypatch.setattr(secretary_curate, "YSTAR_DIR", workspace)
    monkeypatch.setattr(secretary_curate, "CIEU_DB", cieu_db)
    monkeypatch.setattr(secretary_curate, "MEMORY_DIR", workspace / "memory")
    monkeypatch.setattr(secretary_curate, "KNOWLEDGE_DIR", workspace / "knowledge")

    # Insert test Board correction
    session_start = time.time() - 3600
    conn.execute("""
        INSERT INTO cieu_events (event_id, seq_global, created_at, session_id, agent_id,
                                event_type, decision, passed, task_description, params_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ("evt_001", int(session_start * 1e6), session_start + 100, "test_session_001", "board",
          "BOARD_DECISION", "allow", 1, "Must always run tests before committing", "{}"))
    conn.commit()

    # Create wisdom package
    wisdom_path = workspace / "memory" / "wisdom_package_latest.md"
    wisdom_path.write_text("Board emphasized testing discipline")

    # Create handoff
    handoff_path = workspace / "memory" / "session_handoff.md"
    handoff_path.write_text("Test-first approach")

    ctx = {
        "session_id": "test_session_001",
        "trigger": "session_close",
        "agent": "ceo"
    }

    # Run step 1
    result = step1_skill_extract(ctx)

    # Verify results
    assert result["step"] == 1
    assert result["status"] == "implemented"
    assert result["corrections_analyzed"] >= 1

    # If patterns found, check draft files created
    if result["patterns_found"] > 0:
        assert result["skills_drafted"] > 0
        draft_dir = workspace / "knowledge" / "ceo" / "skills" / "_draft_"
        assert draft_dir.exists()
        drafts = list(draft_dir.glob("*.md"))
        assert len(drafts) > 0

    conn.close()


def test_step1_skill_extract_no_violations(temp_workspace, monkeypatch):
    """Test step1 rejects drafts with red-line violations."""
    workspace, cieu_db, conn = temp_workspace

    import secretary_curate
    monkeypatch.setattr(secretary_curate, "YSTAR_DIR", workspace)
    monkeypatch.setattr(secretary_curate, "CIEU_DB", cieu_db)
    monkeypatch.setattr(secretary_curate, "MEMORY_DIR", workspace / "memory")
    monkeypatch.setattr(secretary_curate, "KNOWLEDGE_DIR", workspace / "knowledge")

    # Insert correction with violation-triggering language
    session_start = time.time() - 3600
    conn.execute("""
        INSERT INTO cieu_events (event_id, seq_global, created_at, session_id, agent_id,
                                event_type, decision, passed, task_description, params_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ("evt_002", int(session_start * 1e6), session_start + 100, "test_session_001", "board",
          "BOARD_DECISION", "allow", 1, "Secretary must decide on strategy", "{}"))
    conn.commit()

    wisdom_path = workspace / "memory" / "wisdom_package_latest.md"
    wisdom_path.write_text("")
    handoff_path = workspace / "memory" / "session_handoff.md"
    handoff_path.write_text("")

    ctx = {"session_id": "test_session_001", "trigger": "session_close", "agent": "ceo"}

    # Mock format_skill_draft to return violation content
    original_format = secretary_curate.format_skill_draft
    def mock_format(pattern, session_id):
        draft = original_format(pattern, session_id)
        # Inject violation into TODO section
        return draft.replace("[TODO:", "[TODO: decide on strategy and")

    monkeypatch.setattr(secretary_curate, "format_skill_draft", mock_format)

    result = step1_skill_extract(ctx)

    # Even if patterns found, violations should be rejected
    # No files should be written
    draft_dir = workspace / "knowledge" / "ceo" / "skills" / "_draft_"
    drafts = list(draft_dir.glob("*.md")) if draft_dir.exists() else []
    # Violations detected = files rejected
    assert result["skills_drafted"] == 0

    conn.close()
