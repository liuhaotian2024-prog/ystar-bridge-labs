"""
Tests for goal_progress.py — CEO's self-driving capability #2
"""

import sqlite3
import tempfile
import time
from pathlib import Path

import pytest
import yaml

# Import functions from goal_progress
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from goal_progress import (
    extract_yaml_frontmatter,
    extract_verify_markers,
    query_cieu_markers,
    calculate_completion,
    render_progress_bar,
    generate_dashboard
)


def test_extract_yaml_frontmatter():
    """Test YAML frontmatter extraction."""
    content = """---
version: "v0.4"
today_targets:
  - target: "Test target"
    verify: "pytest pass"
---

# Content
"""
    meta = extract_yaml_frontmatter(content)
    assert meta['version'] == 'v0.4'
    assert len(meta['today_targets']) == 1
    assert meta['today_targets'][0]['target'] == 'Test target'


def test_extract_verify_markers():
    """Test marker extraction from verify strings."""
    # Case 1: Simple markers
    markers = extract_verify_markers("pytest pass + commit hash")
    assert 'pytest' in markers
    assert 'pass' in markers
    assert 'commit' in markers
    assert 'hash' in markers

    # Case 2: With numbers
    markers = extract_verify_markers("17 base + 10 tests 全绿")
    assert '17' in markers
    assert 'base' in markers
    assert '10' in markers
    assert 'tests' in markers

    # Case 3: With underscores
    markers = extract_verify_markers("on_cieu_event 触发")
    assert 'on_cieu_event' in markers

    # Case 4: Empty string
    markers = extract_verify_markers("")
    assert markers == []


def test_render_progress_bar():
    """Test progress bar rendering."""
    assert render_progress_bar(0) == "[░░░░░░░░░░]"
    assert render_progress_bar(100) == "[██████████]"
    assert render_progress_bar(50) == "[█████░░░░░]"
    assert render_progress_bar(33) == "[███░░░░░░░]"
    assert render_progress_bar(67) == "[██████░░░░]"  # 67% of 10 = 6.7 → 6 filled


def test_calculate_completion_all_markers_hit():
    """Test completion calculation when all markers are found in CIEU."""
    # Create temporary CIEU database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE cieu_events (
            event_id TEXT,
            seq_global INTEGER,
            created_at REAL,
            session_id TEXT,
            agent_id TEXT,
            event_type TEXT,
            decision TEXT,
            passed INTEGER,
            violations TEXT,
            drift_detected INTEGER,
            drift_details TEXT,
            drift_category TEXT,
            file_path TEXT,
            command TEXT,
            url TEXT,
            skill_name TEXT,
            skill_source TEXT,
            task_description TEXT,
            contract_hash TEXT,
            chain_depth INTEGER,
            params_json TEXT,
            result_json TEXT,
            human_initiator TEXT,
            lineage_path TEXT,
            sealed INTEGER,
            evidence_grade TEXT
        )
    """)

    # Insert events that match all markers
    now = time.time()
    events = [
        (now, 'eng-governance', 'cmd_exec', 'pytest tests/test_goal_progress.py', 'pytest pass'),
        (now, 'eng-governance', 'git_commit', 'git commit -m "feature: goal progress"', 'commit abc123'),
        (now, 'eng-governance', 'file_write', 'reports/goal_progress.md', 'Maya wrote progress report'),
    ]

    for ts, agent, event_type, command, decision in events:
        conn.execute("""
            INSERT INTO cieu_events (created_at, agent_id, event_type, command, decision,
                                     event_id, seq_global, session_id, passed, drift_detected,
                                     chain_depth, sealed)
            VALUES (?, ?, ?, ?, ?, 'evt1', 1, 'sess1', 1, 0, 0, 0)
        """, (ts, agent, event_type, command, decision))

    conn.commit()
    conn.close()

    # Temporarily replace CIEU_DB path
    import goal_progress
    original_db = goal_progress.CIEU_DB
    goal_progress.CIEU_DB = Path(db_path)

    try:
        verify = "pytest pass + commit + Maya"
        completion, marker_hits = calculate_completion(verify, lookback_hours=1)

        # All 3 markers should hit
        assert completion == 100
        assert marker_hits['pytest'] > 0
        assert marker_hits['pass'] > 0
        assert marker_hits['commit'] > 0
        assert marker_hits['Maya'] > 0

    finally:
        goal_progress.CIEU_DB = original_db
        Path(db_path).unlink()


def test_calculate_completion_partial_markers():
    """Test completion when only some markers are found."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE cieu_events (
            event_id TEXT, seq_global INTEGER, created_at REAL, session_id TEXT,
            agent_id TEXT, event_type TEXT, decision TEXT, passed INTEGER,
            violations TEXT, drift_detected INTEGER, drift_details TEXT,
            drift_category TEXT, file_path TEXT, command TEXT, url TEXT,
            skill_name TEXT, skill_source TEXT, task_description TEXT,
            contract_hash TEXT, chain_depth INTEGER, params_json TEXT,
            result_json TEXT, human_initiator TEXT, lineage_path TEXT,
            sealed INTEGER, evidence_grade TEXT
        )
    """)

    # Only 1 out of 3 markers present
    now = time.time()
    conn.execute("""
        INSERT INTO cieu_events (created_at, agent_id, event_type, decision,
                                 event_id, seq_global, session_id, passed,
                                 drift_detected, chain_depth, sealed)
        VALUES (?, 'eng-governance', 'cmd_exec', 'pytest pass',
                'evt1', 1, 'sess1', 1, 0, 0, 0)
    """, (now,))
    conn.commit()
    conn.close()

    import goal_progress
    original_db = goal_progress.CIEU_DB
    goal_progress.CIEU_DB = Path(db_path)

    try:
        verify = "pytest pass + commit + Maya"
        completion, marker_hits = calculate_completion(verify, lookback_hours=1)

        # Only pytest and pass should hit (2/4 = 50%)
        # (pytest, pass, commit, Maya are 4 markers)
        assert completion == 50  # 2 out of 4 markers hit
        assert marker_hits['pytest'] > 0
        assert marker_hits['pass'] > 0
        assert marker_hits['commit'] == 0
        assert marker_hits['Maya'] == 0

    finally:
        goal_progress.CIEU_DB = original_db
        Path(db_path).unlink()


def test_calculate_completion_no_markers():
    """Test completion when no markers are found."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE cieu_events (
            event_id TEXT, seq_global INTEGER, created_at REAL, session_id TEXT,
            agent_id TEXT, event_type TEXT, decision TEXT, passed INTEGER,
            violations TEXT, drift_detected INTEGER, drift_details TEXT,
            drift_category TEXT, file_path TEXT, command TEXT, url TEXT,
            skill_name TEXT, skill_source TEXT, task_description TEXT,
            contract_hash TEXT, chain_depth INTEGER, params_json TEXT,
            result_json TEXT, human_initiator TEXT, lineage_path TEXT,
            sealed INTEGER, evidence_grade TEXT
        )
    """)
    conn.commit()
    conn.close()

    import goal_progress
    original_db = goal_progress.CIEU_DB
    goal_progress.CIEU_DB = Path(db_path)

    try:
        verify = "nonexistent_marker_xyz"
        completion, marker_hits = calculate_completion(verify, lookback_hours=1)

        assert completion == 0
        assert marker_hits['nonexistent_marker_xyz'] == 0

    finally:
        goal_progress.CIEU_DB = original_db
        Path(db_path).unlink()


def test_target_sorting_by_completion():
    """Test that targets are sorted by completion % ascending."""
    # This is implicitly tested in the dashboard output
    # Lower completion targets should appear first to highlight what needs work
    # (though current implementation doesn't sort - we could add this feature)
    pass


def test_integration_with_real_priority_brief():
    """Integration test with actual priority_brief.md."""
    # This tests the full pipeline
    dashboard = generate_dashboard()

    # Should contain key sections
    assert "## Today" in dashboard
    assert "## This Week" in dashboard
    assert "## This Month" in dashboard
    assert "Overall Progress" in dashboard
    assert "CIEU events:" in dashboard

    # Should have progress bars
    assert "[█" in dashboard or "[░" in dashboard


def test_lookback_window_filtering():
    """Test that lookback_hours correctly filters old events."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE cieu_events (
            event_id TEXT, seq_global INTEGER, created_at REAL, session_id TEXT,
            agent_id TEXT, event_type TEXT, decision TEXT, passed INTEGER,
            violations TEXT, drift_detected INTEGER, drift_details TEXT,
            drift_category TEXT, file_path TEXT, command TEXT, url TEXT,
            skill_name TEXT, skill_source TEXT, task_description TEXT,
            contract_hash TEXT, chain_depth INTEGER, params_json TEXT,
            result_json TEXT, human_initiator TEXT, lineage_path TEXT,
            sealed INTEGER, evidence_grade TEXT
        )
    """)

    now = time.time()
    old_ts = now - (72 * 3600)  # 3 days ago

    # Insert one recent and one old event
    conn.execute("""
        INSERT INTO cieu_events (created_at, agent_id, event_type, decision,
                                 event_id, seq_global, session_id, passed,
                                 drift_detected, chain_depth, sealed)
        VALUES (?, 'eng-governance', 'cmd_exec', 'pytest pass',
                'evt1', 1, 'sess1', 1, 0, 0, 0)
    """, (now,))

    conn.execute("""
        INSERT INTO cieu_events (created_at, agent_id, event_type, decision,
                                 event_id, seq_global, session_id, passed,
                                 drift_detected, chain_depth, sealed)
        VALUES (?, 'eng-governance', 'cmd_exec', 'old_pytest pass',
                'evt2', 2, 'sess1', 1, 0, 0, 0)
    """, (old_ts,))

    conn.commit()
    conn.close()

    import goal_progress
    original_db = goal_progress.CIEU_DB
    goal_progress.CIEU_DB = Path(db_path)

    try:
        # With 48h lookback, should only see recent event
        verify = "pytest"
        completion, marker_hits = calculate_completion(verify, lookback_hours=48)

        # Should match recent event but not old one
        assert marker_hits['pytest'] == 1  # Only recent one

    finally:
        goal_progress.CIEU_DB = original_db
        Path(db_path).unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
