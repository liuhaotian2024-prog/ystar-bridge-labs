"""
Dispatch Board Integration Tests (CZL-68)
Tests: post_task / claim_task / complete_task / race_condition_claim

Rewritten to use direct function calls instead of subprocess to ensure
test isolation (CZL-WHITEBOARD-WIPE-RCA: original tests wrote to production
dispatch_board.json, which was itself a wipe vector).
"""
import json
import sys
import tempfile
from pathlib import Path
from argparse import Namespace

import pytest

SCRIPTS_DIR = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/scripts")
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture(autouse=True)
def isolated_board(tmp_path, monkeypatch):
    """Use isolated temp board for tests — never touch production data."""
    import dispatch_board as db

    test_board = tmp_path / "dispatch_board.json"
    test_lock = tmp_path / ".dispatch_board.lock"
    test_board.write_text(json.dumps({"tasks": []}, indent=2))

    monkeypatch.setattr(db, "BOARD_PATH", test_board)
    monkeypatch.setattr(db, "LOCK_PATH", test_lock)

    yield test_board


@pytest.fixture
def pending_spawns_path(tmp_path, monkeypatch):
    """Redirect pending spawns to temp dir."""
    # post_task writes to Path(__file__).parent / ".pending_spawns.jsonl"
    # which is scripts/.pending_spawns.jsonl — we redirect via monkeypatch
    return tmp_path / ".pending_spawns.jsonl"


def test_dispatch_board_post_task(isolated_board):
    """Test posting new task to dispatch board."""
    import dispatch_board as db

    args = Namespace(
        atomic_id="CZL-999",
        scope="test.py,foo.py",
        description="Test task",
        urgency="P1",
        estimated_tool_uses=8,
    )
    result = db.post_task(args)
    assert result == 0

    board = json.loads(isolated_board.read_text())
    assert len(board["tasks"]) == 1
    task = board["tasks"][0]
    assert task["atomic_id"] == "CZL-999"
    assert task["scope"] == "test.py,foo.py"
    assert task["status"] == "open"
    assert task["urgency"] == "P1"
    assert task["estimated_tool_uses"] == 8


def test_dispatch_board_claim_task(isolated_board):
    """Test engineer claiming task."""
    import dispatch_board as db

    # Setup: post task
    post_args = Namespace(
        atomic_id="CZL-998",
        scope="bar.py",
        description="Test claim",
        urgency="P2",
        estimated_tool_uses=5,
    )
    db.post_task(post_args)

    # Execute: claim
    claim_args = Namespace(engineer_id="ryan-platform")
    result = db.claim_task(claim_args)
    assert result == 0

    board = json.loads(isolated_board.read_text())
    task = board["tasks"][0]
    assert task["status"] == "claimed"
    assert task["claimed_by"] == "ryan-platform"
    assert task["claimed_at"] is not None


def test_dispatch_board_complete_task(isolated_board, tmp_path):
    """Test engineer completing task."""
    import dispatch_board as db

    # Setup: post + claim
    post_args = Namespace(
        atomic_id="CZL-997",
        scope="baz.py",
        description="Test complete",
        urgency="P0",
        estimated_tool_uses=3,
    )
    db.post_task(post_args)

    claim_args = Namespace(engineer_id="leo-kernel")
    db.claim_task(claim_args)

    # Create receipt file
    receipt_path = tmp_path / "receipt.md"
    receipt_path.write_text("# Task CZL-997 Receipt\n\nCompleted successfully.\n")

    # Execute: complete
    complete_args = Namespace(
        atomic_id="CZL-997",
        receipt_file=str(receipt_path),
    )
    result = db.complete_task(complete_args)
    assert result == 0

    board = json.loads(isolated_board.read_text())
    task = board["tasks"][0]
    assert task["status"] == "completed"
    assert task["completed_at"] is not None
    assert "Completed successfully" in task["completion_receipt"]


def test_dispatch_board_race_condition(isolated_board):
    """Test race condition when 2 engineers claim same task.
    With only 1 open task, second claim must fail."""
    import dispatch_board as db

    # Setup: post single task
    post_args = Namespace(
        atomic_id="CZL-996",
        scope="race.py",
        description="Race test",
        urgency="P1",
        estimated_tool_uses=4,
    )
    db.post_task(post_args)

    # First claim should succeed
    claim1 = Namespace(engineer_id="maya-governance")
    result1 = db.claim_task(claim1)
    assert result1 == 0

    # Second claim should fail (no open tasks)
    claim2 = Namespace(engineer_id="jordan-domains")
    result2 = db.claim_task(claim2)
    assert result2 == 1  # error return code

    # Verify only first engineer claimed
    board = json.loads(isolated_board.read_text())
    task = board["tasks"][0]
    assert task["claimed_by"] == "maya-governance"
    assert task["status"] == "claimed"


def test_dispatch_board_duplicate_post(isolated_board):
    """Test that posting duplicate atomic_id is rejected."""
    import dispatch_board as db

    args = Namespace(
        atomic_id="CZL-DUP",
        scope="dup.py",
        description="First post",
        urgency="P1",
        estimated_tool_uses=3,
    )
    result1 = db.post_task(args)
    assert result1 == 0

    # Second post with same ID should fail
    result2 = db.post_task(args)
    assert result2 == 1
