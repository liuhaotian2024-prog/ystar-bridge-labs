#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from office.mission_command.e26_existing_live_readiness_wheel_inventory import build_all


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


def create_e26(repo_root: Path, output_root: Path) -> List[str]:
    data = build_all(repo_root)
    json_outputs = {
        "operations/external_validation/e26_existing_live_readiness_wheel_inventory.json": data["inventory"],
        "operations/external_validation/e26_live_readiness_duplicate_conflict_map.json": data["conflicts"],
        "operations/external_validation/e26_reuse_wrap_extend_build_decision.json": data["decision"],
        "operations/external_validation/e26_live_config_capability_sync.json": data["live_config"],
        "operations/external_validation/e26_persistent_idempotency_readiness.json": data["idempotency"],
        "operations/external_validation/e26_kill_switch_readiness.json": data["kill_switch"],
        "operations/external_validation/e26_live_receipt_boundary.json": data["receipt_boundary"],
        "operations/external_validation/e26_live_provider_readiness_validator.json": data["validator"],
        "operations/external_validation/e26_one_action_canary_plan.json": data["canary"],
        "operations/external_validation/e26_ceo_brain_portfolio_update.json": data["brain"],
        "operations/external_validation/e26_live_readiness_control_room.json": data["control"],
        "operations/external_validation/e26_ecosystem_alignment_gate.json": data["alignment"],
        "operations/external_validation/e26_repo_modification_decision_packet.json": data["repo_decision"],
        "operations/external_validation/e26_future_anti_duplication_policy.json": data["future_policy"],
        "operations/external_validation/e26_czl_closure.json": data["closure"],
        "operations/knowledge_graph/e26_ceo_kg_live_readiness_feedback.json": data["feedback"],
        "operations/knowledge_graph/e26_ceo_kg_read_model_update.json": {
            "artifact_id": "e26_ceo_kg_read_model_update",
            "selected_revenue_path": data["brain"]["selected_revenue_path"],
            "live_ready": data["validator"]["live_ready"],
            "live_ready_action_count": data["validator"]["live_ready_action_count"],
            "live_blocked_action_count": data["validator"]["live_blocked_action_count"],
            "current_strategic_bottleneck": data["brain"]["current_strategic_bottleneck"],
            "external_action_executed": False,
        },
        "operations/knowledge_graph/e26_ceo_kg_promotion_candidates_update.json": {
            "artifact_id": "e26_ceo_kg_promotion_candidates_update",
            "promotion_candidates_count": data["feedback"]["promotion_candidates_count"],
            "promotion_candidates": data["feedback"]["promotion_candidates"],
            "canonical_truth_promoted": False,
            "external_action_executed": False,
        },
    }
    for rel, payload in json_outputs.items():
        write_json(output_root / rel, payload)
    write_jsonl(output_root / "operations/knowledge_graph/e26_ceo_kg_nodes_delta.jsonl", data["feedback"]["kg_delta_nodes"])
    write_jsonl(output_root / "operations/knowledge_graph/e26_ceo_kg_edges_delta.jsonl", data["feedback"]["kg_delta_edges"])
    md_outputs = {
        "operations/external_validation/e26_live_readiness_control_room.md": md("E26 Live Readiness Control Room", [
            f"existing_wheels_found: {data['inventory']['existing_live_readiness_wheels_found']}",
            f"new_wheels_added_with_justification: {data['inventory']['newly_built_wheels_count']}",
            f"selected_revenue_path: {data['canary']['selected_revenue_path']}",
            f"live_ready: {data['validator']['live_ready']}",
            f"canary_executed: {data['canary']['canary_executed']}",
            "external_action_executed: false",
        ]),
        "reports/integration/e26_live_readiness_existing_wheel_integration.md": md("E26 Live Readiness Existing Wheel Integration", [
            "Audited existing wheels before creating E26 integrations.",
            "Reused/wrapped/extended existing provider, idempotency, receipt, promotion, KG, suppression, compliance, and audit wheels.",
            "Prepared one-action canary gate as a plan only; no live execution occurred.",
        ]),
        "reports/integration/e26_existing_live_readiness_wheel_inventory.md": md("E26 Existing Live Readiness Wheel Inventory", [
            f"repos_scanned: {data['inventory']['repos_scanned_count']}",
            f"wheels_found: {data['inventory']['existing_live_readiness_wheels_found']}",
            f"reused: {data['inventory']['reused_wheels_count']}",
            f"wrapped: {data['inventory']['wrapped_wheels_count']}",
            f"extended: {data['inventory']['extended_wheels_count']}",
            f"newly_built: {data['inventory']['newly_built_wheels_count']}",
        ]),
        "reports/integration/e26_live_readiness_duplicate_conflict_map.md": md("E26 Live Readiness Duplicate Conflict Map", [
            f"cluster_count: {data['conflicts']['cluster_count']}",
            f"destructive_refactor_performed: {data['conflicts']['destructive_refactor_performed']}",
        ]),
        "reports/integration/e26_reuse_wrap_extend_build_decision.md": md("E26 Reuse Wrap Extend Build Decision", [
            f"decisions: {len(data['decision']['decisions'])}",
            f"all_new_wheels_have_justification: {data['decision']['all_new_wheels_have_justification']}",
        ]),
        "reports/integration/e26_live_config_capability_sync.md": md("E26 Live Config Capability Sync", [
            f"schema_ready: {data['live_config']['live_config_schema_ready']}",
            f"credentials_committed: {data['live_config']['secrets_committed']}",
            f"live_enabled: {data['live_config']['live_enabled']}",
        ]),
        "reports/integration/e26_persistent_idempotency_readiness.md": md("E26 Persistent Idempotency Readiness", [
            f"persistent_status: {data['idempotency']['persistent_status']}",
            f"store_type: {data['idempotency']['store_type']}",
            f"duplicate_protection: {data['idempotency']['duplicate_protection_result']}",
        ]),
        "reports/integration/e26_live_provider_readiness_validator.md": md("E26 Live Provider Readiness Validator", [
            f"live_ready: {data['validator']['live_ready']}",
            f"live_ready_action_count: {data['validator']['live_ready_action_count']}",
            f"live_blocked_action_count: {data['validator']['live_blocked_action_count']}",
            f"primary_blockers: {', '.join(data['validator']['primary_blockers'])}",
        ]),
        "reports/integration/e26_one_action_canary_plan.md": md("E26 One Action Canary Plan", [
            f"canary_plan_created: {data['canary']['canary_plan_created']}",
            f"canary_executed: {data['canary']['canary_executed']}",
            f"selected_revenue_path: {data['canary']['selected_revenue_path']}",
        ]),
        "reports/integration/e26_ceo_kg_live_readiness_feedback.md": md("E26 CEO KG Live Readiness Feedback", [
            f"kg_delta_nodes: {data['feedback']['kg_delta_node_count']}",
            f"kg_delta_edges: {data['feedback']['kg_delta_edge_count']}",
            f"market_validation_claimed: {data['feedback']['market_validation_claimed']}",
        ]),
        "reports/integration/e26_ceo_brain_portfolio_update.md": md("E26 CEO Brain Portfolio Update", [
            f"selected_revenue_path: {data['brain']['selected_revenue_path']}",
            f"strategic_bottleneck: {data['brain']['current_strategic_bottleneck']}",
            f"next_decision_horizon: {data['brain']['next_decision_horizon']}",
        ]),
        "reports/integration/e26_ecosystem_alignment_gate.md": md("E26 Ecosystem Alignment Gate", [
            f"repos_checked: {len(data['alignment']['repos_checked'])}",
            f"gov_mcp_delivered: {data['alignment']['gov_mcp_delivered']}",
            f"closure_status: {data['alignment']['closure_status']}",
        ]),
        "reports/integration/e26_future_anti_duplication_policy.md": md("E26 Future Anti Duplication Policy", [
            f"future_start_requirements: {len(data['future_policy']['future_milestone_start_requirements'])}",
            f"future_live_canary_requirements: {len(data['future_policy']['future_live_canary_requirements'])}",
        ]),
        "reports/integration/e26_czl_closure.md": md("E26 CZL Closure", [
            f"Rt+1: {data['closure']['Rt_plus_1']}",
            f"no_real_external_action_occurred: {data['closure']['no_real_external_action_occurred']}",
            f"no_provider_api_called: {data['closure']['no_provider_api_called']}",
            f"no_live_receipt_created: {data['closure']['no_live_receipt_created']}",
        ]),
    }
    for rel, text in md_outputs.items():
        write_text(output_root / rel, text)
    files = sorted(list(json_outputs) + [
        "operations/knowledge_graph/e26_ceo_kg_nodes_delta.jsonl",
        "operations/knowledge_graph/e26_ceo_kg_edges_delta.jsonl",
    ] + list(md_outputs))
    return files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    files = create_e26(Path(args.repo_root), Path(args.output_root))
    result = {"status": "created", "file_count": len(files), "files": files}
    print(json.dumps(result, indent=2) if args.json else f"created {len(files)} E26 files")


if __name__ == "__main__":
    main()
