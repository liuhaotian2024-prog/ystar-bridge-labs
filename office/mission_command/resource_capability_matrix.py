from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

from .research_capability import audit_research_capability


@dataclass(frozen=True)
class ResourceInventoryItem:
    resource: str
    type: str
    value_for_meta_development: str
    evidence_ref: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class BehaviorCapability:
    capability: str
    autonomous_now: bool
    requires_tier: str
    requires_owner_approval: bool
    requires_tool: bool
    external_side_effect: bool
    current_status: str
    risk: str
    next_possible_u: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_resource_inventory(repo_root: Path) -> List[Dict[str, str]]:
    resources = [
        ResourceInventoryItem(
            "Y-star-gov",
            "governance kernel",
            "Deterministic permission, mission, admin, and escalation policy for safe company runtime.",
            "../Y-star-gov/ystar/domains/company_runtime",
        ),
        ResourceInventoryItem(
            "gov-mcp",
            "execution boundary",
            "Preflight gateway that separates allowed internal work from approval-required external actions.",
            "../gov-mcp/gov_mcp/company_runtime_tools.py",
        ),
        ResourceInventoryItem(
            "Aiden CEO Meeting Room",
            "CEO interface",
            "Repo-grounded owner conversation surface for context, decisions, and mission framing.",
            "office/aiden_meeting_room",
        ),
        ResourceInventoryItem(
            "Mission Command",
            "operating spine",
            "Turns owner missions into M Triangle alignment, team tasks, preflight, and owner decisions.",
            "office/mission_command",
        ),
        ResourceInventoryItem(
            "M Triangle / WORK_METHODOLOGY",
            "method doctrine",
            "Stable anchor for survivability, governability, value production, OODA, and plan-vs-done discipline.",
            "knowledge/ceo/wisdom",
        ),
        ResourceInventoryItem(
            "CIEU / CZL / audit chain",
            "proof and governance assets",
            "Proof language for governance, traceability, and operational credibility.",
            "AGENTS.md",
        ),
        ResourceInventoryItem(
            "sales/prospect history",
            "commercial history",
            "Historical sales/prospect evidence that can seed offers but should not be treated as fresh market proof.",
            "sales/",
        ),
        ResourceInventoryItem(
            "content/product assets",
            "distribution and packaging assets",
            "Existing explanations, templates, and product ideas that can be repackaged after evidence review.",
            "content/",
        ),
        ResourceInventoryItem(
            "owner network/manual judgment",
            "strategic leverage",
            "Owner can approve target segment, external action, pricing boundary, and final commercial judgment.",
            "governance/ACTIVE_OPERATING_CHARTER.md",
        ),
        ResourceInventoryItem(
            "team roles",
            "execution capacity",
            "Aiden, Sofia, Marco, Zara, Ethan, Samantha, Jinjin/K9 Scout, and engineers provide role-specific analysis.",
            "README.md",
        ),
    ]
    return [item.to_dict() for item in resources]


def build_behavior_capability_matrix(repo_root: Path) -> List[Dict[str, Any]]:
    audit = audit_research_capability(repo_root)
    live_read_only_ready = audit.plan_confidence_allowed == "evidence_backed_live_read_only"
    capabilities = [
        BehaviorCapability(
            "internal analysis",
            True,
            "Tier 0",
            False,
            False,
            False,
            "available",
            "Low risk if evidence status is stated honestly.",
            "Synthesize owner mission into a decision brief.",
        ),
        BehaviorCapability(
            "internal asset scan",
            True,
            "Tier 0",
            False,
            False,
            False,
            "available",
            "Can overvalue historical assets if not marked stale.",
            "Scan safe repo files and map assets to opportunities.",
        ),
        BehaviorCapability(
            "directive retriage",
            True,
            "Tier 0",
            False,
            False,
            False,
            "available",
            "Can become paperwork unless tied to M Triangle decisions.",
            "Classify old tasks as active, revenue-relevant, archival, or owner-decision-required.",
        ),
        BehaviorCapability(
            "strategy brief",
            True,
            "Tier 0",
            False,
            False,
            False,
            "available",
            "Plan-vs-done confusion if no executable U is attached.",
            "Draft owner-readable recommendation with evidence status and next U.",
        ),
        BehaviorCapability(
            "offer draft",
            True,
            "Tier 0",
            False,
            False,
            False,
            "available",
            "Must remain review-only until owner approves external use.",
            "Write a one-page offer brief for the selected hypothesis.",
        ),
        BehaviorCapability(
            "sample deliverable",
            True,
            "Tier 0",
            False,
            False,
            False,
            "available",
            "May be too generic unless anchored to a buyer scenario.",
            "Prepare a sample CEO Command Brief outline.",
        ),
        BehaviorCapability(
            "read-only research planning",
            True,
            "Tier 0/Tier 1 prep",
            False,
            False,
            False,
            "available",
            "Planning can masquerade as evidence if not labeled.",
            "Define research questions, source types, stop conditions, and evidence fields.",
        ),
        BehaviorCapability(
            "live read-only research execution status",
            live_read_only_ready,
            "Tier 1",
            False,
            not live_read_only_ready,
            False,
            "available" if live_read_only_ready else "architecture_only",
            "Must not be treated as live market evidence until explicitly enabled, budgeted, and recorded.",
            "Ask owner to approve a Tier 1 read-only mission budget or proceed with internal-only plan.",
        ),
        BehaviorCapability(
            "customer contact",
            False,
            "Tier 2/Tier 3",
            True,
            False,
            True,
            "approval_required",
            "External side effect and relationship risk.",
            "Prepare exact proposed message and target rationale for owner approval.",
        ),
        BehaviorCapability(
            "email/message sending",
            False,
            "Tier 2/Tier 3",
            True,
            False,
            True,
            "approval_required",
            "External side effect; must not auto-send.",
            "Prepare manual-send draft only.",
        ),
        BehaviorCapability(
            "publication",
            False,
            "Tier 2/Tier 3",
            True,
            False,
            True,
            "approval_required",
            "Public reputation and factuality risk.",
            "Prepare review-only content draft.",
        ),
        BehaviorCapability(
            "payment",
            False,
            "Tier 4",
            True,
            False,
            True,
            "blocked_or_review_gated",
            "Financial and legal risk.",
            "Ask owner for payment strategy; do not create or process payment.",
        ),
        BehaviorCapability(
            "account creation",
            False,
            "Tier 4",
            True,
            False,
            True,
            "blocked_or_review_gated",
            "Credential, ToS, and identity risk.",
            "Prepare need statement only.",
        ),
        BehaviorCapability(
            "core writeback",
            False,
            "Tier 4",
            True,
            False,
            False,
            "review_gated",
            "Canonical memory/brain/CIEU drift risk.",
            "Prepare review-gated learning candidate only.",
        ),
        BehaviorCapability(
            "repo modification",
            True,
            "Tier 0 for current repo, review for protected repos",
            False,
            False,
            False,
            "available_with_scope",
            "Must avoid unrelated repos and user work.",
            "Patch scoped files, run tests, and commit only intentional changes.",
        ),
    ]
    return [item.to_dict() for item in capabilities]


def find_behavior_capability(repo_root: Path, action: str) -> Dict[str, Any]:
    normalized = action.lower()
    for item in build_behavior_capability_matrix(repo_root):
        if item["capability"].lower() in normalized or normalized in item["capability"].lower():
            return item
    if any(key in normalized for key in ["contact", "customer", "email", "message"]):
        return next(item for item in build_behavior_capability_matrix(repo_root) if item["capability"] == "customer contact")
    if any(key in normalized for key in ["writeback", "brain", "memory", "cieu", "core"]):
        return next(item for item in build_behavior_capability_matrix(repo_root) if item["capability"] == "core writeback")
    return {
        "capability": action,
        "autonomous_now": False,
        "requires_tier": "unknown",
        "requires_owner_approval": True,
        "requires_tool": True,
        "external_side_effect": False,
        "current_status": "unknown_requires_review",
        "risk": "Unknown action class should be reviewed before execution.",
        "next_possible_u": "Classify the action before attempting execution.",
    }
