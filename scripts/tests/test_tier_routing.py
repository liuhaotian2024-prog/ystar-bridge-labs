"""Test: Gemma tier routing picks correct model by task type.

M14 Board 2026-04-21 night directive: Aiden 本地 Gemma 分层推理.
- bg_scan 任务 → gemma4:e4b (轻快)
- decision 任务 → ystar-gemma (fine-tuned Y* context)
- env YSTAR_TIER_DEFAULT overrides

M-tag: M-1 Survivability (local inference) + M-3 Value Production (local-first).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiden_cluster_daemon import pick_tier, BG_SCAN_TASKS, DECISION_TASKS


def test_pick_tier_bg_scan_by_type():
    assert pick_tier("bounty_scan") == "gemma4:e4b"
    assert pick_tier("k9_patrol") == "gemma4:e4b"
    assert pick_tier("daily_report") == "gemma4:e4b"
    assert pick_tier("dialogue_compression") == "gemma4:e4b"


def test_pick_tier_decision_by_type():
    assert pick_tier("ceo_reply") == "ystar-gemma"
    assert pick_tier("cto_ruling") == "ystar-gemma"
    assert pick_tier("amendment_proposal") == "ystar-gemma"
    assert pick_tier("reflection_generation") == "ystar-gemma"


def test_pick_tier_env_override_bg(monkeypatch):
    monkeypatch.setenv("YSTAR_TIER_DEFAULT", "bg_scan")
    assert pick_tier("ceo_reply") == "gemma4:e4b"
    assert pick_tier("cto_ruling") == "gemma4:e4b"


def test_pick_tier_env_override_decision(monkeypatch):
    monkeypatch.setenv("YSTAR_TIER_DEFAULT", "decision")
    assert pick_tier("bounty_scan") == "ystar-gemma"
    assert pick_tier("k9_patrol") == "ystar-gemma"


def test_pick_tier_unknown_defaults_decision():
    assert pick_tier("random_task") == "ystar-gemma"
    assert pick_tier(None) == "ystar-gemma"
    assert pick_tier("") == "ystar-gemma"


def test_tier_constants_are_disjoint():
    assert BG_SCAN_TASKS.isdisjoint(DECISION_TASKS)


def test_tier_env_override_precedence_over_task_type(monkeypatch):
    monkeypatch.setenv("YSTAR_TIER_DEFAULT", "bg_scan")
    assert pick_tier("ceo_reply") == "gemma4:e4b"
