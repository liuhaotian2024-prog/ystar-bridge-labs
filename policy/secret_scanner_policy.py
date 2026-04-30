#!/usr/bin/env python3
"""Contextual secret scanning policy helper.

The helper is strict about real-looking secrets, but it understands approved
redacted examples and test fixtures so tests do not need string-splitting hacks.
It never includes candidate secret values in decision reasons.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


POLICY_DIR = Path(__file__).resolve().parent
POLICY_PATH = POLICY_DIR / "secret_scanning_policy.json"

KNOWN_SECRET_NAMES = {
    "TAVILY_API_KEY": "TAVILY_API_KEY",
    "BRAVE_SEARCH_API_KEY": "BRAVE_SEARCH_API_KEY",
    "SERPAPI_API_KEY": "SERPAPI_API_KEY",
    "API_KEY": "generic API key",
    "SECRET_KEY": "generic API key",
    "ACCESS_TOKEN": "OAuth token",
    "REFRESH_TOKEN": "OAuth token",
    "OAUTH_TOKEN": "OAuth token",
    "PRIVATE_KEY": "private key",
}

ASSIGNMENT_RE = re.compile(
    r"(?i)\b(?P<name>TAVILY_API_KEY|BRAVE_SEARCH_API_KEY|SERPAPI_API_KEY|API_KEY|SECRET_KEY|ACCESS_TOKEN|REFRESH_TOKEN|OAUTH_TOKEN|PRIVATE_KEY)\b"
    r"\s*(?:=|:)\s*[\"']?(?P<value>[^\s\"',;]+)"
)
BEARER_RE = re.compile(r"(?i)\bBearer\s+(?P<value>[A-Za-z0-9._~+/=-]{8,})")
TAVILY_PREFIX_RE = re.compile(r"(?i)\btvly-[A-Za-z0-9_-]{12,}\b")
PRIVATE_KEY_MARKER_RE = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")

SAFE_MARKERS = ("REDACTED", "PLACEHOLDER", "TEST_ONLY", "EXAMPLE", "DUMMY")
SAFE_TEST_CONTEXT_PARTS = ("/tests/", "test_", "_test.", "/fixtures/")
DOC_CONTEXT_PARTS = ("/docs/", ".md")
SCANNER_RULE_CONTEXT_PARTS = (
    "secret_scanning_policy.json",
    "secret_scanner_policy.py",
    "test_l7_secret_scanner_policy.py",
)
UNSAFE_PATH_PARTS = (
    "controlled_observation.env",
    "/.env",
    ".env",
    ".pem",
    ".key",
    ".p12",
    ".crt",
    ".db",
    ".db-wal",
    ".db-shm",
    ".sqlite",
    ".sqlite3",
    ".log",
    "__pycache__",
    "active_agent",
    "active-agent",
)


def load_secret_scanning_policy() -> dict[str, Any]:
    """Load the contextual secret scanning policy."""
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def _decision(
    decision: str,
    risk: str,
    matched_family: str,
    reason: str,
    safe_for_commit: bool,
    requires_review: bool,
    classification: str,
) -> dict[str, Any]:
    return {
        "decision": decision,
        "risk": risk,
        "matched_family": matched_family,
        "reason": reason,
        "policy_ref": "policy/secret_scanning_policy.json",
        "safe_for_commit": safe_for_commit,
        "requires_review": requires_review,
        "classification": classification,
    }


def _path_text(file_path: str | None) -> str:
    if not file_path:
        return ""
    return file_path.replace("\\", "/")


def _context_is_test(file_path: str | None, context_hint: str | None = None) -> bool:
    if context_hint == "test_fixture":
        return True
    path = _path_text(file_path)
    return any(part in path for part in SAFE_TEST_CONTEXT_PARTS)


def _context_is_doc(file_path: str | None, context_hint: str | None = None) -> bool:
    if context_hint == "documentation":
        return True
    path = _path_text(file_path)
    return any(part in path for part in DOC_CONTEXT_PARTS)


def _context_is_scanner_rule(file_path: str | None, context_hint: str | None = None) -> bool:
    if context_hint == "scanner_rule":
        return True
    path = _path_text(file_path)
    return any(part in path for part in SCANNER_RULE_CONTEXT_PARTS)


def _context_is_unsafe(file_path: str | None, context_hint: str | None = None) -> bool:
    if context_hint == "unsafe":
        return True
    path = _path_text(file_path)
    if not path:
        return False
    return any(part in path for part in UNSAFE_PATH_PARTS)


def _contains_safe_marker(value: str) -> bool:
    upper = value.upper()
    if "UNREDACTED" in upper:
        return False
    return any(marker in upper for marker in SAFE_MARKERS)


def is_redacted_placeholder(text: str) -> bool:
    """Return true when text is an approved redacted/placeholder token."""
    value = text.strip()
    upper = value.upper()
    policy = load_secret_scanning_policy()
    approved = set(policy["allowed_redacted_placeholders"]) | set(policy["allowed_documentation_tokens"])
    if value in approved or upper in approved:
        return True
    return _contains_safe_marker(value) or value in {"<REDACTED>", "<TEST_SECRET_PLACEHOLDER>"}


def is_safe_test_fixture(text: str, file_path: str | None = None) -> bool:
    """Return true for approved test fixture tokens, never for real-looking values."""
    value = text.strip()
    policy = load_secret_scanning_policy()
    if value in set(policy["allowed_test_fixture_tokens"]):
        return True
    if _context_is_test(file_path) and is_redacted_placeholder(value):
        return True
    return False


def _value_is_realish(value: str) -> bool:
    if is_redacted_placeholder(value):
        return False
    if TAVILY_PREFIX_RE.search(value):
        return True
    if len(value) < 16:
        return False
    has_alpha = any(char.isalpha() for char in value)
    has_digit = any(char.isdigit() for char in value)
    has_symbol = any(char in "-_./+=" for char in value)
    return has_alpha and (has_digit or has_symbol)


def is_real_secret_candidate(text: str) -> bool:
    """Return true for real-looking secret candidates."""
    if is_redacted_placeholder(text):
        return False
    if PRIVATE_KEY_MARKER_RE.search(text):
        return True
    if TAVILY_PREFIX_RE.search(text):
        return True
    for match in ASSIGNMENT_RE.finditer(text):
        if _value_is_realish(match.group("value")):
            return True
    for match in BEARER_RE.finditer(text):
        if _value_is_realish(match.group("value")):
            return True
    return False


def _classify_assignment(text: str, file_path: str | None, context_hint: str | None) -> dict[str, Any] | None:
    match = ASSIGNMENT_RE.search(text)
    if not match:
        return None

    name = match.group("name").upper()
    value = match.group("value")
    family = KNOWN_SECRET_NAMES.get(name, "generic API key")

    if is_redacted_placeholder(value):
        if _context_is_doc(file_path, context_hint):
            return _decision(
                "allowed_documentation_example",
                "none",
                family,
                "Redacted documentation example uses an approved placeholder.",
                True,
                False,
                "documentation_example",
            )
        return _decision(
            "allowed_redacted_placeholder",
            "none",
            family,
            "Secret assignment is redacted with an approved placeholder.",
            True,
            False,
            "redacted_placeholder",
        )

    if _value_is_realish(value):
        return _decision(
            "hard_forbidden_real_secret",
            "critical",
            family,
            "Known secret assignment contains an unredacted real-looking value.",
            False,
            False,
            "real_secret_candidate",
        )

    if _context_is_unsafe(file_path, context_hint):
        return _decision(
            "blocked_suspicious_secret",
            "high",
            family,
            "Secret assignment appears in an unsafe context and is not an approved placeholder.",
            False,
            True,
            "unsafe_secret_literal",
        )

    return _decision(
        "review_required",
        "medium",
        family,
        "Secret-like assignment is not clearly redacted or approved as a fixture.",
        False,
        True,
        "unsafe_secret_literal",
    )


def classify_secret_pattern(text: str, file_path: str | None = None, context_hint: str | None = None) -> dict[str, Any]:
    """Classify one candidate string under the contextual secret policy."""
    stripped = text.strip()

    if is_safe_test_fixture(stripped, file_path):
        return _decision(
            "allowed_test_fixture",
            "none",
            "test fixture token",
            "Approved test fixture token does not contain a real secret value.",
            True,
            False,
            "test_fixture_pattern",
        )

    if is_redacted_placeholder(stripped):
        if _context_is_doc(file_path, context_hint):
            return _decision(
                "allowed_documentation_example",
                "none",
                "redacted placeholder",
                "Documentation example is redacted with an approved placeholder.",
                True,
                False,
                "documentation_example",
            )
        return _decision(
            "allowed_redacted_placeholder",
            "none",
            "redacted placeholder",
            "Approved placeholder does not contain a real secret value.",
            True,
            False,
            "redacted_placeholder",
        )

    if _context_is_scanner_rule(file_path, context_hint) and not is_real_secret_candidate(stripped):
        return _decision(
            "allowed_scanner_rule_example",
            "low",
            "scanner rule example",
            "Scanner-rule context may describe symbolic patterns without concrete secret values.",
            True,
            False,
            "scanner_rule_example",
        )

    assignment = _classify_assignment(stripped, file_path, context_hint)
    if assignment:
        return assignment

    bearer = BEARER_RE.search(stripped)
    if bearer:
        if is_redacted_placeholder(bearer.group("value")):
            return _decision(
                "allowed_redacted_placeholder",
                "none",
                "bearer token",
                "Bearer example is redacted with an approved placeholder.",
                True,
                False,
                "redacted_placeholder",
            )
        if _value_is_realish(bearer.group("value")):
            return _decision(
                "hard_forbidden_real_secret",
                "critical",
                "bearer token",
                "Bearer token contains an unredacted real-looking value.",
                False,
                False,
                "real_secret_candidate",
            )

    if PRIVATE_KEY_MARKER_RE.search(stripped):
        return _decision(
            "hard_forbidden_real_secret",
            "critical",
            "private key",
            "Private key block marker is a hard-forbidden secret literal.",
            False,
            False,
            "unsafe_secret_literal",
        )

    if TAVILY_PREFIX_RE.search(stripped):
        return _decision(
            "hard_forbidden_real_secret",
            "critical",
            "TAVILY_API_KEY",
            "Tavily-shaped key prefix with long value is not allowed in repo content.",
            False,
            False,
            "real_secret_candidate",
        )

    if _context_is_unsafe(file_path, context_hint):
        return _decision(
            "review_required",
            "medium",
            "unknown",
            "Unsafe context requires review even when no concrete secret shape was detected.",
            False,
            True,
            "unsafe_secret_literal",
        )

    return _decision(
        "review_required",
        "low",
        "unknown",
        "No approved placeholder or concrete real-secret shape was detected.",
        False,
        True,
        "safe_policy_token",
    )


def scan_text_for_secret_policy(text: str, file_path: str | None = None) -> list[dict[str, Any]]:
    """Scan text and return contextual secret policy decisions for candidates."""
    decisions: list[dict[str, Any]] = []

    for match in ASSIGNMENT_RE.finditer(text):
        decisions.append(classify_secret_pattern(match.group(0), file_path=file_path))

    for match in BEARER_RE.finditer(text):
        decisions.append(classify_secret_pattern(match.group(0), file_path=file_path))

    for match in TAVILY_PREFIX_RE.finditer(text):
        # Avoid duplicate Tavily reports when the prefix was already part of an assignment.
        span = match.span()
        if not any("TAVILY_API_KEY" in text[max(0, span[0] - 40) : span[0]] for _ in [None]):
            decisions.append(classify_secret_pattern(match.group(0), file_path=file_path))

    for token in load_secret_scanning_policy()["allowed_test_fixture_tokens"]:
        if token in text:
            decisions.append(classify_secret_pattern(token, file_path=file_path, context_hint="test_fixture"))

    for token in load_secret_scanning_policy()["allowed_redacted_placeholders"]:
        if token in text:
            decisions.append(classify_secret_pattern(token, file_path=file_path))

    if PRIVATE_KEY_MARKER_RE.search(text):
        decisions.append(classify_secret_pattern("private key block marker", file_path=file_path))

    return decisions


def explain_secret_scan_decision(decision: dict[str, Any]) -> str:
    """Return a safe explanation without echoing candidate secret values."""
    return (
        f"{decision['decision']} ({decision['risk']}): {decision['reason']} "
        f"Policy: {decision['policy_ref']}"
    )


if __name__ == "__main__":
    policy = load_secret_scanning_policy()
    print(f"Loaded {policy['policy_id']} from policy/secret_scanning_policy.json")
