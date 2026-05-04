#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from office.mission_command.e28_existing_production_live_wheel_inventory import build_all


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def md(title: str, bullets: Iterable[str]) -> str:
    return "# " + title + "\n\n" + "\n".join(f"- {bullet}" for bullet in bullets) + "\n"


def create_e28(repo_root: Path, output_root: Path) -> List[str]:
    data = build_all(repo_root)
    json_outputs = {
        "operations/external_validation/e28_existing_production_live_wheel_inventory.json": data["inventory"],
        "operations/external_validation/e28_production_live_duplicate_conflict_map.json": data["conflicts"],
        "operations/external_validation/e28_reuse_wrap_extend_build_decision.json": data["reuse"],
        "operations/external_validation/e28_production_live_decision_gate.json": data["decision"],
        "operations/external_validation/e28_provider_category_comparison.json": data["provider"],
        "operations/external_validation/e28_secure_credential_source_contract.json": data["credentials"],
        "operations/external_validation/e28_production_live_blocker_matrix.json": data["blockers"],
        "operations/external_validation/e28_evidence_vs_live_tradeoff.json": data["tradeoff"],
        "operations/external_validation/e28_canary_prerequisite_refinement.json": data["canary"],
        "operations/external_validation/e28_ceo_brain_portfolio_update.json": data["brain"],
        "operations/external_validation/e28_decision_control_room.json": data["control"],
        "operations/external_validation/e28_ecosystem_alignment_gate.json": data["alignment"],
        "operations/external_validation/e28_repo_modification_decision_packet.json": data["repo_decision"],
        "operations/external_validation/e28_future_production_live_policy.json": data["future_policy"],
        "operations/external_validation/e28_czl_closure.json": data["closure"],
        "operations/knowledge_graph/e28_ceo_kg_production_live_feedback.json": data["feedback"],
        "operations/knowledge_graph/e28_ceo_kg_read_model_update.json": {
            "artifact_id": "e28_ceo_kg_read_model_update",
            "selected_revenue_path": data["decision"]["selected_revenue_path"],
            "production_live_decision": data["decision"]["decision"],
            "selected_provider_category": data["provider"]["selected_provider_category"],
            "production_live_ready": data["blockers"]["production_live_ready"],
            "production_live_blocked_reasons": data["blockers"]["primary_blockers"],
            "current_strategic_bottleneck": data["brain"]["current_strategic_bottleneck"],
            "external_action_executed": False,
        },
        "operations/knowledge_graph/e28_ceo_kg_promotion_candidates_update.json": {
            "artifact_id": "e28_ceo_kg_promotion_candidates_update",
            "promotion_candidates_count": data["feedback"]["promotion_candidates_count"],
            "promotion_candidates": data["feedback"]["promotion_candidates"],
            "canonical_truth_promoted": False,
            "external_action_executed": False,
        },
    }
    for rel, payload in json_outputs.items():
        write_json(output_root / rel, payload)
    write_jsonl(output_root / "operations/knowledge_graph/e28_ceo_kg_nodes_delta.jsonl", data["feedback"]["kg_delta_nodes"])
    write_jsonl(output_root / "operations/knowledge_graph/e28_ceo_kg_edges_delta.jsonl", data["feedback"]["kg_delta_edges"])
    md_outputs = {
        "operations/external_validation/e28_decision_control_room.md": md("E28 Decision Control Room", [
            f"recommended_route: {data['decision']['recommended_route']}",
            f"provider_category: {data['provider']['selected_provider_category']}",
            f"production_live_ready: {data['blockers']['production_live_ready']}",
            f"production_live_receipt_count: {data['blockers']['production_live_receipt_count']}",
            "external_action_executed: false",
        ]),
        "reports/integration/e28_production_live_configuration_decision_gate.md": md("E28 Production Live Configuration Decision Gate", [
            f"decision: {data['decision']['decision']}",
            f"production_config_preparation_recommended: {data['decision']['production_live_config_preparation_recommended']}",
            f"evidence_expansion_recommended: {data['decision']['evidence_expansion_recommended']}",
        ]),
        "reports/integration/e28_existing_production_live_wheel_inventory.md": md("E28 Existing Production Live Wheel Inventory", [
            f"repos_scanned: {data['inventory']['repos_scanned_count']}",
            f"wheels_found: {data['inventory']['existing_production_live_wheels_found']}",
            f"reused: {data['inventory']['reused_wheels_count']}",
            f"wrapped_or_extended: {data['inventory']['wrapped_or_extended_wheels_count']}",
            f"newly_built: {data['inventory']['newly_built_wheels_count']}",
        ]),
        "reports/integration/e28_production_live_duplicate_conflict_map.md": md("E28 Production Live Duplicate Conflict Map", [
            f"cluster_count: {data['conflicts']['cluster_count']}",
            f"destructive_refactor_performed: {data['conflicts']['destructive_refactor_performed']}",
        ]),
        "reports/integration/e28_reuse_wrap_extend_build_decision.md": md("E28 Reuse Wrap Extend Build Decision", [
            f"decisions: {len(data['reuse']['decisions'])}",
            f"all_new_wheels_have_justification: {data['reuse']['all_new_wheels_have_justification']}",
            f"gov_mcp_modification_needed: {data['reuse']['gov_mcp_modification_needed']}",
        ]),
        "reports/integration/e28_provider_category_comparison.md": md("E28 Provider Category Comparison", [
            f"selected_provider_category: {data['provider']['selected_provider_category']}",
            f"provider_uncertainty: {data['provider']['provider_uncertainty']}",
            f"provider_selection_research_needed: {data['provider']['provider_selection_research_needed']}",
        ]),
        "reports/integration/e28_secure_credential_source_contract.md": md("E28 Secure Credential Source Contract", [
            f"config_contract_ready: {data['credentials']['config_contract_ready']}",
            f"credentials_committed: {data['credentials']['credentials_committed']}",
            f"production_credentials_configured: {data['credentials']['production_credentials_configured']}",
        ]),
        "reports/integration/e28_production_live_blocker_matrix.md": md("E28 Production Live Blocker Matrix", [
            f"production_live_ready: {data['blockers']['production_live_ready']}",
            f"production_live_enabled: {data['blockers']['production_live_enabled']}",
            f"production_live_receipt_count: {data['blockers']['production_live_receipt_count']}",
            f"primary_blockers: {', '.join(data['blockers']['primary_blockers'])}",
        ]),
        "reports/integration/e28_evidence_vs_live_tradeoff.md": md("E28 Evidence Vs Live Tradeoff", [
            f"recommended_route: {data['tradeoff']['recommended_route']}",
            f"backup_route: {data['tradeoff']['backup_route']}",
            f"provider_selection_research_needed: {data['tradeoff']['provider_selection_research_needed']}",
        ]),
        "reports/integration/e28_canary_prerequisite_refinement.md": md("E28 Canary Prerequisite Refinement", [
            f"canary_prerequisite_refined: {data['canary']['canary_prerequisite_refined']}",
            f"canary_executed: {data['canary']['canary_executed']}",
            f"live_ready_action_count: {data['canary']['live_ready_action_count']}",
            f"live_blocked_action_count: {data['canary']['live_blocked_action_count']}",
        ]),
        "reports/integration/e28_ceo_kg_production_live_feedback.md": md("E28 CEO KG Production Live Feedback", [
            f"kg_delta_nodes: {data['feedback']['kg_delta_node_count']}",
            f"kg_delta_edges: {data['feedback']['kg_delta_edge_count']}",
            f"market_validation_claimed: {data['feedback']['market_validation_claimed']}",
        ]),
        "reports/integration/e28_ceo_brain_portfolio_update.md": md("E28 CEO Brain Portfolio Update", [
            f"selected_revenue_path: {data['brain']['selected_revenue_path']}",
            f"strategic_bottleneck: {data['brain']['current_strategic_bottleneck']}",
            f"next_decision_horizon: {data['brain']['next_decision_horizon']}",
        ]),
        "reports/integration/e28_ecosystem_alignment_gate.md": md("E28 Ecosystem Alignment Gate", [
            f"repos_checked: {data['alignment']['repos_checked_count']}",
            f"gov_mcp_modified: {data['alignment']['gov_mcp_modified']}",
            f"closure_status: {data['alignment']['closure_status']}",
        ]),
        "reports/integration/e28_future_production_live_policy.md": md("E28 Future Production Live Policy", [
            f"start_requirements: {len(data['future_policy']['every_future_production_live_milestone_must_start_with'])}",
            f"future_requirements: {len(data['future_policy']['future_production_live_configuration_or_canary_requirements'])}",
        ]),
        "reports/integration/e28_czl_closure.md": md("E28 CZL Closure", [
            f"Rt+1: {data['closure']['Rt_plus_1']}",
            f"no_real_external_action_occurred: {data['closure']['no_real_external_action_occurred']}",
            f"production_live_receipt_count: {data['closure']['production_live_receipt_count']}",
            f"production_live_mode_not_enabled: {data['closure']['production_live_mode_not_enabled']}",
        ]),
    }
    for rel, text in md_outputs.items():
        write_text(output_root / rel, text)
    files = sorted(
        list(json_outputs)
        + [
            "operations/knowledge_graph/e28_ceo_kg_nodes_delta.jsonl",
            "operations/knowledge_graph/e28_ceo_kg_edges_delta.jsonl",
        ]
        + list(md_outputs)
    )
    return files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    files = create_e28(Path(args.repo_root), Path(args.output_root))
    result = {"status": "created", "file_count": len(files), "files": files}
    print(json.dumps(result, indent=2) if args.json else f"created {len(files)} E28 files")


if __name__ == "__main__":
    main()
