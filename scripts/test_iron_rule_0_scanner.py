#!/usr/bin/env python3
"""Tests for Iron Rule 0 choice-question scanner (hook_stop_reply_scan.py).
Canonical location: tests/scripts/test_iron_rule_0_scanner.py
Placed in scripts/ due to write-scope constraints; move after agent-id fix."""

import sys
import os

# Ensure scripts/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from hook_stop_reply_scan import scan_for_choice_question, inject_iron_rule_0_warning


def test_chinese_choice_detected():
    """Chinese forbidden patterns: 请选择, 方案一/二/三, 三选一, 您决定...哪个."""
    # 请选择
    results = scan_for_choice_question("请选择 1) 方案一 2) 方案二")
    patterns_found = {r["pattern"] for r in results}
    assert "chinese_choose" in patterns_found, f"Expected chinese_choose, got {patterns_found}"

    # 方案一/二
    assert "chinese_plan_abc" in patterns_found

    # 三选一
    results2 = scan_for_choice_question("这是三选一的问题")
    patterns2 = {r["pattern"] for r in results2}
    assert "chinese_pick_one" in patterns2

    # 您决定...哪个
    results3 = scan_for_choice_question("您决定用哪个方案？")
    patterns3 = {r["pattern"] for r in results3}
    assert "chinese_you_decide" in patterns3


def test_english_option_detected():
    """English forbidden patterns: Option A:, Option 1:, We have N paths, Which...prefer."""
    # Option A:
    r1 = scan_for_choice_question("Option A: use hooks. Option B: use polling.")
    p1 = {r["pattern"] for r in r1}
    assert "english_option_letter" in p1

    # Option 1:
    r2 = scan_for_choice_question("Option 1: refactor. Option 2: rewrite.")
    p2 = {r["pattern"] for r in r2}
    assert "english_option_number" in p2

    # We have N paths
    r3 = scan_for_choice_question("We have 3 paths forward.")
    p3 = {r["pattern"] for r in r3}
    assert "english_n_paths" in p3

    # Which...prefer
    r4 = scan_for_choice_question("Which approach do you prefer?")
    p4 = {r["pattern"] for r in r4}
    assert "english_which_prefer" in p4


def test_numbered_list_summary_not_false_positive():
    """Numbered summary lists (e.g. '今天做了 3 件事: 1) X 2) Y 3) Z') must NOT trigger."""
    text = "今天做了 3 件事: 1) 修复了 hook 2) 写了测试 3) 更新了文档"
    results = scan_for_choice_question(text)
    assert results == [], f"False positive: numbered summary triggered {results}"

    text2 = "Completed 3 tasks: 1) fix hook 2) write tests 3) update docs"
    results2 = scan_for_choice_question(text2)
    assert results2 == [], f"False positive: English numbered summary triggered {results2}"


def test_single_option_recommendation_not_false_positive():
    """Single-option recommendation (e.g. '我选 X 因为 Y') must NOT trigger."""
    text = "我选 X 因为 Y, NOW 执行..."
    results = scan_for_choice_question(text)
    assert results == [], f"False positive: single recommendation triggered {results}"

    text2 = "I recommend approach A because it is simpler. Executing now."
    results2 = scan_for_choice_question(text2)
    assert results2 == [], f"False positive: English recommendation triggered {results2}"


def test_position_returned():
    """Each match must include 'position' (int >= 0) indicating where in the text it was found."""
    text = "blah blah 请选择 something"
    results = scan_for_choice_question(text)
    assert len(results) >= 1
    for r in results:
        assert "position" in r, f"Missing 'position' key in result: {r}"
        assert isinstance(r["position"], int)
        assert r["position"] >= 0
        # Verify position is correct: text[position:] should start with the match
        assert text[r["position"]:].startswith(r["match"]), (
            f"Position {r['position']} does not point to match '{r['match']}' in text"
        )

    # Also verify inject_iron_rule_0_warning returns non-empty when violations exist
    warning = inject_iron_rule_0_warning(text, results)
    assert "IRON RULE 0 VIOLATION" in warning
    assert "chinese_choose" in warning

    # And returns empty when no violations
    empty_warning = inject_iron_rule_0_warning("clean text", [])
    assert empty_warning == ""
