#!/usr/bin/env python3
"""
Create directive annotation JSON files for Phase 1 retro-annotation.

Per Ethan Ruling #6: 4 P2-pause directives + 2 FG proxy annotations.
This script creates governance/directives/*.json files.

Run once: python3 scripts/create_directive_annotations.py
"""
import json
import os
import time

DIRECTIVES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "governance", "directives",
)

DIRECTIVES = [
    # ── P2 Pause Family (4 directives) ──
    {
        "directive_id": "CZL-P2-PAUSE-20260418",
        "issued_at": "2026-04-18T22:00:00Z",
        "issued_by": "Board",
        "trigger": {
            "statement": "ARCH enforce-as-router design unclear; P2 migration risks wrong foundation",
            "check": {
                "type": "doc_exists",
                "path": "docs/arch17_behavioral_governance_spec.md",
                "min_status": "L1",
            },
            "current_state": "present",
        },
        "release": {
            "statement": "CTO architecture review complete — ARCH-17 canonical at L1+, router_registry stable",
            "check": {
                "type": "doc_exists",
                "path": "docs/arch17_behavioral_governance_spec.md",
                "min_status": "L1",
            },
            "current_state": "unmet",
        },
        "scope": {
            "statement": "all P2 migration work (P2-b/c/d/e)",
            "covers": ["CZL-P2-b", "CZL-P2-c", "CZL-P2-d", "CZL-P2-e"],
            "pattern": "^CZL-P2-[bcde]",
        },
        "evaluator": {
            "last_run": None,
            "verdict": "LIVE",
            "evidence": [],
            "requires_human_ack": True,
        },
    },
    {
        "directive_id": "CZL-P2-b-DISPATCH-EXEC-20260418",
        "issued_at": "2026-04-18T22:00:00Z",
        "issued_by": "Board",
        "trigger": {
            "statement": "Dispatch-exec migration depends on stable router_registry API",
            "current_state": "present",
        },
        "release": {
            "statement": "ARCH-17 consolidated and router_registry at L3 with test coverage",
            "check": {
                "type": "doc_exists",
                "path": "docs/arch17_behavioral_governance_spec.md",
                "min_status": "L1",
            },
            "current_state": "unmet",
        },
        "scope": {
            "statement": "P2-b dispatch-exec workflow migration",
            "covers": ["CZL-P2-b"],
            "pattern": "^CZL-P2-b",
        },
        "evaluator": {
            "last_run": None,
            "verdict": "LIVE",
            "evidence": [],
            "requires_human_ack": True,
        },
    },
    {
        "directive_id": "CZL-P2-c-PROTOCOL-ENFORCEMENT-20260418",
        "issued_at": "2026-04-18T22:00:00Z",
        "issued_by": "Board",
        "trigger": {
            "statement": "Protocol enforcement rule registration depends on router_registry pattern validation",
            "current_state": "present",
        },
        "release": {
            "statement": "Router registry has at least one rule registered and smoke-tested; ARCH-17 at L1+",
            "check": {
                "type": "doc_exists",
                "path": "docs/arch17_behavioral_governance_spec.md",
                "min_status": "L1",
            },
            "current_state": "unmet",
        },
        "scope": {
            "statement": "P2-c protocol enforcement migration",
            "covers": ["CZL-P2-c"],
            "pattern": "^CZL-P2-c",
        },
        "evaluator": {
            "last_run": None,
            "verdict": "LIVE",
            "evidence": [],
            "requires_human_ack": True,
        },
    },
    {
        "directive_id": "CZL-P2-d-BATCH-MIGRATION-20260418",
        "issued_at": "2026-04-18T22:00:00Z",
        "issued_by": "Board",
        "trigger": {
            "statement": "Batch migration of 40 governance protocols to router rules depends on P2-a stable",
            "current_state": "present",
        },
        "release": {
            "statement": "CTO review of first 3-rule batch complete; ARCH-17 canonical doc at L1+",
            "check": {
                "type": "doc_exists",
                "path": "docs/arch17_behavioral_governance_spec.md",
                "min_status": "L1",
            },
            "current_state": "unmet",
        },
        "scope": {
            "statement": "P2-d batch governance protocol migration",
            "covers": ["CZL-P2-d"],
            "pattern": "^CZL-P2-d",
        },
        "evaluator": {
            "last_run": None,
            "verdict": "LIVE",
            "evidence": [],
            "requires_human_ack": True,
        },
    },
    # ── FG Proxy Annotations (2 auto-synthesized per Ethan Ruling #3/#6) ──
    {
        "directive_id": "FG-PROXY-enforcement_gap_persistent",
        "issued_at": "2026-04-16T20:00:00Z",
        "issued_by": "eng-governance",
        "trigger": {
            "statement": "Persistent enforcement gaps detected in >=2 consecutive observer scans",
            "current_state": "present",
        },
        "release": {
            "statement": "ForgetGuard rule dry_run_until expired (2026-04-18T08:00:00Z / ts 1776499200)",
            "check": {
                "type": "fg_rule_is_expired",
                "rule_name": "enforcement_gap_persistent",
            },
            "current_state": "unmet",
        },
        "scope": {
            "statement": "FG rule enforcement_gap_persistent dry_run period",
            "covers": ["enforcement_gap_persistent"],
            "pattern": "enforcement_gap_persistent",
        },
        "evaluator": {
            "last_run": None,
            "verdict": "LIVE",
            "evidence": [],
            "requires_human_ack": False,
        },
    },
    {
        "directive_id": "FG-PROXY-task_dispatch_without_y_star",
        "issued_at": "2026-04-15T14:00:00Z",
        "issued_by": "eng-governance",
        "trigger": {
            "statement": "Task dispatch missing CIEU 5-tuple; 7-day grace period for ecosystem adaptation",
            "current_state": "present",
        },
        "release": {
            "statement": "ForgetGuard rule dry_run_until expired (2026-04-22T00:00:00Z / ts 1744750800)",
            "check": {
                "type": "fg_rule_is_expired",
                "rule_name": "task_dispatch_without_y_star",
            },
            "current_state": "unmet",
        },
        "scope": {
            "statement": "FG rule task_dispatch_without_y_star dry_run period",
            "covers": ["task_dispatch_without_y_star"],
            "pattern": "task_dispatch_without_y_star",
        },
        "evaluator": {
            "last_run": None,
            "verdict": "LIVE",
            "evidence": [],
            "requires_human_ack": False,
        },
    },
]


def main():
    os.makedirs(DIRECTIVES_DIR, exist_ok=True)

    for directive in DIRECTIVES:
        filename = f"{directive['directive_id']}.json"
        filepath = os.path.join(DIRECTIVES_DIR, filename)
        with open(filepath, "w") as f:
            json.dump(directive, f, indent=2)
        print(f"  Created: {filepath}")

    print(f"\nTotal: {len(DIRECTIVES)} directive annotations written to {DIRECTIVES_DIR}")


if __name__ == "__main__":
    main()
