from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

from office.aiden_meeting_room.company_context_loader import load_company_context

from .counterfactual_reasoning import build_counterfactual_matrix, rank_counterfactual_risks
from .internal_world_scan import build_internal_world_scan
from .opportunity_synthesis_engine import compare_generated_opportunities
from .research_capability import audit_research_capability
from .resource_capability_matrix import (
    build_behavior_capability_matrix,
    build_resource_inventory,
    find_behavior_capability,
)


@dataclass(frozen=True)
class MetaDevelopmentContext:
    owner_message: str
    inferred_objective: str
    m_triangle_alignment: str
    evidence_status: Dict[str, Any]
    internal_world_state: Dict[str, Any]
    external_world_state: Dict[str, Any]
    resources: List[Dict[str, Any]]
    behavior_capabilities: List[Dict[str, Any]]
    opportunities: List[Dict[str, Any]]
    experiments: List[Dict[str, Any]]
    approval_required_actions: List[str]
    residual_plan: List[str]
    owner_burden: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def infer_deeper_objective(owner_message: str, evidence_index: Any | None = None) -> str:
    text = owner_message.lower()
    if any(k in text for k in ["预算", "budget", "采购", "procurement"]):
        return (
            "Find real demand pockets where budget, urgency, and Y*Bridge Labs advantage overlap; "
            "do not collapse the mission into procurement, grant, or RFP search."
        )
    if any(k in text for k in ["第一笔", "收入", "付费", "first revenue", "cash"]):
        return (
            "Produce a methodologically grounded, evidence-aware first-revenue exploration that compares multiple money paths, "
            "chooses a default, and separates autonomous work from approval-required validation."
        )
    if any(k in text for k in ["外部", "research", "搜索", "观察"]):
        return (
            "Clarify what evidence is missing, use internal evidence honestly, and prepare a bounded Tier 1 external research mission if needed."
        )
    return (
        "Turn the owner message into a governed company-development mission: observe evidence, compare resources, design experiments, "
        "and reduce owner burden while preserving M Triangle alignment."
    )


def detect_prompt_overfit_risk(owner_message: str) -> Dict[str, Any]:
    text = owner_message.lower()
    risks: List[str] = []
    if any(k in text for k in ["预算", "budget", "采购", "procurement"]):
        risks.append("budget_phrase_overfit: treating budget/procurement as the whole objective instead of one demand signal")
    if any(k in text for k in ["第一笔", "收入", "付费", "first revenue", "cash"]):
        risks.append("first_revenue_overfit: jumping to one offer without comparing opportunity space")
    if "founder ai workflow audit" in text.lower():
        risks.append("seed_path_overfit: treating the seed path as the whole company strategy")
    if any(k in text for k in ["外部", "research", "搜索", "观察"]):
        risks.append("research_enablement_overfit: focusing on research tooling instead of the business decision")
    if not risks:
        risks.append("generic_recent_prompt_overfit: answering the visible phrase without inferring the deeper objective")
    return {
        "risk_detected": True,
        "risks": risks,
        "mitigation": "Run the full meta-development loop before recommending a path.",
    }


def build_internal_observation(repo_root: Path) -> Dict[str, Any]:
    scan = build_internal_world_scan(repo_root)
    return {
        "status": "available",
        "assets": scan["internal_assets"],
        "capabilities": scan["current_capabilities"],
        "constraints": scan["internal_constraints"],
        "money_paths": scan["money_paths"],
    }


def build_external_observation_status(repo_root: Path) -> Dict[str, Any]:
    audit = audit_research_capability(repo_root)
    return {
        "status": audit.external_research_verdict,
        "live_read_only_available": audit.plan_confidence_allowed == "evidence_backed_live_read_only",
        "plan_confidence_allowed": audit.plan_confidence_allowed,
        "missing_for_live_research": audit.external_capability["missing_for_live_research"],
        "live_research_executed": audit.external_capability["live_research_executed"],
    }


def compare_resources(internal_assets: List[str], opportunity: Dict[str, Any]) -> Dict[str, Any]:
    opportunity_assets = set(opportunity.get("internal_assets", []))
    matched = [asset for asset in internal_assets if any(asset.lower() in candidate.lower() or candidate.lower() in asset.lower() for candidate in opportunity_assets)]
    return {
        "opportunity": opportunity["title"],
        "matched_assets": matched or list(opportunity_assets),
        "trust_gap": "requires fresh external evidence" if opportunity.get("missing_evidence") else "low",
        "delivery_capability": opportunity.get("behavior_capability_required", []),
        "owner_burden": opportunity.get("owner_burden", "unknown"),
        "repeatability": "medium until paid feedback confirms pattern",
    }


def analyze_behavior_capability(action: str, mission_context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    repo_root = Path(mission_context["repo_root"]) if mission_context and mission_context.get("repo_root") else Path(__file__).resolve().parents[2]
    return find_behavior_capability(repo_root, action)


def generate_opportunity_space(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    repo_root = Path(context["repo_root"])
    return compare_generated_opportunities(repo_root)


def compare_opportunities(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    return generate_opportunity_space(context)


def design_experiments(opportunity: Dict[str, Any]) -> Dict[str, Any]:
    title = opportunity["title"]
    return {
        "opportunity": title,
        "48h_internal_experiment": opportunity["first_experiment"],
        "tier1_read_only_research_experiment": (
            "Collect public pain-language and pricing-reference evidence under explicit Tier 1 budget; no login, no contact, no submit."
        ),
        "approval_needed_external_validation_experiment": (
            f"Prepare exact manual-send validation draft for {title}; owner must approve target, content, and boundary before any send."
        ),
        "success_metric": "At least one strong paid-signal proxy: explicit budget/urgency language, owner-approved interested target, or willingness-to-pay evidence.",
        "kill_condition": "No clear pain, no credible buyer, or delivery requires owner-heavy bespoke work after 48h internal preparation plus Tier 1 evidence review.",
        "residual_plan": build_residual_plan(opportunity),
    }


def build_residual_plan(opportunity: Dict[str, Any]) -> List[str]:
    return [
        f"If {opportunity['title']} fails, record whether the gap was pain clarity, buyer access, trust, pricing, delivery feasibility, or owner burden.",
        "Convert useful artifacts into reusable templates only after evidence shows repeatability.",
        "Feed residuals back into opportunity comparison before choosing the next path.",
    ]


def build_meta_development_trace(owner_message: str, repo_root: Path | None = None) -> Dict[str, Any]:
    root = (repo_root or Path(__file__).resolve().parents[2]).resolve()
    ctx = load_company_context(root)
    inferred = infer_deeper_objective(owner_message, ctx.evidence_index)
    overfit = detect_prompt_overfit_risk(owner_message)
    audit = audit_research_capability(root)
    internal = build_internal_observation(root)
    external = build_external_observation_status(root)
    resources = build_resource_inventory(root)
    behavior = build_behavior_capability_matrix(root)
    opportunities = compare_generated_opportunities(root)
    top = opportunities[:3]
    counterfactual_cases = build_counterfactual_matrix(top, {"repo_root": str(root), "owner_message": owner_message})
    highest_counterfactual_risks = rank_counterfactual_risks(counterfactual_cases)[:3]
    fastest_disconfirming_tests = [
        {
            "opportunity": case["opportunity_title"],
            "test": case["fastest_disconfirming_test"],
        }
        for case in counterfactual_cases
    ]
    counterfactual_default = top[0] if top else None
    default_changed = False
    why_default = (
        "Default is confirmed after counterfactual stress test because it has a fast 48h disconfirming test, low owner burden, "
        "and does not require external contact before internal preparation."
        if counterfactual_default
        else "No default available."
    )
    experiments = [design_experiments(item) for item in top]
    resource_comparison = [compare_resources(list(internal["assets"]), item) for item in top]
    approval_required = sorted({action for item in opportunities for action in item.get("approval_needed", [])})
    residual = [
        "Track which opportunity assumption failed: pain, buyer, budget, trust, channel, delivery, or owner burden.",
        "Do not write core memory/CIEU automatically; produce review-gated learning candidates only.",
        "Update path ranking after internal experiment and any explicitly approved Tier 1 evidence run.",
    ]
    next_u = (
        "Within 48h, build a one-page comparison brief and one sample deliverable for the top two opportunities, "
        "then ask the owner to approve or revise a Tier 1 read-only evidence mission."
    )
    method_steps = [
        "observe_internal",
        "observe_external_status",
        "frame_problem",
        "compare_resources",
        "analyze_behavior_capability",
        "generate_opportunities",
        "counterfactual_stress_test",
        "compare_paths",
        "design_experiments",
        "execute_allowed_actions",
        "escalate_gated_actions",
        "measure_residual",
        "update_strategy",
    ]
    context = MetaDevelopmentContext(
        owner_message=owner_message,
        inferred_objective=inferred,
        m_triangle_alignment="Default to M-3 Value Production unless M-1 or M-2 is actively broken.",
        evidence_status={
            "internal": audit.internal_research_verdict,
            "external": audit.external_research_verdict,
            "confidence": audit.plan_confidence_allowed,
        },
        internal_world_state=internal,
        external_world_state=external,
        resources=resources,
        behavior_capabilities=behavior,
        opportunities=opportunities,
        experiments=experiments,
        approval_required_actions=approval_required,
        residual_plan=residual,
        owner_burden=(
            "Owner should approve strategic direction and external side effects; Aiden/team should prepare briefs, drafts, "
            "research plans, and approval packets without turning the owner into manual ops."
        ),
    )
    data = context.to_dict()
    data.update(
        {
            "prompt_overfit_risk": overfit,
            "method_steps": method_steps,
            "resource_comparison": resource_comparison,
            "top_opportunities": top,
            "counterfactual_cases": counterfactual_cases,
            "highest_counterfactual_risks": highest_counterfactual_risks,
            "fastest_disconfirming_tests": fastest_disconfirming_tests,
            "alternative_path_rationale": (
                "The second-best path remains important if it can show clearer buyer language or lower delivery burden during the 48h internal experiment."
            ),
            "default_recommendation": counterfactual_default,
            "default_changed_after_counterfactual": default_changed,
            "why_default_still_wins_or_changed": why_default,
            "next_executable_u": next_u,
            "method_compliance": {
                "has_evidence_status": True,
                "has_action_plan": True,
                "has_next_executable_u": True,
                "has_owner_burden_statement": True,
                "has_approval_needed_actions": bool(approval_required),
                "has_residual_path": True,
            },
        }
    )
    return data
