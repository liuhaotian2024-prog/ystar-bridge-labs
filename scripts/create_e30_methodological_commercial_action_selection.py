#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from office.mission_command.e30_existing_method_wheel_inventory import build_all


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


def create_e30(repo_root: Path, output_root: Path) -> List[str]:
    data = build_all(repo_root)
    json_outputs = {
        "operations/external_validation/e30_existing_method_wheel_inventory.json": data["inventory"],
        "operations/external_validation/e30_system_state_reconstruction.json": data["state"],
        "operations/external_validation/e30_open_commercial_action_space.json": data["action_space"],
        "operations/external_validation/e30_action_objective_scores.json": data["scores"],
        "operations/external_validation/e30_action_falsification_analysis.json": data["falsification"],
        "operations/external_validation/e30_methodological_route_selection.json": data["selection"],
        "operations/external_validation/e30_selected_action_execution_package.json": data["package"],
        "operations/external_validation/e30_ceo_brain_methodological_update.json": data["brain"],
        "operations/external_validation/e30_methodological_action_control_room.json": data["control"],
        "operations/external_validation/e30_ecosystem_alignment_gate.json": data["alignment"],
        "operations/external_validation/e30_repo_modification_decision_packet.json": {
            "artifact_id": "e30_repo_modification_decision_packet",
            "modification_decision": "bridge_labs_only",
            "bridge_labs_modified": True,
            "gov_mcp_modified": False,
            "Y_star_gov_modified": False,
            "ystar_company_modified": False,
            "justification": "E30 is method-based commercial action selection above existing provider/governance wheels.",
            "external_action_executed": False,
        },
        "operations/external_validation/e30_future_methodological_action_policy.json": data["policy"],
        "operations/external_validation/e30_czl_closure.json": data["closure"],
        "operations/knowledge_graph/e30_ceo_kg_methodological_action_selection.json": {
            "artifact_id": "e30_ceo_kg_methodological_action_selection",
            "selected_route": data["selection"]["selected_route"],
            "selected_action_id": data["selection"]["selected_action_id"],
            "kg_delta_node_count": data["kg"]["kg_delta_node_count"],
            "kg_delta_edge_count": data["kg"]["kg_delta_edge_count"],
            "internal_strategy_evidence_only": True,
            "customer_feedback_claimed": False,
            "market_validation_claimed": False,
            "external_action_executed": False,
        },
        "operations/knowledge_graph/e30_ceo_kg_read_model_update.json": {
            "artifact_id": "e30_ceo_kg_read_model_update",
            "active_branch": data["brain"]["active_branch"],
            "selected_route": data["selection"]["selected_route"],
            "top_action_id": data["scores"]["top_action_id"],
            "candidate_action_count": data["action_space"]["candidate_action_count"],
            "next_decision_horizon": data["brain"]["next_decision_horizon"],
            "production_live_enabled": False,
            "production_live_receipt_count": 0,
            "external_action_executed": False,
        },
    }
    for rel, payload in json_outputs.items():
        write_json(output_root / rel, payload)
    write_jsonl(output_root / "operations/knowledge_graph/e30_ceo_kg_nodes_delta.jsonl", data["kg"]["kg_delta_nodes"])
    write_jsonl(output_root / "operations/knowledge_graph/e30_ceo_kg_edges_delta.jsonl", data["kg"]["kg_delta_edges"])

    markdown_specs = {
        "e30_existing_method_wheel_inventory": ["E30 Existing Method Wheel Inventory", [f"repos_scanned: {data['inventory']['repos_scanned_count']}", f"wheels_found: {data['inventory']['existing_method_wheels_found']}", f"reused: {data['inventory']['reused_wheels_count']}", f"wrapped: {data['inventory']['wrapped_wheels_count']}", f"newly_built: {data['inventory']['newly_built_wheels_count']}"]],
        "e30_system_state_reconstruction": ["E30 System State Reconstruction", [f"active_branch: {data['state']['current_active_branch']}", f"previous_route_candidate: {data['state']['previous_route_candidate']}", f"production_live_enabled: {data['state']['execution_capabilities']['production_live_enabled']}", f"underbuilt_action_heavy_areas: {len(data['state']['underbuilt_action_heavy_areas'])}"]],
        "e30_open_commercial_action_space": ["E30 Open Commercial Action Space", [f"candidate_action_count: {data['action_space']['candidate_action_count']}", f"generation_method: {data['action_space']['generation_method']}"]],
        "e30_action_objective_scores": ["E30 Action Objective Scores", [f"top_action_id: {data['scores']['top_action_id']}", f"scored_action_count: {data['scores']['scored_action_count']}", f"fake_progress_penalty_enabled: {data['scores']['fake_progress_penalty_enabled']}"]],
        "e30_action_falsification_analysis": ["E30 Action Falsification Analysis", [f"top_candidate_count: {data['falsification']['top_candidate_count']}", f"selected_survived: {data['falsification']['selected_candidate_survived_falsification']}", f"main_objection: {data['falsification']['main_objection_to_selected']}"]],
        "e30_methodological_route_selection": ["E30 Methodological Route Selection", [f"selected_route: {data['selection']['selected_route']}", f"selected_action_id: {data['selection']['selected_action_id']}", f"production_config_selected: {data['selection']['production_config_selected']}"]],
        "e30_selected_action_execution_package": ["E30 Selected Action Execution Package", [f"selected_route: {data['package']['selected_route']}", f"branch: {data['package']['branch']}", f"produced_outputs: {len(data['package']['produced_outputs_for_next_milestone'])}"]],
        "e30_ceo_brain_methodological_update": ["E30 CEO Brain Methodological Update", [f"selected_route: {data['brain']['selected_route']}", f"updated_bottleneck: {data['brain']['updated_bottleneck']}", f"next_decision_horizon: {data['brain']['next_decision_horizon']}"]],
        "e30_methodological_action_control_room": ["E30 Methodological Action Control Room", [f"selected_route: {data['control']['selected_route']}", f"generated_action_space_count: {data['control']['generated_action_space_count']}", f"recommended_next_milestone: {data['control']['recommended_next_milestone']}", f"real_external_action_occurred: {data['control']['real_external_action_occurred']}"]],
        "e30_ecosystem_alignment_gate": ["E30 Ecosystem Alignment Gate", [f"repos_checked: {data['alignment']['repos_checked_count']}", f"gov_mcp_modified: {data['alignment']['gov_mcp_modified']}", f"status: {data['alignment']['ecosystem_alignment_status']}"]],
        "e30_future_methodological_action_policy": ["E30 Future Methodological Action Policy", [data["policy"]["policy"], f"required_steps: {len(data['policy']['required_method_steps'])}", f"owner_manual_send_default_allowed: {data['policy']['owner_manual_send_default_allowed']}"]],
        "e30_czl_closure": ["E30 CZL Closure", [f"Rt+1: {data['closure']['Rt_plus_1']}", f"route_selected_by_method_not_hardcoded_menu: {data['closure']['route_selected_by_method_not_hardcoded_menu']}", f"production_live_enabled: {data['closure']['production_live_enabled']}", f"production_live_receipt_count: {data['closure']['production_live_receipt_count']}", f"no_external_action: {data['closure']['no_real_external_action_occurred']}"]],
    }
    md_outputs: Dict[str, str] = {}
    for stem, (title, bullets) in markdown_specs.items():
        md_outputs[f"reports/integration/{stem}.md"] = md(title, bullets)
    md_outputs["operations/external_validation/e30_methodological_action_control_room.md"] = md_outputs["reports/integration/e30_methodological_action_control_room.md"]
    md_outputs["operations/external_validation/e30_czl_closure.md"] = md_outputs["reports/integration/e30_czl_closure.md"]
    for rel, text in md_outputs.items():
        write_text(output_root / rel, text)
    files = sorted(list(json_outputs) + ["operations/knowledge_graph/e30_ceo_kg_nodes_delta.jsonl", "operations/knowledge_graph/e30_ceo_kg_edges_delta.jsonl"] + list(md_outputs))
    return files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    files = create_e30(Path(args.repo_root), Path(args.output_root))
    result = {"status": "created", "file_count": len(files), "files": files}
    print(json.dumps(result, indent=2) if args.json else f"created {len(files)} E30 files")


if __name__ == "__main__":
    main()
