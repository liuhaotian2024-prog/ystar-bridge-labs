#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from office.mission_command.e25_ceo_kg_sandbox_route_selector import build_all


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


def create_e25(repo_root: Path, output_root: Path, gov_root: Path) -> List[str]:
    data = build_all(repo_root, gov_root)
    json_outputs = {
        "operations/external_validation/e25_ceo_kg_sandbox_route_selection.json": data["route"],
        "operations/external_validation/e25_provider_sandbox_capability_sync.json": data["capability"],
        "operations/external_validation/e25_sandbox_envelopes.json": data["envelopes"],
        "operations/external_validation/e25_sandbox_guard_results.json": data["guards"],
        "operations/external_validation/e25_sandbox_execution_results.json": data["execution"],
        "operations/external_validation/e25_sandbox_receipt_ledger.json": data["ledger"],
        "operations/external_validation/e25_persistent_idempotency_status.json": data["idempotency"],
        "operations/external_validation/e25_live_promotion_blockers.json": data["blockers"],
        "operations/external_validation/e25_ceo_brain_update.json": data["brain"],
        "operations/external_validation/e25_revenue_portfolio_update.json": data["portfolio"],
        "operations/external_validation/e25_sandbox_control_room.json": data["control"],
        "operations/external_validation/e25_ecosystem_alignment_gate.json": data["alignment"],
        "operations/external_validation/e25_repo_modification_decision_packet.json": data["repo_decision"],
        "operations/external_validation/e25_future_sandbox_live_policy.json": data["future_policy"],
        "operations/external_validation/e25_czl_closure.json": data["closure"],
        "operations/knowledge_graph/e25_ceo_kg_feedback_ingestion.json": data["feedback"],
        "operations/knowledge_graph/e25_ceo_kg_read_model_update.json": {
            "artifact_id": "e25_ceo_kg_read_model_update",
            "selected_revenue_path": data["brain"]["selected_revenue_path_after_sandbox"],
            "sandbox_execution_count": data["execution"]["sandbox_executed_count"],
            "sandbox_receipt_count": data["ledger"]["sandbox_receipt_count"],
            "live_ready": False,
            "live_blockers": data["blockers"]["primary_live_blockers"],
            "market_truth_claimed": False,
            "external_action_executed": False,
        },
        "operations/knowledge_graph/e25_ceo_kg_promotion_candidates_update.json": {
            "artifact_id": "e25_ceo_kg_promotion_candidates_update",
            "promotion_candidates_count": data["feedback"]["promotion_candidates_count"],
            "promotion_candidates": data["feedback"]["promotion_candidates"],
            "canonical_market_truth_promoted": False,
            "external_action_executed": False,
        },
    }
    for rel, value in json_outputs.items():
        write_json(output_root / rel, value)
    write_jsonl(output_root / "operations/knowledge_graph/e25_ceo_kg_nodes_delta.jsonl", data["feedback"]["kg_delta_nodes"])
    write_jsonl(output_root / "operations/knowledge_graph/e25_ceo_kg_edges_delta.jsonl", data["feedback"]["kg_delta_edges"])
    md_outputs = {
        "operations/external_validation/e25_sandbox_control_room.md": md("E25 Sandbox Control Room", [
            f"selected_route: {data['route']['sandbox_route_candidate']['route_id']}",
            f"sandbox_mode_available: {data['capability']['sandbox_mode_available']}",
            f"sandbox_executed_count: {data['execution']['sandbox_executed_count']}",
            f"sandbox_receipt_count: {data['ledger']['sandbox_receipt_count']}",
            f"live_receipt_count: {data['ledger']['live_receipt_count']}",
            f"live_enabled: {data['capability']['live_enabled']}",
            f"current_bottleneck: {data['brain']['current_strategic_bottleneck']}",
            "external_action_executed: false",
        ]),
        "reports/integration/e25_provider_sandbox_ceo_kg_feedback_loop.md": md("E25 Provider Sandbox CEO KG Feedback Loop", [
            "Built a provider-shaped sandbox layer and routed the selected CEO KG revenue path through it.",
            "Sandbox output is internal execution evidence only, not customer or market truth.",
            "Live remains disabled and blocked by live config/tests and production persistent idempotency.",
        ]),
        "reports/integration/e25_ceo_kg_sandbox_route_selection.md": md("E25 CEO KG Sandbox Route Selection", [
            f"selected_revenue_path: {data['route']['selected_revenue_path_id']}",
            f"why_sandbox_now: {data['route']['why_sandbox_now']}",
        ]),
        "reports/integration/e25_provider_sandbox_capability_sync.md": md("E25 Provider Sandbox Capability Sync", [
            f"gov_mcp_head: {data['capability']['source_head']}",
            f"sandbox_scaffold_ready: {data['capability']['sandbox_scaffold_ready']}",
            f"live_enabled: {data['capability']['live_enabled']}",
        ]),
        "reports/integration/e25_sandbox_execution_results.md": md("E25 Sandbox Execution Results", [
            f"selected: {data['execution']['sandbox_selected_count']}",
            f"executed: {data['execution']['sandbox_executed_count']}",
            f"blocked: {data['execution']['sandbox_blocked_count']}",
            f"live_receipts: {data['execution']['live_receipt_count']}",
        ]),
        "reports/integration/e25_ceo_kg_feedback_ingestion.md": md("E25 CEO KG Feedback Ingestion", [
            f"delta_nodes: {data['feedback']['kg_delta_node_count']}",
            f"delta_edges: {data['feedback']['kg_delta_edge_count']}",
            f"customer_or_market_truth_claimed: {data['feedback']['customer_or_market_truth_claimed']}",
        ]),
        "reports/integration/e25_ceo_brain_update.md": md("E25 CEO Brain Update", [
            f"selected_path: {data['brain']['selected_revenue_path_after_sandbox']}",
            f"strategic_bottleneck: {data['brain']['current_strategic_bottleneck']}",
            f"next_decision_horizon: {data['brain']['next_decision_horizon']}",
        ]),
        "reports/integration/e25_revenue_portfolio_update.md": md("E25 Revenue Portfolio Update", [
            f"selected_path_remains_selected: {data['portfolio']['selected_path_remains_selected']}",
            f"live_sandbox_ready_paths: {len(data['portfolio']['live_sandbox_ready_paths'])}",
            f"live_blocked_count: {data['portfolio']['live_blocked_count']}",
        ]),
        "reports/integration/e25_ecosystem_alignment_gate.md": md("E25 Ecosystem Alignment Gate", [
            f"repos_checked: {len(data['alignment']['repos_checked'])}",
            f"gov_mcp_modified: {data['alignment']['gov_mcp_modified']}",
            f"gov_mcp_delivered: {data['alignment']['gov_mcp_delivered']}",
            f"closure_status: {data['alignment']['closure_status']}",
        ]),
        "reports/integration/e25_future_sandbox_live_policy.md": md("E25 Future Sandbox Live Policy", [
            f"requirements: {len(data['future_policy']['future_sandbox_live_milestone_requirements'])}",
            f"owner_manual_send_default_allowed: {data['future_policy']['owner_manual_send_default_allowed']}",
        ]),
        "reports/integration/e25_czl_closure.md": md("E25 CZL Closure", [
            f"Rt+1: {data['closure']['Rt_plus_1']}",
            f"no_real_external_action_occurred: {data['closure']['no_real_external_action_occurred']}",
            f"no_provider_api_called: {data['closure']['no_provider_api_called']}",
            f"no_message_sent: {data['closure']['no_message_sent']}",
            f"no_live_receipt_created: {data['closure']['no_live_receipt_created']}",
        ]),
    }
    for rel, value in md_outputs.items():
        write_text(output_root / rel, value)
    files = sorted(list(json_outputs) + [
        "operations/knowledge_graph/e25_ceo_kg_nodes_delta.jsonl",
        "operations/knowledge_graph/e25_ceo_kg_edges_delta.jsonl",
    ] + list(md_outputs))
    return files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-root", default=".")
    parser.add_argument("--gov-root", default="/Users/haotianliu/.openclaw/workspace/gov-mcp")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    files = create_e25(Path(args.repo_root), Path(args.output_root), Path(args.gov_root))
    result = {"status": "created", "file_count": len(files), "files": files}
    print(json.dumps(result, indent=2) if args.json else f"created {len(files)} E25 files")


if __name__ == "__main__":
    main()
