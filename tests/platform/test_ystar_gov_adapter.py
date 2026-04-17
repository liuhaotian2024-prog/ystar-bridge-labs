#!/usr/bin/env python3
"""
Test Y*gov governance→production adapter (CTO CZL-150)
≥4 assertions | Data isolation | No hardcoded paths
"""
import os
import sys
import pytest
from pathlib import Path

# Inject ystar-company/scripts to path for adapter import
YSTAR_COMPANY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(YSTAR_COMPANY_ROOT / "scripts"))

# Set YSTAR_GOV_ROOT env var for data isolation
os.environ["YSTAR_GOV_ROOT"] = str(Path.home() / ".openclaw/workspace/Y-star-gov")

from ystar_gov_adapter import (
    task_to_call_record,
    task_to_scm,
    update_adaptive_thresholds,
    trace_root_cause,
)


def test_task_to_call_record_mapping():
    """Assertion 1: task receipt → CallRecord mapping."""
    receipt = {
        "agent_id": "cto",
        "task_title": "test_task",
        "tool_uses_claimed": 10,
        "tool_uses_metadata": {"count": 10},
        "rt_plus_1": 0,
        "y_star": "ideal",
        "x_t": "current",
        "u": ["action1", "action2"],
        "y_t_plus_1": "final",
    }
    record = task_to_call_record(receipt)
    assert record.agent_id == "cto"
    assert record.func_name == "test_task"
    assert record.rt_plus_1 == 0
    assert record.outcome == "success"


def test_task_to_scm_mapping():
    """Assertion 2: dispatch → SCM mapping."""
    dispatch = {
        "agent_id": "ceo",
        "task_id": "W1",
        "y_star": "ideal_state",
        "x_t": "current_state",
        "u": ["step1", "step2"],
    }
    scm = task_to_scm(dispatch)
    assert scm.variables["Y_star"] == "ideal_state"
    assert scm.variables["X_t"] == "current_state"
    assert len(scm.variables["U"]) == 2
    assert scm.metadata["agent_id"] == "ceo"


def test_adaptive_threshold_update():
    """Assertion 3: CIEU events → adaptive threshold update."""
    events = [
        {"event_type": "GOVERNANCE_VIOLATION", "rule_id": "phantom_variable"},
        {"event_type": "GOVERNANCE_VIOLATION", "rule_id": "phantom_variable"},
        {"event_type": "GOVERNANCE_VIOLATION", "rule_id": "root_cause_fix_required"},
    ]
    thresholds = update_adaptive_thresholds(events)
    assert "phantom_variable" in thresholds
    assert thresholds["phantom_variable"] < 0.7  # backoff applied
    assert "root_cause_fix_required" in thresholds


def test_data_isolation_no_hardcoded_paths():
    """Assertion 4: isolation check — no ystar-company paths in Y-star-gov imports."""
    import ystar_gov_adapter
    adapter_source = Path(ystar_gov_adapter.__file__).read_text()

    # FORBIDDEN patterns: hardcoded absolute paths
    forbidden = [
        "/Users/haotianliu/.openclaw/workspace/ystar-company",
        "C:\\Users\\liuha\\OneDrive",
        "ystar-company/",
    ]
    for pattern in forbidden:
        assert pattern not in adapter_source, f"Hardcoded path detected: {pattern}"

    # REQUIRED pattern: YSTAR_GOV_ROOT env var usage
    assert "YSTAR_GOV_ROOT" in adapter_source
    assert "os.environ.get" in adapter_source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
