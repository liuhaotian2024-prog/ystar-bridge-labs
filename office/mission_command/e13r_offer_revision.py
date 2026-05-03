from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List


E13R_REVISED_OFFER_IDS = [
    "ai_ops_operating_room_implementation_support",
    "coding_agent_governance_audit",
    "ai_agent_workflow_recovery_room",
    "ai_ops_bottleneck_risk_map",
    "ai_agent_implementation_readiness_review",
]


@dataclass(frozen=True)
class E13RDiagnosis:
    e13_classification: str
    e13_top_path: str
    e13_second_best_path: str
    e13_evidence_count: int
    direct_buyer_pain_count: int
    pricing_or_budget_count: int
    substitute_count: int
    reason: str
    e14_entry_allowed: bool = False
    public_evidence_is_validation_feedback: bool = False
    readiness_is_revenue: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class E13ROfferCandidate:
    offer_id: str
    offer_name: str
    buyer_pain_hypothesis: str
    buyer_segment: str
    urgency_claim: str
    budget_pricing_hypothesis: str
    substitute_comparable_service: str
    deliverable_48h: str
    trust_gap_mitigation: str
    owner_burden: str
    fastest_disconfirming_evidence: str
    strongest_reason_to_reject: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def diagnose_e13_result(repo_root: Path) -> E13RDiagnosis:
    readiness = load_json(repo_root / "operations" / "external_validation" / "e13_paid_signal_readiness_report.json")
    path_results = readiness.get("path_results", [])
    direct = sum(int(item.get("direct_buyer_pain_count", 0) or 0) for item in path_results)
    pricing = sum(int(item.get("pricing_or_budget_count", 0) or 0) for item in path_results)
    substitute = sum(int(item.get("substitute_count", 0) or 0) for item in path_results)
    classification = str(readiness.get("classification", "missing_e13_readiness_report"))
    reason = (
        "E13 found pricing/budget-style public evidence, but direct buyer pain and substitute/comparable evidence were insufficient."
        if classification == "needs_offer_revision"
        else "E13R could not confirm the expected E13 needs_offer_revision state from the readiness report."
    )
    return E13RDiagnosis(
        e13_classification=classification,
        e13_top_path=str(readiness.get("top_path", "unknown")),
        e13_second_best_path=str(readiness.get("second_best_path", "unknown")),
        e13_evidence_count=int(readiness.get("evidence_count", 0) or 0),
        direct_buyer_pain_count=direct,
        pricing_or_budget_count=pricing,
        substitute_count=substitute,
        reason=reason,
    )


def generate_revised_offer_candidates() -> List[E13ROfferCandidate]:
    return [
        E13ROfferCandidate(
            offer_id="ai_ops_operating_room_implementation_support",
            offer_name="48h AI Ops Operating Room Implementation Support",
            buyer_pain_hypothesis="Teams have AI workflow ideas but struggle to turn them into safe, governed operating routines.",
            buyer_segment="AI consultants/agencies needing governance layer and AI-heavy teams moving from demo to operations.",
            urgency_claim="Agentic workflows are moving toward production before governance, observability, and ownership are clear.",
            budget_pricing_hypothesis="$500-$2,500 diagnostic range remains a hypothesis until E14 validation feedback exists.",
            substitute_comparable_service="AI automation consulting, agent governance advisory, implementation readiness reviews.",
            deliverable_48h="Bottleneck map, governance risk map, fastest safe implementation step, and owner-ready next decision.",
            trust_gap_mitigation="AI-transparent scope, no production changes, read-only diagnosis, explicit risk boundary.",
            owner_burden="Medium: requires owner review of one short diagnostic packet and optional validation script.",
            fastest_disconfirming_evidence="Public buyers discuss implementation spend but not AI operating-room or workflow-risk pain.",
            strongest_reason_to_reject="Too broad if buyers search for one concrete failure mode rather than an operating-room metaphor.",
        ),
        E13ROfferCandidate(
            offer_id="coding_agent_governance_audit",
            offer_name="48h Coding-Agent Governance Audit",
            buyer_pain_hypothesis="Engineering teams using coding agents worry about unsafe changes, hidden risk, and weak review gates.",
            buyer_segment="AI-heavy engineering teams, CTOs, AI platform leads, and consultants supporting coding-agent adoption.",
            urgency_claim="Coding agents can create fast productivity gains while introducing code safety, review, and compliance gaps.",
            budget_pricing_hypothesis="Comparable spend may come from code review, AI governance, DevSecOps, and audit/advisory budgets.",
            substitute_comparable_service="AI code review tools, DevSecOps audits, agent governance consulting, secure SDLC reviews.",
            deliverable_48h="Risk inventory, governance gap map, bypass paths, approval workflow, and next validation question.",
            trust_gap_mitigation="No repo write access, no secrets, no production access, evidence-only review checklist.",
            owner_burden="Low-medium: strongest if packaged as a short owner-operated audit template.",
            fastest_disconfirming_evidence="Public evidence shows coding-agent risk but buyers prefer tooling subscriptions over audit services.",
            strongest_reason_to_reject="May require more technical credibility and sample artifacts before buyers trust an external audit.",
        ),
        E13ROfferCandidate(
            offer_id="ai_agent_workflow_recovery_room",
            offer_name="48h AI Agent Workflow Recovery Room",
            buyer_pain_hypothesis="Teams have agent workflows that break, drift, or stall in production-like use and need recovery triage.",
            buyer_segment="AI-heavy small teams, founders, operators, and agencies with broken or unreliable agent workflows.",
            urgency_claim="Production failures compound across multi-step agent workflows and are hard to debug after launch.",
            budget_pricing_hypothesis="Comparable spend may come from incident response, workflow automation consulting, and LLMOps advisory.",
            substitute_comparable_service="LLMOps observability, AI incident response, automation consultants, agent eval tooling.",
            deliverable_48h="Failure pattern map, recovery path, instrumentation checklist, and smallest safe next test.",
            trust_gap_mitigation="Work from public docs or owner-provided sanitized workflow; no live credentials or production mutation.",
            owner_burden="Low if framed as a recovery map from sanitized workflow notes.",
            fastest_disconfirming_evidence="Public pain exists around agent failures but not around paying for a 48h recovery room.",
            strongest_reason_to_reject="Incident language may imply emergency support beyond current owner capacity.",
        ),
        E13ROfferCandidate(
            offer_id="ai_ops_bottleneck_risk_map",
            offer_name="48h AI Ops Bottleneck & Risk Map",
            buyer_pain_hypothesis="Buyers know AI workflows are blocked but cannot see which bottleneck, risk, or owner decision matters first.",
            buyer_segment="Founder-led AI teams, ops leads, AI consultants, and operators coordinating tool-heavy workflows.",
            urgency_claim="AI tool sprawl and unclear ownership slow teams down while creating governance and reliability risk.",
            budget_pricing_hypothesis="Comparable spend may sit between founder advisory, operations consulting, and workflow automation audits.",
            substitute_comparable_service="Workflow audits, automation consultants, AI ops advisory, governance readiness reviews.",
            deliverable_48h="Ranked bottleneck/risk map, kill criteria, fast validation script, and owner burden estimate.",
            trust_gap_mitigation="Starts from public/source-provided evidence and produces decision support, not implementation claims.",
            owner_burden="Low: light diagnostic deliverable with no production access.",
            fastest_disconfirming_evidence="Evidence shows general AI adoption friction but not urgent willingness to pay for mapping.",
            strongest_reason_to_reject="Could sound like generic consulting unless anchored to one painful buyer workflow.",
        ),
        E13ROfferCandidate(
            offer_id="ai_agent_implementation_readiness_review",
            offer_name="48h AI Agent Implementation Readiness Review",
            buyer_pain_hypothesis="Teams want to adopt agents but are unsure whether governance, evaluation, and data boundaries are ready.",
            buyer_segment="AI-heavy teams preparing agentic workflows, AI consultants, CTOs, and innovation teams.",
            urgency_claim="Agentic AI spend may be delayed or wasted if teams cannot prove readiness, ROI, and risk control.",
            budget_pricing_hypothesis="Comparable spend may come from readiness assessments, governance advisory, and LLMOps consulting.",
            substitute_comparable_service="Agentic AI readiness assessments, governance playbooks, architecture reviews.",
            deliverable_48h="Readiness scorecard, top blockers, governance checklist, and next validation/pilot question.",
            trust_gap_mitigation="Diagnostic-only; no claims of deployment, no production changes, no customer contact.",
            owner_burden="Low-medium: repeatable checklist and brief can be owner-operated.",
            fastest_disconfirming_evidence="Buyers prefer implementation vendors over readiness reviews.",
            strongest_reason_to_reject="May be viewed as too early-stage or abstract if buyers already demand hands-on implementation.",
        ),
    ]


def write_offer_candidates(repo_root: Path) -> Path:
    candidates = generate_revised_offer_candidates()
    path = repo_root / "operations" / "external_validation" / "e13r_offer_candidates.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"candidates": [item.to_dict() for item in candidates]}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def render_offer_revision_report(diagnosis: E13RDiagnosis, candidates: List[E13ROfferCandidate]) -> str:
    lines = [
        "# E13R Offer Revision",
        "",
        "## E13 Diagnosis",
        f"- e13_classification: {diagnosis.e13_classification}",
        f"- e13_top_path: {diagnosis.e13_top_path}",
        f"- e13_second_best_path: {diagnosis.e13_second_best_path}",
        f"- e13_evidence_count: {diagnosis.e13_evidence_count}",
        f"- direct_buyer_pain_count: {diagnosis.direct_buyer_pain_count}",
        f"- pricing_or_budget_count: {diagnosis.pricing_or_budget_count}",
        f"- substitute_count: {diagnosis.substitute_count}",
        f"- reason: {diagnosis.reason}",
        "",
        "## Revised Offer Candidates",
    ]
    for item in candidates:
        lines.extend(
            [
                f"### {item.offer_name}",
                f"- offer_id: {item.offer_id}",
                f"- buyer_pain_hypothesis: {item.buyer_pain_hypothesis}",
                f"- buyer_segment: {item.buyer_segment}",
                f"- urgency_claim: {item.urgency_claim}",
                f"- budget_pricing_hypothesis: {item.budget_pricing_hypothesis}",
                f"- substitute_comparable_service: {item.substitute_comparable_service}",
                f"- deliverable_48h: {item.deliverable_48h}",
                f"- trust_gap_mitigation: {item.trust_gap_mitigation}",
                f"- owner_burden: {item.owner_burden}",
                f"- fastest_disconfirming_evidence: {item.fastest_disconfirming_evidence}",
                f"- strongest_reason_to_reject: {item.strongest_reason_to_reject}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()
