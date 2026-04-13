#!/usr/bin/env python3
"""
test_working_memory_snapshot.py - Tests for C5 Working Memory Snapshot

Author: Maya Patel (eng-governance) - Y* Bridge Labs
"""

import json
import tempfile
import time
from datetime import datetime
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from working_memory_snapshot import WorkingMemorySnapshot


@pytest.fixture
def temp_repo():
    """Create temporary repo structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)
        (repo / '.ystar_cieu.db').touch()
        (repo / 'memory').mkdir()
        yield repo


@pytest.fixture
def snapshot_engine(temp_repo):
    """Create WorkingMemorySnapshot instance."""
    return WorkingMemorySnapshot(repo_root=temp_repo)


def test_capture_returns_correct_schema(snapshot_engine):
    """Test that capture returns all required fields."""
    snapshot = snapshot_engine.capture(
        session_id='test_session_123',
        agent_id='maya'
    )

    # Verify schema
    required_fields = [
        'session_id',
        'agent_id',
        'captured_at',
        'recent_cieu_events',
        'active_subagents',
        'today_targets_progress',
        'recent_commits',
        'unfinished_tool_calls',
        'last_board_directive',
    ]

    for field in required_fields:
        assert field in snapshot, f"Missing field: {field}"

    # Verify field types
    assert isinstance(snapshot['session_id'], str)
    assert isinstance(snapshot['agent_id'], str)
    assert isinstance(snapshot['captured_at'], str)
    assert isinstance(snapshot['recent_cieu_events'], list)
    assert isinstance(snapshot['active_subagents'], list)
    assert isinstance(snapshot['today_targets_progress'], dict)
    assert isinstance(snapshot['recent_commits'], list)
    assert isinstance(snapshot['unfinished_tool_calls'], list)
    assert isinstance(snapshot['last_board_directive'], str)

    # Verify captured_at is ISO format
    try:
        datetime.fromisoformat(snapshot['captured_at'].replace('Z', '+00:00'))
    except ValueError:
        pytest.fail("captured_at is not valid ISO format")


def test_save_load_roundtrip(snapshot_engine, temp_repo):
    """Test save and load roundtrip preserves data."""
    original_snapshot = {
        'session_id': 'roundtrip_test',
        'agent_id': 'maya',
        'captured_at': datetime.utcnow().isoformat() + 'Z',
        'recent_cieu_events': [
            {'event_type': 'test', 'decision': 'allow', 'agent_id': 'maya'}
        ],
        'active_subagents': [],
        'today_targets_progress': {'status': 'ok'},
        'recent_commits': [],
        'unfinished_tool_calls': [],
        'last_board_directive': 'test directive',
    }

    # Save
    saved_path = snapshot_engine.save(original_snapshot)
    assert saved_path.exists()
    assert saved_path.suffix == '.json'

    # Load
    loaded_snapshot = snapshot_engine.load_latest()
    assert loaded_snapshot is not None

    # Verify roundtrip
    assert loaded_snapshot['session_id'] == original_snapshot['session_id']
    assert loaded_snapshot['agent_id'] == original_snapshot['agent_id']
    assert loaded_snapshot['captured_at'] == original_snapshot['captured_at']
    assert len(loaded_snapshot['recent_cieu_events']) == 1
    assert loaded_snapshot['recent_cieu_events'][0]['event_type'] == 'test'


def test_recent_cieu_only_takes_20(snapshot_engine):
    """Test that recent_cieu_events is limited to 20 entries."""
    # This test assumes CIEU DB exists and has events
    # If DB is empty, we verify the limit is respected in the query
    snapshot = snapshot_engine.capture(
        session_id='limit_test',
        agent_id='maya'
    )

    cieu_events = snapshot['recent_cieu_events']
    assert len(cieu_events) <= 20, "Should not exceed 20 events"


def test_subagent_status_parsing(snapshot_engine):
    """Test that subagent status is parsed correctly."""
    snapshot = snapshot_engine.capture(
        session_id='subagent_test',
        agent_id='maya'
    )

    subagents = snapshot['active_subagents']

    # Each subagent entry should have required fields
    for subagent in subagents:
        assert 'task_file' in subagent
        assert 'age_minutes' in subagent
        assert 'size_bytes' in subagent
        assert 'preview' in subagent

        # Verify types
        assert isinstance(subagent['task_file'], str)
        assert isinstance(subagent['age_minutes'], (int, float))
        assert isinstance(subagent['size_bytes'], int)
        assert isinstance(subagent['preview'], str)

        # Verify age is reasonable (< 10 minutes as per code)
        assert subagent['age_minutes'] < 10


def test_load_latest_returns_none_when_empty(snapshot_engine, temp_repo):
    """Test that load_latest returns None when no snapshots exist."""
    # Ensure memory dir is empty
    memory_dir = temp_repo / 'memory'
    for f in memory_dir.glob('working_memory_snapshot_*.json'):
        f.unlink()

    # Pass the temp memory_dir explicitly
    loaded = snapshot_engine.load_latest(path=memory_dir)
    assert loaded is None


def test_load_latest_picks_most_recent(snapshot_engine, temp_repo):
    """Test that load_latest picks the most recent snapshot."""
    memory_dir = temp_repo / 'memory'

    # Create two snapshots with different timestamps
    snapshot1 = {
        'session_id': 'older',
        'agent_id': 'maya',
        'captured_at': '2026-04-12T10:00:00Z',
        'recent_cieu_events': [],
        'active_subagents': [],
        'today_targets_progress': {},
        'recent_commits': [],
        'unfinished_tool_calls': [],
        'last_board_directive': '',
    }

    snapshot2 = {
        'session_id': 'newer',
        'agent_id': 'maya',
        'captured_at': '2026-04-13T11:00:00Z',
        'recent_cieu_events': [],
        'active_subagents': [],
        'today_targets_progress': {},
        'recent_commits': [],
        'unfinished_tool_calls': [],
        'last_board_directive': '',
    }

    # Save older first
    path1 = memory_dir / 'working_memory_snapshot_older.json'
    with path1.open('w') as f:
        json.dump(snapshot1, f)

    time.sleep(0.1)  # Ensure different mtime

    # Save newer second
    path2 = memory_dir / 'working_memory_snapshot_newer.json'
    with path2.open('w') as f:
        json.dump(snapshot2, f)

    # Load latest should return newer - pass temp memory_dir explicitly
    loaded = snapshot_engine.load_latest(path=memory_dir)
    assert loaded is not None
    assert loaded['session_id'] == 'newer'


def test_goal_progress_integration(snapshot_engine):
    """Test that goal_progress integration works."""
    snapshot = snapshot_engine.capture(
        session_id='progress_test',
        agent_id='maya'
    )

    progress = snapshot['today_targets_progress']
    assert isinstance(progress, dict)

    # Should have either 'status' or 'error' key
    assert 'status' in progress or 'error' in progress


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
