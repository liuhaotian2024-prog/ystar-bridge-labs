#!/usr/bin/env python3
"""
Per-Rule Detectors Telemetry Test — CZL-124 P1 Atomic
Platform Engineer: Ryan Park (eng-platform)
Version: 1.0 (2026-04-16)

Test that 6 per-rule detectors emit distinct CIEU event types when triggered.
"""
import sys
from pathlib import Path

# Add scripts to path for per_rule_detectors import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from per_rule_detectors import (
    detect_czl_dispatch_missing_5tuple,
    detect_czl_receipt_rt_not_zero,
    detect_charter_drift_mid_session,
    detect_wave_scope_undeclared,
    detect_subagent_unauthorized_git_op,
    detect_realtime_artifact_archival_sla,
)


def test_czl_dispatch_missing_5tuple():
    """Detect Agent dispatch lacking Y*/Xt/U/Yt+1/Rt+1 structure."""
    payload = {
        "tool_name": "Agent",
        "tool_input": {
            "subagent_type": "cto",
            "instructions": "Fix bug in hook.py. No structure.",
        },
    }
    result = detect_czl_dispatch_missing_5tuple(payload)
    assert result is not None
    assert result["violation_type"] == "CZL_DISPATCH_MISSING_5TUPLE"
    assert "Y*" in result["missing_sections"]
    assert result["severity"] == "high"


def test_czl_receipt_rt_not_zero():
    """Detect SendMessage receipt claiming Rt+1=0 without bash evidence."""
    payload = {
        "tool_name": "SendMessage",
        "tool_input": {
            "content": "Task complete. **Rt+1**: 0. All tests pass.",
        },
    }
    result = detect_czl_receipt_rt_not_zero(payload)
    assert result is not None
    assert result["violation_type"] == "CZL_RECEIPT_RT_NOT_ZERO"
    assert result["claimed_rt"] == 0.0
    assert result["severity"] == "high"


def test_charter_drift_mid_session():
    """Detect non-Secretary editing AGENTS.md without break-glass mode."""
    payload = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "/workspace/AGENTS.md"},
        "agent_id": "eng-platform",
        "ceo_mode": "normal",
    }
    result = detect_charter_drift_mid_session(payload)
    assert result is not None
    assert result["violation_type"] == "CHARTER_DRIFT_MID_SESSION"
    assert result["severity"] == "high"


def test_wave_scope_undeclared():
    """Detect CEO campaign report without Goal/Scope in first paragraph."""
    payload = {
        "tool_name": "Write",
        "tool_input": {
            "file_path": "reports/ceo/campaign_v99.md",
            "content": "This is a campaign report. Details follow...",
        },
    }
    result = detect_wave_scope_undeclared(payload)
    assert result is not None
    assert result["violation_type"] == "WAVE_SCOPE_UNDECLARED"
    assert result["severity"] == "medium"


def test_subagent_unauthorized_git_op():
    """Detect sub-agent attempting git reset --hard."""
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "git reset --hard origin/main"},
        "agent_id": "eng-governance",
    }
    result = detect_subagent_unauthorized_git_op(payload)
    assert result is not None
    assert result["violation_type"] == "SUBAGENT_UNAUTHORIZED_GIT_OP"
    assert result["severity"] == "high"


def test_realtime_artifact_archival_sla():
    """Detect artifact in archival scope (telemetry event)."""
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "reports/ceo/new_analysis.md"},
    }
    result = detect_realtime_artifact_archival_sla(payload)
    assert result is not None
    assert result["violation_type"] == "ARTIFACT_ARCHIVAL_SCOPE_DETECTED"
    assert result["severity"] == "low"


def test_no_false_positives():
    """Ensure detectors return None for unrelated payloads."""
    # Normal Agent dispatch with full 5-tuple
    payload_agent = {
        "tool_name": "Agent",
        "tool_input": {
            "subagent_type": "cto",
            "instructions": "**Y***: Fix bug. **Xt**: Bug exists. **U**: Edit file. **Yt+1**: Bug fixed. **Rt+1**: 0.",
        },
    }
    assert detect_czl_dispatch_missing_5tuple(payload_agent) is None

    # Receipt with bash evidence
    payload_receipt = {
        "tool_name": "SendMessage",
        "tool_input": {
            "content": "**Rt+1**: 0. Evidence: ```bash\nls -la test.py\n-rw-r--r-- 1 user 100 Apr 16 test.py\n```",
        },
    }
    assert detect_czl_receipt_rt_not_zero(payload_receipt) is None

    # Secretary editing AGENTS.md (authorized)
    payload_secretary = {
        "tool_name": "Edit",
        "tool_input": {"file_path": "/workspace/AGENTS.md"},
        "agent_id": "Samantha-Secretary",
    }
    assert detect_charter_drift_mid_session(payload_secretary) is None

    # CEO report with Goal declaration
    payload_goal = {
        "tool_name": "Write",
        "tool_input": {
            "file_path": "reports/ceo/campaign_v99.md",
            "content": "Goal: Drain backlog. Scope: W1-W10...",
        },
    }
    assert detect_wave_scope_undeclared(payload_goal) is None

    # CTO git reset (authorized)
    payload_cto_git = {
        "tool_name": "Bash",
        "tool_input": {"command": "git reset --hard origin/main"},
        "agent_id": "Ethan-CTO",
    }
    assert detect_subagent_unauthorized_git_op(payload_cto_git) is None

    # Non-archival file write
    payload_non_archival = {
        "tool_name": "Write",
        "tool_input": {"file_path": "tmp/scratch.txt"},
    }
    assert detect_realtime_artifact_archival_sla(payload_non_archival) is None
