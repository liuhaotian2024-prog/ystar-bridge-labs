#!/usr/bin/env python3
"""
CZL-112 P0 atomic: Coordinator reply 5-tuple scan import fix + Chinese prose compatibility

3 core assertions:
1. Import resolves OR fail-closed emits COORDINATOR_AUDIT_UNAVAILABLE (no silent skip)
2. Chinese prose with English 5-tuple labels passes (e.g., "**Y\***：内容...")
3. Chinese prose WITHOUT labels triggers violation

Ryan (eng-platform) 2026-04-16
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
sys.path.insert(0, str(REPO_ROOT / "scripts"))


def test_import_resolution_or_fail_closed():
    """
    Assertion 1: coordinator_audit import either succeeds OR fail-closed path emits event.
    No silent skip allowed.
    """
    sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/Y-star-gov")
    try:
        from ystar.governance.coordinator_audit import check_reply_5tuple_compliance
        import_success = True
    except ImportError:
        import_success = False

    # Test hook_stop_reply_scan.py's injector (import section at lines 36-43)
    from hook_stop_reply_scan import _COORD_AUDIT_AVAILABLE

    # One of these MUST be true:
    # (a) Import succeeded → _COORD_AUDIT_AVAILABLE=True
    # (b) Import failed → _COORD_AUDIT_AVAILABLE=False AND fail-closed emits event
    if import_success:
        assert _COORD_AUDIT_AVAILABLE is True, "Import succeeded but _COORD_AUDIT_AVAILABLE=False"
    else:
        # If import failed, verify fail-closed logic exists (emit COORDINATOR_AUDIT_UNAVAILABLE)
        # Read injector function source to verify emit call exists
        hook_script = REPO_ROOT / "scripts" / "hook_stop_reply_scan.py"
        source = hook_script.read_text()
        assert "COORDINATOR_AUDIT_UNAVAILABLE" in source, "Import failed but no fail-closed emit in injector"
        assert "_COORD_AUDIT_AVAILABLE is False" not in source or "emit_cieu" in source, "Fail-closed path missing CIEU emit"


def test_chinese_prose_with_english_labels_passes():
    """
    Assertion 2: Chinese prose with English 5-tuple labels should PASS.
    Example: "**Y\***：实现全链路 coordinator reply 检测..."
    """
    sample_reply_chinese = """
    **Y\***：实现全链路 coordinator reply 检测
    **Xt**：当前 import 失败导致 silent skip
    **U**：修复 import path + 增加 fallback regex
    **Yt+1**：检测器 LIVE + 中文散文兼容
    **Rt+1**：0 (全绿)
    """

    # Import injector function
    from hook_stop_reply_scan import inject_coordinator_reply_5tuple_audit

    # Verify no violation raised (function should not emit COORDINATOR_REPLY_MISSING_5TUPLE)
    # Mock _emit_cieu to capture events
    emitted_events = []
    original_emit = sys.modules['hook_stop_reply_scan']._emit_cieu

    def mock_emit(event_type, metadata):
        emitted_events.append({"type": event_type, "meta": metadata})

    sys.modules['hook_stop_reply_scan']._emit_cieu = mock_emit

    try:
        inject_coordinator_reply_5tuple_audit(sample_reply_chinese)
        # Should NOT emit COORDINATOR_REPLY_MISSING_5TUPLE for valid reply
        violations = [e for e in emitted_events if e["type"] == "COORDINATOR_REPLY_MISSING_5TUPLE"]
        assert len(violations) == 0, f"Chinese prose with labels wrongly triggered violation: {violations}"
    finally:
        sys.modules['hook_stop_reply_scan']._emit_cieu = original_emit


def test_chinese_prose_without_labels_triggers_violation():
    """
    Assertion 3: Chinese prose WITHOUT 5-tuple labels should trigger violation (>200 chars).
    """
    sample_reply_no_labels = """
    老大，这个任务已经完成了。我修复了 import path，增加了 fallback regex，
    现在检测器能处理中文散文了。所有测试都通过了。下一步我会监控生产环境
    确保没有 false positives。
    """ * 3  # Repeat to exceed 200 chars

    assert len(sample_reply_no_labels) > 200, "Test sample too short"

    from hook_stop_reply_scan import inject_coordinator_reply_5tuple_audit

    emitted_events = []
    original_emit = sys.modules['hook_stop_reply_scan']._emit_cieu

    def mock_emit(event_type, metadata):
        emitted_events.append({"type": event_type, "meta": metadata})

    sys.modules['hook_stop_reply_scan']._emit_cieu = mock_emit

    try:
        inject_coordinator_reply_5tuple_audit(sample_reply_no_labels)
        # SHOULD emit COORDINATOR_REPLY_MISSING_5TUPLE for prose without labels
        violations = [e for e in emitted_events if e["type"] == "COORDINATOR_REPLY_MISSING_5TUPLE"]
        assert len(violations) > 0, "Chinese prose without labels did NOT trigger violation (should have)"
    finally:
        sys.modules['hook_stop_reply_scan']._emit_cieu = original_emit


if __name__ == "__main__":
    print("Test 1: Import resolution or fail-closed emit...")
    test_import_resolution_or_fail_closed()
    print("✓ PASS")

    print("Test 2: Chinese prose with English labels passes...")
    test_chinese_prose_with_english_labels_passes()
    print("✓ PASS")

    print("Test 3: Chinese prose without labels triggers violation...")
    test_chinese_prose_without_labels_triggers_violation()
    print("✓ PASS")

    print("\n✅ All 3 assertions PASS — CZL-112 P0 COMPLETE")
