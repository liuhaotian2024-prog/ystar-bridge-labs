#!/usr/bin/env python3
"""
tests/platform/test_stop_reply_scan_wiring.py

Board 2026-04-16: Verify orphan Y-star-gov injectors now wired into production Stop hook.

Tests:
  1. All 4 injector functions importable from stop_hook.py
  2. Each function callable without crashing (mock CEO reply)
  3. Import path in hook_stop_reply_scan.py is correct
  4. YSTAR_ADAPTERS_AVAILABLE flag set True on success

Test Run:
  pytest tests/platform/test_stop_reply_scan_wiring.py -v
"""
import sys
from pathlib import Path

# Add Y-star-gov to sys.path (same as production hook)
sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/Y-star-gov")

def test_injector_imports():
    """Verify all 4 injectors importable from ystar.adapters.hooks.stop_hook."""
    try:
        from ystar.adapters.hooks.stop_hook import (
            inject_warnings_to_session,
            inject_czl_corrections,
            auto_validate_subagent_receipt,
            inject_coordinator_audit_warning,
        )
    except ImportError as e:
        pytest.fail(f"Injector import failed: {e}")

    # Verify each is callable
    assert callable(inject_warnings_to_session), "inject_warnings_to_session not callable"
    assert callable(inject_czl_corrections), "inject_czl_corrections not callable"
    assert callable(auto_validate_subagent_receipt), "auto_validate_subagent_receipt not callable"
    assert callable(inject_coordinator_audit_warning), "inject_coordinator_audit_warning not callable"


def test_injector_no_crash_on_empty_input():
    """Verify each injector handles empty/None input gracefully (fail-safe)."""
    from ystar.adapters.hooks.stop_hook import (
        inject_warnings_to_session,
        inject_czl_corrections,
        auto_validate_subagent_receipt,
        inject_coordinator_audit_warning,
    )

    # 1. K9-RT inject (no queue file → returns None)
    result = inject_warnings_to_session()
    assert result is None or isinstance(result, str), "K9-RT inject broke on empty queue"

    # 2. CZL inject (no receipt text → returns None)
    result = inject_czl_corrections(receipt_text="")
    assert result is None or isinstance(result, str), "CZL inject broke on empty receipt"

    # 3. Auto-validate receipt (no artifacts → returns pass)
    result = auto_validate_subagent_receipt(receipt_text="Some reply")
    assert isinstance(result, dict), "Auto-validate broke on simple receipt"
    assert "is_valid" in result, "Auto-validate missing is_valid field"

    # 4. Coordinator audit (no taskstate → returns None)
    result = inject_coordinator_audit_warning(reply_text="Some reply", taskstate=None)
    assert result is None or isinstance(result, str), "Coord audit broke on None taskstate"


def test_production_hook_imports_adapters():
    """Verify hook_stop_reply_scan.py correctly imports Y-star-gov adapters."""
    hook_script = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/hook_stop_reply_scan.py")
    assert hook_script.exists(), "hook_stop_reply_scan.py not found"

    hook_source = hook_script.read_text()

    # Check sys.path.insert line present
    assert 'sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/Y-star-gov")' in hook_source, \
        "hook_stop_reply_scan.py missing sys.path.insert for Y-star-gov"

    # Check all 4 imports present
    required_imports = [
        "inject_warnings_to_session",
        "inject_czl_corrections",
        "auto_validate_subagent_receipt",
        "inject_coordinator_audit_warning",
    ]
    for func_name in required_imports:
        assert func_name in hook_source, f"hook_stop_reply_scan.py missing import for {func_name}"


def test_production_hook_calls_all_injectors():
    """Verify hook_stop_reply_scan.py calls all 4 injectors in main()."""
    hook_script = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/hook_stop_reply_scan.py")
    hook_source = hook_script.read_text()

    # Check each injector called in main()
    assert "inject_warnings_to_session()" in hook_source, "hook missing inject_warnings_to_session call"
    assert "inject_czl_corrections(receipt_text=reply)" in hook_source, "hook missing inject_czl_corrections call"
    assert "auto_validate_subagent_receipt(receipt_text=reply)" in hook_source, "hook missing auto_validate_subagent_receipt call"
    assert "inject_coordinator_audit_warning(reply_text=reply)" in hook_source, "hook missing inject_coordinator_audit_warning call"

    # Check each call wrapped in try/except (fail-safe)
    assert hook_source.count("try:") >= 4, "hook missing fail-safe try/except wrappers (expected ≥4)"
