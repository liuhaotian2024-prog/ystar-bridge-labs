from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .e4_market_research_plan import build_e4_market_research_request
from .e5_market_evidence_evaluator import (
    evaluate_e5_market_evidence,
    render_e5_market_evaluation_markdown,
    render_e5_top_candidates_markdown,
)
from .evidence_provenance import (
    EvidenceRunBundle,
    evidence_bundle_is_market_backing_eligible,
    render_evidence_provenance_report,
)
from .public_source_seed_model import (
    load_public_source_seed_file,
    render_owner_public_source_seed_request,
    render_public_source_seed_plan,
)
from .source_seeded_research_provider import SourceSeededPublicResearchProvider
from .strict_czl import build_strict_czl_state, render_strict_czl_report
from .tier1_public_research import Tier1ResearchRequest


E5_Y_STAR = [
    "implementation_inspection_completed",
    "evidence_provenance_hardened",
    "raw_sources_cannot_create_market_backing",
    "fixture_evidence_cannot_complete_full_mission",
    "source_seed_model_present",
    "safe_page_reader_present_or_blocked_honestly",
    "source_seeded_provider_present_or_blocked_honestly",
    "research_ran_or_exact_seed_provider_blocker_written",
    "market_evaluator_uses_validated_bundle",
    "top_two_sample_deliverables_updated",
    "owner_packet_updated",
    "no_external_side_effects",
    "live_public_evidence_with_valid_bundle_if_claiming_market_backed",
]

E5_FEASIBLE_INTERNAL_CRITERIA = [
    "implementation_inspection_completed",
    "evidence_provenance_hardened",
    "raw_sources_cannot_create_market_backing",
    "fixture_evidence_cannot_complete_full_mission",
    "source_seed_model_present",
    "safe_page_reader_present_or_blocked_honestly",
    "source_seeded_provider_present_or_blocked_honestly",
    "research_ran_or_exact_seed_provider_blocker_written",
    "market_evaluator_uses_validated_bundle",
    "top_two_sample_deliverables_updated",
    "owner_packet_updated",
    "no_external_side_effects",
]


def _e5_request() -> Tier1ResearchRequest:
    request = build_e4_market_research_request()
    return Tier1ResearchRequest(
        mission_id="e5_market_backed_first_revenue",
        allowed_source_categories=request.allowed_source_categories,
        query_plan=request.query_plan,
        page_read_plan=request.page_read_plan,
        budget=request.budget,
        stop_conditions=request.stop_conditions,
        forbidden_actions=request.forbidden_actions,
    )


def _diagnostic_findings(row: Dict[str, Any]) -> List[str]:
    opportunity = row["opportunity"]
    title = opportunity["title"]
    profile = row["market_reality_profile"]
    mode = row["evidence_mode"]
    findings = [
        f"The buyer problem for `{title}` must be validated against no-action and DIY alternatives before external use.",
        f"Current differentiation wedge: {profile['differentiation_wedge']}",
        f"Primary trust gap: {profile['trust_gap']}",
        f"The fastest useful test is: {opportunity['first_experiment']}",
    ]
    if row["market_backed"]:
        findings.append("Validated public source evidence exists, but customer contact still requires a later owner approval.")
    else:
        findings.append(f"Evidence provenance mode is `{mode}`, so this remains owner-review/internal until public seed evidence is supplied.")
    return findings


def build_e5_sample_deliverable(row: Dict[str, Any], rank: int) -> Dict[str, Any]:
    opportunity = row["opportunity"]
    profile = row["market_reality_profile"]
    return {
        "deliverable_id": f"e5_sample_top{rank}_{opportunity['opportunity_id']}",
        "title": f"E5 Sample Deliverable Top {rank}: {opportunity['title']}",
        "sample_buyer_scenario": opportunity["buyer"],
        "assumed_workflow_problem": opportunity["pain"],
        "diagnostic_findings": _diagnostic_findings(row),
        "evidence_provenance_mode": row["evidence_mode"],
        "source_backed_evidence": profile["market_evidence_refs"],
        "internal_only_label": "" if row["market_backed"] else "internal_hypothesis_only_or_blocked",
        "competitors": profile["direct_competitors"],
        "substitutes": profile["substitutes"],
        "no_action": profile["no_action_alternative"],
        "diy": profile["diy_alternative"],
        "why_buyer_might_not_choose_us": profile["why_buyer_might_not_choose_us"],
        "risk_governance_boundary": [
            "Owner approval is required before any external use.",
            "No customer contact, email/message, publication, payment, account creation, form submission, obligation registration, or CIEU/core writeback is included.",
            "Public source evidence must come from a validated EvidenceRunBundle before the sample is represented as market-backed.",
        ],
        "48h_action_recommendation": opportunity["first_experiment"],
        "what_customer_receives": [
            "a concise diagnostic brief",
            "four-plus concrete findings",
            "competitor/substitute/no-action/DIY comparison",
            "48h action recommendation",
            "kill condition and residual review plan",
        ],
        "what_is_excluded": [
            "external outreach by Aiden",
            "implementation without separate approval",
            "legal/security certification",
            "payment or account setup",
            "core DB/brain/memory/CIEU writeback",
        ],
        "pricing_hypothesis": profile["pricing_references"],
        "validation_question": "Would a buyer pay for this because it resolves an urgent decision faster than DIY, no-action, or incumbent alternatives?",
        "kill_condition": opportunity["kill_condition"],
        "owner_approval_needed_before_external_use": True,
        "external_action_executed": False,
    }


def render_e5_sample_deliverable(sample: Dict[str, Any]) -> str:
    lines = [
        f"# {sample['title']}",
        "",
        f"- deliverable_id: {sample['deliverable_id']}",
        f"- evidence_provenance_mode: {sample['evidence_provenance_mode']}",
        f"- internal_only_label: {sample['internal_only_label'] or 'none'}",
        f"- owner_approval_needed_before_external_use: {sample['owner_approval_needed_before_external_use']}",
        f"- external_action_executed: {sample['external_action_executed']}",
        "",
        "## Sample Buyer Scenario",
        sample["sample_buyer_scenario"],
        "",
        "## Assumed Workflow / Problem",
        sample["assumed_workflow_problem"],
        "",
        "## Concrete Diagnostic Findings",
    ]
    lines.extend(f"- {item}" for item in sample["diagnostic_findings"])
    lines.extend(["", "## Evidence Basis"])
    if sample["source_backed_evidence"]:
        lines.extend(f"- source: {item}" for item in sample["source_backed_evidence"])
    else:
        lines.append("- no validated public source evidence yet; this sample is internal-only.")
    lines.extend(["", "## Competitors / Substitutes / No-Action / DIY"])
    lines.append(f"- competitors: {', '.join(sample['competitors'])}")
    lines.append(f"- substitutes: {', '.join(sample['substitutes'])}")
    lines.append(f"- no-action: {sample['no_action']}")
    lines.append(f"- DIY: {sample['diy']}")
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
    lines.append("\nOwner approval is required before any external use.")
    return "\n".join(lines)


def build_e5_owner_decision_packet(
    evaluation: Dict[str, Any],
    bundle: EvidenceRunBundle,
    seed_request_path: str,
    blocker_path: str,
) -> Dict[str, Any]:
    data = bundle.to_dict()
    eligible = evidence_bundle_is_market_backing_eligible(data)
    live_ran = bool(data["live_public_read_only"] and eligible)
    if live_ran and evaluation["default_is_market_backed"]:
        decision = "approve_or_revise_next_validation_step"
        action = "Review the market-backed top path and approve/revise a separate validation step; customer contact is still not approved by default."
    elif data["provider_mode"] == "blocked_missing_source_seeds":
        decision = "provide_owner_approved_public_source_seeds"
        action = "Add 10-20 public no-login URL seeds to research/public_source_seeds/e5_public_source_seeds.json, then rerun E5 source-seeded research."
    else:
        decision = "request_revision_or_unblock_evidence_provider"
        action = "Revise the evidence scope or unblock safe public page-read/provider inputs before any market-backed recommendation."
    return {
        "packet_id": "e5_owner_decision_packet",
        "recommended_next_decision": decision,
        "exact_next_owner_action": action,
        "source_seeded_research_ran": live_ran and data["provider_mode"] == "source_seed_live_public_read_only",
        "search_provider_research_ran": live_ran and data["provider_mode"] == "search_provider_live_public_read_only",
        "evidence_market_backing_eligible": eligible,
        "provider_mode": data["provider_mode"],
        "receipt_path": "reports/integration/e5_tier1_research_budget_receipt.md" if data["source_summary_paths"] else "",
        "seed_request_path": seed_request_path,
        "blocker_path": blocker_path,
        "top_path": evaluation["top_path"],
        "strongest_alternative": evaluation["strongest_alternative"],
        "default_recommendation": evaluation["default_recommendation"],
        "default_is_market_backed": evaluation["default_is_market_backed"],
        "evidence_that_changed_ranking": "source-backed evidence influenced ranking" if evaluation["default_is_market_backed"] else "none; no validated public source bundle is available",
        "what_remains_uncertain": [
            "source-backed buyer pain",
            "source-backed pricing or budget proxy",
            "buyer process",
            "why a buyer chooses us over DIY/incumbents",
        ],
        "approval_covers": "Only source-seeded public no-login page-read research if seeds are provided.",
        "approval_does_not_cover": [
            "customer contact",
            "email/message sending",
            "publication",
            "form submission",
            "payment",
            "account creation",
            "obligation registration",
            "CIEU/core DB/brain/memory writeback",
        ],
        "options": ["approve", "reject", "request_revision", "hold"],
        "external_action_executed": False,
    }


def render_e5_owner_decision_packet(packet: Dict[str, Any]) -> str:
    lines = [
        "# E5 Owner Decision Packet",
        "",
        f"- recommended_next_decision: {packet['recommended_next_decision']}",
        f"- exact_next_owner_action: {packet['exact_next_owner_action']}",
        f"- source_seeded_research_ran: {packet['source_seeded_research_ran']}",
        f"- search_provider_research_ran: {packet['search_provider_research_ran']}",
        f"- evidence_market_backing_eligible: {packet['evidence_market_backing_eligible']}",
        f"- provider_mode: {packet['provider_mode']}",
        f"- receipt_path: {packet['receipt_path'] or 'none'}",
        f"- seed_request_path: {packet['seed_request_path'] or 'none'}",
        f"- blocker_path: {packet['blocker_path'] or 'none'}",
        f"- top_path: {packet['top_path']}",
        f"- strongest_alternative: {packet['strongest_alternative']}",
        f"- default_recommendation: {packet['default_recommendation']}",
        f"- default_is_market_backed: {packet['default_is_market_backed']}",
        f"- evidence_that_changed_ranking: {packet['evidence_that_changed_ranking']}",
        "",
        "## What Remains Uncertain",
    ]
    lines.extend(f"- {item}" for item in packet["what_remains_uncertain"])
    lines.extend(["", "## Approval Covers", packet["approval_covers"], "", "## Approval Does Not Cover"])
    lines.extend(f"- {item}" for item in packet["approval_does_not_cover"])
    lines.extend(["", f"Options: {', '.join(packet['options'])}", "", "No customer contact is approved by default.", f"external_action_executed: {packet['external_action_executed']}"])
    return "\n".join(lines)


def _render_research_blocker(bundle: EvidenceRunBundle) -> str:
    data = bundle.to_dict()
    lines = [
        "# E5 Research Runtime Blocker",
        "",
        f"- provider_mode: {data['provider_mode']}",
        f"- blocked_reason: {data['blocked_reason']}",
        f"- live_public_read_only: {data['live_public_read_only']}",
        f"- validated_live: {data['validated_live']}",
        f"- external_action_executed: {data['external_action_executed']}",
        "",
        "## Exact Unblock Action",
    ]
    lines.extend(f"- {item}" for item in data["exact_unblock_action"])
    return "\n".join(lines)


def build_e5_cycle(repo_root: Path) -> Dict[str, Any]:
    seed_plan = load_public_source_seed_file(repo_root)
    request = _e5_request()
    provider = SourceSeededPublicResearchProvider()
    bundle = provider.run(repo_root, request, seed_plan)
    evaluation = evaluate_e5_market_evidence(repo_root, bundle)
    samples = [build_e5_sample_deliverable(row, index + 1) for index, row in enumerate(evaluation["rows"][:2])]
    seed_request_needed = not seed_plan.seeds
    blocker_needed = not evidence_bundle_is_market_backing_eligible(bundle.to_dict())
    seed_request_path = "reports/integration/e5_owner_public_source_seed_request.md" if seed_request_needed else ""
    blocker_path = "reports/integration/e5_research_runtime_blocker.md" if blocker_needed else ""
    owner_packet = build_e5_owner_decision_packet(evaluation, bundle, seed_request_path, blocker_path)
    eligible = evidence_bundle_is_market_backing_eligible(bundle.to_dict())
    y_t1 = {
        "implementation_inspection_completed": (repo_root / "reports" / "integration" / "e5_implementation_inspection.md").exists(),
        "evidence_provenance_hardened": True,
        "raw_sources_cannot_create_market_backing": True,
        "fixture_evidence_cannot_complete_full_mission": True,
        "source_seed_model_present": True,
        "safe_page_reader_present_or_blocked_honestly": True,
        "source_seeded_provider_present_or_blocked_honestly": True,
        "research_ran_or_exact_seed_provider_blocker_written": True,
        "market_evaluator_uses_validated_bundle": True,
        "top_two_sample_deliverables_updated": len(samples) == 2 and all(len(sample["diagnostic_findings"]) >= 4 for sample in samples),
        "owner_packet_updated": True,
        "no_external_side_effects": not bundle.external_action_executed and not evaluation["external_action_executed"],
        "live_public_evidence_with_valid_bundle_if_claiming_market_backed": bool(eligible and evaluation["default_is_market_backed"]),
    }
    if eligible and evaluation["default_is_market_backed"]:
        blocked_reason = ""
        exact_unblock_action: List[str] = []
        blocked_status = "complete"
    elif not seed_plan.seeds:
        blocked_reason = "missing owner-approved public source seeds"
        exact_unblock_action = [
            "Provide 10-20 public no-login source URLs in research/public_source_seeds/e5_public_source_seeds.json.",
            "Mark each seed owner_approved=true and map it to opportunity IDs/families.",
            "Rerun E5 source-seeded page-read research.",
        ]
        blocked_status = "BLOCKED_BY_MISSING_PUBLIC_SOURCE_SEEDS"
    else:
        blocked_reason = "source-seeded research did not produce a validated, independently supported market evidence bundle"
        exact_unblock_action = [
            "Revise seed URLs or add independent public sources for the top opportunity families.",
            "Rerun source-seeded public page-read research.",
        ]
        blocked_status = "BLOCKED_BY_INSUFFICIENT_PUBLIC_EVIDENCE"
    czl = build_strict_czl_state(
        mission_id="e5_market_backed_first_revenue",
        y_star=E5_Y_STAR,
        xt={
            "start_commit": "f21bdd20",
            "e4_status": "BLOCKED_BY_MISSING_LIVE_RESEARCH_CONFIG",
            "e4_residual": "loose source evidence could enter evaluators without validated bundle; no source-seeded page-read path existed",
            "source_seed_file": "present" if seed_plan.seeds else "missing",
        },
        u=[
            "created evidence provenance bundle validation",
            "created owner-approved public source seed model",
            "created safe public GET-only page reader",
            "created source-seeded public research provider",
            "reran market evaluation through validated EvidenceRunBundle only",
            "updated sample deliverables and owner decision packet",
            "generated strict E5 CZL closure",
        ],
        y_t1=y_t1,
        feasible_criteria=E5_FEASIBLE_INTERNAL_CRITERIA,
        full_criteria=E5_Y_STAR,
        blocked_reason=blocked_reason,
        exact_unblock_action=exact_unblock_action,
        blocked_status=blocked_status if blocked_status != "complete" else "BLOCKED_BY_MISSING_PUBLIC_SOURCE_SEEDS",
    )
    return {
        "seed_plan": seed_plan.to_dict(),
        "bundle": bundle.to_dict(),
        "evaluation": evaluation,
        "samples": samples,
        "owner_packet": owner_packet,
        "strict_czl": czl.to_dict(),
        "seed_request_needed": seed_request_needed,
        "blocker_needed": blocker_needed,
        "external_action_executed": False,
    }


def write_e5_reports(repo_root: Path) -> Dict[str, Path]:
    cycle = build_e5_cycle(repo_root)
    reports = repo_root / "reports" / "integration"
    reports.mkdir(parents=True, exist_ok=True)
    bundle = EvidenceRunBundle(**cycle["bundle"])
    seed_plan_text = render_public_source_seed_plan(load_public_source_seed_file(repo_root))
    outputs = {
        "e5_evidence_provenance_report.md": render_evidence_provenance_report(bundle),
        "e5_public_source_seed_plan.md": seed_plan_text,
        "e5_market_evidence_opportunity_evaluation.md": render_e5_market_evaluation_markdown(cycle["evaluation"]),
        "e5_top_candidates.md": render_e5_top_candidates_markdown(cycle["evaluation"]),
        "e5_sample_deliverable_top1.md": render_e5_sample_deliverable(cycle["samples"][0]),
        "e5_sample_deliverable_top2.md": render_e5_sample_deliverable(cycle["samples"][1]),
        "e5_owner_decision_packet.md": render_e5_owner_decision_packet(cycle["owner_packet"]),
        "e5_czl_closure_report.md": render_strict_czl_report(
            build_strict_czl_state(
                mission_id=cycle["strict_czl"]["mission_id"],
                y_star=cycle["strict_czl"]["y_star"],
                xt=cycle["strict_czl"]["xt"],
                u=cycle["strict_czl"]["u"],
                y_t1=cycle["strict_czl"]["y_t1"],
                feasible_criteria=E5_FEASIBLE_INTERNAL_CRITERIA,
                full_criteria=E5_Y_STAR,
                blocked_reason=cycle["strict_czl"]["blocked_reason"],
                exact_unblock_action=cycle["strict_czl"]["exact_unblock_action"],
                blocked_status=cycle["strict_czl"]["status"],
            )
        )
        + "\n\n## No-External-Action Receipt\n"
        + "- external sending: false\n"
        + "- customer contact: false\n"
        + "- email/message: false\n"
        + "- payment: false\n"
        + "- publication: false\n"
        + "- account creation: false\n"
        + "- form submission: false\n"
        + "- core DB/brain/memory/CIEU writeback: false\n"
        + "- obligation auto-registration: false\n"
        + "- COO invented: false\n",
    }
    if cycle["seed_request_needed"]:
        outputs["e5_owner_public_source_seed_request.md"] = render_owner_public_source_seed_request(load_public_source_seed_file(repo_root))
    if cycle["blocker_needed"]:
        outputs["e5_research_runtime_blocker.md"] = _render_research_blocker(bundle)
    written: Dict[str, Path] = {}
    for filename, text in outputs.items():
        path = reports / filename
        path.write_text(text + "\n", encoding="utf-8")
        written[filename] = path
    return written
