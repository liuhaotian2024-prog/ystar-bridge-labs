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

def safety_check(content: str, role: str, action: str = 'posts', require_disclosure: bool = True) -> Tuple[bool, List[str]]:
    """
    Comprehensive safety check before publishing.

    Args:
        content: Post/reply text
        role: Agent role
        action: 'posts', 'likes', 'follows', 'replies'
        require_disclosure: If True, enforce R1 disclosure presence

    Returns:
        (pass, reasons) — pass=True if safe, reasons=list of failure reasons
    """
    reasons = []

    # R2: Content filtering (only if content present)
    if content:
        reasons.extend(has_profanity(content))
        reasons.extend(has_political_content(content))
        reasons.extend(has_religious_content(content))

        needs_escalation, sentiment_reason = check_sentiment(content)
        if needs_escalation:
            reasons.append(sentiment_reason)

    # R1: Disclosure check
    if require_disclosure and not check_disclosure_present(content, role):
        reasons.append("missing_disclosure")

    # R4: Rate limit
    exceeded, rate_reason = check_rate_limit(role, action)
    if exceeded:
        reasons.append(rate_reason)

    return (len(reasons) == 0, reasons)
