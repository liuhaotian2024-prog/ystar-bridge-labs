"""Test suite for reply_taxonomy whitelist enforcement.

Authority: Maya Patel (eng-governance) per CZL-128 P1 LIGHT atomic
Upstream: CZL-123 hallucinated this file (claimed 15 assertions PASS, file did NOT exist)
Downstream: reply_taxonomy.py (impl), reply_taxonomy_whitelist_v1.md (spec)
Purpose: Validate 5 templates (DISPATCH/RECEIPT/NOTIFICATION/QUERY/ACK) structure enforcement
"""

import pytest
from ystar.governance.reply_taxonomy import (
    audit_reply,
    extract_template_tag,
    validate_template,
)


# ====================
# Positive Tests (5)
# ====================

def test_dispatch_valid():
    """Template: [DISPATCH] with 5-tuple + agent_id + action verbs."""
    reply = r"""[DISPATCH] Maya CZL-999 P0 atomic

**Y\***: Test task
**Xt**: State X
**U**: Action U
**Yt+1**: Expected Y
**Rt+1**: 0 when done

派 Maya sub-agent, atomic ≤6 tool_uses.
"""
    tag = extract_template_tag(reply)
    assert tag == "DISPATCH"
    is_valid, errors = validate_template(tag, reply)
    assert is_valid is True
    assert errors == []


def test_receipt_valid():
    """Template: [RECEIPT] with 5-tuple + test paste + empirical pastes."""
    reply = r"""[RECEIPT] CZL-999 done

**Y\***: Test
**Xt**: X
**U**: 3 tool_uses
**Yt+1**: Y
**Rt+1**: 0

pytest: 10/10 PASS
ls -la: file.py 1234 bytes
git log: commit abc123
"""
    tag = extract_template_tag(reply)
    assert tag == "RECEIPT"
    is_valid, errors = validate_template(tag, reply)
    assert is_valid is True
    assert errors == []


def test_notification_valid():
    """Template: [NOTIFICATION] with metrics/artifact."""
    reply = """[NOTIFICATION] Campaign v6 W1 closed

W1: commit f00e91ac LIVE, 0 false-positives
2/10 subgoals closed.
"""
    tag = extract_template_tag(reply)
    assert tag == "NOTIFICATION"
    is_valid, errors = validate_template(tag, reply)
    assert is_valid is True
    assert errors == []


def test_query_valid():
    """Template: [QUERY] ≤120 chars, ends with ?"""
    reply = "[QUERY] W11 needs P0 priority升级吗？"
    tag = extract_template_tag(reply)
    assert tag == "QUERY"
    is_valid, errors = validate_template(tag, reply)
    assert is_valid is True
    assert errors == []


def test_ack_valid():
    """Template: [ACK] ≤30 chars, no action verbs."""
    reply = "[ACK] 收到"
    tag = extract_template_tag(reply)
    assert tag == "ACK"
    is_valid, errors = validate_template(tag, reply)
    assert is_valid is True
    assert errors == []


# ====================
# Negative Tests (3)
# ====================

def test_missing_tag():
    """No tag prefix → violation."""
    reply = "I will dispatch Maya to do X."
    tag = extract_template_tag(reply)
    assert tag is None
    violation = audit_reply(reply, agent_id="ceo")
    assert violation is not None
    assert "tag" in str(violation).lower()


def test_dispatch_missing_5tuple():
    """[DISPATCH] without Y*/Xt/U/Yt+1/Rt+1 → violation."""
    reply = "[DISPATCH] Maya please do X."
    tag = extract_template_tag(reply)
    assert tag == "DISPATCH"
    is_valid, errors = validate_template(tag, reply)
    assert is_valid is False
    assert any("5tuple" in e for e in errors)


def test_query_too_long():
    """[QUERY] >120 chars → violation."""
    reply = "[QUERY] " + ("A" * 121) + "?"
    tag = extract_template_tag(reply)
    assert tag == "QUERY"
    is_valid, errors = validate_template(tag, reply)
    assert is_valid is False
    assert any("120" in e for e in errors)


# ====================
# Edge Cases (2)
# ====================

def test_receipt_missing_empirical_pastes():
    """[RECEIPT] with 5-tuple but <2 empirical pastes → violation."""
    reply = r"""[RECEIPT] CZL-999

**Y\***: X
**Xt**: Y
**U**: Z
**Yt+1**: A
**Rt+1**: 0

Only one paste: ls -la file.py
"""
    tag = extract_template_tag(reply)
    assert tag == "RECEIPT"
    is_valid, errors = validate_template(tag, reply)
    assert is_valid is False
    assert any("empirical" in e.lower() for e in errors)


def test_ack_contains_metric():
    """[ACK] with metric/number → violation (should be RECEIPT)."""
    reply = "[ACK] 收到，commit abc123de"
    tag = extract_template_tag(reply)
    assert tag == "ACK"
    is_valid, errors = validate_template(tag, reply)
    assert is_valid is False
    assert any("metric" in e.lower() for e in errors)
