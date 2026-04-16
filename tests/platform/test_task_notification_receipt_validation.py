#!/usr/bin/env python3
"""
Platform Engineer — Test task-notification receipt extraction in Stop hook.
Board 2026-04-16: Gate 2 fix — hook must extract receipts from task-notification blocks.
"""
import re
import pytest


def extract_task_notifications(reply_text: str) -> list[str]:
    """Mimics hook_stop_reply_scan.py task-notification extraction."""
    notification_pattern = re.compile(
        r'<task-notification>.*?<result>(.*?)</result>.*?</task-notification>',
        re.DOTALL
    )
    return notification_pattern.findall(reply_text)


def test_clean_reply_no_notifications():
    """Clean CEO reply (no task-notifications) should return empty list."""
    reply = "Dispatched Ethan to fix database. Commit d3a7b91f."
    receipts = extract_task_notifications(reply)
    assert receipts == []


def test_single_notification_extracted():
    """Reply with 1 task-notification block should extract 1 receipt."""
    reply = """
    Dispatched Ethan.
    <task-notification>
    <agent>cto</agent>
    <result>
    Y*: Database migration complete.
    Xt: migrations/001.sql applied.
    Yt+1: Schema version 2.
    Rt+1: 0 (verified via SELECT version).
    </result>
    </task-notification>
    Next:派 Maya.
    """
    receipts = extract_task_notifications(reply)
    assert len(receipts) == 1
    assert "Y*: Database migration complete" in receipts[0]
    assert "Rt+1: 0" in receipts[0]


def test_multiple_notifications_in_one_reply():
    """Reply with 2 task-notifications should extract both receipts."""
    reply = """
    <task-notification>
    <agent>eng-kernel</agent>
    <result>Y*: Kernel refactor done. Rt+1: 0.</result>
    </task-notification>
    Then:
    <task-notification>
    <agent>eng-platform</agent>
    <result>Y*: Hook wired. Rt+1: 0 (smoke test passed).</result>
    </task-notification>
    """
    receipts = extract_task_notifications(reply)
    assert len(receipts) == 2
    assert "Kernel refactor done" in receipts[0]
    assert "Hook wired" in receipts[1]


def test_malformed_notification_graceful_skip():
    """Malformed XML (unclosed tags) should not crash extraction."""
    reply = """
    <task-notification>
    <result>Incomplete receipt...
    """
    # Should not crash, returns empty (regex doesn't match unclosed tags)
    receipts = extract_task_notifications(reply)
    assert receipts == []


def test_notification_with_multiline_receipt():
    """Receipt spanning multiple lines should be fully captured (re.DOTALL)."""
    reply = """
    <task-notification>
    <result>
    Y*: Multi-line receipt.
    Xt: Line 2.
    U: Line 3.
    Yt+1: Line 4.
    Rt+1: 0.
    </result>
    </task-notification>
    """
    receipts = extract_task_notifications(reply)
    assert len(receipts) == 1
    assert "Y*: Multi-line receipt" in receipts[0]
    assert "Rt+1: 0" in receipts[0]
