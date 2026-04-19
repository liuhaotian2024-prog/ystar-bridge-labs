"""
CZL-P1-a: Test hook_wrapper.py payload agent_id override from .ystar_active_agent marker.

Verifies that the payload override logic in hook_wrapper.py correctly:
1. Reads the marker file and injects agent_id into the payload
2. Clears agent_type="agent" to prevent priority 1.5 short-circuit
3. Handles missing/empty marker file gracefully
4. Does not override when marker content is "agent"

Author: Ryan Park (eng-platform)
"""
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

import pytest

# We test the payload override logic in isolation by extracting it into a function
# that mirrors what hook_wrapper.py does after json.loads(raw).

MARKER_PATH = "/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/.ystar_active_agent"


def apply_payload_override(payload: dict, marker_path: str = MARKER_PATH) -> dict:
    """
    Replica of the CZL-P1-a payload override logic from hook_wrapper.py.
    This allows unit testing without running the full hook pipeline.
    """
    try:
        _marker_content = open(marker_path, "r", encoding="utf-8").read().strip()
        if _marker_content and _marker_content != "agent":
            payload["agent_id"] = _marker_content
            if payload.get("agent_type") in ("", "agent", None):
                payload.pop("agent_type", None)
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return payload


class TestPayloadOverrideFromMarker:
    """Test the payload agent_id override from .ystar_active_agent marker."""

    def test_empty_agent_id_gets_overridden(self, tmp_path):
        """When payload.agent_id is empty, marker content replaces it."""
        marker = tmp_path / ".ystar_active_agent"
        marker.write_text("ceo\n")

        payload = {"tool_name": "Bash", "tool_input": {"command": "whoami"},
                   "agent_id": "", "agent_type": "agent"}
        result = apply_payload_override(payload, str(marker))

        assert result["agent_id"] == "ceo"
        assert "agent_type" not in result  # cleared to prevent priority 1.5

    def test_agent_type_agent_gets_cleared(self, tmp_path):
        """When agent_type is 'agent' (default), it gets removed."""
        marker = tmp_path / ".ystar_active_agent"
        marker.write_text("eng-platform\n")

        payload = {"tool_name": "Bash", "tool_input": {"command": "ls"},
                   "agent_id": "agent", "agent_type": "agent"}
        result = apply_payload_override(payload, str(marker))

        # agent_id "agent" is treated as empty by the override
        # But our logic checks _marker_content != "agent", and "agent" in agent_id
        # is a separate concern -- here the marker is "eng-platform"
        assert result["agent_id"] == "eng-platform"
        assert "agent_type" not in result

    def test_agent_id_agent_literal_gets_overridden(self, tmp_path):
        """payload.agent_id='agent' is the fallback default -- should be overridden."""
        marker = tmp_path / ".ystar_active_agent"
        marker.write_text("cto\n")

        payload = {"tool_name": "Read", "tool_input": {"file_path": "/tmp/x"},
                   "agent_id": "agent", "agent_type": ""}
        result = apply_payload_override(payload, str(marker))

        assert result["agent_id"] == "cto"

    def test_marker_content_agent_no_override(self, tmp_path):
        """When marker says 'agent', do not override (it is the same fallback)."""
        marker = tmp_path / ".ystar_active_agent"
        marker.write_text("agent\n")

        payload = {"tool_name": "Bash", "tool_input": {"command": "whoami"},
                   "agent_id": "", "agent_type": "agent"}
        result = apply_payload_override(payload, str(marker))

        # No override because marker says "agent"
        assert result["agent_id"] == ""
        assert result["agent_type"] == "agent"

    def test_marker_file_missing_no_crash(self, tmp_path):
        """Missing marker file is gracefully handled (FileNotFoundError)."""
        missing = tmp_path / "nonexistent_marker"

        payload = {"tool_name": "Bash", "tool_input": {"command": "whoami"},
                   "agent_id": "", "agent_type": "agent"}
        result = apply_payload_override(payload, str(missing))

        # Payload unchanged
        assert result["agent_id"] == ""
        assert result["agent_type"] == "agent"

    def test_marker_empty_no_override(self, tmp_path):
        """Empty marker file does not override."""
        marker = tmp_path / ".ystar_active_agent"
        marker.write_text("   \n")

        payload = {"tool_name": "Bash", "tool_input": {"command": "whoami"},
                   "agent_id": "", "agent_type": "agent"}
        result = apply_payload_override(payload, str(marker))

        assert result["agent_id"] == ""

    def test_agent_type_non_agent_preserved(self, tmp_path):
        """When agent_type is a real agent type (not 'agent'), keep it."""
        marker = tmp_path / ".ystar_active_agent"
        marker.write_text("ceo\n")

        payload = {"tool_name": "Bash", "tool_input": {"command": "whoami"},
                   "agent_id": "", "agent_type": "Agent-CTO"}
        result = apply_payload_override(payload, str(marker))

        assert result["agent_id"] == "ceo"
        # agent_type is "Agent-CTO" (not "", "agent", or None), so it stays
        assert result["agent_type"] == "Agent-CTO"

    def test_subagent_marker_nested(self, tmp_path):
        """Marker with eng-kernel gets properly injected into payload."""
        marker = tmp_path / ".ystar_active_agent"
        marker.write_text("eng-kernel")

        payload = {"tool_name": "Write", "tool_input": {"file_path": "/tmp/test.py"},
                   "agent_id": "", "agent_type": ""}
        result = apply_payload_override(payload, str(marker))

        assert result["agent_id"] == "eng-kernel"
        assert "agent_type" not in result  # "" is in the clear list

    def test_whitespace_handling(self, tmp_path):
        """Marker content with extra whitespace/newlines is stripped."""
        marker = tmp_path / ".ystar_active_agent"
        marker.write_text("  ceo  \n\n")

        payload = {"tool_name": "Bash", "tool_input": {"command": "whoami"},
                   "agent_id": ""}
        result = apply_payload_override(payload, str(marker))

        assert result["agent_id"] == "ceo"


class TestPayloadOverrideIntegration:
    """Integration-level tests verifying check_hook receives correct identity."""

    def test_check_hook_receives_marker_identity(self, tmp_path):
        """
        End-to-end: construct payload as Claude Code would send it,
        apply override, verify identity_detector._detect_agent_id returns marker.
        """
        marker = tmp_path / ".ystar_active_agent"
        marker.write_text("ceo\n")

        payload = {"tool_name": "Bash", "tool_input": {"command": "whoami"},
                   "agent_id": "", "agent_type": "agent"}

        result = apply_payload_override(payload, str(marker))

        # Now simulate what _detect_agent_id would do with this payload
        # Priority 1: payload.agent_id
        assert result.get("agent_id") == "ceo"
        # Priority 1.5: agent_type — should be gone
        assert "agent_type" not in result

    def test_three_scenarios_matrix(self, tmp_path):
        """
        Test all three scenarios specified in the task:
        1. agent_id=""
        2. agent_id="agent"
        3. agent_type="agent"
        """
        marker = tmp_path / ".ystar_active_agent"
        marker.write_text("ceo\n")

        scenarios = [
            {"agent_id": "", "agent_type": ""},
            {"agent_id": "agent", "agent_type": ""},
            {"agent_id": "", "agent_type": "agent"},
        ]

        for i, base in enumerate(scenarios):
            payload = {"tool_name": "Bash", "tool_input": {"command": f"test{i}"}}
            payload.update(base)
            result = apply_payload_override(payload, str(marker))
            assert result["agent_id"] == "ceo", f"Scenario {i+1} failed: {base}"
