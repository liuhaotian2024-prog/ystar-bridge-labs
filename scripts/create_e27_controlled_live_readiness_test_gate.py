#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from office.mission_command.e27_existing_live_test_wheel_inventory import build_all


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


def create_e27(repo_root: Path, output_root: Path) -> List[str]:
    data = build_all(repo_root)
    json_outputs = {
        "operations/external_validation/e27_existing_live_test_wheel_inventory.json": data["inventory"],
        "operations/external_validation/e27_live_test_duplicate_conflict_map.json": data["conflicts"],
        "operations/external_validation/e27_reuse_wrap_extend_build_decision.json": data["decision"],
        "operations/external_validation/e27_live_test_config_sync.json": data["config"],
        "operations/external_validation/e27_persistent_idempotency_test_gate.json": data["idempotency"],
        "operations/external_validation/e27_kill_switch_live_test_gate.json": data["kill_switch"],
        "operations/external_validation/e27_receipt_boundary_live_test_gate.json": data["receipt_boundary"],
        "operations/external_validation/e27_live_readiness_validator_v2.json": data["validator"],
        "operations/external_validation/e27_canary_prerequisite_matrix.json": data["canary"],
        "operations/external_validation/e27_ceo_brain_portfolio_update.json": data["brain"],
        "operations/external_validation/e27_live_test_control_room.json": data["control"],
        "operations/external_validation/e27_ecosystem_alignment_gate.json": data["alignment"],
        "operations/external_validation/e27_repo_modification_decision_packet.json": data["repo_decision"],
        "operations/external_validation/e27_future_live_test_canary_policy.json": data["future_policy"],
        "operations/external_validation/e27_czl_closure.json": data["closure"],
        "operations/knowledge_graph/e27_ceo_kg_live_test_feedback.json": data["feedback"],
        "operations/knowledge_graph/e27_ceo_kg_read_model_update.json": {
            "artifact_id": "e27_ceo_kg_read_model_update",
            "selected_revenue_path": data["brain"]["selected_revenue_path"],
            "live_test_gate_ready": data["validator"]["live_test_gate_ready"],
            "production_live_ready": data["validator"]["production_live_ready"],
            "production_live_blocked_reasons": data["validator"]["production_live_blocked_reasons"],
            "current_strategic_bottleneck": data["brain"]["current_strategic_bottleneck"],
            "external_action_executed": False,
        },
        "operations/knowledge_graph/e27_ceo_kg_promotion_candidates_update.json": {
            "artifact_id": "e27_ceo_kg_promotion_candidates_update",
            "promotion_candidates_count": data["feedback"]["promotion_candidates_count"],
            "promotion_candidates": data["feedback"]["promotion_candidates"],
            "canonical_truth_promoted": False,
            "external_action_executed": False,
        },
    }
    for rel, payload in json_outputs.items():
        write_json(output_root / rel, payload)
    write_jsonl(output_root / "operations/knowledge_graph/e27_ceo_kg_nodes_delta.jsonl", data["feedback"]["kg_delta_nodes"])
    write_jsonl(output_root / "operations/knowledge_graph/e27_ceo_kg_edges_delta.jsonl", data["feedback"]["kg_delta_edges"])

    md_outputs = {
        "operations/external_validation/e27_live_test_control_room.md": md("E27 Live Test Control Room", [
            f"existing_wheels_found: {data['inventory']['existing_live_test_wheels_found']}",
            f"live_test_gate_ready: {data['validator']['live_test_gate_ready']}",
            f"production_live_ready: {data['validator']['production_live_ready']}",
            f"canary_executed: {data['canary']['canary_executed']}",
            "external_action_executed: false",
        ]),
        "reports/integration/e27_controlled_live_readiness_test_gate.md": md("E27 Controlled Live Readiness Test Gate", [
            "Added a non-production live-test gate without enabling production live execution.",
            "Kept owner manual send out of the default route.",
            "Updated CEO KG with internal readiness evidence only.",
        ]),
        "reports/integration/e27_existing_live_test_wheel_inventory.md": md("E27 Existing Live Test Wheel Inventory", [
            f"repos_scanned: {data['inventory']['repos_scanned_count']}",
            f"wheels_found: {data['inventory']['existing_live_test_wheels_found']}",
            f"reused: {data['inventory']['reused_wheels_count']}",
            f"wrapped_or_extended: {data['inventory']['wrapped_or_extended_wheels_count']}",
            f"newly_built: {data['inventory']['newly_built_wheels_count']}",
        ]),
        "reports/integration/e27_live_test_duplicate_conflict_map.md": md("E27 Live Test Duplicate Conflict Map", [
            f"cluster_count: {data['conflicts']['cluster_count']}",
            f"destructive_refactor_performed: {data['conflicts']['destructive_refactor_performed']}",
        ]),
        "reports/integration/e27_reuse_wrap_extend_build_decision.md": md("E27 Reuse Wrap Extend Build Decision", [
            f"decisions: {len(data['decision']['decisions'])}",
            f"all_new_wheels_have_justification: {data['decision']['all_new_wheels_have_justification']}",
        ]),
        "reports/integration/e27_live_test_config_sync.md": md("E27 Live Test Config Sync", [
            f"live_test_config_ready: {data['config']['live_test_config_ready']}",
            f"production_live_config_ready: {data['config']['production_live_config_ready']}",
            f"credentials_committed: {data['config']['credentials_committed']}",
        ]),
        "reports/integration/e27_persistent_idempotency_test_gate.md": md("E27 Persistent Idempotency Test Gate", [
            f"live_test_persistent_ready: {data['idempotency']['live_test_persistent_ready']}",
            f"production_persistent_ready: {data['idempotency']['production_persistent_ready']}",
            f"store_type: {data['idempotency']['store_type']}",
        ]),
        "reports/integration/e27_live_readiness_validator_v2.md": md("E27 Live Readiness Validator V2", [
            f"dry_run_ready: {data['validator']['dry_run_ready']}",
            f"sandbox_ready: {data['validator']['sandbox_ready']}",
            f"live_test_gate_ready: {data['validator']['live_test_gate_ready']}",
            f"production_live_ready: {data['validator']['production_live_ready']}",
            f"production_blockers: {', '.join(data['validator']['production_live_blocked_reasons'])}",
        ]),
        "reports/integration/e27_canary_prerequisite_matrix.md": md("E27 Canary Prerequisite Matrix", [
            f"canary_matrix_created: {data['canary']['canary_matrix_created']}",
            f"canary_executed: {data['canary']['canary_executed']}",
            f"live_ready_action_count: {data['canary']['live_ready_action_count']}",
            f"live_blocked_action_count: {data['canary']['live_blocked_action_count']}",
        ]),
        "reports/integration/e27_ceo_kg_live_test_feedback.md": md("E27 CEO KG Live Test Feedback", [
            f"kg_delta_nodes: {data['feedback']['kg_delta_node_count']}",
            f"kg_delta_edges: {data['feedback']['kg_delta_edge_count']}",
            f"market_validation_claimed: {data['feedback']['market_validation_claimed']}",
        ]),
        "reports/integration/e27_ceo_brain_portfolio_update.md": md("E27 CEO Brain Portfolio Update", [
            f"selected_revenue_path: {data['brain']['selected_revenue_path']}",
            f"strategic_bottleneck: {data['brain']['current_strategic_bottleneck']}",
            f"next_decision_horizon: {data['brain']['next_decision_horizon']}",
        ]),
        "reports/integration/e27_ecosystem_alignment_gate.md": md("E27 Ecosystem Alignment Gate", [
            f"repos_checked: {data['alignment']['repos_checked_count']}",
            f"gov_mcp_delivered: {data['alignment']['gov_mcp_delivered']}",
            f"closure_status: {data['alignment']['closure_status']}",
        ]),
        "reports/integration/e27_future_live_test_canary_policy.md": md("E27 Future Live Test Canary Policy", [
            f"future_start_requirements: {len(data['future_policy']['every_future_milestone_must_start_with'])}",
            f"future_live_canary_requirements: {len(data['future_policy']['future_live_canary_requirements'])}",
        ]),
        "reports/integration/e27_czl_closure.md": md("E27 CZL Closure", [
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
            "operations/knowledge_graph/e27_ceo_kg_nodes_delta.jsonl",
            "operations/knowledge_graph/e27_ceo_kg_edges_delta.jsonl",
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
    files = create_e27(Path(args.repo_root), Path(args.output_root))
    result = {"status": "created", "file_count": len(files), "files": files}
    print(json.dumps(result, indent=2) if args.json else f"created {len(files)} E27 files")


if __name__ == "__main__":
    main()
