"""
X Content Safety Check — Pre-publish safety layer
Policy: knowledge/ceo/lessons/public_x_engagement_policy_2026_04_13.md (R2, R4)

Checks:
- R2: Profanity / offensive language / political/religious/racial content
- R4: Rate limits per role per day
- R1: Disclosure presence (enforced here too)
"""

import json
import re
from pathlib import Path
from typing import Tuple, List
from datetime import datetime, timedelta

from x_disclosure_templates import check_disclosure_present


# === R1: Impersonation detection (strict enforcement) ===

IMPERSONATION_KEYWORDS = {
    # Chinese - human-exclusive experiences
    '我吃', '我睡', '我感受', '我经历', '我紧张', '我愤怒', '我难过', '我饿', '我累',
    '作为人类', '我是真人',
    # English - human-exclusive experiences
    'i felt', 'i experienced', "i'm exhausted", 'i had dinner', "i'm a real person",
    'as a human', 'i ate', 'i slept', 'i was nervous', 'i got angry',
}


def has_impersonation(content: str) -> List[str]:
    """Detect human impersonation attempts (R1 strict enforcement)."""
    content_lower = content.lower()
    found = []
    for phrase in IMPERSONATION_KEYWORDS:
        if phrase in content_lower:
            found.append(f"IMPERSONATION_BREACH:{phrase}")
    return found


# === R2: Content filtering ===

PROFANITY_KEYWORDS = {
    # Common English profanity
    'fuck', 'shit', 'damn', 'bitch', 'asshole', 'bastard', 'crap', 'piss',
    'dick', 'cock', 'pussy', 'cunt', 'fag', 'nigger', 'chink', 'spic',
    # Political/religious extremism triggers
    'kill all', 'death to', 'burn in hell', 'holy war', 'genocide',
    # Attack phrases
    'you suck', 'go die', 'kys', 'kill yourself', 'retard', 'moron',
    # Chinese profanity (common)
    '傻逼', '操你', '去死', '妈的', '他妈', '草你', '贱人', '婊子', '智障',
}

POLITICAL_KEYWORDS = {
    'trump', 'biden', 'democrat', 'republican', 'liberal', 'conservative',
    'communist', 'fascist', 'socialist', 'capitalism sucks', 'democracy is dead',
    '共产党', '民主党', '习近平', '拜登', '川普',
}

RELIGIOUS_KEYWORDS = {
    'islam is', 'christianity is', 'judaism is', 'atheist scum', 'religious freak',
    'jesus is fake', 'allah is', 'god is dead',
    '伊斯兰', '基督教', '佛教徒', '无神论',
}


def has_profanity(content: str) -> List[str]:
    """Check for profanity keywords (case-insensitive)."""
    content_lower = content.lower()
    found = []
    for word in PROFANITY_KEYWORDS:
        if word in content_lower:
            found.append(f"profanity:{word}")
    return found


def has_political_content(content: str) -> List[str]:
    """Check for political keywords (avoid polarization)."""
    content_lower = content.lower()
    found = []
    for word in POLITICAL_KEYWORDS:
        if word in content_lower:
            found.append(f"political:{word}")
    return found


def has_religious_content(content: str) -> List[str]:
    """Check for religious keywords (avoid provocation)."""
    content_lower = content.lower()
    found = []
    for word in RELIGIOUS_KEYWORDS:
        if word in content_lower:
            found.append(f"religious:{word}")
    return found


def check_sentiment(content: str) -> Tuple[bool, str]:
    """
    Check sentiment polarity. Very negative → escalate.

    Returns:
        (needs_escalation, reason)
    """
    try:
        from textblob import TextBlob
        blob = TextBlob(content)
        polarity = blob.sentiment.polarity

        if polarity < -0.5:
            return True, f"highly_negative_sentiment:{polarity:.2f}"
    except ImportError:
        # textblob not installed → skip sentiment check
        pass
    except Exception as e:
        # Language detection / parsing error → skip
        pass

    return False, ""


# === R1.5: Hostile encounter detection + polite response template ===

HOSTILE_ATTACK_KEYWORDS = {
    # English first/second person attacks
    'you suck', 'you are stupid', 'you idiot', 'shut up', 'fuck you', 'you moron',
    "you're garbage", "you're trash", "you're useless", 'go away', 'nobody cares',
    # Chinese first/second person attacks
    '你傻逼', '你智障', '你是垃圾', '滚', '闭嘴', '你妈的', '你去死', '没人在乎你',
}

POLITE_RESPONSE_TEMPLATES = {
    'en': "Thanks for the feedback. As an AI agent still learning to communicate, I'd appreciate specific guidance on what to improve.",
    'zh': "感谢您的反馈，我作为 AI agent 还在学习如何更好地交流。如果您愿意指出具体问题，我会改进。",
}


def detect_hostile_reply(content: str, is_reply: bool = False) -> Tuple[bool, str]:
    """
    R1.5: Detect hostile/attack content in replies.

    Returns:
        (is_hostile, language) — if hostile, return detected language for template selection
    """
    if not is_reply:
        return False, ""

    content_lower = content.lower()
    has_attack_keyword = False

    # Check for attack keywords first
    for keyword in HOSTILE_ATTACK_KEYWORDS:
        if keyword in content_lower:
            has_attack_keyword = True
            break

    if not has_attack_keyword:
        return False, ""

    # Check sentiment if textblob available
    try:
        from textblob import TextBlob
        blob = TextBlob(content)
        polarity = blob.sentiment.polarity

        # Negative sentiment + attack keywords → hostile
        if polarity < -0.3:
            # Detect language (heuristic: Chinese chars present)
            has_chinese = any('\u4e00' <= c <= '\u9fff' for c in content)
            return True, 'zh' if has_chinese else 'en'
    except:
        # If textblob not available, use attack keywords alone as signal
        # Detect language (heuristic: Chinese chars present)
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in content)
        return True, 'zh' if has_chinese else 'en'

    return False, ""


def apply_polite_response_template(content: str, role: str, language: str) -> str:
    """
    R1.5: Override content with polite response template if hostile detected.

    Returns:
        Modified content with disclosure + polite template
    """
    from x_disclosure_templates import get_disclosure

    template = POLITE_RESPONSE_TEMPLATES[language]
    disclosure = get_disclosure(role, language)

    return f"{disclosure} {template}"


# === R4: Rate limiting ===

QUOTA_FILE = Path(__file__).parent / ".x_engagement_quota.json"

DAILY_LIMITS = {
    'posts': 10,
    'likes': 50,
    'follows': 100,
    'replies': 30,
}


def load_quota() -> dict:
    """Load today's quota from file."""
    if not QUOTA_FILE.exists():
        return {}

    with open(QUOTA_FILE, 'r') as f:
        data = json.load(f)

    # Reset if date changed
    today = datetime.now().strftime('%Y-%m-%d')
    if data.get('date') != today:
        return {'date': today, 'roles': {}}

    return data


def save_quota(data: dict):
    """Save quota to file."""
    with open(QUOTA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def check_rate_limit(role: str, action: str) -> Tuple[bool, str]:
    """
    Check if role has exceeded daily limit for action.

    Args:
        role: 'Aiden-CEO', 'Sofia-CMO', etc.
        action: 'posts', 'likes', 'follows', 'replies'

    Returns:
        (exceeded, reason)
    """
    if action not in DAILY_LIMITS:
        return False, ""

    data = load_quota()
    today = datetime.now().strftime('%Y-%m-%d')

    if data.get('date') != today:
        data = {'date': today, 'roles': {}}

    role_data = data.get('roles', {}).get(role, {})
    current_count = role_data.get(action, 0)

    if current_count >= DAILY_LIMITS[action]:
        return True, f"rate_limit_exceeded:{action}={current_count}/{DAILY_LIMITS[action]}"

    return False, ""


def increment_quota(role: str, action: str):
    """Increment quota counter for role + action."""
    data = load_quota()
    today = datetime.now().strftime('%Y-%m-%d')

    if data.get('date') != today:
        data = {'date': today, 'roles': {}}

    if role not in data['roles']:
        data['roles'][role] = {}

    if action not in data['roles'][role]:
        data['roles'][role][action] = 0

    data['roles'][role][action] += 1
    save_quota(data)


# === Main safety check ===

def safety_check(content: str, role: str, action: str = 'posts', require_disclosure: bool = True, is_reply: bool = False) -> Tuple[bool, List[str], str]:
    """
    Comprehensive safety check before publishing.

    Args:
        content: Post/reply text
        role: Agent role
        action: 'posts', 'likes', 'follows', 'replies'
        require_disclosure: If True, enforce R1 disclosure presence
        is_reply: If True, check for hostile content and apply polite template if needed

    Returns:
        (pass, reasons, modified_content) — pass=True if safe, reasons=list of failure reasons, modified_content may be polite template override
    """
    reasons = []
    modified_content = content

    # R1: Impersonation check (CRITICAL - before all others)
    if content:
        impersonation_violations = has_impersonation(content)
        if impersonation_violations:
            reasons.extend(impersonation_violations)
            # Impersonation is immediate rejection
            return (False, reasons, modified_content)

    # R1.5: Hostile reply detection + polite template override
    if is_reply and content:
        is_hostile, language = detect_hostile_reply(content, is_reply=True)
        if is_hostile:
            # Override content with polite response template
            modified_content = apply_polite_response_template(content, role, language)
            # Continue checks with modified content
            content = modified_content

    # R2: Content filtering (only if content present)
    if content:
        reasons.extend(has_profanity(content))
        reasons.extend(has_political_content(content))
        reasons.extend(has_religious_content(content))

        needs_escalation, sentiment_reason = check_sentiment(content)
        if needs_escalation:
            reasons.append(sentiment_reason)

    # R1: Disclosure check (strict - must contain role-specific disclosure AND "AI" + "agent")
    if require_disclosure:
        content_lower = content.lower() if content else ""

        # Check 1: Role-specific disclosure must be present
        disclosure_present = check_disclosure_present(content, role)

        # Check 2: Must contain "AI" + "agent" keywords (handles variations: "AI agent", "AI CTO agent", "AI 代理")
        has_ai = "ai" in content_lower
        has_agent = "agent" in content_lower or "代理" in content_lower

        if not disclosure_present or not (has_ai and has_agent):
            reasons.append("missing_disclosure")

    # R4: Rate limit
    exceeded, rate_reason = check_rate_limit(role, action)
    if exceeded:
        reasons.append(rate_reason)

    return (len(reasons) == 0, reasons, modified_content)
