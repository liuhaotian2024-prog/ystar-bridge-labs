"""
Test: hook_who_i_am_staleness — per-agent reply counter + enforce→omission chain.

Milestone 10b 2026-04-21: Board proposal "WHO_I_AM reminder 放 enforce 里,
每 agent 都受约束, enforce 后接 omission". Structural防identity drift.

M-tag: M-2a structural inject + M-2b staleness overdue.
"""
import os
import sys
import json
import tempfile
import pytest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hook_who_i_am_staleness as mod


def test_first_reply_no_inject(tmp_path, monkeypatch):
    """Reply #1 should NOT trigger inject (below interval)."""
    monkeypatch.setattr(mod, "COUNTER_DIR", tmp_path)
    result = mod.check_staleness("ceo", reminder_interval=3, staleness_threshold=10)
    assert result["reply_count"] == 1
    assert result["action"] == "none"


def test_interval_reply_triggers_inject(tmp_path, monkeypatch):
    """At reply #N (N=interval), must trigger inject."""
    monkeypatch.setattr(mod, "COUNTER_DIR", tmp_path)
    for _ in range(2):
        mod.check_staleness("ceo", reminder_interval=3, staleness_threshold=10)
    # 3rd reply — interval hit
    r = mod.check_staleness("ceo", reminder_interval=3, staleness_threshold=10)
    assert r["reply_count"] == 3
    assert r["action"] == "inject"
    assert "Quick Lookup Table" in r["inject_text"] or "Section 1" in r["inject_text"]


def test_per_agent_counters_independent(tmp_path, monkeypatch):
    """Each agent has its own counter — CEO reply doesn't increment CTO."""
    monkeypatch.setattr(mod, "COUNTER_DIR", tmp_path)
    mod.check_staleness("ceo")
    mod.check_staleness("ceo")
    ceo_r = mod.check_staleness("ceo")  # reply_count=3 for CEO
    cto_r = mod.check_staleness("cto")   # reply_count=1 for CTO
    assert ceo_r["reply_count"] == 3
    assert cto_r["reply_count"] == 1


def test_overdue_threshold_triggers_warn(tmp_path, monkeypatch):
    """If gap >= staleness_threshold, return 'warn_overdue'."""
    monkeypatch.setattr(mod, "COUNTER_DIR", tmp_path)
    # simulate 10 replies with no inject (reminder_interval=100)
    for i in range(9):
        mod.check_staleness("ceo", reminder_interval=100, staleness_threshold=10)
    r = mod.check_staleness("ceo", reminder_interval=100, staleness_threshold=10)
    assert r["reply_count"] == 10
    assert r["action"] == "warn_overdue"
    assert "OMISSION WARN" in r["warn_text"]
    assert "WHO_I_AM_STALENESS_OVERDUE" in r["warn_text"]


def test_warn_overdue_includes_fix_command_and_skill_ref(tmp_path, monkeypatch):
    """Aligned to hook.py REDIRECT schema: FIX_COMMAND + SKILL_REF keys."""
    monkeypatch.setattr(mod, "COUNTER_DIR", tmp_path)
    for _ in range(9):
        mod.check_staleness("ceo", reminder_interval=100, staleness_threshold=10)
    r = mod.check_staleness("ceo", reminder_interval=100, staleness_threshold=10)
    assert "FIX_COMMAND:" in r["warn_text"]
    assert "SKILL_REF:" in r["warn_text"]


def test_inject_resets_last_reminder_cursor(tmp_path, monkeypatch):
    """After inject, cursor advances so next inject is N replies later."""
    monkeypatch.setattr(mod, "COUNTER_DIR", tmp_path)
    for _ in range(2):
        mod.check_staleness("ceo", reminder_interval=3, staleness_threshold=100)
    r1 = mod.check_staleness("ceo", reminder_interval=3, staleness_threshold=100)
    assert r1["action"] == "inject"
    # next 2 replies: no inject
    r2 = mod.check_staleness("ceo", reminder_interval=3, staleness_threshold=100)
    assert r2["action"] == "none"
    r3 = mod.check_staleness("ceo", reminder_interval=3, staleness_threshold=100)
    assert r3["action"] == "none"
    # reply after that (gap=3 again) → inject
    r4 = mod.check_staleness("ceo", reminder_interval=3, staleness_threshold=100)
    assert r4["action"] == "inject"


def test_counter_persists_across_calls(tmp_path, monkeypatch):
    """Counter state survives process re-start (critical for per-reply hook)."""
    monkeypatch.setattr(mod, "COUNTER_DIR", tmp_path)
    mod.check_staleness("ceo")
    mod.check_staleness("ceo")
    # simulate fresh read
    state = mod._read_counter("ceo")
    assert state["reply_count"] == 2


def test_missing_who_i_am_file_graceful(tmp_path, monkeypatch):
    """Unknown agent_id (no WHO_I_AM) — should not crash, still increment counter."""
    monkeypatch.setattr(mod, "COUNTER_DIR", tmp_path)
    r = mod.check_staleness("unknown_agent", reminder_interval=1, staleness_threshold=10)
    assert r["reply_count"] == 1
    # action may be "inject" (interval=1) but inject_text empty (no md mapping)
    assert r["action"] in ("inject", "none")


def test_extract_quick_lookup_returns_section1_content():
    """Extract must include Section 1 Quick Lookup Table headers."""
    ceo_md = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/"
                  "knowledge/ceo/wisdom/WHO_I_AM.md")
    if not ceo_md.exists():
        pytest.skip("CEO WHO_I_AM.md not in test env")
    content = mod._extract_quick_lookup_table(ceo_md)
    assert "Section 1" in content or "Quick Lookup" in content
    # Should be non-empty
    assert len(content) > 100
