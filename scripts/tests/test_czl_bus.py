"""
Test: CZL unified message bus POC.

Milestone 9 2026-04-21: verify Board proposal — 统一 CZL 通讯 + 双订阅
(forget_guard 防乱做 + omission 防漏做) 同步触发治理.

M-tag: M-2a + M-2b structural 双面.
"""
import os
import sys
import time
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from czl_bus import (
    CZLMessageEnvelope,
    publish,
    subscribe,
    forget_guard_subscribe,
    omission_subscribe,
    DANGEROUS_ACTION_KEYWORDS,
)


def _make_envelope(**kwargs):
    defaults = dict(
        y_star="test goal",
        x_t="test pre",
        u=["step 1"],
        y_t_plus_1="test post",
        rt_value=1.0,
        task_id="T-TEST",
        sender="ceo",
        recipient="eng-kernel",
        message_type="dispatch",
    )
    defaults.update(kwargs)
    return CZLMessageEnvelope(**defaults)


def test_publish_assigns_message_id_and_timestamp():
    with tempfile.TemporaryDirectory() as td:
        bus = Path(td) / "bus.jsonl"
        env = _make_envelope()
        mid = publish(env, bus_path=bus)
        assert mid.startswith("czl_")
        assert env.message_id == mid
        assert env.created_at > 0
        assert bus.exists()


def test_subscribe_returns_all_envelopes_when_no_cursor():
    with tempfile.TemporaryDirectory() as td:
        bus = Path(td) / "bus.jsonl"
        publish(_make_envelope(task_id="T1"), bus_path=bus)
        publish(_make_envelope(task_id="T2"), bus_path=bus)
        publish(_make_envelope(task_id="T3"), bus_path=bus)
        envs = subscribe(bus_path=bus)
        assert len(envs) == 3
        ids = [e["task_id"] for e in envs]
        assert ids == ["T1", "T2", "T3"]


def test_subscribe_since_cursor_skips_earlier():
    with tempfile.TemporaryDirectory() as td:
        bus = Path(td) / "bus.jsonl"
        env1 = _make_envelope(task_id="T1")
        mid1 = publish(env1, bus_path=bus)
        publish(_make_envelope(task_id="T2"), bus_path=bus)
        publish(_make_envelope(task_id="T3"), bus_path=bus)
        envs = subscribe(since_message_id=mid1, bus_path=bus)
        ids = [e["task_id"] for e in envs]
        assert ids == ["T2", "T3"]


def test_forget_guard_flags_dangerous_u_action():
    with tempfile.TemporaryDirectory() as td:
        bus = Path(td) / "bus.jsonl"
        # safe
        publish(_make_envelope(task_id="SAFE", u=["git add README.md", "pytest"]),
                bus_path=bus)
        # dangerous
        publish(_make_envelope(task_id="DANGER-1", u=["rm -rf /tmp/test", "restart"]),
                bus_path=bus)
        publish(_make_envelope(task_id="DANGER-2", u=["git push --force", "deploy"]),
                bus_path=bus)
        publish(_make_envelope(task_id="DANGER-3", u=["chmod 777 /etc/shadow"]),
                bus_path=bus)

        violations = forget_guard_subscribe(bus_path=bus)
        flagged_ids = {v["task_id"] for v in violations}
        assert "SAFE" not in flagged_ids
        assert "DANGER-1" in flagged_ids
        assert "DANGER-2" in flagged_ids  # matches "force push"
        assert "DANGER-3" in flagged_ids


def test_forget_guard_reports_matched_keyword():
    with tempfile.TemporaryDirectory() as td:
        bus = Path(td) / "bus.jsonl"
        publish(_make_envelope(task_id="TEST", u=["run rm -rf /tmp/foo"]),
                bus_path=bus)
        violations = forget_guard_subscribe(bus_path=bus)
        assert len(violations) == 1
        assert violations[0]["matched_keyword"] == "rm -rf"


def test_omission_flags_overdue_dispatch_without_receipt():
    with tempfile.TemporaryDirectory() as td:
        bus = Path(td) / "bus.jsonl"
        past = time.time() - 3600  # 1h ago
        future = time.time() + 3600
        # dispatch 1: overdue, no receipt
        publish(_make_envelope(task_id="OVERDUE", deadline=past,
                               message_type="dispatch"), bus_path=bus)
        # dispatch 2: future, no receipt (shouldn't flag)
        publish(_make_envelope(task_id="FUTURE", deadline=future,
                               message_type="dispatch"), bus_path=bus)
        # dispatch 3: overdue, BUT with closure receipt (shouldn't flag)
        publish(_make_envelope(task_id="CLOSED", deadline=past,
                               message_type="dispatch"), bus_path=bus)
        publish(_make_envelope(task_id="CLOSED", message_type="receipt",
                               rt_value=0.0), bus_path=bus)

        overdue = omission_subscribe(bus_path=bus)
        ids = [o["task_id"] for o in overdue]
        assert "OVERDUE" in ids
        assert "FUTURE" not in ids
        assert "CLOSED" not in ids
        assert len(overdue) == 1


def test_omission_reports_overdue_seconds():
    with tempfile.TemporaryDirectory() as td:
        bus = Path(td) / "bus.jsonl"
        past = time.time() - 500
        publish(_make_envelope(task_id="T-OVERDUE", deadline=past,
                               message_type="dispatch"), bus_path=bus)
        overdue = omission_subscribe(bus_path=bus)
        assert len(overdue) == 1
        assert overdue[0]["overdue_sec"] > 490


def test_envelope_serializes_to_dict_with_all_fields():
    env = _make_envelope(task_id="SER", deadline=1234.56, urgency="P0")
    d = env.to_dict()
    assert d["task_id"] == "SER"
    assert d["deadline"] == 1234.56
    assert d["urgency"] == "P0"
    assert d["schema_version"] == "1.0"


def test_dual_subscribers_see_same_bus_concurrently():
    """Core Board proposal: forget_guard + omission 同步看同一 bus."""
    with tempfile.TemporaryDirectory() as td:
        bus = Path(td) / "bus.jsonl"
        past = time.time() - 1000
        # 1 dangerous overdue message: BOTH subscribers must flag it
        publish(_make_envelope(task_id="BOTH",
                               u=["rm -rf /etc/passwd"],
                               deadline=past,
                               message_type="dispatch"), bus_path=bus)

        fg_violations = forget_guard_subscribe(bus_path=bus)
        om_overdue = omission_subscribe(bus_path=bus)

        # Both must independently catch the same message
        assert len(fg_violations) == 1
        assert fg_violations[0]["task_id"] == "BOTH"
        assert len(om_overdue) == 1
        assert om_overdue[0]["task_id"] == "BOTH"
