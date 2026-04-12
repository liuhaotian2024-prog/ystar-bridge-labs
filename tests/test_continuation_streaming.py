"""
test_continuation_streaming.py — Unit tests for Closure 3 (continuation streaming).

Tests:
- Normal update to action_queue
- Idempotency (modulo timestamp)
- Atomic write on failure
- Missing continuation file bootstraps
"""
import json
import os
import time
from pathlib import Path
from unittest.mock import patch

import pytest
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import continuation_writer as cw


@pytest.fixture
def temp_repo(tmp_path):
    """Create temporary repo with memory directory."""
    repo = tmp_path / "ystar-company"
    repo.mkdir()
    (repo / "memory").mkdir()
    (repo / "scripts").mkdir()
    (repo / "scripts" / "hook_debug.log").touch()
    return repo


def test_rewrite_updates_action_queue_item(temp_repo):
    """Update should mark action_queue item as done."""
    continuation_path = temp_repo / "memory" / "continuation.json"

    # Initial state with pending task
    initial_state = {
        "generated_at": "2026-04-12T00:00:00",
        "generated_by": "ceo",
        "campaign": {},
        "team_state": {},
        "action_queue": [
            {
                "seq": 1,
                "task_id": "task_123",
                "action": "implement_feature",
                "command": "do_work",
                "done": False
            }
        ],
        "obligations": []
    }

    continuation_path.write_text(json.dumps(initial_state, indent=2))

    # Apply update
    updates = {
        "event": "INTENT_COMPLETED",
        "task_id": "task_123",
        "role": "cto",
        "task": "implement feature X",
        "output": "path/to/output"
    }

    cw.rewrite_continuation(temp_repo, updates)

    # Verify update
    with open(continuation_path) as f:
        new_state = json.load(f)

    action = new_state["action_queue"][0]
    assert action["done"] is True
    assert "completed_at" in action
    assert new_state.get("last_updated_ts") is not None


def test_rewrite_is_idempotent_modulo_timestamp(temp_repo):
    """Repeated identical updates should produce same result (except timestamp)."""
    continuation_path = temp_repo / "memory" / "continuation.json"

    initial_state = {
        "generated_at": "2026-04-12T00:00:00",
        "generated_by": "ceo",
        "campaign": {},
        "team_state": {},
        "action_queue": [
            {"seq": 1, "task_id": "task_123", "action": "test", "done": False}
        ],
        "obligations": []
    }

    continuation_path.write_text(json.dumps(initial_state, indent=2))

    updates = {
        "event": "INTENT_COMPLETED",
        "task_id": "task_123",
        "role": "cto",
        "task": "test task",
        "output": "output"
    }

    # Apply update twice
    cw.rewrite_continuation(temp_repo, updates)
    time.sleep(0.01)  # Small delay to ensure different timestamp
    with open(continuation_path) as f:
        state1 = json.load(f)

    cw.rewrite_continuation(temp_repo, updates)
    with open(continuation_path) as f:
        state2 = json.load(f)

    # Same structural content (action marked done, team_state updated)
    assert state1["action_queue"][0]["done"] is True
    assert state2["action_queue"][0]["done"] is True
    assert state1["team_state"]["cto"]["progress"] == "completed"
    assert state2["team_state"]["cto"]["progress"] == "completed"
    # Timestamps differ (last_updated_ts and completed_at both update)
    assert state1["last_updated_ts"] != state2["last_updated_ts"]


def test_rewrite_atomic_no_partial_on_failure(temp_repo):
    """Failed write should not leave partial/corrupt continuation.json."""
    continuation_path = temp_repo / "memory" / "continuation.json"

    initial_state = {
        "generated_at": "2026-04-12T00:00:00",
        "generated_by": "ceo",
        "campaign": {},
        "team_state": {},
        "action_queue": [],
        "obligations": []
    }

    continuation_path.write_text(json.dumps(initial_state, indent=2))
    original_content = continuation_path.read_text()

    # Mock os.replace to fail
    updates = {
        "event": "INTENT_COMPLETED",
        "task_id": "task_123",
        "role": "cto",
        "task": "test",
        "output": "out"
    }

    with patch('os.replace', side_effect=OSError("simulated failure")):
        # Should fail-open (not raise)
        cw.rewrite_continuation(temp_repo, updates)

    # Original file should be unchanged
    assert continuation_path.read_text() == original_content


def test_missing_continuation_file_bootstraps(temp_repo):
    """If continuation.json doesn't exist, should create it."""
    continuation_path = temp_repo / "memory" / "continuation.json"
    assert not continuation_path.exists()

    updates = {
        "event": "INTENT_COMPLETED",
        "task_id": "task_123",
        "role": "cto",
        "task": "test task",
        "output": "output"
    }

    cw.rewrite_continuation(temp_repo, updates)

    # File should now exist
    assert continuation_path.exists()

    with open(continuation_path) as f:
        state = json.load(f)

    assert state["team_state"]["cto"]["task"] == "test task"
    assert state["team_state"]["cto"]["progress"] == "completed"


def test_obligations_cleared_by_task(temp_repo):
    """Obligations with cleared_by=task_id should be removed."""
    continuation_path = temp_repo / "memory" / "continuation.json"

    initial_state = {
        "generated_at": "2026-04-12T00:00:00",
        "generated_by": "ceo",
        "campaign": {},
        "team_state": {},
        "action_queue": [],
        "obligations": [
            {"content": "obligation 1", "cleared_by": "task_123"},
            {"content": "obligation 2", "cleared_by": "task_999"},
            {"content": "obligation 3"}
        ]
    }

    continuation_path.write_text(json.dumps(initial_state, indent=2))

    updates = {
        "event": "INTENT_COMPLETED",
        "task_id": "task_123",
        "role": "cto",
        "task": "test",
        "output": "out"
    }

    cw.rewrite_continuation(temp_repo, updates)

    with open(continuation_path) as f:
        state = json.load(f)

    # Only task_123 obligation should be removed
    assert len(state["obligations"]) == 2
    assert all(ob.get("cleared_by") != "task_123" for ob in state["obligations"])
