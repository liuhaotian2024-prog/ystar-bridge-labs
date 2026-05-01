from __future__ import annotations

from pathlib import Path

from office.aiden_meeting_room.company_context_loader import load_company_context
from office.aiden_meeting_room.evidence_extractor import format_evidence

from .mission_model import Mission


def _mission_id(owner_message: str) -> str:
    compact = "".join(ch for ch in owner_message.lower() if ch.isalnum())[:24]
    return f"mission_{compact or 'owner_goal'}"


def build_mission_from_owner_message(owner_message: str, repo_root: Path | None = None) -> Mission:
    ctx = load_company_context(repo_root)
    index = ctx.evidence_index
    evidence_items = []
    if index:
        evidence_items.extend(index.by_label("Active charter default priority")[:2])
        evidence_items.extend(index.by_label("M-3 Value Production")[:2])
        evidence_items.extend(index.by_label("Without M-3 toy warning")[:2])
        evidence_items.extend(index.by_label("Revenue blocker")[:2])
        evidence_items.extend(index.by_label("Board NL pipeline")[:1])
    evidence_basis = format_evidence(evidence_items, limit=7).splitlines()

    recommended_path = (
        "Run a 7-day first-revenue mission: compare the Founder AI Workflow Audit / CEO Command Brief seed "
        "against AI Company Cockpit Setup, Coding-Agent Governance Audit, Agent Workflow Bottleneck Diagnosis, "
        "and Runtime Setup Advisory; prepare one owner-approved manual action packet only after evidence review."
    )

    return Mission(
        mission_id=_mission_id(owner_message),
        owner_message=owner_message,
        goal=owner_message.strip(),
        mission_type="first_revenue_mission",
        default_priority="M-3 Value Production unless M-1 or M-2 is actively broken",
        allowed_permission_tier=1,
        research_budget={"max_search_queries": 10, "max_pages_read": 20, "max_domains": 8},
        recommended_path=recommended_path,
        evidence_basis=evidence_basis,
    )

