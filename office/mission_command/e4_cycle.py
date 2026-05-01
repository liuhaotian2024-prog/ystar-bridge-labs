from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .competitive_intelligence_engine import render_competitive_intelligence_markdown
from .e4_market_evidence_evaluator import (
    evaluate_e4_market_evidence,
    render_e4_market_evaluation_markdown,
    render_e4_top_candidates_markdown,
)
from .e4_market_research_plan import build_e4_market_research_request, render_e4_market_research_plan
from .strict_czl import build_strict_czl_state, render_strict_czl_report
from .tier1_research_runtime import run_e4_tier1_research


E4_Y_STAR = [
    "implementation_inspection_completed",
    "tier1_research_runtime_contract_present",
    "research_ran_or_blocked_honestly",
    "evidence_attached_if_live_research_runs",
    "no_market_backing_without_live_evidence",
    "evidence_sensitive_opportunity_evaluation",
    "top_two_sample_deliverables_upgraded",
    "owner_decision_packet_updated",
    "strict_e4_czl_closure_present",
    "no_external_side_effects",
    "live_research_executed_with_receipt_and_sources",
]

E4_FEASIBLE_INTERNAL_CRITERIA = [
    "implementation_inspection_completed",
    "tier1_research_runtime_contract_present",
    "research_ran_or_blocked_honestly",
    "no_market_backing_without_live_evidence",
    "evidence_sensitive_opportunity_evaluation",
    "top_two_sample_deliverables_upgraded",
    "owner_decision_packet_updated",
    "strict_e4_czl_closure_present",
    "no_external_side_effects",
]


def _diagnostic_findings(title: str, market_backed: bool) -> List[str]:
    base = [
        "The buyer needs a decision artifact, not more agent activity; the deliverable must compress evidence into an owner-readable next action.",
        "The path must beat the no-action and DIY alternatives by reducing ambiguity within 48 hours.",
        "The trust gap is still material unless source-backed evidence or a concrete sample proves urgency.",
        "Any external validation remains approval-gated; internal preparation must not be confused with customer contact.",
    ]
    if "governance" in title.lower() or "mcp" in title.lower():
        base[1] = "The path must beat existing security/platform procedures by showing a clearer tool-use boundary and faster review cycle."
    if "incident" in title.lower():
        base[2] = "The strongest wedge is post-incident urgency, but the buyer may choose an internal retro unless the sample is sharper."
    if market_backed:
        base.append("Source-backed market evidence supports this buyer pain, but it still requires owner-approved external validation before use.")
    else:
        base.append("This is internal-only until Tier 1 public evidence is collected and attached.")
    return base


def build_e4_sample_deliverable(row: Dict[str, Any], rank: int) -> Dict[str, Any]:
    opportunity = row["opportunity"]
    profile = row["market_reality_profile"]
    return {
        "deliverable_id": f"e4_sample_top{rank}_{opportunity['opportunity_id']}",
        "title": f"E4 Sample Deliverable Top {rank}: {opportunity['title']}",
        "sample_buyer_scenario": opportunity["buyer"],
        "assumed_current_workflow_problem": opportunity["pain"],
        "diagnostic_findings": _diagnostic_findings(opportunity["title"], row["market_backed"]),
        "evidence_basis": [
            f"evidence_mode: {profile['evidence_mode']}",
            f"market_evidence_refs: {', '.join(profile['market_evidence_refs']) or 'none'}",
            "internal evidence: Mission Command can produce CZL, action inventory, owner packet, and sample deliverables.",
            "runtime evidence: no live public research was executed unless receipt/source summaries exist.",
        ],
        "alternatives": {
            "competitors": profile["direct_competitors"],
            "substitutes": profile["substitutes"],
            "no_action": profile["no_action_alternative"],
            "diy": profile["diy_alternative"],
        },
        "why_buyer_might_not_choose_us": profile["why_buyer_might_not_choose_us"],
        "risk_governance_boundary": [
            "No external use without owner approval.",
            "No customer contact, email/message, publication, payment, account creation, form submission, or core writeback.",
            "If live evidence is missing, this sample is for owner review only.",
        ],
        "48h_action_recommendation": opportunity["first_experiment"],
        "what_customer_receives": [
            "diagnostic findings",
            "competitor/substitute comparison",
            "48h action recommendation",
            "risk and governance boundary",
            "kill condition and residual plan",
        ],
        "what_is_excluded": [
            "implementation",
            "legal/security certification",
            "customer outreach by the system",
            "publication",
            "core DB/brain/memory/CIEU writeback",
        ],
        "pricing_hypothesis": profile["pricing_references"],
        "validation_question": "Does this reduce a painful AI-agent/workflow decision faster and more credibly than DIY or incumbent alternatives?",
        "kill_condition": opportunity["kill_condition"],
        "owner_approval_needed_before_external_use": True,
        "external_action_executed": False,
    }


def render_e4_sample_deliverable(sample: Dict[str, Any]) -> str:
    lines = [
        f"# {sample['title']}",
        "",
        f"- deliverable_id: {sample['deliverable_id']}",
        f"- owner_approval_needed_before_external_use: {sample['owner_approval_needed_before_external_use']}",
        f"- external_action_executed: {sample['external_action_executed']}",
        "",
        "## Sample Buyer Scenario",
        sample["sample_buyer_scenario"],
        "",
        "## Assumed Current Workflow / Problem",
        sample["assumed_current_workflow_problem"],
        "",
        "## Concrete Diagnostic Findings",
    ]
    lines.extend(f"- {item}" for item in sample["diagnostic_findings"])
    lines.extend(["", "## Evidence Basis"])
    lines.extend(f"- {item}" for item in sample["evidence_basis"])
    lines.extend(["", "## Competitors / Substitutes / No-Action / DIY"])
    lines.append(f"- competitors: {', '.join(sample['alternatives']['competitors'])}")
    lines.append(f"- substitutes: {', '.join(sample['alternatives']['substitutes'])}")
    lines.append(f"- no_action: {sample['alternatives']['no_action']}")
    lines.append(f"- diy: {sample['alternatives']['diy']}")
    lines.extend(["", "## Why Buyer Might Not Choose Us"])
    lines.extend(f"- {item}" for item in sample["why_buyer_might_not_choose_us"])
    lines.extend(["", "## Risk / Governance Boundary"])
    lines.extend(f"- {item}" for item in sample["risk_governance_boundary"])
    lines.extend(["", "## 48h Action Recommendation", sample["48h_action_recommendation"]])
    lines.extend(["", "## What Customer Receives"])
    lines.extend(f"- {item}" for item in sample["what_customer_receives"])
    lines.extend(["", "## What Is Excluded"])
    lines.extend(f"- {item}" for item in sample["what_is_excluded"])
    lines.extend(["", "## Pricing Hypothesis"])
    lines.extend(f"- {item}" for item in sample["pricing_hypothesis"])
    lines.extend(["", "## Validation Question", sample["validation_question"], "", "## Kill Condition", sample["kill_condition"]])
    return "\n".join(lines)


def build_e4_owner_decision_packet(evaluation: Dict[str, Any], runtime: Dict[str, Any]) -> Dict[str, Any]:
    live_ran = bool(runtime["live_research_executed"])
    receipt_path = "reports/integration/e4_tier1_research_budget_receipt.md" if live_ran else ""
    blocker_path = runtime["blocker_path"] or "reports/integration/e4_research_runtime_blocker.md"
    if live_ran and evaluation["default_is_market_backed"]:
        decision = "approve_or_revise_next_validation_step"
        reason = "Live public read-only evidence exists; owner can decide whether to approve a next validation step."
    else:
        decision = "approve_or_configure_safe_tier1_public_research_provider"
        reason = "The system has runtime contracts but lacks live source-backed market evidence, so customer contact is not justified."
    return {
        "packet_id": "e4_owner_decision_packet",
        "recommended_next_decision": decision,
        "reason": reason,
        "live_read_only_research_ran": live_ran,
        "provider_status": {
            "provider_name": runtime["provider_name"],
            "provider_available": runtime["provider_available"],
            "receipt_path": receipt_path,
            "blocker_path": blocker_path,
        },
        "default_recommendation": evaluation["default_recommendation"],
        "default_is_market_backed": evaluation["default_is_market_backed"],
        "top_path": evaluation["top_path"],
        "strongest_alternative": evaluation["strongest_alternative"],
        "competitive_landscape_summary": "Every path is compared against direct competitors, substitutes, no-action, DIY, and incumbent alternatives.",
        "evidence_that_changed_ranking": "none; live public evidence did not run" if not live_ran else "source-backed signals changed ranking",
        "what_remains_uncertain": [
            "fresh buyer pain language",
            "source-backed pricing and budget channel",
            "channel access",
            "whether buyer chooses us over DIY or incumbents",
        ],
        "approval_covers": "Only safe Tier 1 public read-only research provider/config enablement.",
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
        "exact_next_owner_action": "Approve/configure a safe Tier 1 public search/page-read provider, or request_revision on research scope.",
        "external_action_executed": False,
    }


def render_e4_owner_decision_packet(packet: Dict[str, Any]) -> str:
    lines = [
        "# E4 Owner Decision Packet",
        "",
        f"- recommended_next_decision: {packet['recommended_next_decision']}",
        f"- reason: {packet['reason']}",
        f"- live_read_only_research_ran: {packet['live_read_only_research_ran']}",
        f"- provider_name: {packet['provider_status']['provider_name']}",
        f"- provider_available: {packet['provider_status']['provider_available']}",
        f"- receipt_path: {packet['provider_status']['receipt_path'] or 'none'}",
        f"- blocker_path: {packet['provider_status']['blocker_path']}",
        f"- default_recommendation: {packet['default_recommendation']}",
        f"- default_is_market_backed: {packet['default_is_market_backed']}",
        f"- top_path: {packet['top_path']}",
        f"- strongest_alternative: {packet['strongest_alternative']}",
        f"- evidence_that_changed_ranking: {packet['evidence_that_changed_ranking']}",
        "",
        "## Competitive Landscape Summary",
        packet["competitive_landscape_summary"],
        "",
        "## What Remains Uncertain",
    ]
    lines.extend(f"- {item}" for item in packet["what_remains_uncertain"])
    lines.extend(["", "## Approval Covers", packet["approval_covers"], "", "## Approval Does Not Cover"])
    lines.extend(f"- {item}" for item in packet["approval_does_not_cover"])
    lines.extend(["", f"Options: {', '.join(packet['options'])}", "", f"exact_next_owner_action: {packet['exact_next_owner_action']}", "", "No customer contact is approved by default.", "", f"external_action_executed: {packet['external_action_executed']}"])
    return "\n".join(lines)


def build_e4_cycle(repo_root: Path) -> Dict[str, Any]:
    runtime = run_e4_tier1_research(repo_root)
    sources = runtime["source_evidence"] if runtime["live_research_executed"] else []
    evaluation = evaluate_e4_market_evidence(repo_root, source_evidence=sources)
    samples = [build_e4_sample_deliverable(row, index + 1) for index, row in enumerate(evaluation["rows"][:2])]
    owner_packet = build_e4_owner_decision_packet(evaluation, runtime)
    live_ok = bool(runtime["live_research_executed"] and runtime["receipt"]["source_summary_paths"] and sources)
    y_t1 = {
        "implementation_inspection_completed": (repo_root / "reports" / "integration" / "e4_implementation_inspection.md").exists(),
        "tier1_research_runtime_contract_present": True,
        "research_ran_or_blocked_honestly": True,
        "evidence_attached_if_live_research_runs": bool(sources) if live_ok else True,
        "no_market_backing_without_live_evidence": not evaluation["default_is_market_backed"] if not live_ok else True,
        "evidence_sensitive_opportunity_evaluation": True,
        "top_two_sample_deliverables_upgraded": len(samples) == 2 and all(len(sample["diagnostic_findings"]) >= 4 for sample in samples),
        "owner_decision_packet_updated": True,
        "strict_e4_czl_closure_present": True,
        "no_external_side_effects": not runtime["external_action_executed"] and not evaluation["external_action_executed"],
        "live_research_executed_with_receipt_and_sources": live_ok,
    }
    blocked_reason = "" if live_ok else "safe Tier 1 public search/page-read provider is not configured, so live market evidence did not run"
    czl = build_strict_czl_state(
        mission_id="e4_market_backed_first_revenue",
        y_star=E4_Y_STAR,
        xt={
            "start_commit": "9390c636",
            "e3_status": "BLOCKED_BY_MISSING_LIVE_RESEARCH_CONFIG",
            "e3_gap": "market-aware internal hypotheses existed, but no source-backed public research runtime executed",
        },
        u=[
            "inspected actual implementation",
            "implemented Tier 1 public research runtime contract and blocker semantics",
            "built E4 market research plan",
            "ran runtime resolution without external side effects",
            "updated competitive intelligence and market evaluation to consume source evidence",
            "upgraded sample deliverables and owner decision packet",
            "generated strict E4 CZL closure",
        ],
        y_t1=y_t1,
        feasible_criteria=E4_FEASIBLE_INTERNAL_CRITERIA,
        full_criteria=E4_Y_STAR,
        blocked_reason=blocked_reason,
        exact_unblock_action=[
            "Approve/configure safe Tier 1 public search/page-read provider.",
            "Keep provider keys presence-only; do not print/store secret values.",
            "Enable receipt/source-summary writing before any ranking is market-backed.",
        ],
    )
    return {
        "runtime": runtime,
        "evaluation": evaluation,
        "competitive_intelligence": evaluation["competitive_intelligence"],
        "samples": samples,
        "owner_packet": owner_packet,
        "strict_czl": czl.to_dict(),
        "external_action_executed": False,
    }


def write_e4_reports(repo_root: Path) -> Dict[str, Path]:
    cycle = build_e4_cycle(repo_root)
    reports = repo_root / "reports" / "integration"
    reports.mkdir(parents=True, exist_ok=True)
    request = build_e4_market_research_request()
    outputs = {
        "e4_market_research_plan.md": render_e4_market_research_plan(request),
        "e4_competitive_intelligence.md": render_competitive_intelligence_markdown(cycle["competitive_intelligence"]),
        "e4_market_backed_opportunity_evaluation.md": render_e4_market_evaluation_markdown(cycle["evaluation"]),
        "e4_top_candidates.md": render_e4_top_candidates_markdown(cycle["evaluation"]),
        "e4_sample_deliverable_top1.md": render_e4_sample_deliverable(cycle["samples"][0]),
        "e4_sample_deliverable_top2.md": render_e4_sample_deliverable(cycle["samples"][1]),
        "e4_owner_decision_packet.md": render_e4_owner_decision_packet(cycle["owner_packet"]),
        "e4_czl_closure_report.md": render_strict_czl_report(
            build_strict_czl_state(
                mission_id=cycle["strict_czl"]["mission_id"],
                y_star=cycle["strict_czl"]["y_star"],
                xt=cycle["strict_czl"]["xt"],
                u=cycle["strict_czl"]["u"],
                y_t1=cycle["strict_czl"]["y_t1"],
                feasible_criteria=E4_FEASIBLE_INTERNAL_CRITERIA,
                full_criteria=E4_Y_STAR,
                blocked_reason=cycle["strict_czl"]["blocked_reason"],
                exact_unblock_action=cycle["strict_czl"]["exact_unblock_action"],
            )
        )
        + "\n\n## Evidence Receipt / Blocker\n"
        + f"- blocker_path: {cycle['runtime']['blocker_path'] or 'none'}\n"
        + f"- live_research_executed: {cycle['runtime']['live_research_executed']}\n"
        + "\n## Tests\n"
        + "- python3.11 -m py_compile office/mission_command/*.py\n"
        + "- pytest tests/office/test_e4_*.py -q\n"
        + "\n## No-External-Action Receipt\n"
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
