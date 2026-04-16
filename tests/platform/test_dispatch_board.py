"""
Dispatch Board Integration Tests (CZL-68)
Tests: post_task / claim_task / complete_task / race_condition_claim
"""
import json
import subprocess
import tempfile
from pathlib import Path
import pytest

BOARD_PATH = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/governance/dispatch_board.json")
DISPATCH_BOARD_CLI = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/dispatch_board.py")


@pytest.fixture(autouse=True)
def reset_board():
    """Reset dispatch board before each test."""
    BOARD_PATH.write_text('{"tasks": []}')
    yield
    BOARD_PATH.write_text('{"tasks": []}')


def test_dispatch_board_post_task():
    """Test posting new task to dispatch board."""
    result = subprocess.run(
        [
            "python3", str(DISPATCH_BOARD_CLI), "post",
            "--atomic_id", "CZL-999",
            "--scope", "test.py,foo.py",
            "--description", "Test task",
            "--urgency", "P1",
            "--estimated_tool_uses", "8"
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Post failed: {result.stderr}"
    assert "Posted task CZL-999" in result.stdout

    # Verify board state
    board = json.loads(BOARD_PATH.read_text())
    assert len(board["tasks"]) == 1
    task = board["tasks"][0]
    assert task["atomic_id"] == "CZL-999"
    assert task["scope"] == "test.py,foo.py"
    assert task["status"] == "open"
    assert task["urgency"] == "P1"
    assert task["estimated_tool_uses"] == 8


def test_dispatch_board_claim_task():
    """Test engineer claiming task."""
    # Setup: post task
    subprocess.run(
        [
            "python3", str(DISPATCH_BOARD_CLI), "post",
            "--atomic_id", "CZL-998",
            "--scope", "bar.py",
            "--description", "Test claim",
            "--urgency", "P2",
            "--estimated_tool_uses", "5"
        ],
        check=True,
    )

    # Execute: claim
    result = subprocess.run(
        [
            "python3", str(DISPATCH_BOARD_CLI), "claim",
            "--engineer_id", "ryan-platform"
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Claim failed: {result.stderr}"
    assert "Claimed task CZL-998" in result.stdout
    assert "ryan-platform" in result.stdout

    # Verify board state
    board = json.loads(BOARD_PATH.read_text())
    task = board["tasks"][0]
    assert task["status"] == "claimed"
    assert task["claimed_by"] == "ryan-platform"
    assert task["claimed_at"] is not None


def test_dispatch_board_complete_task():
    """Test engineer completing task."""
    # Setup: post + claim
    subprocess.run(
        [
            "python3", str(DISPATCH_BOARD_CLI), "post",
            "--atomic_id", "CZL-997",
            "--scope", "baz.py",
            "--description", "Test complete",
            "--urgency", "P0",
            "--estimated_tool_uses", "3"
        ],
        check=True,
    )
    subprocess.run(
        [
            "python3", str(DISPATCH_BOARD_CLI), "claim",
            "--engineer_id", "leo-kernel"
        ],
        check=True,
    )

    # Create receipt file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        receipt_path = f.name
        f.write("# Task CZL-997 Receipt\n\nCompleted successfully.\n")

    try:
        # Execute: complete
        result = subprocess.run(
            [
                "python3", str(DISPATCH_BOARD_CLI), "complete",
                "--atomic_id", "CZL-997",
                "--receipt_file", receipt_path
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Complete failed: {result.stderr}"
        assert "Completed task CZL-997" in result.stdout

        # Verify board state
        board = json.loads(BOARD_PATH.read_text())
        task = board["tasks"][0]
        assert task["status"] == "completed"
        assert task["completed_at"] is not None
        assert "Completed successfully" in task["completion_receipt"]
    finally:
        Path(receipt_path).unlink()


def test_dispatch_board_race_condition():
    """Test race condition when 2 engineers claim same task."""
    # Setup: post task
    subprocess.run(
        [
            "python3", str(DISPATCH_BOARD_CLI), "post",
            "--atomic_id", "CZL-996",
            "--scope", "race.py",
            "--description", "Race test",
            "--urgency", "P1",
            "--estimated_tool_uses", "4"
        ],
        check=True,
    )

    # First claim should succeed
    result1 = subprocess.run(
        [
            "python3", str(DISPATCH_BOARD_CLI), "claim",
            "--engineer_id", "maya-governance"
        ],
        capture_output=True,
        text=True,
    )
    assert result1.returncode == 0, "First claim should succeed"

    # Second claim should fail (no open tasks)
    result2 = subprocess.run(
        [
            "python3", str(DISPATCH_BOARD_CLI), "claim",
            "--engineer_id", "jordan-domains"
        ],
        capture_output=True,
        text=True,
    )
    assert result2.returncode != 0, "Second claim should fail"
    assert "No open tasks" in result2.stderr

    # Verify only first engineer claimed
    board = json.loads(BOARD_PATH.read_text())
    task = board["tasks"][0]
    assert task["claimed_by"] == "maya-governance"
    assert task["status"] == "claimed"
