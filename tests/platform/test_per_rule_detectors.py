#!/usr/bin/env python3
"""
Per-Rule Detector Tests — CZL-78 P1 Atomic Task
Platform Engineer: Ryan Park (eng-platform)
Version: 1.0 (2026-04-16)

Test coverage: 6 detectors × 2 cases (fire + no-fire) = 12 assertions minimum
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add scripts/ to path for per_rule_detectors import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from per_rule_detectors import (
    detect_czl_dispatch_missing_5tuple,
    detect_czl_receipt_rt_not_zero,
    detect_charter_drift_mid_session,
    detect_wave_scope_undeclared,
    detect_subagent_unauthorized_git_op,
    detect_realtime_artifact_archival_sla,
)


# ── Test 1: czl_dispatch_missing_5tuple ───────────────────────────────────

def test_czl_dispatch_missing_5tuple_fires():
    """Fire: Agent call without Y* section"""
    payload = {
        "tool_name": "Agent",
        "tool_input": {
            "subagent_type": "Ethan-CTO",
            "prompt": "Please fix bug in hook.py. Task: CZL-78.",
        }
    }
    result = detect_czl_dispatch_missing_5tuple(payload)
    assert result is not None
    assert result["violation_type"] == "CZL_DISPATCH_MISSING_5TUPLE"
    assert "Y*" in result["missing_sections"]
    assert result["severity"] == "high"


def test_czl_dispatch_missing_5tuple_no_fire():
    """No-fire: Agent call with complete 5-tuple"""
    payload = {
        "tool_name": "Agent",
        "tool_input": {
            "subagent_type": "Ethan-CTO",
            "prompt": """
**Y***: Hook response <10ms
**Xt**: Current response 45ms
**U**: (1) Profile hook (2) Optimize DB query
**Yt+1**: Response <10ms verified
**Rt+1**: 0
            """,
        }
    }
    result = detect_czl_dispatch_missing_5tuple(payload)
    assert result is None  # No violation


# ── Test 2: czl_receipt_rt_not_zero ───────────────────────────────────────

def test_czl_receipt_rt_not_zero_fires():
    """Fire: Receipt claims Rt+1=0 but lacks bash evidence"""
    payload = {
        "tool_name": "SendMessage",
        "tool_input": {
            "content": """
Task complete.
**Rt+1**: 0

All done, no issues.
            """,
        }
    }
    result = detect_czl_receipt_rt_not_zero(payload)
    assert result is not None
    assert result["violation_type"] == "CZL_RECEIPT_RT_NOT_ZERO"
    assert result["claimed_rt"] == 0.0
    assert result["severity"] == "high"


def test_czl_receipt_rt_not_zero_no_fire():
    """No-fire: Receipt with Rt+1=0 AND bash verification"""
    payload = {
        "tool_name": "SendMessage",
        "tool_input": {
            "content": """
**Rt+1**: 0

Verification:
$ ls -la scripts/per_rule_detectors.py
-rw-r--r--  1 user  staff  8543 Apr 16 12:00 scripts/per_rule_detectors.py
$ wc -l scripts/per_rule_detectors.py
     245 scripts/per_rule_detectors.py
            """,
        }
    }
    result = detect_czl_receipt_rt_not_zero(payload)
    assert result is None  # Evidence present


# ── Test 3: charter_drift_mid_session ─────────────────────────────────────

def test_charter_drift_mid_session_fires():
    """Fire: CEO editing AGENTS.md without break-glass"""
    payload = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "AGENTS.md",
        },
        "agent_id": "Aiden-CEO",
        "ceo_mode": "normal",
    }
    result = detect_charter_drift_mid_session(payload)
    assert result is not None
    assert result["violation_type"] == "CHARTER_DRIFT_MID_SESSION"
    assert "AGENTS.md" in result["file_path"]
    assert result["severity"] == "high"


def test_charter_drift_mid_session_no_fire():
    """No-fire: Secretary editing governance file (authorized)"""
    payload = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "governance/WORKING_STYLE.md",
        },
        "agent_id": "Samantha-Secretary",
        "ceo_mode": "normal",
    }
    result = detect_charter_drift_mid_session(payload)
    assert result is None  # Secretary authorized


# ── Test 4: wave_scope_undeclared ─────────────────────────────────────────

def test_wave_scope_undeclared_fires():
    """Fire: Campaign report without Goal/Scope in first para"""
    payload = {
        "tool_name": "Write",
        "tool_input": {
            "file_path": "reports/ceo/campaign_v8_summary.md",
            "content": """
# Campaign v8 Summary

We launched many features this week.
Performance was good overall.
            """,
        }
    }
    result = detect_wave_scope_undeclared(payload)
    assert result is not None
    assert result["violation_type"] == "WAVE_SCOPE_UNDECLARED"
    assert result["severity"] == "medium"


def test_wave_scope_undeclared_no_fire():
    """No-fire: Campaign report with Goal declared"""
    payload = {
        "tool_name": "Write",
        "tool_input": {
            "file_path": "reports/ceo/campaign_v8_summary.md",
            "content": """
# Campaign v8 Summary

Goal: Ship Y*gov 0.7 with CZL protocol + ForgetGuard enforcement.

We launched the following features...
            """,
        }
    }
    result = detect_wave_scope_undeclared(payload)
    assert result is None  # Goal declared


# ── Test 5: subagent_unauthorized_git_op ──────────────────────────────────

def test_subagent_unauthorized_git_op_fires():
    """Fire: Sub-agent attempting git reset --hard"""
    payload = {
        "tool_name": "Bash",
        "tool_input": {
            "command": "git reset --hard origin/main && git push --force",
        },
        "agent_id": "Ryan-Platform",
    }
    result = detect_subagent_unauthorized_git_op(payload)
    assert result is not None
    assert result["violation_type"] == "SUBAGENT_UNAUTHORIZED_GIT_OP"
    assert result["severity"] == "high"


def test_subagent_unauthorized_git_op_no_fire():
    """No-fire: CTO running destructive git op (authorized)"""
    payload = {
        "tool_name": "Bash",
        "tool_input": {
            "command": "git reset --hard HEAD~1",
        },
        "agent_id": "Ethan-CTO",
    }
    result = detect_subagent_unauthorized_git_op(payload)
    assert result is None  # CTO authorized


# ── Test 6: realtime_artifact_archival_sla ───────────────────────────────

def test_realtime_artifact_archival_sla_fires():
    """Fire: New artifact in archival scope"""
    payload = {
        "tool_name": "Write",
        "tool_input": {
            "file_path": "reports/ceo/autonomous_summary_20260416.md",
            "content": "# Autonomous Work Summary\n\nCompleted tasks...",
        }
    }
    result = detect_realtime_artifact_archival_sla(payload)
    assert result is not None
    assert result["violation_type"] == "ARTIFACT_ARCHIVAL_SCOPE_DETECTED"
    assert result["severity"] == "low"


def test_realtime_artifact_archival_sla_no_fire():
    """No-fire: Edit to file outside archival scope"""
    payload = {
        "tool_name": "Write",
        "tool_input": {
            "file_path": "scripts/test_debug.py",
            "content": "# Debug script",
        }
    }
    result = detect_realtime_artifact_archival_sla(payload)
    assert result is None  # Outside archival scope


# ── Test Suite Runner ─────────────────────────────────────────────────────

if __name__ == "__main__":
    test_czl_dispatch_missing_5tuple_fires()
    test_czl_dispatch_missing_5tuple_no_fire()
    test_czl_receipt_rt_not_zero_fires()
    test_czl_receipt_rt_not_zero_no_fire()
    test_charter_drift_mid_session_fires()
    test_charter_drift_mid_session_no_fire()
    test_wave_scope_undeclared_fires()
    test_wave_scope_undeclared_no_fire()
    test_subagent_unauthorized_git_op_fires()
    test_subagent_unauthorized_git_op_no_fire()
    test_realtime_artifact_archival_sla_fires()
    test_realtime_artifact_archival_sla_no_fire()

    print("✓ All 12 per-rule detector tests PASSED")
