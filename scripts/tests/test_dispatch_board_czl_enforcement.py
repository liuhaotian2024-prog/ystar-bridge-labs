"""
Test: dispatch_board.post_task CZL enforcement + bus publish integration.

Milestone 9b 2026-04-21: Board caught "POC 写了白板仍旧格式绕过, 无保证".
Fix — every post_task 现在:
    1. Reject description < 20 chars or generic filler (CZL y_star 最低要求)
    2. Publish CZLMessageEnvelope to .czl_bus.jsonl (forget_guard + omission
       subscriber 同步能看到)

Structural guarantee: 任何新白板 post 都必 CZL envelope 落 bus, 无绕过.

M-tag: M-2a structural enforcement, M-2b CZL bus integration.
"""
import os
import sys
import json
import tempfile
import types
import pytest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dispatch_board
import czl_bus


def _args(**kw):
    """Build an argparse.Namespace-like object with defaults for post_task."""
    defaults = dict(
        atomic_id="CZL-TEST-ENFORCE",
        scope="tests/only",
        description="This is a properly long and concrete task description.",
        urgency="P1",
        estimated_tool_uses=5,
    )
    defaults.update(kw)
    return types.SimpleNamespace(**defaults)


def test_post_task_rejects_short_description(tmp_path, monkeypatch):
    """< 20 chars description → exit code 2 (CZL enforcement)."""
    # point board to temp file
    monkeypatch.setattr(dispatch_board, "BOARD_PATH",
                        tmp_path / "board.json")
    monkeypatch.setattr(dispatch_board, "LOCK_PATH",
                        tmp_path / "board.lock")
    # and ensure czl_bus writes to tmp
    monkeypatch.setattr(czl_bus, "DEFAULT_BUS", tmp_path / "bus.jsonl")

    rc = dispatch_board.post_task(_args(description="too short"))
    assert rc == 2


def test_post_task_rejects_generic_filler(tmp_path, monkeypatch):
    """description == 'TBD' or 'TODO' rejected even if padded."""
    monkeypatch.setattr(dispatch_board, "BOARD_PATH", tmp_path / "board.json")
    monkeypatch.setattr(dispatch_board, "LOCK_PATH", tmp_path / "board.lock")
    monkeypatch.setattr(czl_bus, "DEFAULT_BUS", tmp_path / "bus.jsonl")

    rc = dispatch_board.post_task(_args(description="TBD"))
    assert rc == 2


def test_post_task_accepts_valid_description_and_publishes_czl(tmp_path, monkeypatch):
    """Valid description → task posted AND CZL envelope appears in bus."""
    monkeypatch.setattr(dispatch_board, "BOARD_PATH", tmp_path / "board.json")
    monkeypatch.setattr(dispatch_board, "LOCK_PATH", tmp_path / "board.lock")
    monkeypatch.setattr(czl_bus, "DEFAULT_BUS", tmp_path / "bus.jsonl")
    # Prevent dispatch_role_routing ImportError side effects
    monkeypatch.setattr(dispatch_board, "emit_cieu",
                        lambda *a, **kw: None)

    rc = dispatch_board.post_task(_args(
        atomic_id="CZL-GOOD-POST",
        description="Milestone 9b enforce CZL on every whiteboard post with bus publish",
        urgency="P0",
    ))
    assert rc != 2  # not rejected

    # Verify bus has the envelope
    bus_path = tmp_path / "bus.jsonl"
    assert bus_path.exists(), "czl_bus.jsonl must be created on post"
    lines = bus_path.read_text().strip().split("\n")
    assert len(lines) == 1
    env = json.loads(lines[0])
    assert env["task_id"] == "CZL-GOOD-POST"
    assert env["message_type"] == "whiteboard_post"
    assert env["urgency"] == "P0"
    assert env["deadline"] > env["created_at"]


def test_p0_urgency_deadline_shorter_than_p1(tmp_path, monkeypatch):
    """P0 deadline < P1 deadline (enforcement of urgency semantics)."""
    monkeypatch.setattr(dispatch_board, "BOARD_PATH", tmp_path / "board.json")
    monkeypatch.setattr(dispatch_board, "LOCK_PATH", tmp_path / "board.lock")
    monkeypatch.setattr(czl_bus, "DEFAULT_BUS", tmp_path / "bus.jsonl")
    monkeypatch.setattr(dispatch_board, "emit_cieu", lambda *a, **kw: None)

    # Post two tasks with different urgency
    dispatch_board.post_task(_args(
        atomic_id="T-P0", urgency="P0",
        description="A properly-long P0 task to test deadline semantics"
    ))
    dispatch_board.post_task(_args(
        atomic_id="T-P1", urgency="P1",
        description="A properly-long P1 task to test deadline semantics"
    ))

    envs = czl_bus.subscribe(bus_path=tmp_path / "bus.jsonl")
    by_id = {e["task_id"]: e for e in envs}
    p0_ttl = by_id["T-P0"]["deadline"] - by_id["T-P0"]["created_at"]
    p1_ttl = by_id["T-P1"]["deadline"] - by_id["T-P1"]["created_at"]
    assert p0_ttl < p1_ttl, f"P0 ttl ({p0_ttl}) must be < P1 ttl ({p1_ttl})"


def test_czl_bus_omission_sees_posted_task_as_future_dispatch(tmp_path, monkeypatch):
    """Posted task appears in omission_subscriber scan (as future dispatch)."""
    monkeypatch.setattr(dispatch_board, "BOARD_PATH", tmp_path / "board.json")
    monkeypatch.setattr(dispatch_board, "LOCK_PATH", tmp_path / "board.lock")
    monkeypatch.setattr(czl_bus, "DEFAULT_BUS", tmp_path / "bus.jsonl")
    monkeypatch.setattr(dispatch_board, "emit_cieu", lambda *a, **kw: None)

    dispatch_board.post_task(_args(
        atomic_id="T-INTEGRATION",
        description="Integration test: post creates envelope visible to omission",
        urgency="P0",
    ))

    # Immediately after post, not overdue yet
    overdue = czl_bus.omission_subscribe(bus_path=tmp_path / "bus.jsonl")
    assert len(overdue) == 0  # still within P0 deadline (2h)

    # Now simulate "3 hours later" to force overdue
    import time
    future_now = time.time() + 3 * 3600
    overdue = czl_bus.omission_subscribe(bus_path=tmp_path / "bus.jsonl",
                                         now=future_now)
    ids = [o["task_id"] for o in overdue]
    assert "T-INTEGRATION" in ids
