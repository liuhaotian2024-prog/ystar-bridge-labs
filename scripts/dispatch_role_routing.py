#!/usr/bin/env python3
"""
Dispatch Role Routing — Canonical scope-to-engineer routing table.

ARCH RULING CZL-DISPATCH-EXEC (2026-04-19, Ethan Wright CTO):
Pattern C: whiteboard is ledger, CEO main thread is executor, subscriber is claim-only.
This module provides scope-to-role regex matching used by dispatch_board.py and
engineer_task_subscriber.py.

Input: card["scope"] string (comma-separated file paths).
Output: first matching engineer canonical ID.
Order matters: first match wins. Fallback is always eng-cto-triage.
"""
import argparse
import re
import sys
from typing import List, Tuple

# Canonical scope-to-engineer routing table.
# Each entry: (compiled regex, canonical engineer ID).
# Order matters: first match wins.
ROUTE_TABLE: List[Tuple[re.Pattern, str]] = [
    # 1. Kernel: Y*gov core engine, adapters, identity, hook internals, boundary enforcer
    (re.compile(r"Y-star-gov/ystar/(adapters|kernel)/|identity_detector|boundary_enforcer"), "eng-kernel"),

    # 2. Governance: omission engine, forget guard, intervention, CIEU stores, router registry
    (re.compile(r"Y-star-gov/ystar/governance/|OmissionEngine|ForgetGuard|router_registry|omission_|intervention_engine"), "eng-governance"),

    # 3. Platform: hook wrappers, dispatch scripts, CLI, subscriber, watchdog, boot scripts, czl_ prefix
    (re.compile(r"scripts/(hook_|dispatch_|engineer_task_|session_|governance_boot|cron_wrapper|czl_)"), "eng-platform"),

    # 4. Domains: domain packs, policy templates, OpenClaw adapter
    (re.compile(r"Y-star-gov/ystar/domains/|domains/|policy|template"), "eng-domains"),

    # 5. CTO triage: architecture specs, CTO reports, cross-cutting reviews
    (re.compile(r"reports/cto/|arch/|SPEC|review"), "eng-cto-triage"),

    # 6. Tests: resolved by stripping "tests/" prefix and re-matching against rules 1-5.
    #    Handled in route_scope() logic, not as a regex entry.

    # 7. Fallback: anything unmatched goes to CTO for triage assignment.
    #    Handled by return value in route_scope().
]

ENGINEER_DISPLAY_NAMES = {
    "eng-kernel":      "Leo Chen (eng-kernel)",
    "eng-governance":  "Maya Patel (eng-governance)",
    "eng-platform":    "Ryan Park (eng-platform)",
    "eng-domains":     "Jordan Lee (eng-domains)",
    "eng-cto-triage":  "Ethan Wright (CTO -- manual triage)",
}

FALLBACK_ENGINEER = "eng-cto-triage"


def _match_against_table(scope_str: str) -> str:
    """Match scope string against ROUTE_TABLE. Returns engineer ID or FALLBACK."""
    for pattern, engineer_id in ROUTE_TABLE:
        if pattern.search(scope_str):
            return engineer_id
    return FALLBACK_ENGINEER


def route_scope(scope_str: str) -> str:
    """
    Return canonical engineer ID for the given scope string.

    Handles:
    - Direct file path matching against ROUTE_TABLE
    - Test file routing: strips "tests/" prefix and re-matches against rules 1-5
    - Comma-separated scope strings: first match wins based on path order in scope string
    - Fallback: eng-cto-triage (never silent drop)
    """
    if not scope_str or not scope_str.strip():
        return FALLBACK_ENGINEER

    # Try direct match first (whole scope string)
    result = _match_against_table(scope_str)
    if result != FALLBACK_ENGINEER:
        return result

    # Handle comma-separated scopes: try each path individually
    paths = [p.strip() for p in scope_str.split(",")]
    for path in paths:
        # Try direct match on individual path
        match = _match_against_table(path)
        if match != FALLBACK_ENGINEER:
            return match

        # Rule 6: Test file routing — strip tests/ prefix and retry
        stripped = re.sub(r"^tests/", "", path)
        if stripped != path:  # was a test file
            match = _match_against_table(stripped)
            if match != FALLBACK_ENGINEER:
                return match

    return FALLBACK_ENGINEER


def display_name(engineer_id: str) -> str:
    """Return human-readable display name for engineer ID."""
    return ENGINEER_DISPLAY_NAMES.get(engineer_id, engineer_id)


def main():
    parser = argparse.ArgumentParser(description="Dispatch Role Router — test scope-to-role mapping")
    parser.add_argument("--scope", required=True, help="Scope string (comma-separated file paths)")
    args = parser.parse_args()

    engineer = route_scope(args.scope)
    print(f"Scope: {args.scope}")
    print(f"Routed to: {engineer} ({display_name(engineer)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
