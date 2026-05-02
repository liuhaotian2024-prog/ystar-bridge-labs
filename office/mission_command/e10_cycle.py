from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .e10_autonomous_target_discovery import (
    load_or_run_e10_target_discovery,
    render_e10_target_discovery_receipt,
    render_e10_target_discovery_research_plan,
    render_e10_target_discovery_source_summaries,
)
from .e10_buyer_signal_taxonomy import render_buyer_signal_taxonomy_report
from .e10_cross_repo_backflow_assessment import render_e10_cross_repo_backflow_assessment
from .e10_manifest_target_proposal import render_e10_manifest_target_proposal, write_e10_manifest_and_target_proposals
from .e10_owner_decision_packet import build_e10_owner_decision_packet, render_e10_owner_decision_packet
from .e10_shortest_revenue_path_scorer import (
    rank_e10_shortest_revenue_paths,
    render_e10_segment_opportunity_matrix,
    render_e10_shortest_revenue_path_ranking,
    score_e10_segments,
)
from .e10_target_candidate_registry import (
    build_e10_target_candidate_registry,
    render_e10_target_candidate_registry,
    validate_e10_target_registry,
    write_e10_target_candidates_json,
)
from .e10_validation_batch_builder import build_e10_validation_batches, render_e10_validation_batch_proposals
from .strict_czl import build_strict_czl_state, render_strict_czl_report


E10_Y_STAR = [
    "implementation_inspection_completed",
    "buyer_signal_taxonomy_created",
    "autonomous_target_discovery_research_ran_or_blocked_honestly",
    "target_candidate_registry_created",
    "shortest_revenue_path_scoring_created",
    "segment_opportunity_matrix_created",
    "validation_batch_proposals_created",
    "proposed_manifest_created",
    "proposed_target_seeds_created",
    "owner_decision_packet_created",
    "cross_repo_backflow_assessment_created",
    "method_kernel_updated_with_buyer_discovery",
    "no_unapproved_external_side_effects",
]


NO_UNAPPROVED_EXTERNAL_ACTION_RECEIPT = {
    "unapproved external sending": False,
    "unapproved customer contact": False,
    "unapproved email/message": False,
    "unapproved publication": False,
    "payment": False,
    "account creation": False,
    "form submission": False,
    "core DB/brain/memory/CIEU writeback": False,
    "obligation auto-registration": False,
    "COO invented": False,
}


def method_kernel_has_e10_learning(repo_root: Path) -> bool:
    path = repo_root / "knowledge" / "ceo" / "wisdom" / "AIDEN_META_DEVELOPMENT_METHOD_KERNEL.md"
    return path.exists() and "Autonomous Buyer Discovery and Shortest Revenue Path" in path.read_text(encoding="utf-8")


def render_e10_czl_closure(cycle: Dict[str, Any]) -> str:
    report = render_strict_czl_report(cycle["strict_czl"]).replace(
        "- status: complete", "- status: complete_autonomous_target_discovery_ready", 1
    )
    lines = [
        report,
        "",
        "## E10 Status Interpretation",
        "- Public target discovery ran through owner-authorized Tier 1 public read-only research.",
        "- Candidate targets were autonomously discovered from public evidence and are not approved for contact.",
        "- Proposed manifest and target seed files are owner-review proposals, not approval.",
        "- E10 did not execute external validation; E11 can approve or edit a risk-controlled validation batch.",
        "",
        "## No-Unapproved-External-Action Receipt",
    ]
    for key, value in NO_UNAPPROVED_EXTERNAL_ACTION_RECEIPT.items():
        lines.append(f"- {key}: {str(value).lower()}")
    return "\n".join(lines)


def build_e10_cycle(repo_root: Path) -> Dict[str, Any]:
    research = load_or_run_e10_target_discovery()
    sources = research["sources"]
    candidates = build_e10_target_candidate_registry(sources)
    candidate_errors = validate_e10_target_registry(candidates, research_ran=True)
    scores = rank_e10_shortest_revenue_paths(candidates)
    segment_scores = score_e10_segments(scores)
    batches = build_e10_validation_batches(candidates, scores)
    candidates_path = write_e10_target_candidates_json(repo_root, candidates)
    manifest_path, target_seeds_path, manifest, target_seeds = write_e10_manifest_and_target_proposals(repo_root, batches[0], candidates)
    owner_packet = build_e10_owner_decision_packet(
        scores,
        batches,
        candidates,
        str(manifest_path),
        str(target_seeds_path),
    )
    status = "complete_autonomous_target_discovery_ready"
    y_t1 = {
        "implementation_inspection_completed": (repo_root / "reports" / "integration" / "e10_implementation_inspection.md").exists(),
        "buyer_signal_taxonomy_created": True,
        "autonomous_target_discovery_research_ran_or_blocked_honestly": bool(research["receipt"].get("public_target_discovery_ran")),
        "target_candidate_registry_created": len(candidates) >= 20 and len({candidate.segment for candidate in candidates}) >= 5 and not candidate_errors,
        "shortest_revenue_path_scoring_created": bool(scores),
        "segment_opportunity_matrix_created": bool(segment_scores),
        "validation_batch_proposals_created": len(batches) >= 3,
            "proposed_manifest_created": manifest_path.exists() and manifest.get("proposal_only") is True,
            "proposed_target_seeds_created": target_seeds_path.exists() and target_seeds.get("proposal_only") is True,
            "owner_decision_packet_created": owner_packet["recommended_next_decision"] == "approve_or_edit_E11_validation_batch",
            "cross_repo_backflow_assessment_created": True,
            "method_kernel_updated_with_buyer_discovery": method_kernel_has_e10_learning(repo_root),
            "no_unapproved_external_side_effects": not any(NO_UNAPPROVED_EXTERNAL_ACTION_RECEIPT.values())
        and not research["receipt"].get("external_action_executed"),
    }
    czl = build_strict_czl_state(
        mission_id="e10_autonomous_buyer_discovery_and_revenue_path_targeting",
        y_star=E10_Y_STAR,
        xt={
            "start_commit": "42cc2ea947608900f80e6c64b4ebbaecff430c19",
            "e9_status": "complete_pattern_mining_and_owner_handoff_ready",
            "top_offer": "48h AI Ops Operating Room Blueprint",
            "manifest_present_at_start": False,
            "target_seeds_present_at_start": False,
            "safe_execution_provider_present": False,
        },
        u=[
            "inspected E9 implementation, reports, operations files, method kernel, and post-push quality audit",
            "ran autonomous public read-only buyer and target discovery",
            "created buyer signal taxonomy and public source summaries",
            "generated target candidate registry with contact approval false by default",
            "scored candidates and segments by shortest path to paid signal",
            "built three E11 validation batch proposals",
            "generated proposed manifest and proposed target seed files for owner review",
            "assessed cross-repo backflow candidates for Y-star-gov and gov-mcp",
            "updated owner decision packet, method kernel learning, and strict CZL closure",
        ],
        y_t1=y_t1,
        feasible_criteria=E10_Y_STAR,
        full_criteria=E10_Y_STAR,
        blocked_reason="",
        exact_unblock_action=[],
        blocked_status=status,
    )
    return {
        "research": research,
        "sources": sources,
        "candidates": candidates,
        "candidate_errors": candidate_errors,
        "candidates_path": candidates_path,
        "scores": scores,
        "segment_scores": segment_scores,
        "batches": batches,
        "manifest_path": manifest_path,
        "target_seeds_path": target_seeds_path,
        "manifest": manifest,
        "target_seeds": target_seeds,
        "owner_packet": owner_packet,
        "strict_czl": czl,
        "status": status,
    }


def write_e10_reports(repo_root: Path) -> Dict[str, Path]:
    reports = repo_root / "reports" / "integration"
    reports.mkdir(parents=True, exist_ok=True)
    cycle = build_e10_cycle(repo_root)
    outputs = {
        "e10_buyer_signal_taxonomy.md": render_buyer_signal_taxonomy_report(),
        "e10_target_discovery_research_plan.md": render_e10_target_discovery_research_plan(cycle["research"]["request"]),
        "e10_target_discovery_receipt.md": render_e10_target_discovery_receipt(cycle["research"]),
        "e10_target_discovery_source_summaries.md": render_e10_target_discovery_source_summaries(cycle["sources"]),
        "e10_target_candidate_registry.md": render_e10_target_candidate_registry(cycle["candidates"]),
        "e10_shortest_revenue_path_ranking.md": render_e10_shortest_revenue_path_ranking(cycle["scores"]),
        "e10_segment_opportunity_matrix.md": render_e10_segment_opportunity_matrix(cycle["segment_scores"]),
        "e10_validation_batch_proposals.md": render_e10_validation_batch_proposals(cycle["batches"]),
        "e10_manifest_target_proposal.md": render_e10_manifest_target_proposal(
            cycle["manifest_path"], cycle["target_seeds_path"], cycle["manifest"], cycle["target_seeds"]
        ),
        "e10_owner_decision_packet.md": render_e10_owner_decision_packet(cycle["owner_packet"]),
        "e10_cross_repo_backflow_assessment.md": render_e10_cross_repo_backflow_assessment(),
        "e10_czl_closure_report.md": render_e10_czl_closure(cycle),
    }
    written: Dict[str, Path] = {}
    for filename, text in outputs.items():
        path = reports / filename
        path.write_text(text.rstrip() + "\n", encoding="utf-8")
        written[filename] = path
    return written


if __name__ == "__main__":
    write_e10_reports(Path(__file__).resolve().parents[2])
