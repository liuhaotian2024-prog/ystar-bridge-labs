#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from office.mission_command.e29_existing_revenue_branch_wheel_inventory import build_all


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


def create_e29(repo_root: Path, output_root: Path) -> List[str]:
    data = build_all(repo_root)
    json_outputs = {
        "operations/external_validation/e29_existing_revenue_branch_wheel_inventory.json": data["inventory"],
        "operations/external_validation/e29_revenue_branch_duplicate_conflict_map.json": data["duplicates"],
        "operations/external_validation/e29_reuse_wrap_extend_build_decision.json": data["reuse"],
        "operations/external_validation/e29_revenue_mode_branch_scoring.json": data["scoring"],
        "operations/external_validation/e29_branch_selection_confirmation_gate.json": data["gate"],
        "operations/external_validation/e29_branch_scoped_execution_route_activation.json": data["route"],
        "operations/external_validation/e29_multi_branch_portfolio_guardrail.json": data["guardrail"],
        "operations/external_validation/e29_ceo_brain_branch_update.json": data["brain"],
        "operations/external_validation/e29_branch_decision_control_room.json": data["control"],
        "operations/external_validation/e29_ecosystem_alignment_gate.json": data["alignment"],
        "operations/external_validation/e29_repo_modification_decision_packet.json": {
            "artifact_id": "e29_repo_modification_decision_packet",
            "bridge_labs_modified": True,
            "gov_mcp_modified": False,
            "Y_star_gov_modified": False,
            "ystar_company_modified": False,
            "modification_decision": "bridge_labs_only",
            "justification": "E29 is a CEO KG/commercial branch-selection layer above existing provider and governance wheels.",
            "external_action_executed": False,
        },
        "operations/external_validation/e29_future_revenue_branch_policy.json": data["policy"],
        "operations/external_validation/e29_czl_closure.json": data["closure"],
        "operations/knowledge_graph/e29_ceo_kg_branch_selection_feedback.json": {
            "artifact_id": "e29_ceo_kg_branch_selection_feedback",
            "active_branch": data["gate"]["active_branch"],
            "selected_route": data["route"]["selected_route"],
            "kg_delta_node_count": data["kg"]["kg_delta_node_count"],
            "kg_delta_edge_count": data["kg"]["kg_delta_edge_count"],
            "internal_strategy_evidence_only": True,
            "customer_feedback_claimed": False,
            "market_validation_claimed": False,
            "external_action_executed": False,
        },
        "operations/knowledge_graph/e29_ceo_kg_read_model_update.json": {
            "artifact_id": "e29_ceo_kg_read_model_update",
            "active_branch": data["gate"]["active_branch"],
            "selected_route": data["route"]["selected_route"],
            "backup_branch_count": data["gate"]["backup_branch_count"],
            "deferred_branch_count": data["gate"]["deferred_branch_count"],
            "blocked_branch_count": data["gate"]["blocked_branch_count"],
            "production_live_config_scope": data["route"]["production_live_config_recommendation_scope"],
            "next_decision_horizon": data["brain"]["next_decision_horizon"],
            "external_action_executed": False,
        },
        "operations/knowledge_graph/e29_ceo_kg_promotion_candidates_update.json": {
            "artifact_id": "e29_ceo_kg_promotion_candidates_update",
            "promotion_candidates_count": 1,
            "promotion_candidates": [
                {
                    "id": "e29_branch_selection_decision",
                    "promotion_status": "working_only",
                    "reason": "Branch confirmation is internal strategy evidence, not customer/market truth.",
                }
            ],
            "canonical_truth_promoted": False,
            "external_action_executed": False,
        },
    }
    for rel, payload in json_outputs.items():
        write_json(output_root / rel, payload)
    write_jsonl(output_root / "operations/knowledge_graph/e29_ceo_kg_nodes_delta.jsonl", data["kg"]["kg_delta_nodes"])
    write_jsonl(output_root / "operations/knowledge_graph/e29_ceo_kg_edges_delta.jsonl", data["kg"]["kg_delta_edges"])

    md_outputs = {
        "operations/external_validation/e29_branch_decision_control_room.md": md("E29 Branch Decision Control Room", [
            f"active_branch: {data['gate']['active_branch']}",
            f"selected_route: {data['route']['selected_route']}",
            f"production_live_config_scope: {data['route']['production_live_config_recommendation_scope']}",
            f"next_decision_horizon: {data['brain']['next_decision_horizon']}",
            "external_action_executed: false",
        ]),
        "reports/integration/e29_revenue_mode_branch_selection_confirmation.md": md("E29 Revenue Mode Branch Selection Confirmation", [
            f"selection_decision: {data['gate']['selection_decision']}",
            f"active_branch: {data['gate']['active_branch']}",
            f"selected_route: {data['route']['selected_route']}",
            f"kg_delta_nodes: {data['kg']['kg_delta_node_count']}",
            f"kg_delta_edges: {data['kg']['kg_delta_edge_count']}",
        ]),
        "reports/integration/e29_existing_revenue_branch_wheel_inventory.md": md("E29 Existing Revenue Branch Wheel Inventory", [
            f"repos_scanned: {data['inventory']['repos_scanned_count']}",
            f"wheels_found: {data['inventory']['existing_revenue_branch_wheels_found']}",
            f"reused: {data['inventory']['reused_wheels_count']}",
            f"wrapped_or_extended: {data['inventory']['wrapped_or_extended_wheels_count']}",
            f"newly_built: {data['inventory']['newly_built_wheels_count']}",
        ]),
        "reports/integration/e29_revenue_branch_duplicate_conflict_map.md": md("E29 Revenue Branch Duplicate Conflict Map", [
            f"duplicate_conflict_clusters: {data['duplicates']['duplicate_conflict_cluster_count']}",
            "destructive_refactor_performed: false",
        ]),
        "reports/integration/e29_reuse_wrap_extend_build_decision.md": md("E29 Reuse Wrap Extend Build Decision", [
            f"decisions: {len(data['reuse']['decisions'])}",
            f"newly_built_wheels_count: {data['reuse']['newly_built_wheels_count']}",
            f"all_new_wheels_justified: {data['reuse']['all_new_wheels_have_build_missing_or_extend_existing_justification']}",
        ]),
        "reports/integration/e29_revenue_mode_branch_scoring.md": md("E29 Revenue Mode Branch Scoring", [
            f"branch_count: {data['scoring']['branch_count']}",
            f"top_scored_branch: {data['scoring']['top_scored_branch']}",
            f"opaque_llm_judge_used: {data['scoring']['opaque_llm_judge_used']}",
        ]),
        "reports/integration/e29_branch_selection_confirmation_gate.md": md("E29 Branch Selection Confirmation Gate", [
            f"selection_decision: {data['gate']['selection_decision']}",
            f"active_branch: {data['gate']['active_branch']}",
            f"backup_branch_count: {data['gate']['backup_branch_count']}",
            f"deferred_branch_count: {data['gate']['deferred_branch_count']}",
            f"blocked_branch_count: {data['gate']['blocked_branch_count']}",
        ]),
        "reports/integration/e29_branch_scoped_execution_route_activation.md": md("E29 Branch Scoped Execution Route Activation", [
            f"selected_route: {data['route']['selected_route']}",
            f"production_live_config_recommended: {data['route']['production_live_config_recommended']}",
            f"production_live_config_global_default: {data['route']['production_live_config_global_default']}",
            f"canary_executed: {data['route']['canary_executed']}",
        ]),
        "reports/integration/e29_multi_branch_portfolio_guardrail.md": md("E29 Multi Branch Portfolio Guardrail", [
            f"active_branch: {data['guardrail']['active_branch']}",
            f"re_evaluation_triggers: {len(data['guardrail']['branch_re_evaluation_triggers'])}",
            f"route_alternatives_preserved: {len(data['guardrail']['route_alternatives_preserved'])}",
        ]),
        "reports/integration/e29_ceo_brain_branch_update.md": md("E29 CEO Brain Branch Update", [
            f"active_branch: {data['brain']['active_branch']}",
            f"selected_route: {data['brain']['selected_route']}",
            f"strategic_bottleneck: {data['brain']['strategic_bottleneck']}",
            f"next_decision_horizon: {data['brain']['next_decision_horizon']}",
        ]),
        "reports/integration/e29_branch_decision_control_room.md": md("E29 Branch Decision Control Room", [
            f"selected_active_branch: {data['control']['selected_active_branch']}",
            f"selected_branch_route: {data['control']['selected_branch_route']}",
            f"recommended_next_milestone: {data['control']['recommended_next_milestone']}",
        ]),
        "reports/integration/e29_ecosystem_alignment_gate.md": md("E29 Ecosystem Alignment Gate", [
            f"repos_checked: {data['alignment']['repos_checked_count']}",
            f"gov_mcp_modified: {data['alignment']['gov_mcp_modified']}",
            f"status: {data['alignment']['ecosystem_alignment_status']}",
        ]),
        "reports/integration/e29_future_revenue_branch_policy.md": md("E29 Future Revenue Branch Policy", [
            data["policy"]["policy"],
            f"required_steps: {len(data['policy']['required_before_route_assumption'])}",
            f"owner_manual_send_default_allowed: {data['policy']['owner_manual_send_default_allowed']}",
        ]),
        "reports/integration/e29_czl_closure.md": md("E29 CZL Closure", [
            f"Rt+1: {data['closure']['Rt_plus_1']}",
            f"whole_ecosystem_audited_first: {data['closure']['whole_ecosystem_existing_wheel_audited_first']}",
            f"production_live_enabled: {data['closure']['production_live_enabled']}",
            f"production_live_receipt_count: {data['closure']['production_live_receipt_count']}",
            f"no_external_action: {data['closure']['no_real_external_action_occurred']}",
        ]),
    }
    for rel, text in md_outputs.items():
        write_text(output_root / rel, text)
    files = sorted(
        list(json_outputs)
        + [
            "operations/knowledge_graph/e29_ceo_kg_nodes_delta.jsonl",
            "operations/knowledge_graph/e29_ceo_kg_edges_delta.jsonl",
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
    files = create_e29(Path(args.repo_root), Path(args.output_root))
    result = {"status": "created", "file_count": len(files), "files": files}
    print(json.dumps(result, indent=2) if args.json else f"created {len(files)} E29 files")


if __name__ == "__main__":
    main()
