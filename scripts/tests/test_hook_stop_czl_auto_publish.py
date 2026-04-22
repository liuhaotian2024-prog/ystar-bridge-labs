"""
Test: hook_stop_czl_auto_publish — CEO reply 口头派 task 自动走 CZL bus.

Milestone 10 2026-04-21: close Board-caught绕过 gap. CEO reply 里的承诺/派发
via Stop hook 被结构级 extract + publish to .czl_bus.jsonl, 下游
forget_guard + omission 自动订阅.

M-tag: M-2a (CEO reply dispatch 走同一 bus 无绕过) + M-2b (承诺自动 track).
"""
import json
import os
import sys
import tempfile
from pathlib import Path
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import czl_bus
from hook_stop_czl_auto_publish import (
    commitment_to_envelope,
    process_reply_text,
)


SAMPLE_REPLY = """
Milestone 9 (CZL unified bus POC) Rt+1=0 ✅.

下 reply 立刻开 Milestone 10 = Gemma 4 12B Ollama install + master daemon prototype.

Pilot 成功再 template scale 到 8 agent.

立刻做 hook_stop POC 不 defer.
"""


def test_commitment_to_envelope_maps_next_reply_to_P0():
    """next_reply_commitment → P0 urgency (10 min deadline)."""
    c = {
        "statement": "下 reply 立刻开 X",
        "commitment_type": "next_reply_commitment",
        "created_at": 1000.0,
        "deadline": 1600.0,
        "deadline_hint_sec": 600,
    }
    env = commitment_to_envelope(c)
    assert env.urgency == "P0"
    assert env.message_type == "reply_commitment"
    assert env.sender == "ceo"
    assert "下 reply 立刻开 X" in env.y_star


def test_commitment_to_envelope_maps_milestone_to_P1():
    c = {
        "statement": "Milestone 10 = Gemma install",
        "commitment_type": "milestone_scope_declaration",
        "created_at": 1000.0,
        "deadline": 2800.0,
        "deadline_hint_sec": 1800,
    }
    env = commitment_to_envelope(c)
    assert env.urgency == "P1"
    assert env.role_tags["commitment_type"] == "milestone_scope_declaration"


def test_commitment_envelope_has_unique_task_id():
    """Each commitment must have unique task_id (dedupe later by content)."""
    c1 = {
        "statement": "do X",
        "commitment_type": "immediate_action",
        "created_at": 1000.0,
        "deadline": 1300.0,
        "deadline_hint_sec": 300,
    }
    c2 = {
        "statement": "do Y",
        "commitment_type": "immediate_action",
        "created_at": 1000.1,  # slightly later
        "deadline": 1300.1,
        "deadline_hint_sec": 300,
    }
    env1 = commitment_to_envelope(c1)
    env2 = commitment_to_envelope(c2)
    assert env1.task_id != env2.task_id
    assert env1.task_id.startswith("CEO-COMMIT-")


def test_process_reply_text_publishes_all_commitments(tmp_path, monkeypatch):
    """Integration: CEO reply text → multiple envelopes published to bus."""
    bus = tmp_path / "bus.jsonl"
    monkeypatch.setattr(czl_bus, "DEFAULT_BUS", bus)

    published = process_reply_text(SAMPLE_REPLY, session_id="s1", reply_id="r1",
                                    bus_path=bus)

    assert len(published) >= 3, f"expected >=3 commitments, got {len(published)}"

    # Verify bus content
    envs = czl_bus.subscribe(bus_path=bus)
    types_found = {e["role_tags"].get("commitment_type") for e in envs}
    assert "next_reply_commitment" in types_found  # "下 reply 立刻开"
    assert "milestone_scope_declaration" in types_found  # "Milestone 10 ="
    assert "pilot_then_scale" in types_found  # "Pilot 成功再"


def test_published_envelopes_are_reply_commitment_type(tmp_path, monkeypatch):
    bus = tmp_path / "bus.jsonl"
    monkeypatch.setattr(czl_bus, "DEFAULT_BUS", bus)

    process_reply_text(SAMPLE_REPLY, bus_path=bus)
    envs = czl_bus.subscribe(bus_path=bus)

    assert all(e["message_type"] == "reply_commitment" for e in envs), \
        "every published envelope must be tagged reply_commitment"


def test_empty_reply_publishes_nothing(tmp_path, monkeypatch):
    bus = tmp_path / "bus.jsonl"
    monkeypatch.setattr(czl_bus, "DEFAULT_BUS", bus)

    published = process_reply_text("", bus_path=bus)
    assert published == []
    assert not bus.exists() or bus.stat().st_size == 0


def test_published_envelopes_visible_to_omission_subscriber(tmp_path, monkeypatch):
    """End-to-end: CEO reply → Stop hook → bus → omission_subscribe catches."""
    bus = tmp_path / "bus.jsonl"
    monkeypatch.setattr(czl_bus, "DEFAULT_BUS", bus)

    process_reply_text(SAMPLE_REPLY, bus_path=bus)

    # Immediately: not overdue (all deadlines in future)
    overdue_now = czl_bus.omission_subscribe(bus_path=bus)
    assert len(overdue_now) == 0

    # Simulate 1 hour later: next_reply_commitment P0 (10 min deadline) overdue;
    # milestone P1 (30 min) also overdue; pilot P1 also overdue.
    import time
    future = time.time() + 3 * 3600
    overdue_later = czl_bus.omission_subscribe(bus_path=bus, now=future)
    assert len(overdue_later) >= 2


def test_published_envelopes_visible_to_forget_guard_subscriber(tmp_path, monkeypatch):
    """Dangerous commitment (e.g., CEO promises 'rm -rf') → forget_guard flags."""
    bus = tmp_path / "bus.jsonl"
    monkeypatch.setattr(czl_bus, "DEFAULT_BUS", bus)

    danger = "立刻做 rm -rf /tmp/foo 作为 Milestone 清理."
    process_reply_text(danger, bus_path=bus)

    violations = czl_bus.forget_guard_subscribe(bus_path=bus)
    assert len(violations) >= 1
    assert any("rm -rf" in v["matched_keyword"] for v in violations)


def test_regression_board_catch_20260421_2045_reply():
    """Regression: the exact pattern Board caught at 2045 — CEO committed 'Pilot
    成功再 scale 到 8 agent. 下 reply 立刻开' then failed to deliver scale.
    Tracker must extract, publish, and if next reply doesn't deliver, omission
    catches it."""
    with tempfile.TemporaryDirectory() as td:
        bus = Path(td) / "bus.jsonl"
        reply_20_45 = """
        Milestone 8 (Ethan brain pilot) Rt+1=0 ✅
        Milestone 8 self-pick: 节点 5.3 Ethan brain.db pilot
        Pilot 成功再 template scale 到 8 agent. 下 reply 立刻开.
        """
        published = process_reply_text(reply_20_45, bus_path=bus)
        types = {p["commitment_type"] for p in published}
        # Both commitments MUST be captured
        assert "milestone_scope_declaration" in types
        assert "pilot_then_scale" in types
        assert "next_reply_commitment" in types
