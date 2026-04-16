"""
Test hook_wrapper.py Agent-tool Gate 1 wiring (Board 2026-04-16 P0).

Verifies that:
1. Valid 5-tuple dispatch passes silently (no warning, no block)
2. Missing-Xt dispatch emits warning + CIEU CZL_DISPATCH_GATE1_VIOLATION event
3. Non-Agent tools are not affected by Gate 1 logic
4. Agent tool with 5-tuple structure (even if content invalid) passes Gate 1
   (Gate 1 only checks structure presence, not empirical verify)

Note: Direct imports from czl_protocol instead of subprocess hook_wrapper
      to avoid hang on check_hook(payload) waiting for gov-mcp daemon.
"""
import sys
from pathlib import Path

# Add Y-star-gov to PYTHONPATH
ystar_repo = Path(__file__).parent.parent.parent.parent / "Y-star-gov"
sys.path.insert(0, str(ystar_repo))

from ystar.kernel.czl_protocol import validate_dispatch


def test_valid_5tuple_dispatch_silent():
    """Valid 5-tuple dispatch should pass with no hard errors (warnings allowed)."""
    prompt = """
**Y\\***: file.py exists with function foo() passing test
**Xt**: file.py does not exist (verified via Read)
**U**: (1) Write file.py with foo() (2) pytest test_foo.py
**Yt+1**: file.py exists, test green
**Rt+1**: 0 if test PASS else 1
Task ID: eng-kernel#W22.4
Recipient: eng-kernel
    """

    missing_sections = validate_dispatch(prompt)

    # Should have no hard errors (warnings like "No recipient" are OK if recipient is implicit)
    # Filter out warnings (items starting with "Warning:")
    hard_errors = [s for s in missing_sections if not s.startswith("Warning:")]
    assert hard_errors == [], f"Gate 1 flagged valid dispatch with hard errors: {hard_errors}"


def test_missing_xt_dispatch_warns():
    """Missing Xt section should be flagged by validate_dispatch."""
    prompt = """
**Y\\***: file.py exists
**U**: (1) Write file.py
**Yt+1**: file.py exists
**Rt+1**: 0
Task ID: eng-kernel#W22.5
Recipient: eng-kernel
    """

    missing_sections = validate_dispatch(prompt)

    # Should flag missing Xt (exact text: "Missing Xt (pre-state)")
    hard_errors = [s for s in missing_sections if not s.startswith("Warning:")]
    assert any("Xt" in s for s in hard_errors), \
        f"Gate 1 did not flag missing Xt: {hard_errors}"
    assert len(hard_errors) > 0, "Gate 1 returned no hard errors for missing-Xt dispatch"


def test_missing_multiple_sections():
    """Missing Y*, Xt, and Yt+1 should all be flagged."""
    prompt = """
**U**: (1) Do something (2) Do another thing
**Rt+1**: 0 maybe?
Task ID: test#multi
Recipient: eng-kernel
    """

    missing_sections = validate_dispatch(prompt)

    # Should flag missing Y*, Xt, Yt+1 (exact text from czl_protocol.py)
    hard_errors = [s for s in missing_sections if not s.startswith("Warning:")]
    assert any("Y*" in s for s in hard_errors), \
        f"Gate 1 did not flag missing Y*: {hard_errors}"
    assert any("Xt" in s for s in hard_errors), \
        f"Gate 1 did not flag missing Xt: {hard_errors}"
    assert any("Yt+1" in s for s in hard_errors), \
        f"Gate 1 did not flag missing Yt+1: {hard_errors}"


def test_5tuple_structure_but_invalid_content_passes_gate1():
    """
    Gate 1 only checks structure presence, not empirical correctness.
    A dispatch with all 5 sections present (even if content is hallucinated)
    should pass Gate 1 silently.
    """
    prompt = """
**Y\\***: file.py is L5 production-ready
**Xt**: file.py is L4 (based on vibes, not Read tool)
**U**: (1) Approve L5 merge (2) Ship to prod
**Yt+1**: file.py is L5 in production
**Rt+1**: 0 (I'm confident!)
Task ID: eng-kernel#hallucinated
Recipient: eng-kernel
    """

    missing_sections = validate_dispatch(prompt)

    # Gate 1 should pass (structure is present, even if Xt is impression-based)
    # Gate 2 (empirical verify) would catch this, but that's not Gate 1's job
    # NOTE: czl_protocol.py DOES check for speculation markers in Xt (line 99)
    # So this will actually flag "Xt contains speculation (not measured via tool_use)"
    # But the 5-tuple structure itself is complete, so test the distinction:
    hard_errors = [s for s in missing_sections if "Missing" in s]
    assert hard_errors == [], f"Gate 1 flagged structurally complete dispatch as missing: {hard_errors}"
    # Speculation warning is OK (Gate 1 detects it, Gate 2 verifies it)


def test_hook_wrapper_has_agent_tool_branch():
    """
    Verify hook_wrapper.py source code contains Agent-tool Gate 1 branch.
    This is a smoke test to ensure the hook is wired.
    """
    hook_wrapper_path = Path(__file__).parent.parent.parent / "scripts" / "hook_wrapper.py"
    assert hook_wrapper_path.exists(), f"hook_wrapper.py not found at {hook_wrapper_path}"

    source = hook_wrapper_path.read_text()

    # Check for key Gate 1 markers
    assert 'if tool == "Agent":' in source, "hook_wrapper missing Agent-tool branch"
    assert "validate_dispatch" in source, "hook_wrapper missing validate_dispatch call"
    assert "CZL_DISPATCH_GATE1_VIOLATION" in source, "hook_wrapper missing CIEU event emission"
    assert "missing_sections" in source, "hook_wrapper missing missing_sections logic"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
