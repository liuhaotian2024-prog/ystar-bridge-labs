"""Load a safe, local context snapshot for Aiden."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .aiden_context_model import FORBIDDEN_ACTIONS, PACKET_DIRS, ROOT, TEAM_ROSTER, ensure_dirs, now_iso, read_json, write_json


COMPLETED_MILESTONES = [
    "L7.5 Real Labs Whiteboard Collaboration & Team Work Runtime",
    "L7.6 Labs Team Self-Work Scheduler & Autonomous Task Loop",
    "L8.0 First Cash Path Operating Loop",
    "L9.0 Meta-Development Opportunity & Execution Runtime",
    "L10.0 Delegated Live Meta-Development Work Runtime",
]

ACTIVE_CAPABILITIES = [
    "local office",
    "whiteboard interaction",
    "Aiden routing",
    "self-work scheduler",
    "opportunity discovery",
    "money path ranking",
    "owner approval center",
    "manual-send action packets",
    "delegated mission runtime",
    "fixture-backed research demo",
    "configured live read-only research architecture",
]

CURRENT_LIMITATIONS = [
    "Aiden chat layer was previously a thin deterministic response layer and is being repaired",
    "not yet a full LLM autonomous worker",
    "configured live read-only research is disabled unless explicitly enabled and budgeted",
    "no external sending",
    "no customer contact",
    "no payment",
    "no publication",
    "no core writeback",
]

META_DEVELOPMENT_PRINCIPLES = [
    "Labs should not be locked to a single first cash path",
    "Founder AI Workflow Audit is a seed, benchmark, and demo path, not a prison",
    "Labs should discover, compare, rank, and prepare multiple money-making opportunities",
    "owner should make authorization and strategic decisions, not manually operate every internal step",
    "external side effects stay approval-gated and core writeback stays review-gated",
]


def _safe_team_roster() -> list[dict[str, Any]]:
    registry_path = ROOT / "l7_labs_office_legacy_integration/original_team_registry/original_team_registry.json"
    registry = read_json(registry_path, {})
    agents = registry.get("agents") or []
    if not agents:
        return TEAM_ROSTER
    compact = []
    for agent in agents:
        compact.append(
            {
                "agent_id": agent.get("agent_id", "unknown"),
                "display_name": agent.get("display_name", "unknown"),
                "role": agent.get("legacy_role", agent.get("role", "unknown")),
            }
        )
    return compact


def _summary_exists(path: str) -> bool:
    return (ROOT / path).exists()


def load_aiden_context(write_snapshot: bool = False) -> dict[str, Any]:
    ensure_dirs()
    context = {
        "schema_version": "v0",
        "milestone_id": "L10.2",
        "packet_type": "aiden_context_snapshot",
        "generated_at_utc": now_iso(),
        "current_runtime_stage": "L10.2 Aiden CEO Brain Rescue on top of L7.5-L10 local Labs Office",
        "completed_milestones": COMPLETED_MILESTONES,
        "active_capabilities": ACTIVE_CAPABILITIES,
        "current_limitations": CURRENT_LIMITATIONS,
        "commercial_seed_paths": [
            "Founder AI Workflow Audit & CEO Command Brief Sprint",
            "AI Company Cockpit Setup Sprint",
            "Coding-Agent Governance Audit",
            "Agent Workflow Bottleneck Diagnosis",
            "Internal AI Operations Audit for Small Teams",
            "Governance Template Paid Support",
            "Y*Bridge Labs Runtime Setup Advisory",
            "Open-Source-to-Paid-Support Package",
        ],
        "meta_development_principles": META_DEVELOPMENT_PRINCIPLES,
        "permission_boundaries": {
            "local_only": True,
            "forbidden_actions": FORBIDDEN_ACTIONS,
            "external_side_effects": False,
            "core_writeback": False,
        },
        "owner_priorities": [
            "understand what Labs is actually building",
            "get a usable CEO discussion surface",
            "move toward first revenue without locking the company to one offer",
            "avoid dashboards that hide the real answer",
        ],
        "team_roster": _safe_team_roster(),
        "recommended_next_work_modes": [
            "CEO discussion",
            "7-day action plan",
            "L10 delegated mission with fixture-backed or explicitly enabled read-only research",
            "owner-approved manual-send commercial action packet",
        ],
        "safe_source_checks": {
            "l7_5_summary_exists": _summary_exists("l7_labs_whiteboard_collaboration_runtime/l7_5_summary.json"),
            "l7_6_summary_exists": _summary_exists("l7_labs_team_self_work_scheduler/l7_6_summary.json"),
            "l8_summary_exists": _summary_exists("l8_first_cash_path_operating_loop/l8_summary.json"),
            "l9_summary_exists": _summary_exists("l9_meta_development_opportunity_runtime/l9_summary.json"),
            "l10_summary_exists": _summary_exists("l10_delegated_live_meta_development_runtime/l10_summary.json"),
        },
        "no_coo_invented": True,
    }
    if write_snapshot:
        write_json(PACKET_DIRS["context"] / "aiden_context_latest.json", context)
    return context
