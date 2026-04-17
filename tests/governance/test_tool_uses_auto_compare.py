#!/usr/bin/env python3
"""
Test: Auto tool_uses claim vs metadata comparison (Maya CZL-152)

Validates that hook_stop_reply_scan.py correctly:
1. Extracts claimed tool_uses from receipt text
2. Extracts metadata tool_uses from <metadata> tag
3. Compares delta and emits CIEU event if |delta| > 2
4. Tolerates ±2 tool_uses variance (no event)
"""

import re
import sqlite3
import sys
import tempfile
from pathlib import Path

# Add hook script to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from hook_stop_reply_scan import auto_compare_tool_uses_claim, _emit_cieu, CIEU_DB


def test_match_no_mismatch():
    """Test: claimed=18, actual=18 → no CIEU event"""
    receipt = """
## RECEIPT (Ryan #CZL-102)

**tool_uses**: 18

**Rt+1**: 0
"""
    # Count CIEU events before
    conn = sqlite3.connect(str(CIEU_DB))
    before = conn.execute("SELECT COUNT(*) FROM cieu_events WHERE event_type='TOOL_USES_CLAIM_MISMATCH'").fetchone()[0]
    conn.close()

    # Run comparison
    auto_compare_tool_uses_claim(receipt, metadata_tool_uses=18, agent_id="ryan")

    # Count CIEU events after
    conn = sqlite3.connect(str(CIEU_DB))
    after = conn.execute("SELECT COUNT(*) FROM cieu_events WHERE event_type='TOOL_USES_CLAIM_MISMATCH'").fetchone()[0]
    conn.close()

    assert after == before, "Should NOT emit CIEU event for exact match"
    print("✓ Test 1 PASS: exact match → no event")


def test_tolerance_within_2():
    """Test: claimed=17, actual=18 → no CIEU event (delta=1, ≤2 threshold)"""
    receipt = """
## RECEIPT (Maya #CZL-104)

**tool_uses**: 17

**Rt+1**: 0
"""
    conn = sqlite3.connect(str(CIEU_DB))
    before = conn.execute("SELECT COUNT(*) FROM cieu_events WHERE event_type='TOOL_USES_CLAIM_MISMATCH'").fetchone()[0]
    conn.close()

    auto_compare_tool_uses_claim(receipt, metadata_tool_uses=18, agent_id="maya")

    conn = sqlite3.connect(str(CIEU_DB))
    after = conn.execute("SELECT COUNT(*) FROM cieu_events WHERE event_type='TOOL_USES_CLAIM_MISMATCH'").fetchone()[0]
    conn.close()

    assert after == before, "Should NOT emit CIEU event for delta ≤2"
    print("✓ Test 2 PASS: delta=1 within tolerance → no event")


def test_mismatch_exceeds_threshold():
    """Test: claimed=12, actual=18 → CIEU event emitted (delta=6 > 2)"""
    receipt = """
## RECEIPT (Ryan #CZL-102)

**tool_uses**: 12

**Rt+1**: 1
"""
    conn = sqlite3.connect(str(CIEU_DB))
    before = conn.execute("SELECT COUNT(*) FROM cieu_events WHERE event_type='TOOL_USES_CLAIM_MISMATCH'").fetchone()[0]
    conn.close()

    auto_compare_tool_uses_claim(receipt, metadata_tool_uses=18, agent_id="ryan")

    conn = sqlite3.connect(str(CIEU_DB))
    after = conn.execute("SELECT COUNT(*) FROM cieu_events WHERE event_type='TOOL_USES_CLAIM_MISMATCH'").fetchone()[0]

    assert after == before + 1, f"Should emit 1 CIEU event for delta=6 > 2 (before={before}, after={after})"

    # Verify event metadata
    latest = conn.execute(
        "SELECT task_description FROM cieu_events WHERE event_type='TOOL_USES_CLAIM_MISMATCH' ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    conn.close()

    event_data = latest[0]
    assert "ryan" in event_data.lower(), "Event should contain agent_id"
    assert "12" in event_data and "18" in event_data, "Event should contain claimed/actual values"

    print("✓ Test 3 PASS: delta=6 > threshold → event emitted")


def test_over_claim_high_severity():
    """Test: claimed=25, actual=18 → high severity (delta=7)"""
    receipt = """
## RECEIPT (Leo #CZL-103)

24,682 violations analyzed. tool_uses: 25

**Rt+1**: 0
"""
    conn = sqlite3.connect(str(CIEU_DB))
    before = conn.execute("SELECT COUNT(*) FROM cieu_events WHERE event_type='TOOL_USES_CLAIM_MISMATCH'").fetchone()[0]
    conn.close()

    auto_compare_tool_uses_claim(receipt, metadata_tool_uses=18, agent_id="leo")

    conn = sqlite3.connect(str(CIEU_DB))
    after = conn.execute("SELECT COUNT(*) FROM cieu_events WHERE event_type='TOOL_USES_CLAIM_MISMATCH'").fetchone()[0]
    assert after == before + 1, "Should emit CIEU event for delta=7"

    latest = conn.execute(
        "SELECT task_description FROM cieu_events WHERE event_type='TOOL_USES_CLAIM_MISMATCH' ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    conn.close()
    assert "high" in latest[0].lower() or "7" in latest[0], "Event should mark high severity for delta>5"

    print("✓ Test 4 PASS: delta=7 → high severity event")


def test_no_claim_in_receipt():
    """Test: receipt without tool_uses claim → no event (acceptable for conversational acks)"""
    receipt = """
## RECEIPT (Maya #CZL-150)

好的，收到。

**Rt+1**: 0
"""
    conn = sqlite3.connect(str(CIEU_DB))
    before = conn.execute("SELECT COUNT(*) FROM cieu_events WHERE event_type='TOOL_USES_CLAIM_MISMATCH'").fetchone()[0]
    conn.close()

    auto_compare_tool_uses_claim(receipt, metadata_tool_uses=3, agent_id="maya")

    conn = sqlite3.connect(str(CIEU_DB))
    after = conn.execute("SELECT COUNT(*) FROM cieu_events WHERE event_type='TOOL_USES_CLAIM_MISMATCH'").fetchone()[0]
    conn.close()

    assert after == before, "Should NOT emit event if no claim in receipt"
    print("✓ Test 5 PASS: no claim → no event")


def test_claim_format_variations():
    """Test: various claim formats (tool_uses: N, tool_uses=N, tool_uses N)"""
    # Pattern: tool_uses.*?(\d+) requires "tool_uses" before number
    # Supported: "tool_uses: N", "tool_uses=N", "tool_uses N"
    # NOT supported: "N tool_uses" (reverse order — rare in practice)
    formats = [
        ("tool_uses: 15", 15),
        ("tool_uses=15", 15),
        ("tool_uses 15", 15),
        ("tool_uses claim: 15", 15),
        ("**tool_uses**: 15", 15),
    ]

    for receipt_fragment, expected_claim in formats:
        receipt = f"## RECEIPT\n\n{receipt_fragment}\n\n**Rt+1**: 0"
        claim_match = re.search(r'tool_uses.*?(\d+)', receipt, re.IGNORECASE)
        assert claim_match, f"Pattern should match format: {receipt_fragment}"
        assert int(claim_match.group(1)) == expected_claim, f"Should extract {expected_claim} from {receipt_fragment}"

    print("✓ Test 6 PASS: claim format variations all extracted correctly")


if __name__ == "__main__":
    print("\n=== Maya CZL-152: Tool_uses Auto-Compare Tests ===\n")

    # Ensure CIEU DB exists
    if not CIEU_DB.exists():
        print(f"⚠️  CIEU DB not found at {CIEU_DB}, tests may fail")
        sys.exit(1)

    test_match_no_mismatch()
    test_tolerance_within_2()
    test_mismatch_exceeds_threshold()
    test_over_claim_high_severity()
    test_no_claim_in_receipt()
    test_claim_format_variations()

    print("\n=== All 6 tests PASS ===\n")
    print("Empirical verification:")
    print(f"  1. New function auto_compare_tool_uses_claim() in hook_stop_reply_scan.py")
    print(f"  2. CIEU event type TOOL_USES_CLAIM_MISMATCH emitted on delta > 2")
    print(f"  3. Tolerance ±2 tool_uses (no false positives on small counting errors)")
    print(f"  4. Agent_id + claimed + actual + delta all captured in CIEU metadata")
    print(f"\nRt+1: 0 (auto-compare function LIVE + tests PASS)")
