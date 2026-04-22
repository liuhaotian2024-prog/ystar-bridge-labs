"""
Test: parent_session_commitment_tracker — extract / register / overdue / deliver.

Milestone 8c 2026-04-21: close OmissionEngine sleep gap by structurally
extracting CEO reply commitments. Board caught "omission 不作用, 你又被自己骗了"
— without this tracker, CEO "下 reply 开 Milestone 9" 承诺从未被记录.

M-tag: M-2b 防不作为 structural, M-2a 防虚假 done.
"""
import os
import sys
import tempfile
import time
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parent_session_commitment_tracker import (
    extract_commitments,
    register_commitment,
    check_overdue,
    mark_delivered,
    COMMITMENT_PATTERNS,
)


def test_extract_next_reply_commitment():
    text = "下一步我下 reply 开 Milestone 9, 不 defer."
    c = extract_commitments(text)
    assert len(c) >= 1
    assert any(x["commitment_type"] == "next_reply_commitment" for x in c)


def test_extract_milestone_scope_declaration():
    text = "Milestone 8 = Ethan brain pilot + 9-agent scale template"
    c = extract_commitments(text)
    milestones = [x for x in c if x["commitment_type"] == "milestone_scope_declaration"]
    assert len(milestones) == 1
    assert "Ethan brain pilot" in milestones[0]["statement"]


def test_extract_pilot_then_scale_commitment():
    text = "Pilot 成功再 template scale 到 8 agent."
    c = extract_commitments(text)
    pilots = [x for x in c if x["commitment_type"] == "pilot_then_scale"]
    assert len(pilots) >= 1


def test_extract_immediate_action():
    text = "立刻做 Milestone 8 pilot, 不问."
    c = extract_commitments(text)
    actions = [x for x in c if x["commitment_type"] == "immediate_action"]
    assert len(actions) == 1


def test_extract_returns_empty_for_no_commitment():
    text = "今天天气很好."
    c = extract_commitments(text)
    assert len(c) == 0


def test_register_appends_to_jsonl():
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "pending.jsonl"
        commitment = {
            "statement": "下 reply 开 X",
            "commitment_type": "next_reply_commitment",
            "created_at": time.time(),
            "deadline": time.time() + 600,
            "deadline_hint_sec": 600,
        }
        cid = register_commitment(commitment, session_id="sess1",
                                   reply_id="r1", commitments_file=f)
        assert cid.startswith("commit_")
        assert f.exists()
        with open(f) as fh:
            rec = json.loads(fh.read())
            assert rec["commitment_id"] == cid
            assert rec["status"] == "PENDING"


def test_check_overdue_reports_past_deadline():
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "pending.jsonl"
        now = time.time()
        past = {
            "statement": "overdue commitment",
            "commitment_type": "next_reply_commitment",
            "created_at": now - 1000,
            "deadline": now - 500,  # 500s overdue
            "deadline_hint_sec": 600,
        }
        future = {
            "statement": "future commitment",
            "commitment_type": "milestone_scope_declaration",
            "created_at": now,
            "deadline": now + 1000,
            "deadline_hint_sec": 1800,
        }
        register_commitment(past, commitments_file=f)
        register_commitment(future, commitments_file=f)

        over = check_overdue(commitments_file=f)
        assert len(over) == 1
        assert "overdue commitment" == over[0]["statement"]
        assert over[0]["overdue_sec"] > 400


def test_mark_delivered_removes_from_overdue():
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "pending.jsonl"
        now = time.time()
        commitment = {
            "statement": "will deliver",
            "commitment_type": "next_reply_commitment",
            "created_at": now - 1000,
            "deadline": now - 500,
            "deadline_hint_sec": 600,
        }
        cid = register_commitment(commitment, commitments_file=f)
        assert len(check_overdue(commitments_file=f)) == 1

        ok = mark_delivered(cid, commitments_file=f)
        assert ok is True
        assert len(check_overdue(commitments_file=f)) == 0


def test_real_board_catch_20260421_20_15_reply_has_commitments():
    """Regression: the exact CEO reply text that Board caught today has
    2+ commitments that tracker should extract."""
    caught_reply_snippet = """
    Milestone 8 (Ethan brain pilot) Rt+1=0 ✅
    Milestone 8 self-pick (不问): 按 M-tag delta + 5-节点总纲 — 节点 5.3 Ethan brain.db pilot
    Pilot 成功再 template scale 到 8 agent. 下 reply 立刻开.
    """
    c = extract_commitments(caught_reply_snippet)
    # Must find at least milestone_scope + pilot_then_scale
    types = {x["commitment_type"] for x in c}
    assert "milestone_scope_declaration" in types
    assert "pilot_then_scale" in types
