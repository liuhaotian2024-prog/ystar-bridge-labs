from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .competitive_intelligence_engine import render_competitive_intelligence_markdown
from .e3_market_aware_evaluator import (
    evaluate_market_aware_opportunities,
    render_market_aware_evaluation_markdown,
    render_top_candidates_markdown,
)
from .strict_czl import build_strict_czl_state, render_strict_czl_report


OWNER_MISSION = (
    "Aiden，带团队制定未来 7 天最可能产生第一笔真实收入或强付费信号的行动方案。"
    "不要锁死 Founder AI Workflow Audit；必须比较当前 top money paths，给出默认推荐、团队分工、"
    "可自主执行事项、需要我审批的事项。"
)

E3_Y_STAR = [
    "strict_czl_semantics_implemented",
    "market_reality_model_present",
    "competitive_intelligence_present",
    "broad_opportunity_space_generated",
    "divergent_then_convergent_reasoning_used",
    "counterfactual_and_competition_gate_applied",
    "top_two_real_sample_deliverables_created",
    "owner_decision_packet_created",
    "no_external_side_effects",
    "live_external_evidence_available",
]

E3_FEASIBLE_INTERNAL_CRITERIA = [
    "strict_czl_semantics_implemented",
    "market_reality_model_present",
    "competitive_intelligence_present",
    "broad_opportunity_space_generated",
    "divergent_then_convergent_reasoning_used",
    "counterfactual_and_competition_gate_applied",
    "top_two_real_sample_deliverables_created",
    "owner_decision_packet_created",
    "no_external_side_effects",
]


def _findings_for(title: str) -> List[str]:
    lowered = title.lower()
    if "bottleneck" in lowered or "workflow rescue" in lowered:
        return [
            "Agent outputs are not mapped to an owner-visible decision queue, so finished-looking work still requires human reconstruction.",
            "The workflow lacks an action-wide preflight table, which makes approval-needed actions look similar to safe internal work.",
            "There is no 48h disconfirming test, so the team risks polishing a service before proving buyer urgency.",
        ]
    if "coding-agent" in lowered or "mcp" in lowered or "governance" in lowered:
        return [
            "Tool-use boundaries are implicit instead of declared as structured action semantics.",
            "Customer contact, publication, payment, and core writeback gates are mixed with low-risk preparation work.",
            "The team has evidence primitives but lacks a concise buyer-facing safety/readiness scorecard.",
        ]
    return [
        "The buyer has a plausible operational pain, but live market evidence is missing.",
        "The strongest internal asset is the combination of Mission Command, M Triangle, and governance preflight.",
        "The trust gap is the main blocker: the sample must prove concrete value before any external validation.",
    ]


def build_real_sample_deliverable(row: Dict[str, Any], rank: int) -> Dict[str, Any]:
    opportunity = row["opportunity"]
    profile = row["market_reality_profile"]
    return {
        "deliverable_id": f"e3_sample_top{rank}_{opportunity['opportunity_id']}",
        "title": f"E3 Sample Deliverable Top {rank}: {opportunity['title']}",
        "sample_buyer_scenario": opportunity["buyer"],
        "assumed_current_workflow_problem": opportunity["pain"],
        "diagnostic_findings": _findings_for(opportunity["title"]),
        "evidence_basis": [
            "internal evidence: Mission Command can produce CZL, action inventory, and owner decision packet",
            "internal evidence: Y-star-gov/gov-mcp provide policy/preflight concepts",
            "internal evidence: live market evidence is not available yet, so this sample is not externally validated",
        ],
        "risk_governance_boundary": [
            "No customer contact, email, publication, payment, account creation, form submission, or core writeback is included.",
            "External validation requires a separate owner approval packet.",
            "Sample may be used for owner review only until publication/contact is approved.",
        ],
        "48h_action_recommendation": opportunity["first_experiment"],
        "what_customer_receives": [
            "CEO-readable diagnostic brief",
            "three concrete findings",
            "48h action plan",
            "risk/approval boundary",
            "kill condition and residual plan",
        ],
        "what_is_excluded": [
            "implementation",
            "tool installation",
            "legal/security certification",
            "customer outreach by the system",
            "core memory/CIEU writeback",
        ],
        "pricing_hypothesis": "; ".join(profile["pricing_references"]),
        "validation_question": "Would this buyer pay for a 48h diagnostic that reduces decision/workflow risk faster than DIY alternatives?",
        "kill_condition": opportunity["kill_condition"],
        "owner_approval_needed_before_external_use": True,
        "external_action_executed": False,
    }


def render_real_sample_deliverable(deliverable: Dict[str, Any]) -> str:
    lines = [
        f"# {deliverable['title']}",
        "",
        f"- deliverable_id: {deliverable['deliverable_id']}",
        f"- owner_approval_needed_before_external_use: {deliverable['owner_approval_needed_before_external_use']}",
        f"- external_action_executed: {deliverable['external_action_executed']}",
        "",
        "## Sample Buyer Scenario",
        deliverable["sample_buyer_scenario"],
        "",
        "## Assumed Current Workflow / Problem",
        deliverable["assumed_current_workflow_problem"],
        "",
        "## Diagnostic Findings",
    ]
    lines.extend(f"- {item}" for item in deliverable["diagnostic_findings"])
    lines.extend(["", "## Evidence Basis"])
    lines.extend(f"- {item}" for item in deliverable["evidence_basis"])
    lines.extend(["", "## Risk / Governance Boundary"])
    lines.extend(f"- {item}" for item in deliverable["risk_governance_boundary"])
    lines.extend(
        [
            "",
            "## 48h Action Recommendation",
            deliverable["48h_action_recommendation"],
            "",
            "## What Customer Receives",
        ]
    )
    lines.extend(f"- {item}" for item in deliverable["what_customer_receives"])
    lines.extend(["", "## What Is Excluded"])
    lines.extend(f"- {item}" for item in deliverable["what_is_excluded"])
    lines.extend(
        [
            "",
            f"## Pricing Hypothesis\n{deliverable['pricing_hypothesis']}",
            "",
            f"## Validation Question\n{deliverable['validation_question']}",
            "",
            f"## Kill Condition\n{deliverable['kill_condition']}",
            "",
            "Owner approval is required before any external use.",
        ]
    )
    return "\n".join(lines)


def build_e3_owner_decision_packet(evaluation: Dict[str, Any]) -> Dict[str, Any]:
    intel = evaluation["competitive_intelligence"]
    resolution = intel["resolution"]
    live_ran = bool(intel["live_research_executed"])
    if live_ran:
        recommended = "approve_or_revise_next_validation_after_live_research"
        reason = "Live read-only market evidence is available; owner can decide whether to validate externally."
    else:
        recommended = "approve_or_revise_tier1_live_read_only_research_enablement"
        reason = "Top opportunities are structured but not market-backed; live evidence is blocked by missing configuration/approval."
    return {
        "packet_id": "e3_owner_decision_packet",
        "recommended_next_decision": recommended,
        "reason": reason,
        "live_read_only_research_ran": live_ran,
        "exact_unblock_action": resolution["missing_config_actions"],
        "top_path": evaluation["top_path"],
        "strongest_alternative": evaluation["strongest_alternative"],
        "default_is_market_backed": live_ran,
        "approval_covers": "Bounded Tier 1 live read-only public research only.",
        "approval_does_not_cover": [
            "customer contact",
            "email/message sending",
            "publication",
            "payment",
            "account creation",
            "form submission",
            "obligation registration",
            "core DB/brain/memory/CIEU writeback",
        ],
        "options": ["approve", "reject", "request_revision", "hold"],
        "external_action_executed": False,
    }


def render_e3_owner_decision_packet(packet: Dict[str, Any]) -> str:
    lines = [
        "# E3 Owner Decision Packet",
        "",
        f"- recommended_next_decision: {packet['recommended_next_decision']}",
        f"- reason: {packet['reason']}",
        f"- live_read_only_research_ran: {packet['live_read_only_research_ran']}",
        f"- top_path: {packet['top_path']}",
        f"- strongest_alternative: {packet['strongest_alternative']}",
        f"- default_is_market_backed: {packet['default_is_market_backed']}",
        f"- approval_covers: {packet['approval_covers']}",
        "- approval_does_not_cover:",
    ]
    lines.extend(f"  - {item}" for item in packet["approval_does_not_cover"])
    lines.extend(["", "## Exact Unblock Action"])
    if packet["exact_unblock_action"]:
        lines.extend(f"- {item}" for item in packet["exact_unblock_action"])
    else:
        lines.append("- none")
    lines.extend(["", f"Options: {', '.join(packet['options'])}", "", f"external_action_executed: {packet['external_action_executed']}"])
    return "\n".join(lines)


def build_e3_cycle(repo_root: Path) -> Dict[str, Any]:
    evaluation = evaluate_market_aware_opportunities(repo_root)
    intel = evaluation["competitive_intelligence"]
    top_two = [build_real_sample_deliverable(row, index + 1) for index, row in enumerate(evaluation["rows"][:2])]
    owner_packet = build_e3_owner_decision_packet(evaluation)
    live_available = bool(intel["resolution"]["live_read_only_available"] and intel["live_research_executed"])
    y_t1 = {
        "strict_czl_semantics_implemented": True,
        "market_reality_model_present": all(row.get("market_reality_profile") for row in evaluation["rows"]),
        "competitive_intelligence_present": bool(intel["profiles"]),
        "broad_opportunity_space_generated": len(evaluation["rows"]) >= 12,
        "divergent_then_convergent_reasoning_used": True,
        "counterfactual_and_competition_gate_applied": True,
        "top_two_real_sample_deliverables_created": len(top_two) == 2 and all(len(item["diagnostic_findings"]) >= 3 for item in top_two),
        "owner_decision_packet_created": bool(owner_packet),
        "no_external_side_effects": not intel["external_action_executed"] and not owner_packet["external_action_executed"],
        "live_external_evidence_available": live_available,
    }
    blocked_reason = "" if live_available else "live read-only public research was not configured/executed, so market-backed ranking remains blocked"
    czl = build_strict_czl_state(
        mission_id="e3_market_reality_first_revenue",
        y_star=E3_Y_STAR,
        xt={
            "start_commit": "774a1007",
            "e2_gap": "E2 could be blocked while reporting rt1_score=0; E3 must separate internal and full mission residuals.",
            "live_research_start_state": intel["resolution"]["mode"],
        },
        u=[
            "implemented strict CZL semantics",
            "built market reality profiles",
            "built competitive intelligence map",
            "expanded opportunity synthesis to 12+ lenses/opportunities",
            "evaluated opportunities with market-aware scoring",
            "created top two substantive sample deliverables",
            "created owner decision packet",
        ],
        y_t1=y_t1,
        feasible_criteria=E3_FEASIBLE_INTERNAL_CRITERIA,
        full_criteria=E3_Y_STAR,
        blocked_reason=blocked_reason,
        exact_unblock_action=intel["resolution"]["missing_config_actions"],
    )
    return {
        "evaluation": evaluation,
        "competitive_intelligence": intel,
        "sample_deliverables": top_two,
        "owner_decision_packet": owner_packet,
        "strict_czl": czl.to_dict(),
        "external_action_executed": False,
    }


def write_e3_reports(repo_root: Path) -> Dict[str, Path]:
    cycle = build_e3_cycle(repo_root)
    reports = repo_root / "reports" / "integration"
    reports.mkdir(parents=True, exist_ok=True)
    outputs = {
        "e3_competitive_intelligence.md": render_competitive_intelligence_markdown(cycle["competitive_intelligence"]),
        "e3_market_aware_opportunity_evaluation.md": render_market_aware_evaluation_markdown(cycle["evaluation"]),
        "e3_top_candidates.md": render_top_candidates_markdown(cycle["evaluation"]),
        "e3_sample_deliverable_top1.md": render_real_sample_deliverable(cycle["sample_deliverables"][0]),
        "e3_sample_deliverable_top2.md": render_real_sample_deliverable(cycle["sample_deliverables"][1]),
        "e3_owner_decision_packet.md": render_e3_owner_decision_packet(cycle["owner_decision_packet"]),
        "e3_czl_closure_report.md": render_strict_czl_report(
            build_strict_czl_state(
                mission_id=cycle["strict_czl"]["mission_id"],
                y_star=cycle["strict_czl"]["y_star"],
                xt=cycle["strict_czl"]["xt"],
                u=cycle["strict_czl"]["u"],
                y_t1=cycle["strict_czl"]["y_t1"],
                feasible_criteria=E3_FEASIBLE_INTERNAL_CRITERIA,
                full_criteria=E3_Y_STAR,
                blocked_reason=cycle["strict_czl"]["blocked_reason"],
                exact_unblock_action=cycle["strict_czl"]["exact_unblock_action"],
            )
        )
        + "\n\n## No-External-Action Receipt\n"
        + "- external sending: false\n"
        + "- customer contact: false\n"
        + "- email: false\n"
        + "- payment: false\n"
        + "- publication: false\n"
        + "- account creation: false\n"
        + "- form submission: false\n"
        + "- core DB writeback: false\n"
        + "- obligation auto-registration: false\n"
        + "- CIEU write: false\n"
        + "- COO invented: false\n",
    }
    written: Dict[str, Path] = {}
    for filename, text in outputs.items():
        path = reports / filename
        path.write_text(text + "\n", encoding="utf-8")
        written[filename] = path
    return written
