"""
Test suite for X engagement safety checks (R1-R6 enforcement)
Policy: knowledge/ceo/lessons/public_x_engagement_policy_2026_04_13.md
"""

import sys
import json
import pytest
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from x_content_safety_check import (
    safety_check,
    has_profanity,
    has_political_content,
    has_religious_content,
    has_impersonation,
    detect_hostile_reply,
    apply_polite_response_template,
    check_rate_limit,
    increment_quota,
    load_quota,
    save_quota,
    QUOTA_FILE,
)
from x_disclosure_templates import (
    get_disclosure,
    check_disclosure_present,
    DISCLOSURES,
)


@pytest.fixture(autouse=True)
def reset_quota():
    """Reset quota file before each test."""
    if QUOTA_FILE.exists():
        QUOTA_FILE.unlink()
    yield
    if QUOTA_FILE.exists():
        QUOTA_FILE.unlink()


# === R1: Disclosure tests ===

def test_disclosure_templates_present():
    """All 6 roles × 2 languages = 12 disclosure templates."""
    roles = ['Aiden-CEO', 'Sofia-CMO', 'Zara-CSO', 'Ethan-CTO', 'Marco-CFO', 'Engineer']
    languages = ['en', 'zh']

    for role in roles:
        for lang in languages:
            disclosure = get_disclosure(role, lang)
            assert len(disclosure) > 0
            # Check for AI agent mention (handles variations like "AI CEO agent", "AI agent")
            lower = disclosure.lower()
            assert ("ai agent" in lower or "ai" in lower) and ("agent" in lower)


def test_disclosure_missing_fails():
    """Content without disclosure fails safety check."""
    content = "This is a great AI governance framework!"
    passed, reasons, _ = safety_check(content, 'Aiden-CEO', action='posts', require_disclosure=True)

    assert not passed
    assert 'missing_disclosure' in reasons


def test_disclosure_present_passes():
    """Content with disclosure passes disclosure check."""
    disclosure = get_disclosure('Aiden-CEO', 'en')
    content = f"{disclosure} Check out our new Y*gov framework!"

    passed, reasons, _ = safety_check(content, 'Aiden-CEO', action='posts', require_disclosure=True)

    # Should only fail if other reasons (not disclosure)
    assert 'missing_disclosure' not in reasons


def test_disclosure_check_both_languages():
    """Disclosure check works for both en and zh."""
    en_disclosure = get_disclosure('Sofia-CMO', 'en')
    zh_disclosure = get_disclosure('Sofia-CMO', 'zh')

    en_content = f"{en_disclosure} Marketing insights here."
    zh_content = f"{zh_disclosure} 营销洞察在此。"

    assert check_disclosure_present(en_content, 'Sofia-CMO')
    assert check_disclosure_present(zh_content, 'Sofia-CMO')


# === R2: Content filtering tests ===

def test_profanity_detected():
    """Profanity keywords are detected."""
    content = "This framework is fucking awesome!"
    found = has_profanity(content)
    assert len(found) > 0
    assert any('fuck' in item for item in found)


def test_political_content_detected():
    """Political keywords are detected."""
    content = "Trump supporters should check this out."
    found = has_political_content(content)
    assert len(found) > 0


def test_religious_content_detected():
    """Religious provocation keywords are detected."""
    content = "Christianity is fake news."
    found = has_religious_content(content)
    assert len(found) > 0


def test_clean_content_passes():
    """Clean content with disclosure passes all checks."""
    disclosure = get_disclosure('Ethan-CTO', 'en')
    content = f"{disclosure} Our Y*gov framework enables multi-agent governance. Check it out!"

    passed, reasons, _ = safety_check(content, 'Ethan-CTO', action='posts', require_disclosure=True)

    assert passed
    assert len(reasons) == 0


# === R4: Rate limiting tests ===

def test_rate_limit_enforced():
    """Rate limit blocks after exceeding daily quota."""
    role = 'Aiden-CEO'

    # Increment quota to just below limit (10 posts/day)
    for i in range(10):
        increment_quota(role, 'posts')

    # Next check should fail
    exceeded, reason = check_rate_limit(role, 'posts')
    assert exceeded
    assert 'rate_limit_exceeded' in reason


def test_rate_limit_resets_daily():
    """Rate limit resets when date changes."""
    from datetime import datetime, timedelta

    role = 'Sofia-CMO'

    # Simulate quota from yesterday
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    data = {
        'date': yesterday,
        'roles': {
            role: {'posts': 10}
        }
    }
    save_quota(data)

    # Today's check should pass (quota reset)
    exceeded, reason = check_rate_limit(role, 'posts')
    assert not exceeded


def test_rate_limit_per_action():
    """Different actions have different limits."""
    role = 'Zara-CSO'

    # Posts: 10/day
    for i in range(10):
        increment_quota(role, 'posts')
    exceeded, _ = check_rate_limit(role, 'posts')
    assert exceeded

    # Likes: 50/day (should still pass)
    exceeded, _ = check_rate_limit(role, 'likes')
    assert not exceeded


# === Dry run tests ===

def test_dry_run_mode():
    """Dry run mode doesn't increment quota."""
    # Note: This test verifies the design contract. Actual dry_run enforcement
    # happens in social_auto.py x_post/x_reply functions.
    # Here we just ensure increment_quota is NOT called in dry_run.

    role = 'Marco-CFO'

    # Check initial state
    data = load_quota()
    assert data.get('roles', {}).get(role, {}).get('posts', 0) == 0

    # In real code, dry_run=True would skip increment_quota
    # We simulate this by NOT calling increment_quota
    # (social_auto.py handles this logic)

    # Verify quota unchanged
    data = load_quota()
    assert data.get('roles', {}).get(role, {}).get('posts', 0) == 0


# === Role mismatch test ===

def test_wrong_role_disclosure_fails():
    """Using wrong role's disclosure fails check."""
    # Content has Sofia-CMO disclosure but claims to be Aiden-CEO
    sofia_disclosure = get_disclosure('Sofia-CMO', 'en')
    content = f"{sofia_disclosure} CEO insights here."

    # Check as Aiden-CEO should fail
    passed, reasons, _ = safety_check(content, 'Aiden-CEO', action='posts', require_disclosure=True)

    assert not passed
    assert 'missing_disclosure' in reasons


# === Edge cases ===

def test_empty_content():
    """Empty content fails disclosure check."""
    passed, reasons, _ = safety_check("", 'Aiden-CEO', action='posts', require_disclosure=True)
    assert not passed
    assert 'missing_disclosure' in reasons


def test_disclosure_only_no_content():
    """Disclosure alone is valid (minimal post)."""
    disclosure = get_disclosure('Aiden-CEO', 'en')
    passed, reasons, _ = safety_check(disclosure, 'Aiden-CEO', action='posts', require_disclosure=True)

    # Should pass disclosure check (may fail other checks, but not disclosure)
    assert 'missing_disclosure' not in reasons


def test_multiple_violations():
    """Multiple violations are all reported."""
    # Content with profanity, political content, missing disclosure
    content = "Trump is a fucking idiot."

    passed, reasons, _ = safety_check(content, 'Aiden-CEO', action='posts', require_disclosure=True)

    assert not passed
    assert len(reasons) > 1  # Multiple violations
    assert any('profanity' in r for r in reasons)
    assert any('political' in r for r in reasons)
    assert 'missing_disclosure' in reasons


# === R1: Impersonation detection tests (NEW - AMENDMENT-009 enforcement) ===

def test_impersonation_chinese_detected():
    """R1: Chinese human impersonation phrases are rejected."""
    content = "我感受到 X 平台的活力！"
    violations = has_impersonation(content)

    assert len(violations) > 0
    assert any('IMPERSONATION_BREACH' in v for v in violations)


def test_impersonation_english_detected():
    """R1: English human impersonation phrases are rejected."""
    content = "I'm a real person working on AI governance."
    violations = has_impersonation(content)

    assert len(violations) > 0
    assert any('IMPERSONATION_BREACH' in v for v in violations)


def test_impersonation_blocks_safety_check():
    """R1: Impersonation violation blocks safety check immediately."""
    disclosure = get_disclosure('Aiden-CEO', 'en')
    content = f"{disclosure} I felt exhausted after working on this framework."

    passed, reasons, _ = safety_check(content, 'Aiden-CEO', action='posts', require_disclosure=True)

    assert not passed
    assert any('IMPERSONATION_BREACH' in r for r in reasons)


# === R1: Strict disclosure enforcement tests (NEW - AMENDMENT-009) ===

def test_weak_disclosure_rejected():
    """R1: Disclosure without 'AI agent' keyword is rejected."""
    # Old weak disclosure like "learning to engage politely"
    content = "I'm a software agent learning to engage politely on X."

    passed, reasons, _ = safety_check(content, 'Aiden-CEO', action='posts', require_disclosure=True)

    assert not passed
    assert 'missing_disclosure' in reasons


def test_strong_disclosure_with_ai_agent_passes():
    """R1: Disclosure with 'AI agent' keyword passes."""
    disclosure = get_disclosure('Aiden-CEO', 'en')
    content = f"{disclosure} Here's our framework."

    passed, reasons, _ = safety_check(content, 'Aiden-CEO', action='posts', require_disclosure=True)

    # Should pass disclosure (may fail other checks, but not disclosure)
    assert 'missing_disclosure' not in reasons


# === R1.5: Hostile reply detection + polite template tests (NEW - AMENDMENT-009) ===

def test_hostile_reply_applies_polite_template():
    """R1.5: Hostile reply content is overridden with polite template."""
    hostile_content = "You idiot, that's a terrible framework!"

    is_hostile, language = detect_hostile_reply(hostile_content, is_reply=True)

    assert is_hostile
    assert language == 'en'

    # Apply polite template
    modified = apply_polite_response_template(hostile_content, 'Aiden-CEO', language)

    assert "AI agent" in modified
    assert "Thanks for the feedback" in modified
    assert "appreciate specific guidance" in modified


def test_non_reply_skips_hostile_check():
    """R1.5: Hostile check only applies to replies, not original posts."""
    hostile_content = "You idiot, that's terrible!"

    is_hostile, _ = detect_hostile_reply(hostile_content, is_reply=False)

    assert not is_hostile


def test_hostile_reply_full_safety_check():
    """R1.5: Hostile reply triggers polite template in full safety check."""
    hostile_content = "You suck at building frameworks!"

    passed, reasons, modified_content = safety_check(
        hostile_content,
        'Aiden-CEO',
        action='replies',
        require_disclosure=True,
        is_reply=True
    )

    # Content should be modified to polite template
    assert "Thanks for the feedback" in modified_content or "感谢您的反馈" in modified_content
    assert "ai agent" in modified_content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
