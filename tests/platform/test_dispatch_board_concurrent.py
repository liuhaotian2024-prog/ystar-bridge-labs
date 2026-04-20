"""
Concurrent Dispatch Board Regression Tests (CZL-WHITEBOARD-WIPE-RCA)

Tests the atomic-write + fcntl lock + wipe-protection sanity check
that prevents the 37->0 task wipe incident from recurring.

Root cause: non-atomic read-modify-write with open("w") truncation
racing concurrent readers/writers. Fix: separate lockfile +
temp-file-then-rename + sanity check on task count drops.
"""
import json
import os
import sys
import tempfile
import subprocess
import multiprocessing
from pathlib import Path

import pytest

SCRIPTS_DIR = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/scripts")
BOARD_PATH = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/governance/dispatch_board.json")
LOCK_PATH = BOARD_PATH.parent / ".dispatch_board.lock"
DISPATCH_BOARD_CLI = SCRIPTS_DIR / "dispatch_board.py"

# Add scripts dir to path so we can import dispatch_board internals
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture(autouse=True)
def isolated_board(tmp_path, monkeypatch):
    """Use a temporary board file for each test to avoid touching production data."""
    test_board = tmp_path / "dispatch_board.json"
    test_lock = tmp_path / ".dispatch_board.lock"
    test_board.write_text(json.dumps({"tasks": []}, indent=2))

    # Monkeypatch the module-level paths
    import dispatch_board as db
    monkeypatch.setattr(db, "BOARD_PATH", test_board)
    monkeypatch.setattr(db, "LOCK_PATH", test_lock)

    yield test_board


def _seed_board(board_path: Path, n_tasks: int) -> list:
    """Seed the board with n open tasks. Returns list of atomic_ids."""
    tasks = []
    for i in range(n_tasks):
        atomic_id = f"TEST-{i:04d}"
        tasks.append({
            "atomic_id": atomic_id,
            "scope": f"test_{i}.py",
            "description": f"Test task {i}",
            "urgency": "P1",
            "estimated_tool_uses": 5,
            "status": "open",
            "posted_at": f"2026-04-19T17:00:{i:02d}+00:00",
            "claimed_by": None,
            "claimed_at": None,
            "completed_at": None,
            "completion_receipt": None,
        })
    board_path.write_text(json.dumps({"tasks": tasks}, indent=2))
    return [t["atomic_id"] for t in tasks]


def test_atomic_write_no_truncation(isolated_board):
    """Verify that _write_board_locked uses temp-file-then-rename,
    not open('w') which truncates before lock acquisition."""
    import dispatch_board as db

    # Seed 10 tasks
    _seed_board(isolated_board, 10)

    # Write via locked path
    lock_fd = db._acquire_lock()
    try:
        board = db._read_board_locked()
        assert len(board["tasks"]) == 10

        # Add one more task
        board["tasks"].append({
            "atomic_id": "TEST-NEW",
            "scope": "new.py",
            "description": "New task",
            "urgency": "P1",
            "estimated_tool_uses": 3,
            "status": "open",
            "posted_at": "2026-04-19T18:00:00+00:00",
            "claimed_by": None,
            "claimed_at": None,
            "completed_at": None,
            "completion_receipt": None,
        })
        db._write_board_locked(board, prev_task_count=10)
    finally:
        db._release_lock(lock_fd)

    # Verify
    result = json.loads(isolated_board.read_text())
    assert len(result["tasks"]) == 11
    assert result["tasks"][-1]["atomic_id"] == "TEST-NEW"


def test_wipe_protection_blocks_accidental_wipe(isolated_board):
    """Verify sanity check blocks writes that drop task count by >50%
    when there are more than 5 tasks."""
    import dispatch_board as db

    # Seed 20 tasks
    _seed_board(isolated_board, 20)

    # Try to write with only 2 tasks (90% drop)
    lock_fd = db._acquire_lock()
    try:
        wiped_data = {"tasks": [
            {"atomic_id": "SURVIVOR-1", "status": "open"},
            {"atomic_id": "SURVIVOR-2", "status": "open"},
        ]}
        with pytest.raises(RuntimeError, match="WIPE PROTECTION"):
            db._write_board_locked(wiped_data, prev_task_count=20)
    finally:
        db._release_lock(lock_fd)

    # Original data should be intact (wipe was blocked)
    result = json.loads(isolated_board.read_text())
    assert len(result["tasks"]) == 20


def test_wipe_protection_allows_normal_deletion(isolated_board):
    """Verify sanity check allows normal task removal (completing 1 of 10)."""
    import dispatch_board as db

    # Seed 10 tasks
    _seed_board(isolated_board, 10)

    lock_fd = db._acquire_lock()
    try:
        board = db._read_board_locked()
        prev_count = len(board["tasks"])
        # Remove 1 task (normal completion removal)
        board["tasks"] = board["tasks"][1:]
        db._write_board_locked(board, prev_task_count=prev_count)
    finally:
        db._release_lock(lock_fd)

    result = json.loads(isolated_board.read_text())
    assert len(result["tasks"]) == 9


def test_wipe_protection_skipped_for_small_boards(isolated_board):
    """Verify sanity check does not trigger for boards with <= 5 tasks."""
    import dispatch_board as db

    # Seed 3 tasks
    _seed_board(isolated_board, 3)

    lock_fd = db._acquire_lock()
    try:
        board = db._read_board_locked()
        # Wipe to 0 — should be allowed since prev_count <= 5
        db._write_board_locked({"tasks": []}, prev_task_count=3)
    finally:
        db._release_lock(lock_fd)

    result = json.loads(isolated_board.read_text())
    assert len(result["tasks"]) == 0


def _worker_post(board_path_str, lock_path_str, worker_id, n_posts):
    """Worker process: post n_posts tasks to the board."""
    import dispatch_board as db
    db.BOARD_PATH = Path(board_path_str)
    db.LOCK_PATH = Path(lock_path_str)

    for i in range(n_posts):
        lock_fd = db._acquire_lock()
        try:
            board = db._read_board_locked()
            prev_count = len(board["tasks"])
            atomic_id = f"W{worker_id}-T{i}"
            board["tasks"].append({
                "atomic_id": atomic_id,
                "scope": f"w{worker_id}.py",
                "description": f"Worker {worker_id} task {i}",
                "urgency": "P1",
                "estimated_tool_uses": 3,
                "status": "open",
                "posted_at": f"2026-04-19T18:{worker_id:02d}:{i:02d}+00:00",
                "claimed_by": None,
                "claimed_at": None,
                "completed_at": None,
                "completion_receipt": None,
            })
            db._write_board_locked(board, prev_task_count=prev_count)
        finally:
            db._release_lock(lock_fd)


def _worker_claim(board_path_str, lock_path_str, engineer_id, results_list):
    """Worker process: claim tasks until none available."""
    import dispatch_board as db
    db.BOARD_PATH = Path(board_path_str)
    db.LOCK_PATH = Path(lock_path_str)

    claimed = 0
    for _ in range(50):  # max attempts
        lock_fd = db._acquire_lock()
        try:
            board = db._read_board_locked()
            prev_count = len(board["tasks"])
            found = False
            for task in board["tasks"]:
                if task["status"] == "open":
                    task["status"] = "claimed"
                    task["claimed_by"] = engineer_id
                    task["claimed_at"] = "2026-04-19T19:00:00+00:00"
                    db._write_board_locked(board, prev_task_count=prev_count)
                    claimed += 1
                    found = True
                    break
            if not found:
                break
        finally:
            db._release_lock(lock_fd)
    results_list.append(claimed)


def _worker_read(board_path_str, lock_path_str, n_reads, violations_list):
    """Worker process: read the board n times, check for empty tasks."""
    import dispatch_board as db
    db.BOARD_PATH = Path(board_path_str)
    db.LOCK_PATH = Path(lock_path_str)

    for _ in range(n_reads):
        board = db._read_board()
        if len(board.get("tasks", [])) == 0:
            violations_list.append(1)


def test_concurrent_post_no_data_loss(isolated_board):
    """4 concurrent workers each post 10 tasks. Final count must be 40."""
    import dispatch_board as db

    n_workers = 4
    n_posts_per_worker = 10
    expected = n_workers * n_posts_per_worker

    board_str = str(isolated_board)
    lock_str = str(db.LOCK_PATH)

    processes = []
    for w in range(n_workers):
        p = multiprocessing.Process(
            target=_worker_post,
            args=(board_str, lock_str, w, n_posts_per_worker)
        )
        processes.append(p)

    for p in processes:
        p.start()
    for p in processes:
        p.join(timeout=30)

    result = json.loads(isolated_board.read_text())
    assert len(result["tasks"]) == expected, (
        f"Expected {expected} tasks, got {len(result['tasks'])}. "
        f"Data loss detected — concurrent write race condition."
    )


def test_concurrent_post_and_claim(isolated_board):
    """2 posters + 2 claimers running concurrently.
    No tasks should be lost and no double-claims should occur."""
    import dispatch_board as db

    # Seed 10 tasks to start
    _seed_board(isolated_board, 10)

    board_str = str(isolated_board)
    lock_str = str(db.LOCK_PATH)

    manager = multiprocessing.Manager()
    claim_results = manager.list()

    # 2 workers post 5 tasks each
    posters = [
        multiprocessing.Process(target=_worker_post, args=(board_str, lock_str, 10+i, 5))
        for i in range(2)
    ]
    # 2 workers claim tasks
    claimers = [
        multiprocessing.Process(target=_worker_claim, args=(board_str, lock_str, f"eng-{i}", claim_results))
        for i in range(2)
    ]

    for p in posters + claimers:
        p.start()
    for p in posters + claimers:
        p.join(timeout=30)

    result = json.loads(isolated_board.read_text())
    total_tasks = len(result["tasks"])
    # 10 seed + 10 posted = 20 total (claims don't remove tasks)
    assert total_tasks == 20, f"Expected 20 tasks, got {total_tasks}"

    # No double claims
    claimed_ids = [t["atomic_id"] for t in result["tasks"] if t["status"] == "claimed"]
    assert len(claimed_ids) == len(set(claimed_ids)), "Double claim detected"


def test_concurrent_reads_never_see_empty(isolated_board):
    """While one writer adds tasks, readers should never see an empty board
    (which was the symptom of the original wipe bug)."""
    import dispatch_board as db

    # Seed 10 tasks
    _seed_board(isolated_board, 10)

    board_str = str(isolated_board)
    lock_str = str(db.LOCK_PATH)

    manager = multiprocessing.Manager()
    violations = manager.list()

    # 1 writer posting 20 more tasks
    poster = multiprocessing.Process(
        target=_worker_post, args=(board_str, lock_str, 99, 20)
    )
    # 2 readers checking for empty board
    readers = [
        multiprocessing.Process(
            target=_worker_read, args=(board_str, lock_str, 50, violations)
        )
        for _ in range(2)
    ]

    for p in [poster] + readers:
        p.start()
    for p in [poster] + readers:
        p.join(timeout=30)

    assert len(violations) == 0, (
        f"Reader saw empty board {len(violations)} times during concurrent writes. "
        f"This indicates a truncation race (the original wipe bug)."
    )

    result = json.loads(isolated_board.read_text())
    assert len(result["tasks"]) == 30  # 10 seed + 20 posted


def test_deliberate_wipe_attempt_blocked(isolated_board):
    """Simulate a malicious/buggy writer trying to wipe the board.
    The sanity check must block it."""
    import dispatch_board as db

    # Seed 30 tasks (production-like)
    _seed_board(isolated_board, 30)

    lock_fd = db._acquire_lock()
    try:
        # Attempt to write empty tasks
        with pytest.raises(RuntimeError, match="WIPE PROTECTION"):
            db._write_board_locked({"tasks": []}, prev_task_count=30)

        # Attempt to write 5 tasks (>50% drop from 30)
        small = {"tasks": [{"atomic_id": f"X-{i}", "status": "open"} for i in range(5)]}
        with pytest.raises(RuntimeError, match="WIPE PROTECTION"):
            db._write_board_locked(small, prev_task_count=30)
    finally:
        db._release_lock(lock_fd)

    # Board should be unchanged
    result = json.loads(isolated_board.read_text())
    assert len(result["tasks"]) == 30


def test_lock_prevents_interleaved_read_modify_write(isolated_board):
    """Verify that the lock serializes concurrent read-modify-write operations.
    Without the lock, two processes reading the same state and both writing
    would cause one write to be lost."""
    import dispatch_board as db

    # Seed 5 tasks
    _seed_board(isolated_board, 5)

    board_str = str(isolated_board)
    lock_str = str(db.LOCK_PATH)

    # 4 concurrent writers each adding 1 task
    processes = []
    for w in range(4):
        p = multiprocessing.Process(
            target=_worker_post,
            args=(board_str, lock_str, w, 1)
        )
        processes.append(p)

    for p in processes:
        p.start()
    for p in processes:
        p.join(timeout=30)

    result = json.loads(isolated_board.read_text())
    assert len(result["tasks"]) == 9, (
        f"Expected 9 tasks (5 seed + 4 posted), got {len(result['tasks'])}. "
        f"Lock failed to serialize concurrent writes."
    )


# ────────────────────────────────────────────────────────────────────────────
# CZL-WHITEBOARD-BROKER-SUB-SAMEFIX: Broker + Subscriber concurrent tests
# Verifies that cto_dispatch_broker.py (now importing from dispatch_board.py)
# correctly uses the shared lockfile for concurrent access.
# ────────────────────────────────────────────────────────────────────────────

def _worker_broker_route(board_path_str, lock_path_str, n_tasks_to_route):
    """Simulate broker poll_and_route: read board, mark open tasks as broker_routing."""
    import dispatch_board as db
    db.BOARD_PATH = Path(board_path_str)
    db.LOCK_PATH = Path(lock_path_str)

    routed = 0
    for _ in range(n_tasks_to_route):
        lock_fd = db._acquire_lock()
        try:
            board = db._read_board_locked()
            prev_count = len(board["tasks"])
            for task in board["tasks"]:
                if task["status"] == "open":
                    task["status"] = "broker_routing"
                    task["claimed_by"] = "cto-broker"
                    routed += 1
                    break
            db._write_board_locked(board, prev_task_count=prev_count)
        finally:
            db._release_lock(lock_fd)
    return routed


def _worker_subscriber_claim(board_path_str, lock_path_str, engineer_id, results_list):
    """Simulate subscriber claiming broker_routing tasks assigned to it."""
    import dispatch_board as db
    db.BOARD_PATH = Path(board_path_str)
    db.LOCK_PATH = Path(lock_path_str)

    claimed = 0
    for _ in range(50):  # max attempts
        lock_fd = db._acquire_lock()
        try:
            board = db._read_board_locked()
            prev_count = len(board["tasks"])
            found = False
            for task in board["tasks"]:
                if task["status"] == "broker_routing":
                    task["status"] = "claimed"
                    task["claimed_by"] = engineer_id
                    db._write_board_locked(board, prev_task_count=prev_count)
                    claimed += 1
                    found = True
                    break
            if not found:
                break
        finally:
            db._release_lock(lock_fd)
    results_list.append(claimed)


def test_broker_post_concurrent_no_data_loss(isolated_board):
    """Broker routing + CEO posting concurrently. No tasks should be lost.

    Regression for CZL-WHITEBOARD-BROKER-SUB-SAMEFIX: broker previously had
    its own _read_board/_write_board with truncate-before-lock bug.
    """
    import dispatch_board as db

    # Seed 5 open tasks
    _seed_board(isolated_board, 5)

    board_str = str(isolated_board)
    lock_str = str(db.LOCK_PATH)

    # 2 posters adding 5 tasks each + 1 broker routing
    posters = [
        multiprocessing.Process(target=_worker_post, args=(board_str, lock_str, i, 5))
        for i in range(2)
    ]
    broker = multiprocessing.Process(
        target=_worker_broker_route, args=(board_str, lock_str, 5)
    )

    for p in posters + [broker]:
        p.start()
    for p in posters + [broker]:
        p.join(timeout=30)

    result = json.loads(isolated_board.read_text())
    total = len(result["tasks"])
    # 5 seed + 10 posted = 15 total
    assert total == 15, (
        f"Expected 15 tasks (5 seed + 10 posted), got {total}. "
        f"Broker concurrent routing caused data loss."
    )


def test_broker_subscriber_concurrent_no_double_claim(isolated_board):
    """Broker routes + subscriber claims concurrently. No double claims.

    End-to-end: poster -> broker routes -> subscriber claims.
    All running concurrently sharing the same lockfile.
    """
    import dispatch_board as db

    # Seed 10 open tasks
    _seed_board(isolated_board, 10)

    board_str = str(isolated_board)
    lock_str = str(db.LOCK_PATH)

    manager = multiprocessing.Manager()
    claim_results = manager.list()

    # 1 poster (5 more tasks), 1 broker (routes up to 15), 2 subscribers
    poster = multiprocessing.Process(
        target=_worker_post, args=(board_str, lock_str, 50, 5)
    )
    broker = multiprocessing.Process(
        target=_worker_broker_route, args=(board_str, lock_str, 15)
    )
    subscribers = [
        multiprocessing.Process(
            target=_worker_subscriber_claim,
            args=(board_str, lock_str, f"eng-{i}", claim_results)
        )
        for i in range(2)
    ]

    for p in [poster, broker] + subscribers:
        p.start()
    for p in [poster, broker] + subscribers:
        p.join(timeout=30)

    result = json.loads(isolated_board.read_text())
    total = len(result["tasks"])
    # 10 seed + 5 posted = 15 total tasks (routing/claiming changes status, not count)
    assert total == 15, f"Expected 15 tasks, got {total}"

    # No double claims: each claimed task should have a unique atomic_id
    claimed_tasks = [t for t in result["tasks"] if t["status"] == "claimed"]
    claimed_ids = [t["atomic_id"] for t in claimed_tasks]
    assert len(claimed_ids) == len(set(claimed_ids)), "Double claim detected"


def test_concurrent_reads_during_broker_writes_never_empty(isolated_board):
    """Readers never see empty board while broker is writing.

    This specifically tests the fix from WIPE-RCA: the old broker code
    used open("w") which truncates before lock, causing readers to see
    empty JSON and then write back {"tasks": []}.
    """
    import dispatch_board as db

    # Seed 10 tasks
    _seed_board(isolated_board, 10)

    board_str = str(isolated_board)
    lock_str = str(db.LOCK_PATH)

    manager = multiprocessing.Manager()
    violations = manager.list()

    # 1 broker routing tasks + 2 readers
    broker = multiprocessing.Process(
        target=_worker_broker_route, args=(board_str, lock_str, 10)
    )
    readers = [
        multiprocessing.Process(
            target=_worker_read, args=(board_str, lock_str, 50, violations)
        )
        for _ in range(2)
    ]

    for p in [broker] + readers:
        p.start()
    for p in [broker] + readers:
        p.join(timeout=30)

    assert len(violations) == 0, (
        f"Reader saw empty board {len(violations)} times during broker writes. "
        f"Truncation race still present in broker code path."
    )

    result = json.loads(isolated_board.read_text())
    assert len(result["tasks"]) == 10  # tasks routed, not removed
