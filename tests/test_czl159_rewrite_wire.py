"""
CZL-166: Test that CZL-159 deny messages include actionable header template.

Simulates the hook_wrapper CZL-159 path by extracting its logic and verifying
the deny reason contains fill-in-the-blank header fields.
"""
import json
import os
import sys
import subprocess
import pytest

HOOK_WRAPPER = os.path.join(
    os.path.dirname(__file__), "..", "scripts", "hook_wrapper.py"
)


def _build_pretooluse_payload(file_path: str, content: str) -> dict:
    """Build a PreToolUse Write payload matching Claude Code format."""
    return {
        "hook": {
            "hookName": "PreToolUse",
            "toolName": "Write",
            "toolInput": {
                "file_path": file_path,
                "content": content,
            },
        },
        "tool_name": "Write",
        "tool_input": {
            "file_path": file_path,
            "content": content,
        },
    }


def _run_hook(payload: dict) -> dict:
    """Run hook_wrapper.py with given payload, return parsed JSON output."""
    env = os.environ.copy()
    # Ensure ystar module path is available
    env["PYTHONPATH"] = "/Users/haotianliu/.openclaw/workspace/Y-star-gov:" + env.get(
        "PYTHONPATH", ""
    )
    proc = subprocess.run(
        [sys.executable, HOOK_WRAPPER],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=10,
        env=env,
        cwd=os.path.dirname(HOOK_WRAPPER),
    )
    if proc.returncode != 0 and not proc.stdout.strip():
        # Hook denied and exited — stdout should still have JSON
        pytest.fail(
            f"Hook crashed (rc={proc.returncode})\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return json.loads(proc.stdout)


class TestCZL159DenyIncludesHeaderTemplate:
    """CZL-166: deny reason must contain actionable fill-in-the-blank template."""

    def test_missing_signals_deny_includes_header_template(self):
        """Write to content/ with zero U-workflow signals -> deny with template."""
        # Content with no research, synthesis, or audience signals
        payload = _build_pretooluse_payload(
            file_path="content/blog_post.md",
            content="Hello world. This is a bare post with no signals.",
        )
        result = _run_hook(payload)

        hook_output = result.get("hookSpecificOutput", {})
        decision = hook_output.get("permissionDecision", "")
        reason = hook_output.get("permissionDecisionReason", "")

        assert decision == "deny", f"Expected deny, got {decision}"
        assert "CZL-159" in reason, "Deny reason must mention CZL-159"

        # CZL-166 core assertions: template fields present
        assert "Audience:" in reason, "Template must include 'Audience:' field"
        assert "Research basis:" in reason, "Template must include 'Research basis:' field"
        assert "Synthesis:" in reason, "Template must include 'Synthesis:' field"
        assert "Purpose:" in reason, "Template must include 'Purpose:' field"
        assert "Fill in each bracket" in reason or "copy this template" in reason.lower(), (
            "Template must include actionable instruction to fill brackets"
        )

    def test_missing_one_signal_still_includes_template(self):
        """Write with research+synthesis but no audience -> deny includes template."""
        payload = _build_pretooluse_payload(
            file_path="content/quarterly.md",
            content=(
                "Based on research data showing growth patterns, "
                "the analysis concludes upward trend. "
                "No audience or purpose framing."
            ),
        )
        result = _run_hook(payload)

        hook_output = result.get("hookSpecificOutput", {})
        decision = hook_output.get("permissionDecision", "")
        reason = hook_output.get("permissionDecisionReason", "")

        assert decision == "deny", f"Expected deny for missing audience, got {decision}"
        assert "Audience:" in reason, "Template must be present even for single missing signal"

    def test_all_signals_present_no_deny(self):
        """Write with all 3 signals -> allow (no CZL-159 block)."""
        payload = _build_pretooluse_payload(
            file_path="content/analysis.md",
            content=(
                "For the intended audience of decision makers: "
                "Based on research and evidence from multiple sources, "
                "the analysis concludes that the framework is sound. "
                "Therefore the insight is clear."
            ),
        )
        result = _run_hook(payload)

        hook_output = result.get("hookSpecificOutput", {})
        decision = hook_output.get("permissionDecision", "")
        # Should NOT be denied by CZL-159 (all signals present)
        if decision == "deny":
            reason = hook_output.get("permissionDecisionReason", "")
            assert "CZL-159" not in reason, (
                f"CZL-159 should not block when all signals present. Reason: {reason}"
            )
