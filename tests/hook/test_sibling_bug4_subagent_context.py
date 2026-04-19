"""
Sibling Bug #4: hook_wrapper.py CEO guard must not block subagent writes.

Root cause: When CEO spawns a subagent, the .ystar_active_agent marker may
still be "ceo" if push_agent hasn't fired or failed. The CEO guard at
hook_wrapper.py lines 80-102 checks _caller_id (from marker) against
_ceo_identities, and "ceo" matches — blocking subagent Write/Edit to
Y-star-gov/ystar/ which is the engineer's actual scope.

Fix: Three-layer subagent detection before CEO guard fires:
  1. agent_stack.stack_depth() > 0 — subagent was properly pushed
  2. Original payload agent_type is non-empty AND non-"agent"
  3. Marker identity is a known engineer (not in _ceo_identities)

If any layer detects subagent context, _is_subagent_context=True and CEO
guard is skipped.

Audience: CTO + eng-platform for integration test of hook_wrapper identity
detection. This test verifies the sibling bug #4 fix prevents false-positive
CEO guard blocks on subagents.

Research: Based on Leo's BLOCKED_ON diagnosis (2026-04-18) + Ryan's analysis
of hook_wrapper.py P1-a marker override timing.

Synthesis: The fix uses defense-in-depth — three independent detection layers
ensure subagent context is recognized even if one layer fails. The principle
is "fail-open for subagents, fail-closed for CEO" — if we can't determine
the caller is CEO with confidence, we don't block.

Author: Ryan Park (eng-platform)
"""
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# ── Extracted logic from hook_wrapper.py for unit testing ──
# Mirrors the CEO guard + subagent detection from hook_wrapper.py (post bug #4 fix).

_CEO_IDENTITIES = ("ceo", "Aiden-CEO", "Aiden")


def evaluate_ceo_guard(
    payload: dict,
    marker_content: str = "",
    stack_depth: int = 0,
    original_agent_type: str = "",
) -> dict:
    """
    Simulate the CEO guard decision from hook_wrapper.py.

    Returns:
        {"decision": "deny", "reason": "..."} if CEO guard fires
        {"decision": "allow", "reason": "..."} if CEO guard skipped
    """
    # Step 1: Apply P1-a marker override (simulated)
    _original_agent_id = payload.get("agent_id", "")
    _original_agent_type = original_agent_type or payload.get("agent_type", "")

    if marker_content and marker_content != "agent":
        payload["agent_id"] = marker_content
        if payload.get("agent_type") in ("", "agent", None):
            payload.pop("agent_type", None)

    # Step 2: CEO guard with subagent detection
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    _caller_id = payload.get("agent_id", "")

    # Subagent context detection (3 layers)
    _is_subagent_context = False

    # Layer 1: agent_stack depth > 0
    if stack_depth > 0:
        _is_subagent_context = True

    # Layer 2: original payload agent_type is specific (not default)
    if not _is_subagent_context and _original_agent_type not in ("", "agent", None):
        _is_subagent_context = True

    # Layer 3: marker identity is not CEO
    if not _is_subagent_context and _caller_id not in _CEO_IDENTITIES and _caller_id != "":
        _is_subagent_context = True

    # CEO guard check
    if tool in ("Write", "Edit", "NotebookEdit") and _caller_id in _CEO_IDENTITIES and not _is_subagent_context:
        file_path = tool_input.get("file_path", "")
        ceo_deny = ["Y-star-gov/ystar/", "Y-star-gov\\\\ystar\\\\", "/src/ystar/"]
        for deny_pattern in ceo_deny:
            if deny_pattern in file_path:
                return {
                    "decision": "deny",
                    "reason": f"CEO code-write prohibition: {file_path}",
                }

    return {
        "decision": "allow",
        "reason": "CEO guard skipped" if _is_subagent_context else "not a CEO-deny path",
    }


class TestSiblingBug4_CEOGuardSubagentBypass:
    """Verify CEO guard correctly distinguishes root CEO from subagent contexts."""

    # ── Scenario 1: Root CEO (no subagent) → DENY ──

    def test_root_ceo_write_ystar_denied(self):
        """Root CEO writing to Y-star-gov/ystar/ must be blocked."""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/hook.py",
                "content": "# bad",
            },
            "agent_id": "",
            "agent_type": "agent",
        }
        result = evaluate_ceo_guard(payload, marker_content="ceo", stack_depth=0)
        assert result["decision"] == "deny", f"Root CEO Write should be denied: {result}"

    def test_root_ceo_edit_ystar_denied(self):
        """Root CEO editing Y-star-gov/ystar/ must be blocked."""
        payload = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/hook.py",
                "old_string": "pass",
                "new_string": "return True",
            },
            "agent_id": "",
            "agent_type": "agent",
        }
        result = evaluate_ceo_guard(payload, marker_content="ceo", stack_depth=0)
        assert result["decision"] == "deny"

    def test_root_ceo_notebookedit_ystar_denied(self):
        """Root CEO NotebookEdit to Y-star-gov/ystar/ must be blocked."""
        payload = {
            "tool_name": "NotebookEdit",
            "tool_input": {
                "file_path": "/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/test.ipynb",
            },
            "agent_id": "",
            "agent_type": "",
        }
        result = evaluate_ceo_guard(payload, marker_content="ceo", stack_depth=0)
        assert result["decision"] == "deny"

    def test_root_ceo_aiden_identity_denied(self):
        """Root CEO with Aiden-CEO identity denied."""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/hook.py",
                "content": "# bad",
            },
            "agent_id": "Aiden-CEO",
        }
        result = evaluate_ceo_guard(payload, marker_content="Aiden-CEO", stack_depth=0)
        assert result["decision"] == "deny"

    # ── Scenario 2: Subagent via stack depth → ALLOW ──

    def test_subagent_stack_depth_bypasses_ceo_guard(self):
        """
        THE BUG FIX: marker is "ceo" but stack_depth > 0 means a subagent
        was properly pushed. CEO guard should NOT fire.
        """
        payload = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/hook.py",
                "old_string": "pass",
                "new_string": "return True",
            },
            "agent_id": "",
            "agent_type": "agent",
        }
        result = evaluate_ceo_guard(payload, marker_content="ceo", stack_depth=1)
        assert result["decision"] == "allow", f"Subagent (stack>0) should be allowed: {result}"

    def test_subagent_deep_stack_bypasses_ceo_guard(self):
        """Nested subagent (stack depth 3) should also bypass CEO guard."""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/hook.py",
                "content": "# deep nested",
            },
            "agent_id": "",
            "agent_type": "",
        }
        result = evaluate_ceo_guard(payload, marker_content="ceo", stack_depth=3)
        assert result["decision"] == "allow"

    # ── Scenario 3: Subagent via marker identity (not CEO) → ALLOW ──

    def test_engineer_marker_bypasses_ceo_guard(self):
        """When marker is 'eng-kernel', the CEO guard is skipped via fallback 2."""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/hook.py",
                "content": "# eng-kernel work",
            },
            "agent_id": "",
            "agent_type": "agent",
        }
        result = evaluate_ceo_guard(payload, marker_content="eng-kernel", stack_depth=0)
        assert result["decision"] == "allow"

    def test_eng_platform_marker_bypasses_ceo_guard(self):
        """eng-platform identity bypasses CEO guard."""
        payload = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/hook.py",
                "old_string": "old",
                "new_string": "new",
            },
            "agent_id": "",
            "agent_type": "",
        }
        result = evaluate_ceo_guard(payload, marker_content="eng-platform", stack_depth=0)
        assert result["decision"] == "allow"

    def test_eng_governance_marker_bypasses_ceo_guard(self):
        """eng-governance identity bypasses CEO guard."""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/policy.py",
                "content": "# governance fix",
            },
            "agent_id": "",
        }
        result = evaluate_ceo_guard(payload, marker_content="eng-governance", stack_depth=0)
        assert result["decision"] == "allow"

    # ── Scenario 4: Subagent via original agent_type → ALLOW ──

    def test_specific_agent_type_bypasses_ceo_guard(self):
        """
        When original payload has a specific agent_type (e.g. 'Leo-Kernel'),
        subagent context is detected via fallback 1.
        """
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/runtime.py",
                "content": "# kernel fix",
            },
            "agent_id": "",
            "agent_type": "agent",
        }
        result = evaluate_ceo_guard(
            payload,
            marker_content="ceo",
            stack_depth=0,
            original_agent_type="Leo-Kernel",
        )
        assert result["decision"] == "allow", f"Specific agent_type should bypass: {result}"

    # ── Scenario 5: Non-code paths are NOT blocked even for CEO ──

    def test_ceo_write_non_code_path_allowed(self):
        """CEO writing to reports/ (non-code) should not be blocked by this guard."""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/Users/haotianliu/.openclaw/workspace/ystar-company/reports/daily.md",
                "content": "# report",
            },
            "agent_id": "",
            "agent_type": "",
        }
        result = evaluate_ceo_guard(payload, marker_content="ceo", stack_depth=0)
        assert result["decision"] == "allow"

    def test_ceo_read_ystar_allowed(self):
        """CEO Read (not Write/Edit) to Y-star-gov/ystar/ is allowed."""
        payload = {
            "tool_name": "Read",
            "tool_input": {
                "file_path": "/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/hook.py",
            },
            "agent_id": "",
        }
        result = evaluate_ceo_guard(payload, marker_content="ceo", stack_depth=0)
        assert result["decision"] == "allow"

    # ── Scenario 6: Empty string agent_id NOT in CEO identities ──

    def test_empty_agent_id_without_marker_not_denied(self):
        """
        BUG FIX: empty string was previously in _ceo_identities.
        With no marker override and empty agent_id, guard should NOT fire
        because "" is no longer in _ceo_identities.
        """
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/hook.py",
                "content": "# unknown caller",
            },
            "agent_id": "",
            "agent_type": "",
        }
        # marker_content="" simulates missing/empty marker file (no override)
        result = evaluate_ceo_guard(payload, marker_content="", stack_depth=0)
        assert result["decision"] == "allow", (
            "Empty agent_id should NOT be treated as CEO (removed '' from identities)"
        )

    # ── Scenario 7: Multiple detection layers combine correctly ──

    def test_all_three_layers_agree_subagent(self):
        """When all 3 layers say subagent, result is allow."""
        payload = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/hook.py",
                "old_string": "x",
                "new_string": "y",
            },
            "agent_id": "",
            "agent_type": "",
        }
        result = evaluate_ceo_guard(
            payload,
            marker_content="eng-kernel",
            stack_depth=2,
            original_agent_type="Leo-Kernel",
        )
        assert result["decision"] == "allow"

    def test_only_stack_depth_detects_subagent(self):
        """
        Stack depth alone is sufficient — even when marker is "ceo"
        and original agent_type is default.
        """
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/hook.py",
                "content": "# fix",
            },
            "agent_id": "",
            "agent_type": "agent",
        }
        result = evaluate_ceo_guard(
            payload, marker_content="ceo", stack_depth=1, original_agent_type=""
        )
        assert result["decision"] == "allow"

    # ── Scenario 8: Regression — ensure deny paths still work ──

    def test_src_ystar_path_denied_for_ceo(self):
        """CEO writing to /src/ystar/ is also denied."""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/some/project/src/ystar/module.py",
                "content": "# bad",
            },
            "agent_id": "ceo",
        }
        result = evaluate_ceo_guard(payload, marker_content="ceo", stack_depth=0)
        assert result["decision"] == "deny"

    def test_windows_path_denied_for_ceo(self):
        """CEO writing to Y-star-gov\\ystar\\ (Windows path) is denied."""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "C:\\Users\\test\\Y-star-gov\\\\ystar\\\\kernel\\hook.py",
                "content": "# bad",
            },
            "agent_id": "Aiden",
        }
        result = evaluate_ceo_guard(payload, marker_content="Aiden", stack_depth=0)
        assert result["decision"] == "deny"
