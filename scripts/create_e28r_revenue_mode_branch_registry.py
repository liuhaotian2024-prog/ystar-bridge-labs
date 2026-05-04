#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from office.mission_command.e28r_existing_revenue_mode_wheel_inventory import build_all


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


def create_e28r(repo_root: Path, output_root: Path) -> List[str]:
    data = build_all(repo_root)
    json_outputs = {
        "operations/external_validation/e28r_existing_revenue_mode_wheel_inventory.json": data["inventory"],
        "operations/external_validation/e28r_hardcoding_assumption_audit.json": data["audit"],
        "operations/external_validation/e28r_reuse_wrap_build_decision.json": data["reuse"],
        "operations/external_validation/e28r_revenue_mode_branch_registry.json": data["registry"],
        "operations/external_validation/e28r_portfolio_reselection_gate.json": data["gate"],
        "operations/external_validation/e28r_route_decision.json": data["route"],
        "operations/external_validation/e28r_ceo_brain_branch_update.json": data["brain"],
        "operations/external_validation/e28r_future_revenue_mode_policy.json": data["policy"],
        "operations/external_validation/e28r_ecosystem_alignment_gate.json": data["alignment"],
        "operations/external_validation/e28r_control_room.json": data["control"],
        "operations/external_validation/e28r_czl_closure.json": data["closure"],
        "operations/knowledge_graph/e28r_ceo_kg_branch_feedback.json": data["feedback"],
        "operations/knowledge_graph/e28r_ceo_kg_read_model_update.json": {
            "artifact_id": "e28r_ceo_kg_read_model_update",
            "selected_active_branch": data["gate"]["selected_active_branch"],
            "production_live_configuration_global_default": False,
            "production_live_configuration_recommendation_scope": data["gate"]["production_live_recommendation_scope"],
            "next_decision_horizon": data["brain"]["next_decision_horizon"],
            "external_action_executed": False,
        },
        "operations/knowledge_graph/e28r_ceo_kg_promotion_candidates_update.json": {
            "artifact_id": "e28r_ceo_kg_promotion_candidates_update",
            "promotion_candidates_count": 1,
            "promotion_candidates": [{"id": "e28r_branch_selection_policy", "promotion_status": "working_only", "reason": "Future milestones must select revenue mode before assuming route."}],
            "canonical_truth_promoted": False,
            "external_action_executed": False,
        },
    }
    for rel, payload in json_outputs.items():
        write_json(output_root / rel, payload)
    write_jsonl(output_root / "operations/knowledge_graph/e28r_ceo_kg_nodes_delta.jsonl", data["feedback"]["kg_delta_nodes"])
    write_jsonl(output_root / "operations/knowledge_graph/e28r_ceo_kg_edges_delta.jsonl", data["feedback"]["kg_delta_edges"])
    md_outputs = {
        "operations/external_validation/e28r_control_room.md": md("E28R Control Room", [
            f"branch_count: {data['registry']['branch_count']}",
            f"selected_active_branch: {data['gate']['selected_active_branch']}",
            f"production_live_global_default: {data['gate']['production_live_configuration_global_default']}",
            f"next_decision_horizon: {data['brain']['next_decision_horizon']}",
        ]),
        "reports/integration/e28r_revenue_mode_branch_registry.md": md("E28R Revenue Mode Branch Registry", [
            f"branch_count: {data['registry']['branch_count']}",
            f"active_branch: {data['registry']['active_branch']}",
            f"backup_branches: {len(data['registry']['backup_branches'])}",
        ]),
        "reports/integration/e28r_hardcoding_assumption_audit.md": md("E28R Hardcoding Assumption Audit", [
            f"findings: {data['audit']['hardcoded_or_overweighted_assumption_count']}",
            f"production_live_config_global_default_corrected: {data['audit']['production_live_config_global_default_corrected']}",
        ]),
        "reports/integration/e28r_existing_revenue_mode_wheel_inventory.md": md("E28R Existing Revenue Mode Wheel Inventory", [
            f"repos_scanned: {data['inventory']['repos_scanned_count']}",
            f"wheels_found: {data['inventory']['existing_revenue_mode_wheels_found']}",
            f"reused: {data['inventory']['reused_wheels_count']}",
            f"wrapped: {data['inventory']['wrapped_wheels_count']}",
            f"newly_built: {data['inventory']['newly_built_wheels_count']}",
        ]),
        "reports/integration/e28r_reuse_wrap_build_decision.md": md("E28R Reuse Wrap Build Decision", [
            f"decisions: {len(data['reuse']['decisions'])}",
            f"newly_built_wheels_count: {data['reuse']['newly_built_wheels_count']}",
            f"all_new_wheels_have_justification: {data['reuse']['all_new_wheels_have_justification']}",
        ]),
        "reports/integration/e28r_portfolio_reselection_gate.md": md("E28R Portfolio Reselection Gate", [
            f"gate_result: {data['gate']['gate_result']}",
            f"selected_active_branch: {data['gate']['selected_active_branch']}",
            f"production_live_scope: {data['gate']['production_live_recommendation_scope']}",
        ]),
        "reports/integration/e28r_route_decision.md": md("E28R Route Decision", [
            f"route_decision: {data['route']['route_decision']}",
            f"recommended_next_milestone: {data['route']['recommended_next_milestone']}",
            f"production_live_global_default: {data['route']['production_live_configuration_global_default']}",
        ]),
        "reports/integration/e28r_ceo_kg_branch_feedback.md": md("E28R CEO KG Branch Feedback", [
            f"kg_delta_nodes: {data['feedback']['kg_delta_node_count']}",
            f"kg_delta_edges: {data['feedback']['kg_delta_edge_count']}",
            f"market_validation_claimed: {data['feedback']['market_validation_claimed']}",
        ]),
        "reports/integration/e28r_ceo_brain_branch_update.md": md("E28R CEO Brain Branch Update", [
            f"selected_active_branch: {data['brain']['selected_active_branch']}",
            f"backup_branches: {len(data['brain']['backup_branches'])}",
            f"next_decision_horizon: {data['brain']['next_decision_horizon']}",
        ]),
        "reports/integration/e28r_future_revenue_mode_policy.md": md("E28R Future Revenue Mode Policy", [
            data["policy"]["policy"],
            f"required_steps: {len(data['policy']['required_before_route_assumption'])}",
        ]),
        "reports/integration/e28r_ecosystem_alignment_gate.md": md("E28R Ecosystem Alignment Gate", [
            f"repos_checked: {data['alignment']['repos_checked_count']}",
            f"gov_mcp_modified: {data['alignment']['gov_mcp_modified']}",
            f"status: {data['alignment']['ecosystem_alignment_status']}",
        ]),
        "reports/integration/e28r_czl_closure.md": md("E28R CZL Closure", [
            f"Rt+1: {data['closure']['Rt_plus_1']}",
            f"e28_not_undone: {data['closure']['e28_not_undone']}",
            f"no_external_action: {data['closure']['no_real_external_action_occurred']}",
        ]),
    }
    for rel, text in md_outputs.items():
        write_text(output_root / rel, text)
    files = sorted(
        list(json_outputs)
        + [
            "operations/knowledge_graph/e28r_ceo_kg_nodes_delta.jsonl",
            "operations/knowledge_graph/e28r_ceo_kg_edges_delta.jsonl",
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
    files = create_e28r(Path(args.repo_root), Path(args.output_root))
    result = {"status": "created", "file_count": len(files), "files": files}
    print(json.dumps(result, indent=2) if args.json else f"created {len(files)} E28R files")


if __name__ == "__main__":
    main()
