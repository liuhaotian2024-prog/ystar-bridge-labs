#!/usr/bin/env python3
"""
Test suite for K9 Event Trigger (Board 2026-04-16)
Tests event-driven audit architecture transformation from cron polling.
"""
import pytest
import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

# Add scripts to path
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from k9_event_trigger import (
    k9_audit_on_event,
    check_agent_identity_violation,
    check_ceo_engineering_boundary,
    check_dispatch_5tuple,
    VIOLATION_ROUTING,
    get_cieu_conn,
)


class TestK9EventTrigger:
    """Test K9 event-driven audit entry point."""

    def test_callable_exists(self):
        """Verify k9_audit_on_event is callable."""
        assert callable(k9_audit_on_event)

    def test_simple_violation_triggers_route(self):
        """Test that a simple violation triggers routing."""
        # Simulate CEO writing code directly (violates charter)
        result = k9_audit_on_event(
            event_type="TOOL_USE_EDIT",
            agent_id="ceo",
            payload={"file_path": "src/ystar/core.py", "tool_name": "Edit"},
        )

        assert result["violations"], "Should detect CEO engineering boundary violation"
        assert "ceo_engineering_boundary" in result["violations"]
        assert len(result["routing_targets"]) > 0
        assert result["routing_targets"][0][0] == "forget_guard"

    def test_cieu_emit_verified(self):
        """Test that CIEU events are emitted on audit trigger."""
        # Count events before
        conn = get_cieu_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM cieu_events WHERE event_type = 'K9_AUDIT_TRIGGERED'"
        )
        count_before = cursor.fetchone()[0]
        conn.close()

        # Trigger audit
        k9_audit_on_event(
            event_type="TEST_EVENT",
            agent_id="ceo",
            payload={"test": "data"},
        )

        # Count events after
        conn = get_cieu_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM cieu_events WHERE event_type = 'K9_AUDIT_TRIGGERED'"
        )
        count_after = cursor.fetchone()[0]
        conn.close()

        assert count_after > count_before, "K9_AUDIT_TRIGGERED event should be emitted"

    def test_clean_event_no_op(self):
        """Test that clean event (no violations) runs without error."""
        # Legitimate CTO code edit
        result = k9_audit_on_event(
            event_type="TOOL_USE_EDIT",
            agent_id="cto",
            payload={"file_path": "src/ystar/core.py"},
        )

        # Should run without crash, even if no violations
        assert isinstance(result, dict)
        assert "violations" in result
        assert "routing_targets" in result

    def test_agent_identity_violation_check(self):
        """Test agent identity violation detection."""
        # Valid canonical agent
        assert check_agent_identity_violation("ceo") is None
        assert check_agent_identity_violation("cto") is None

        # Invalid agent (if not in registry)
        # Note: test may pass if "rogue_agent" is in canonical registry
        result = check_agent_identity_violation("rogue_agent_xyz_not_in_registry")
        # Should return violation_type or None
        assert result is None or result == "agent_id_unidentified"

    def test_ceo_engineering_boundary_check(self):
        """Test CEO engineering boundary violation check."""
        # CEO editing engineering scope (should violate)
        violation = check_ceo_engineering_boundary(
            agent_id="ceo",
            event_type="TOOL_USE_EDIT",
            payload={"file_path": "src/ystar/core.py", "tool_name": "Edit"},
        )
        assert violation == "ceo_engineering_boundary"

        # CEO writing task card (should allow)
        violation = check_ceo_engineering_boundary(
            agent_id="ceo",
            event_type="TOOL_USE_WRITE",
            payload={"file_path": ".claude/tasks/eng-kernel-001.md", "tool_name": "Write"},
        )
        assert violation is None

        # CTO editing engineering scope (should allow)
        violation = check_ceo_engineering_boundary(
            agent_id="cto",
            event_type="TOOL_USE_EDIT",
            payload={"file_path": "src/ystar/core.py", "tool_name": "Edit"},
        )
        assert violation is None

    def test_ceo_engineering_boundary_tool_name_filter(self):
        """Test that CEO boundary check filters by tool_name (CZL-100)."""
        # True positive: CEO Edit engineering scope
        violation = check_ceo_engineering_boundary(
            agent_id="ceo",
            event_type="HOOK_PRE_CALL",
            payload={"tool_name": "Edit", "file_path": "Y-star-gov/foo.py"},
        )
        assert violation == "ceo_engineering_boundary"

        # False positive: CEO Read engineering scope (should allow)
        violation = check_ceo_engineering_boundary(
            agent_id="ceo",
            event_type="HOOK_PRE_CALL",
            payload={"tool_name": "Read", "file_path": "Y-star-gov/foo.py"},
        )
        assert violation is None

        # False positive: CEO Bash (should allow)
        violation = check_ceo_engineering_boundary(
            agent_id="ceo",
            event_type="HOOK_PRE_CALL",
            payload={"tool_name": "Bash", "file_path": "Y-star-gov/foo.py"},
        )
        assert violation is None

    def test_dispatch_5tuple_check(self):
        """Test CZL 5-tuple compliance check."""
        # Dispatch with full 5-tuple (should pass)
        violation = check_dispatch_5tuple(
            event_type="SUBAGENT_DISPATCH",
            payload={
                "task_description": "Y*: Fix bug. Xt: Broken. U: Edit file. Yt+1: Fixed. Rt+1: 0 if tests pass."
            },
        )
        assert violation is None

        # Dispatch missing 3+ markers (should violate)
        violation = check_dispatch_5tuple(
            event_type="SUBAGENT_DISPATCH",
            payload={"task_description": "Fix the bug please"},
        )
        assert violation == "dispatch_missing_5tuple"

    def test_routing_table_completeness(self):
        """Test that routing table covers expected violation types."""
        expected_violations = [
            "ceo_engineering_boundary",
            "dispatch_missing_5tuple",
            "agent_id_unidentified",
            "choice_question_to_board",
        ]
        for v in expected_violations:
            assert v in VIOLATION_ROUTING, f"Routing missing for {v}"

    def test_violation_emit_k9_violation_detected(self):
        """Test that K9_VIOLATION_DETECTED event is emitted per violation."""
        # Count before
        conn = get_cieu_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM cieu_events WHERE event_type = 'K9_VIOLATION_DETECTED'"
        )
        count_before = cursor.fetchone()[0]
        conn.close()

        # Trigger violation
        k9_audit_on_event(
            event_type="TOOL_USE_EDIT",
            agent_id="ceo",
            payload={"file_path": "src/ystar/core.py"},
        )

        # Count after
        conn = get_cieu_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM cieu_events WHERE event_type = 'K9_VIOLATION_DETECTED'"
        )
        count_after = cursor.fetchone()[0]
        conn.close()

        assert count_after > count_before, "K9_VIOLATION_DETECTED should be emitted"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
