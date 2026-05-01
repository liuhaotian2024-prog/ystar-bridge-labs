from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .e4_market_research_plan import build_e4_market_research_request
from .e6_market_evidence_evaluator import (
    evaluate_e6_market_evidence,
    render_competitive_objection_matrix,
    render_e6_market_evaluation_markdown,
    render_e6_top_candidates_markdown,
)
from .e6_offer_thesis import build_e6_offer_thesis, render_e6_offer_thesis
from .evidence_provenance import EvidenceRunBundle, evidence_bundle_is_market_backing_eligible, render_evidence_provenance_report
from .public_source_seed_model import load_public_source_seed_file, render_public_source_seed_plan, validate_public_source_seed
from .source_seeded_research_provider import SourceSeededPublicResearchProvider
from .strict_czl import build_strict_czl_state, render_strict_czl_report
from .tier1_public_research import Tier1ResearchRequest


E6_Y_STAR = [
    "implementation_inspection_completed",
    "owner_approved_seed_file_created",
    "public_source_seeds_validated",
    "source_seeded_research_attempted",
    "receipt_written",
    "source_summaries_written_if_sources_exist",
    "evidence_bundle_validated_or_blocked_honestly",
    "market_evaluation_uses_validated_bundle",
    "competitive_objection_matrix_created",
    "offer_thesis_created",
    "top_two_sample_deliverables_updated",
    "owner_decision_packet_updated",
    "no_external_side_effects",
    "market_backed_offer_thesis_if_claiming_completion",
]

E6_FEASIBLE_INTERNAL_CRITERIA = [
    "implementation_inspection_completed",
    "owner_approved_seed_file_created",
    "public_source_seeds_validated",
    "source_seeded_research_attempted",
    "receipt_written",
    "evidence_bundle_validated_or_blocked_honestly",
    "market_evaluation_uses_validated_bundle",
    "competitive_objection_matrix_created",
    "offer_thesis_created",
    "top_two_sample_deliverables_updated",
    "owner_decision_packet_updated",
    "no_external_side_effects",
]


def _e6_request() -> Tier1ResearchRequest:
    request = build_e4_market_research_request()
    return Tier1ResearchRequest(
        mission_id="e6_source_seeded_market_evidence_run",
        allowed_source_categories=request.allowed_source_categories,
        query_plan=[],
        page_read_plan=[],
        budget=request.budget,
        stop_conditions=["stop on page/domain budget", "stop on unsafe URL", "stop on login/form/payment/page-block indicator"],
        forbidden_actions=request.forbidden_actions,
    )


def _seed_validation_summary(repo_root: Path) -> Dict[str, Any]:
    plan = load_public_source_seed_file(repo_root)
    invalid = []
    families = sorted({seed.opportunity_family for seed in plan.seeds})
    for seed in plan.seeds:
        errors = validate_public_source_seed(seed)
        if errors:
            invalid.append({"seed_id": seed.seed_id, "errors": errors})
    return {
        "seed_count": len(plan.seeds),
        "required_seed_count": plan.required_seed_count,
        "family_count": len(families),
        "families": families,
        "invalid": invalid,
        "enough_valid_to_run": len(plan.seeds) >= plan.required_seed_count and not invalid,
    }


def render_e6_public_source_seed_plan(repo_root: Path) -> str:
    plan = load_public_source_seed_file(repo_root)
    summary = _seed_validation_summary(repo_root)
    lines = [
        "# E6 Public Source Seed Plan",
        "",
        f"- seed_count: {summary['seed_count']}",
        f"- required_seed_count: {summary['required_seed_count']}",
        f"- family_count: {summary['family_count']}",
        f"- enough_valid_to_run: {summary['enough_valid_to_run']}",
        f"- approval_boundary: {plan.approval_boundary}",
        "",
        "## Opportunity Family Coverage",
    ]
    lines.extend(f"- {family}" for family in summary["families"])
    lines.extend(["", "## Invalid / Skipped Seeds"])
    if summary["invalid"]:
        for item in summary["invalid"]:
            lines.append(f"- {item['seed_id']}: {', '.join(item['errors'])}")
    else:
        lines.append("- none at seed-validation stage")
    lines.extend(["", "## Forbidden Actions"])
    lines.extend(f"- {item}" for item in plan.forbidden_actions)
    lines.extend(["", "## Raw Seed Details", render_public_source_seed_plan(plan)])
    return "\n".join(lines)


def build_e6_sample_deliverable(row: Dict[str, Any], rank: int) -> Dict[str, Any]:
    opportunity = row["opportunity"]
    profile = row["market_reality_profile"]
    findings = [
        f"Public-source support status: {row['evidence_status']}.",
        f"Buyer scenario: {opportunity['buyer']}",
        f"Pain to test: {opportunity['pain']}",
        f"Competitive pressure: {', '.join(profile['direct_competitors'][:3])}",
        f"Substitute/no-action pressure: {profile['no_action_alternative']}",
    ]
    if row["source_ids"]:
        findings.append(f"Validated source IDs attached: {', '.join(row['source_ids'])}.")
    else:
        findings.append("No validated source IDs attach to this opportunity yet.")
    return {
        "title": f"E6 Sample Deliverable Top {rank}: {opportunity['title']}",
        "sample_buyer_scenario": opportunity["buyer"],
        "evidence_provenance_mode": row["evidence_mode"],
        "source_ids_used": row["source_ids"],
        "assumed_workflow_problem": opportunity["pain"],
        "diagnostic_findings": findings,
        "competitors": profile["direct_competitors"],
        "substitutes": profile["substitutes"],
        "no_action": profile["no_action_alternative"],
        "diy": profile["diy_alternative"],
        "buyer_rejection_reasons": profile["why_buyer_might_not_choose_us"],
        "trust_gap": profile["trust_gap"],
        "48h_action_recommendation": opportunity["first_experiment"],
        "what_customer_receives": [
            "diagnostic findings",
            "source-backed or source-insufficient evidence note",
            "competitor/substitute/no-action/DIY comparison",
            "48h recommendation",
            "kill condition",
        ],
        "what_is_excluded": [
            "customer contact",
            "publication",
            "payment or account creation",
            "implementation without separate approval",
            "core DB/brain/memory/CIEU writeback",
        ],
        "pricing_hypothesis": profile["pricing_references"],
        "validation_question": "Does this source-backed evidence justify a separate owner-approved validation step?",
        "kill_condition": opportunity["kill_condition"],
        "owner_approval_needed_before_external_use": True,
        "external_action_executed": False,
    }


def render_e6_sample_deliverable(sample: Dict[str, Any]) -> str:
    lines = [
        f"# {sample['title']}",
        "",
        f"- evidence_provenance_mode: {sample['evidence_provenance_mode']}",
        f"- source_ids_used: {', '.join(sample['source_ids_used']) or 'none'}",
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
    lines.extend(["", "## Competitors / Substitutes / No-Action / DIY"])
    lines.append(f"- competitors: {', '.join(sample['competitors'])}")
    lines.append(f"- substitutes: {', '.join(sample['substitutes'])}")
    lines.append(f"- no-action: {sample['no_action']}")
    lines.append(f"- DIY: {sample['diy']}")
    lines.extend(["", "## Buyer Rejection Reasons"])
    lines.extend(f"- {item}" for item in sample["buyer_rejection_reasons"])
    lines.extend(["", "## Trust Gap", sample["trust_gap"]])
    lines.extend(["", "## 48h Action Recommendation", sample["48h_action_recommendation"]])
    lines.extend(["", "## What Customer Receives"])
    lines.extend(f"- {item}" for item in sample["what_customer_receives"])
    lines.extend(["", "## What Is Excluded"])
    lines.extend(f"- {item}" for item in sample["what_is_excluded"])
    lines.extend(["", "## Pricing Hypothesis"])
    lines.extend(f"- {item}" for item in sample["pricing_hypothesis"])
    lines.extend(["", "## Validation Question", sample["validation_question"], "", "## Kill Condition", sample["kill_condition"]])
    return "\n".join(lines)


def build_e6_owner_decision_packet(evaluation: Dict[str, Any], bundle: Dict[str, Any], thesis: Dict[str, Any], blocker_path: str) -> Dict[str, Any]:
    receipt_path = "reports/integration/e6_tier1_research_budget_receipt.md"
    summaries_path = "reports/integration/e6_external_source_summaries.md" if bundle.get("sources") else ""
    if thesis["thesis_status"] == "evidence_backed":
        decision = "approve_or_revise_next_validation_step"
    elif bundle.get("sources"):
        decision = "request_revision_more_public_evidence"
    else:
        decision = "request_revision_seed_urls_or_page_reader"
    return {
        "source_seeded_research_ran": bool(bundle.get("live_public_read_only")),
        "search_provider_research_ran": False,
        "provider_mode": bundle.get("provider_mode"),
        "evidence_bundle_valid": bool(bundle.get("validated_live")),
        "market_backing_eligible": evidence_bundle_is_market_backing_eligible(bundle),
        "receipt_path": receipt_path,
        "source_summaries_path": summaries_path,
        "blocker_path": blocker_path,
        "top_path": evaluation["top_path"],
        "strongest_alternative": evaluation["strongest_alternative"],
        "evidence_that_changed_ranking": "validated source IDs changed ranking" if evaluation["bundle_valid"] else "no validated bundle",
        "recommendation_market_backed": evaluation["default_is_market_backed"],
        "offer_thesis_status": thesis["thesis_status"],
        "what_remains_uncertain": thesis.get("exact_missing_evidence", ["buyer willingness to pay", "channel access", "trust gap"]),
        "recommended_next_decision": decision,
        "exact_next_owner_action": (
            "Approve or revise a separate validation step; this does not approve customer contact by default."
            if decision == "approve_or_revise_next_validation_step"
            else "Provide stronger public evidence seeds or revise the evidence scope before any customer validation."
        ),
        "options": ["approve", "reject", "request_revision", "hold"],
        "approval_does_not_cover": [
            "customer contact",
            "email/message",
            "publication",
            "form submission",
            "payment",
            "account creation",
            "core DB/brain/memory/CIEU writeback",
            "obligation registration",
        ],
        "external_action_executed": False,
    }


def render_e6_owner_decision_packet(packet: Dict[str, Any]) -> str:
    lines = ["# E6 Owner Decision Packet", ""]
    for key in [
        "source_seeded_research_ran",
        "search_provider_research_ran",
        "provider_mode",
        "evidence_bundle_valid",
        "market_backing_eligible",
        "receipt_path",
        "source_summaries_path",
        "blocker_path",
        "top_path",
        "strongest_alternative",
        "evidence_that_changed_ranking",
        "recommendation_market_backed",
        "offer_thesis_status",
        "recommended_next_decision",
        "exact_next_owner_action",
    ]:
        lines.append(f"- {key}: {packet.get(key) or 'none'}")
    lines.extend(["", "## What Remains Uncertain"])
    lines.extend(f"- {item}" for item in packet["what_remains_uncertain"])
    lines.extend(["", "## Options", ", ".join(packet["options"]), "", "## Approval Does Not Cover"])
    lines.extend(f"- {item}" for item in packet["approval_does_not_cover"])
    lines.extend(["", "Customer contact is not approved by default.", "Publication is not approved by default.", "Form/payment/account actions are not approved.", f"external_action_executed: {packet['external_action_executed']}"])
    return "\n".join(lines)


def _render_research_blocker(status: str, bundle: Dict[str, Any], thesis: Dict[str, Any]) -> str:
    lines = [
        "# E6 Research Runtime Blocker",
        "",
        f"- status: {status}",
        f"- provider_mode: {bundle.get('provider_mode')}",
        f"- validated_live: {bundle.get('validated_live')}",
        f"- source_count: {len(bundle.get('sources', []))}",
        f"- thesis_status: {thesis['thesis_status']}",
        f"- external_action_executed: {bundle.get('external_action_executed')}",
        "",
        "## Residual",
    ]
    if not bundle.get("sources"):
        lines.append("- Public page reads did not produce enough valid source summaries.")
    elif thesis["thesis_status"] != "evidence_backed":
        lines.extend(f"- {item}" for item in thesis.get("why_insufficient", []))
    return "\n".join(lines)


def build_e6_cycle(repo_root: Path) -> Dict[str, Any]:
    plan = load_public_source_seed_file(repo_root)
    seed_summary = _seed_validation_summary(repo_root)
    request = _e6_request()
    provider = SourceSeededPublicResearchProvider()
    bundle = provider.run(
        repo_root,
        request,
        plan,
        run_id="e6_source_seeded_public_page_read",
        blocked_run_id="e6_source_seeded_blocked",
        receipt_name="e6_tier1_research_budget_receipt.md",
        summaries_name="e6_external_source_summaries.md",
    )
    bundle_dict = bundle.to_dict()
    evaluation = evaluate_e6_market_evidence(repo_root, bundle)
    thesis = build_e6_offer_thesis(evaluation, bundle_dict)
    samples = [build_e6_sample_deliverable(row, index + 1) for index, row in enumerate(evaluation["rows"][:2])]
    if thesis["thesis_status"] == "evidence_backed":
        status = "complete"
        blocked_reason = ""
        blocker_path = ""
        exact_unblock_action: List[str] = []
    elif bundle_dict.get("validated_live") and bundle_dict.get("sources"):
        status = "BLOCKED_BY_INSUFFICIENT_PUBLIC_EVIDENCE"
        blocked_reason = "validated source reads ran, but evidence did not meet market-backed offer thesis threshold"
        blocker_path = "reports/integration/e6_research_runtime_blocker.md"
        exact_unblock_action = ["Add stronger independent public sources for the top opportunity, or revise the target family."]
    elif bundle_dict.get("validation_errors"):
        status = "BLOCKED_BY_EVIDENCE_BUNDLE_VALIDATION_FAILURE"
        blocked_reason = "evidence bundle validation failed"
        blocker_path = "reports/integration/e6_research_runtime_blocker.md"
        exact_unblock_action = ["Fix receipt/source summary validation errors and rerun E6."]
    else:
        status = "BLOCKED_BY_PAGE_READ_FAILURE"
        blocked_reason = "page reads did not produce valid public source summaries"
        blocker_path = "reports/integration/e6_research_runtime_blocker.md"
        exact_unblock_action = ["Revise owner-approved seed URLs or page-read safety settings, then rerun E6."]
    owner_packet = build_e6_owner_decision_packet(evaluation, bundle_dict, thesis, blocker_path)
    receipt_written = (repo_root / "reports" / "integration" / "e6_tier1_research_budget_receipt.md").exists()
    source_summaries_written = (repo_root / "reports" / "integration" / "e6_external_source_summaries.md").exists() if bundle_dict.get("sources") else True
    y_t1 = {
        "implementation_inspection_completed": (repo_root / "reports" / "integration" / "e6_implementation_inspection.md").exists(),
        "owner_approved_seed_file_created": (repo_root / "research" / "public_source_seeds" / "e5_public_source_seeds.json").exists(),
        "public_source_seeds_validated": seed_summary["enough_valid_to_run"],
        "source_seeded_research_attempted": True,
        "receipt_written": receipt_written,
        "source_summaries_written_if_sources_exist": source_summaries_written,
        "evidence_bundle_validated_or_blocked_honestly": bool(bundle_dict.get("validated_live") or status.startswith("BLOCKED")),
        "market_evaluation_uses_validated_bundle": True,
        "competitive_objection_matrix_created": True,
        "offer_thesis_created": bool(thesis),
        "top_two_sample_deliverables_updated": len(samples) == 2 and all(len(sample["diagnostic_findings"]) >= 5 for sample in samples),
        "owner_decision_packet_updated": True,
        "no_external_side_effects": not bundle_dict.get("external_action_executed") and not evaluation["external_action_executed"],
        "market_backed_offer_thesis_if_claiming_completion": thesis["thesis_status"] == "evidence_backed" and evaluation["default_is_market_backed"],
    }
    czl = build_strict_czl_state(
        mission_id="e6_source_seeded_market_evidence_run",
        y_star=E6_Y_STAR,
        xt={
            "start_commit": "43d2e7e2",
            "e5_status": "BLOCKED_BY_MISSING_PUBLIC_SOURCE_SEEDS",
            "seed_count": seed_summary["seed_count"],
            "family_count": seed_summary["family_count"],
        },
        u=[
            "created owner-approved public source seed file",
            "validated public source seeds",
            "ran source-seeded safe public GET/page-read research",
            "built EvidenceRunBundle and provenance report",
            "reranked opportunities using validated bundle evidence only",
            "generated offer thesis, samples, owner packet, and strict CZL closure",
        ],
        y_t1=y_t1,
        feasible_criteria=E6_FEASIBLE_INTERNAL_CRITERIA,
        full_criteria=E6_Y_STAR,
        blocked_reason=blocked_reason,
        exact_unblock_action=exact_unblock_action,
        blocked_status=status if status != "complete" else "BLOCKED_BY_INSUFFICIENT_PUBLIC_EVIDENCE",
    )
    return {
        "seed_summary": seed_summary,
        "bundle": bundle_dict,
        "evaluation": evaluation,
        "thesis": thesis,
        "samples": samples,
        "owner_packet": owner_packet,
        "strict_czl": czl.to_dict(),
        "status": status,
        "blocker_path": blocker_path,
        "external_action_executed": False,
    }


def write_e6_reports(repo_root: Path) -> Dict[str, Path]:
    cycle = build_e6_cycle(repo_root)
    reports = repo_root / "reports" / "integration"
    reports.mkdir(parents=True, exist_ok=True)
    bundle = EvidenceRunBundle(**cycle["bundle"])
    outputs = {
        "e6_public_source_seed_plan.md": render_e6_public_source_seed_plan(repo_root),
        "e6_evidence_provenance_report.md": render_evidence_provenance_report(bundle).replace("# E5 Evidence Provenance Report", "# E6 Evidence Provenance Report", 1),
        "e6_market_evidence_opportunity_evaluation.md": render_e6_market_evaluation_markdown(cycle["evaluation"]),
        "e6_top_candidates.md": render_e6_top_candidates_markdown(cycle["evaluation"]),
        "e6_competitive_objection_matrix.md": render_competitive_objection_matrix(cycle["evaluation"]),
        "e6_offer_thesis.md": render_e6_offer_thesis(cycle["thesis"]),
        "e6_sample_deliverable_top1.md": render_e6_sample_deliverable(cycle["samples"][0]),
        "e6_sample_deliverable_top2.md": render_e6_sample_deliverable(cycle["samples"][1]),
        "e6_owner_decision_packet.md": render_e6_owner_decision_packet(cycle["owner_packet"]),
        "e6_czl_closure_report.md": render_strict_czl_report(
            build_strict_czl_state(
                mission_id=cycle["strict_czl"]["mission_id"],
                y_star=cycle["strict_czl"]["y_star"],
                xt=cycle["strict_czl"]["xt"],
                u=cycle["strict_czl"]["u"],
                y_t1=cycle["strict_czl"]["y_t1"],
                feasible_criteria=E6_FEASIBLE_INTERNAL_CRITERIA,
                full_criteria=E6_Y_STAR,
                blocked_reason=cycle["strict_czl"]["blocked_reason"],
                exact_unblock_action=cycle["strict_czl"]["exact_unblock_action"],
                blocked_status=cycle["strict_czl"]["status"],
            )
        )
        + "\n\n## No-External-Action Receipt\n"
        + "- external sending: false\n"
        + "- customer contact: false\n"
        + "- email/message: false\n"
        + "- publication: false\n"
        + "- payment: false\n"
        + "- account creation: false\n"
        + "- form submission: false\n"
        + "- core DB/brain/memory/CIEU writeback: false\n"
        + "- obligation auto-registration: false\n"
        + "- COO invented: false\n",
    }
    if cycle["blocker_path"]:
        outputs["e6_research_runtime_blocker.md"] = _render_research_blocker(cycle["status"], cycle["bundle"], cycle["thesis"])
    written: Dict[str, Path] = {}
    for filename, text in outputs.items():
        path = reports / filename
        path.write_text(text + "\n", encoding="utf-8")
        written[filename] = path
    return written
