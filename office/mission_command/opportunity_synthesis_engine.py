from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

from .research_capability import audit_research_capability
from .resource_capability_matrix import build_resource_inventory


@dataclass(frozen=True)
class OpportunityHypothesis:
    opportunity_id: str
    title: str
    generated_from_lens: str
    buyer: str
    pain: str
    internal_assets: List[str]
    external_unknowns: List[str]
    behavior_capability_required: List[str]
    first_experiment: str
    approval_needed: List[str]
    m_triangle_alignment: str
    owner_burden: str
    confidence: str
    missing_evidence: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _confidence(repo_root: Path) -> str:
    audit = audit_research_capability(repo_root)
    if audit.plan_confidence_allowed == "evidence_backed_live_read_only":
        return "medium_live_read_only_evidence"
    return "low_to_medium_internal_only"


def generate_opportunities(repo_root: Path) -> List[Dict[str, Any]]:
    confidence = _confidence(repo_root)
    common_missing = [
        "fresh external demand evidence",
        "current buyer language from bounded read-only research",
        "willingness-to-pay signal",
    ]
    opportunities = [
        OpportunityHypothesis(
            opportunity_id="opp_internal_asset_founder_audit",
            title="Founder AI Workflow Audit / CEO Command Brief",
            generated_from_lens="internal asset lens",
            buyer="Founder/operator using AI tools but unsure where execution is bottlenecked.",
            pain="AI workflows produce noise, tool sprawl, and unclear executive next steps.",
            internal_assets=["M Triangle", "WORK_METHODOLOGY", "Aiden Meeting Room", "Mission Command"],
            external_unknowns=common_missing,
            behavior_capability_required=["internal analysis", "offer draft", "sample deliverable", "customer contact"],
            first_experiment="48h internal sample audit brief using a fictional founder workflow scenario.",
            approval_needed=["customer contact", "external price quote"],
            m_triangle_alignment="M-3 Value Production with M-2 approval gates.",
            owner_burden="Owner approves target segment and any external send; team prepares the rest.",
            confidence=confidence,
            missing_evidence=common_missing,
        ),
        OpportunityHypothesis(
            opportunity_id="opp_external_pain_agent_bottleneck",
            title="Agent Workflow Bottleneck Diagnosis",
            generated_from_lens="external pain lens",
            buyer="Small team adopting coding agents or AI assistants.",
            pain="Agents produce work but teams cannot tell what is blocked, unsafe, stale, or ready.",
            internal_assets=["directive retriage", "Mission Command", "gov-mcp preflight"],
            external_unknowns=common_missing,
            behavior_capability_required=["strategy brief", "read-only research planning", "sample deliverable"],
            first_experiment="48h internal diagnosis template for a messy AI-team workflow.",
            approval_needed=["customer interview request"],
            m_triangle_alignment="M-3 through buyer bottleneck clarity; M-2 through safe action gates.",
            owner_burden="Low if Aiden prepares the diagnostic package and asks one approval question.",
            confidence=confidence,
            missing_evidence=common_missing,
        ),
        OpportunityHypothesis(
            opportunity_id="opp_budget_governance_audit",
            title="Coding-Agent Governance Audit",
            generated_from_lens="budget/demand lens",
            buyer="Engineering leader worried about AI coding-agent control, review, and auditability.",
            pain="Teams want agent productivity without losing safety, reviewability, and repo control.",
            internal_assets=["Y-star-gov", "gov-mcp", "CIEU/CZL/audit chain", "Active Operating Charter"],
            external_unknowns=common_missing,
            behavior_capability_required=["internal analysis", "sample deliverable", "read-only research planning"],
            first_experiment="48h internal audit checklist for one representative coding-agent workflow.",
            approval_needed=["external buyer validation"],
            m_triangle_alignment="M-2 productized into M-3 value production.",
            owner_burden="Medium: owner may need to choose which technical buyer segment to test first.",
            confidence=confidence,
            missing_evidence=common_missing,
        ),
        OpportunityHypothesis(
            opportunity_id="opp_governance_audit",
            title="Governed AI Runtime Readiness Review",
            generated_from_lens="governance/audit lens",
            buyer="Operator who wants to adopt AI agents without creating unmanaged operational risk.",
            pain="They lack a practical boundary between autonomous internal work and approval-gated external action.",
            internal_assets=["Y-star-gov", "gov-mcp", "Active Operating Charter", "permission tiers"],
            external_unknowns=common_missing,
            behavior_capability_required=["internal analysis", "strategy brief", "sample deliverable"],
            first_experiment="48h readiness scorecard for AI-agent runtime governance.",
            approval_needed=["external buyer validation"],
            m_triangle_alignment="M-2 governance converted into M-3 commercial value.",
            owner_burden="Low if kept as a narrow review product.",
            confidence=confidence,
            missing_evidence=common_missing,
        ),
        OpportunityHypothesis(
            opportunity_id="opp_productization_cockpit",
            title="AI Company Cockpit Setup",
            generated_from_lens="productization lens",
            buyer="Founder who wants an AI-agent operating room but lacks a safe operating spine.",
            pain="They can chat with models, but cannot turn goals into governed missions and decisions.",
            internal_assets=["Aiden Meeting Room", "Mission Command", "Active Operating Charter"],
            external_unknowns=["buyer willingness to pay for setup vs advisory", *common_missing],
            behavior_capability_required=["strategy brief", "sample deliverable", "repo modification"],
            first_experiment="48h internal cockpit setup blueprint, without installing anything externally.",
            approval_needed=["demo to external party", "pricing proposal"],
            m_triangle_alignment="M-3 through setup service; M-2 through governance boundary.",
            owner_burden="Medium-high unless packaged as a narrow advisory sprint first.",
            confidence=confidence,
            missing_evidence=["buyer willingness to pay for setup vs advisory", *common_missing],
        ),
        OpportunityHypothesis(
            opportunity_id="opp_owner_leverage_runtime_advisory",
            title="Runtime Setup Advisory",
            generated_from_lens="owner leverage lens",
            buyer="Technical founder comparing AI-agent operating patterns.",
            pain="They need a credible operating architecture, not generic AI hype.",
            internal_assets=["three-repo architecture", "Mission Command", "backflow repair evidence"],
            external_unknowns=common_missing,
            behavior_capability_required=["strategy brief", "offer draft", "publication"],
            first_experiment="48h advisory outline with before/after architecture examples.",
            approval_needed=["public post", "external call"],
            m_triangle_alignment="M-3 through advisory cash signal; M-2 preserved by approval gates.",
            owner_burden="Low if kept as review-only package until target chosen.",
            confidence=confidence,
            missing_evidence=common_missing,
        ),
        OpportunityHypothesis(
            opportunity_id="opp_speed_feedback_paid_signal",
            title="48h AI Workflow Paid-Signal Sprint",
            generated_from_lens="speed-to-feedback lens",
            buyer="Founder/operator willing to review a concrete diagnostic sample before a paid pilot.",
            pain="They need fast clarity on whether an AI workflow intervention is worth paying for.",
            internal_assets=["Mission Command", "Aiden Meeting Room", "sample deliverable capability"],
            external_unknowns=common_missing,
            behavior_capability_required=["sample deliverable", "offer draft", "customer contact"],
            first_experiment="48h internal sprint package: one sample diagnostic, one buyer question set, one approval packet.",
            approval_needed=["customer contact", "external price quote"],
            m_triangle_alignment="M-3 through fastest feedback while M-2 keeps external action gated.",
            owner_burden="Low if Aiden prepares the packet and asks for one approval.",
            confidence=confidence,
            missing_evidence=common_missing,
        ),
        OpportunityHypothesis(
            opportunity_id="opp_low_burden_template_support",
            title="Governance Template Paid Support",
            generated_from_lens="low-owner-burden lens",
            buyer="Open-source user who wants help adapting governance templates.",
            pain="They can read docs but need hands-on adaptation to their repo and team.",
            internal_assets=["content/product assets", "Y-star-gov policy", "gov-mcp tools"],
            external_unknowns=["whether any current audience wants paid support", *common_missing],
            behavior_capability_required=["offer draft", "sample deliverable", "customer contact"],
            first_experiment="48h package the smallest support offer and sample before/after.",
            approval_needed=["customer contact", "public support offer"],
            m_triangle_alignment="M-3 through paid support; M-2 through explicit boundary.",
            owner_burden="Low after owner approves support boundary.",
            confidence=confidence,
            missing_evidence=["whether any current audience wants paid support", *common_missing],
        ),
        OpportunityHypothesis(
            opportunity_id="opp_competition_gap_incident_postmortem",
            title="AI Agent Incident Postmortem Service",
            generated_from_lens="competition gap lens",
            buyer="Founder/operator whose AI-agent experiment produced wrong code, unsafe workflow changes, or confusing operational drift.",
            pain="They need a fast, credible postmortem that separates tool failure, process failure, and governance failure.",
            internal_assets=["CZL", "action-wide preflight", "WORK_METHODOLOGY", "residual learning bridge"],
            external_unknowns=common_missing,
            behavior_capability_required=["internal analysis", "sample deliverable", "read-only research planning"],
            first_experiment="48h internal incident postmortem sample using a fictional agent workflow failure.",
            approval_needed=["external buyer validation"],
            m_triangle_alignment="M-2 incident learning converted into M-3 paid diagnostic value.",
            owner_burden="Low if sample is prepared before any external validation.",
            confidence=confidence,
            missing_evidence=common_missing,
        ),
        OpportunityHypothesis(
            opportunity_id="opp_regulatory_security_mcp_boundary",
            title="MCP / Tool-Use Boundary Review",
            generated_from_lens="regulatory/security pressure lens",
            buyer="Technical team exposing tools to agents and worried about side effects, approvals, and secrets.",
            pain="They cannot tell which tool calls are safe internal work versus approval-gated external behavior.",
            internal_assets=["gov-mcp", "Y-star-gov company_runtime", "action semantics", "permission tiers"],
            external_unknowns=common_missing,
            behavior_capability_required=["internal analysis", "sample deliverable", "read-only research planning"],
            first_experiment="48h sample boundary review for a generic MCP tool surface.",
            approval_needed=["external technical review request"],
            m_triangle_alignment="M-2 governance packaged as M-3 engineering risk reduction.",
            owner_burden="Low if the team generates a review-only packet.",
            confidence=confidence,
            missing_evidence=common_missing,
        ),
        OpportunityHypothesis(
            opportunity_id="opp_support_subscription_agent_onboarding",
            title="Agent Team Onboarding / Training Package",
            generated_from_lens="support/subscription lens",
            buyer="Small AI-heavy team trying to onboard humans into agent-assisted workflows.",
            pain="People use agents inconsistently, creating uneven quality, duplicated work, and unclear escalation rules.",
            internal_assets=["Aiden Meeting Room", "Active Operating Charter", "M Triangle", "Mission Command"],
            external_unknowns=common_missing,
            behavior_capability_required=["strategy brief", "sample deliverable", "read-only research planning"],
            first_experiment="48h onboarding playbook sample with governance-light operating rules.",
            approval_needed=["external validation interview"],
            m_triangle_alignment="M-3 through training/support revenue; M-2 through safe operating boundaries.",
            owner_burden="Medium until buyer segment is narrowed.",
            confidence=confidence,
            missing_evidence=common_missing,
        ),
        OpportunityHypothesis(
            opportunity_id="opp_content_distribution_diagnostic_funnel",
            title="Content-to-Lead Diagnostic Funnel",
            generated_from_lens="content/distribution lens",
            buyer="Founder/operator who resonates with concrete AI-agent failure examples and wants a diagnostic.",
            pain="They do not yet know they need a service; content must expose the cost of unmanaged AI workflows.",
            internal_assets=["content history", "sample deliverables", "M Triangle narrative", "Aiden CEO Meeting Room"],
            external_unknowns=["which channel currently reaches buyers", *common_missing],
            behavior_capability_required=["content draft", "sample deliverable", "publication"],
            first_experiment="48h internal content + diagnostic sample draft; no publication without approval.",
            approval_needed=["publication", "lead capture form"],
            m_triangle_alignment="M-3 distribution path with M-2 publication approval.",
            owner_burden="Medium because channel choice needs owner judgment.",
            confidence=confidence,
            missing_evidence=["current channel demand evidence", *common_missing],
        ),
        OpportunityHypothesis(
            opportunity_id="opp_integration_implementation_ai_ops_room",
            title="AI Ops Operating Room Implementation Support",
            generated_from_lens="integration/implementation lens",
            buyer="Team that wants a practical AI operating room integrated with existing tools.",
            pain="They can buy tools but cannot wire mission routing, approvals, evidence, and action boundaries together.",
            internal_assets=["Mission Command", "Aiden Meeting Room", "gov-mcp", "Y-star-gov"],
            external_unknowns=["implementation budget threshold", *common_missing],
            behavior_capability_required=["strategy brief", "sample deliverable", "repo modification"],
            first_experiment="48h implementation blueprint and exclusion boundary, without touching customer systems.",
            approval_needed=["external demo", "implementation proposal"],
            m_triangle_alignment="M-3 implementation support; M-2 via explicit preflight and approval scope.",
            owner_burden="High unless constrained to advisory first.",
            confidence=confidence,
            missing_evidence=["implementation budget threshold", *common_missing],
        ),
        OpportunityHypothesis(
            opportunity_id="opp_partner_channel_enablement",
            title="Partner Enablement Package for AI Consultants",
            generated_from_lens="partner/channel lens",
            buyer="AI consultant or agency that needs a governance/evidence layer for client delivery.",
            pain="They can sell AI services but lack proof, safety boundaries, and a crisp client decision brief.",
            internal_assets=["Y-star-gov", "gov-mcp", "sample deliverables", "evidence packets"],
            external_unknowns=["partner willingness to resell or co-deliver", *common_missing],
            behavior_capability_required=["strategy brief", "sample deliverable", "read-only research planning"],
            first_experiment="48h partner kit sample: boundary checklist, diagnostic brief, and residual plan.",
            approval_needed=["partner outreach"],
            m_triangle_alignment="M-3 via channel leverage while M-2 remains permission-gated.",
            owner_burden="Medium: owner may need to choose partner category.",
            confidence=confidence,
            missing_evidence=["partner willingness to resell or co-deliver", *common_missing],
        ),
        OpportunityHypothesis(
            opportunity_id="opp_open_source_paid_support",
            title="Open-Source-to-Paid-Support Governance Pack",
            generated_from_lens="open-source-to-paid-support lens",
            buyer="Developer or small team adopting governance/MCP ideas from public repo materials.",
            pain="They want implementation help but do not want a bespoke consulting engagement.",
            internal_assets=["Y-star-gov domain pack", "gov-mcp tools", "documentation/report history"],
            external_unknowns=["public repo audience demand", *common_missing],
            behavior_capability_required=["sample deliverable", "support package draft", "publication"],
            first_experiment="48h internal paid-support pack with a support boundary and FAQ.",
            approval_needed=["public support offer", "customer contact"],
            m_triangle_alignment="M-3 support revenue from existing M-2 assets.",
            owner_burden="Low after owner approves support scope.",
            confidence=confidence,
            missing_evidence=["public repo audience demand", *common_missing],
        ),
    ]
    enriched: List[Dict[str, Any]] = []
    for item in opportunities:
        data = item.to_dict()
        data["budget_hypothesis"] = "Hypothesis only until live read-only evidence or owner-approved validation confirms budget."
        data["proof_assets"] = data["internal_assets"]
        data["kill_condition"] = "Downgrade if 48h sample cannot show urgent pain, low owner burden, and a clear validation question."
        data["counterfactual_risk"] = "Buyer urgency, trust gap, or channel access may be weaker than internal logic suggests."
        data["market_reality"] = "internal hypothesis only until competitive/pricing/source evidence is collected."
        enriched.append(data)
    return enriched


def score_opportunity(opportunity: Dict[str, Any]) -> int:
    score = 0
    title = opportunity["title"].lower()
    lens = opportunity["generated_from_lens"].lower()
    if "founder" in title or "bottleneck" in title:
        score += 4
    if "incident" in title or "mcp" in title or "partner" in title:
        score += 3
    if "governance" in title:
        score += 3
    if "internal asset" in lens or "external pain" in lens:
        score += 3
    if opportunity["owner_burden"].lower().startswith("low"):
        score += 2
    if "customer contact" not in opportunity["behavior_capability_required"]:
        score += 1
    return score


def compare_generated_opportunities(repo_root: Path) -> List[Dict[str, Any]]:
    opportunities = generate_opportunities(repo_root)
    for item in opportunities:
        item["method_score"] = score_opportunity(item)
    return sorted(opportunities, key=lambda item: int(item["method_score"]), reverse=True)


def summarize_opportunity_lenses(repo_root: Path) -> Dict[str, Any]:
    resources = build_resource_inventory(repo_root)
    opportunities = compare_generated_opportunities(repo_root)
    return {
        "resource_count": len(resources),
        "lenses": sorted({item["generated_from_lens"] for item in opportunities}),
        "opportunities": opportunities,
    }
