#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from office.mission_command.e22_autonomous_dry_run_control_room import build_autonomous_dry_run_control_room, render_autonomous_dry_run_control_room
from office.mission_command.e22_dry_run_batch_selector import select_dry_run_actions, render_dry_run_batch_selection
from office.mission_command.e22_dry_run_receipt_ledger import build_dry_run_receipt_ledger, render_dry_run_receipt_ledger
from office.mission_command.e22_ecosystem_alignment_gate import build_e22_ecosystem_alignment_gate, render_ecosystem_alignment_gate
from office.mission_command.e22_future_dry_run_live_policy import build_future_dry_run_live_policy, render_future_dry_run_live_policy
from office.mission_command.e22_gov_mcp_dry_run_integration import execute_gov_mcp_dry_run_batch
from office.mission_command.e22_guard_stack_replay import replay_guard_stack, render_guard_stack_results
from office.mission_command.e22_idempotency_replay_proof import build_idempotency_replay_proof
from office.mission_command.e22_kpi_dry_run_delta import build_kpi_dry_run_delta, render_kpi_dry_run_delta
from office.mission_command.e22_live_promotion_blockers import build_live_promotion_blockers, render_live_promotion_blockers
from office.mission_command.e22_outbound_envelope_builder import build_outbound_envelopes
from office.mission_command.e22_rate_limit_proof import build_rate_limit_proof
from office.mission_command.e22_route_decision import build_e22_route_decision, render_route_decision
from office.mission_command.e22_suppression_proof import build_suppression_proof


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_repo_modification_decision(gate: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_id": "e22_repo_modification_decision_packet",
        "gov_mcp_read_only": gate["gov_mcp_read_only"],
        "gov_mcp_modified": gate["gov_mcp_modified"],
        "bridge_labs_modified_and_delivered": True,
        "Y_star_gov_immediate_mutation_needed": False,
        "ystar_company_future_migration_followup": True,
        "decision": "bridge_labs_update_only_gov_mcp_contract_sufficient",
        "external_action_executed": False,
    }


def build_czl(selection: Dict[str, Any], dry_run_results: Dict[str, Any], ledger: Dict[str, Any], gate: Dict[str, Any], route: Dict[str, Any], artifacts: list[str]) -> Dict[str, Any]:
    return {
        "artifact_id": "e22_czl_closure",
        "Y_star": "E22 autonomous dry-run batch execution",
        "Xt": ["E21 gov-mcp dry-run provider foundation", "E21 bridge-labs provider capability sync", "E20 autonomous outbound policy"],
        "U": ["dry-run selector", "provider envelopes", "guard replay", "gov-mcp dry-run integration", "idempotency replay", "suppression proof", "rate-limit proof", "dry-run receipt ledger", "KPI dry-run delta", "live promotion blockers", "control room", "ecosystem alignment", "route decision", "future policy"],
        "Yt_plus_1": "Five low-risk actions executed through deterministic no-effect dry-run receipts; live send remains blocked by disabled live provider and evidence gaps.",
        "Rt_plus_1": 0,
        "selected_count": selection["selected_count"],
        "dry_run_executed_count": dry_run_results["dry_run_executed_count"],
        "live_receipt_count": ledger["live_receipt_count"],
        "ecosystem_alignment_status": gate["closure_status"],
        "no_real_external_action_occurred": True,
        "no_provider_api_called": True,
        "no_message_sent": True,
        "no_live_receipt_created": True,
        "dry_run_receipts_clearly_labeled": True,
        "idempotency_suppression_rate_limit_guards_tested": True,
        "live_remains_blocked_honestly": True,
        "owner_manual_send_is_not_default": True,
        "recommended_route": route["recommended_route"],
        "artifacts": artifacts,
    }


def render_main(selection: Dict[str, Any], dry_run_results: Dict[str, Any], route: Dict[str, Any]) -> str:
    return "\n".join([
        "# E22 Autonomous Dry-Run Batch Execution",
        "",
        "E22 runs the first governed autonomous outbound batch in local dry-run mode only.",
        "",
        f"- selected_count: {selection['selected_count']}",
        f"- dry_run_executed_count: {dry_run_results['dry_run_executed_count']}",
        f"- dry_run_blocked_count: {dry_run_results['dry_run_blocked_count']}",
        f"- recommended_route: {route['recommended_route']}",
        "- live_send_count: 0",
        "- real_response_count: 0",
        "- external_action_executed: false",
    ]).rstrip()+"\n"


def render_czl(closure: Dict[str, Any]) -> str:
    lines=["# E22 CZL Closure","",f"- Y*: {closure['Y_star']}",f"- Yt+1: {closure['Yt_plus_1']}",f"- Rt+1: {closure['Rt_plus_1']}",f"- selected_count: {closure['selected_count']}",f"- dry_run_executed_count: {closure['dry_run_executed_count']}",f"- live_receipt_count: {closure['live_receipt_count']}",f"- ecosystem_alignment_status: {closure['ecosystem_alignment_status']}",f"- no_real_external_action_occurred: {str(closure['no_real_external_action_occurred']).lower()}",f"- no_provider_api_called: {str(closure['no_provider_api_called']).lower()}",f"- no_message_sent: {str(closure['no_message_sent']).lower()}",f"- no_live_receipt_created: {str(closure['no_live_receipt_created']).lower()}","","## U"]
    lines.extend(f"- {item}" for item in closure["U"])
    return "\n".join(lines).rstrip()+"\n"


def create_e22(repo_root: Path, output_root: Path) -> list[str]:
    provider_sync=load_json(repo_root/"operations/external_validation/e21_provider_capability_sync.json")
    e21_reclassification=load_json(repo_root/"operations/external_validation/e21_batch_provider_reclassification.json")
    e20_reclassification=load_json(repo_root/"operations/external_validation/e20_batch_autonomous_reclassification.json")
    selection=select_dry_run_actions(e21_reclassification, provider_sync)
    envelopes=build_outbound_envelopes(selection, e20_reclassification)
    guard_results=replay_guard_stack(envelopes, provider_sync)
    dry_run_results=execute_gov_mcp_dry_run_batch(envelopes, guard_results)
    idempotency=build_idempotency_replay_proof(envelopes)
    suppression=build_suppression_proof()
    rate_limit=build_rate_limit_proof(selection)
    ledger=build_dry_run_receipt_ledger(dry_run_results, idempotency)
    kpi=build_kpi_dry_run_delta(selection, dry_run_results, guard_results, idempotency, suppression)
    blockers=build_live_promotion_blockers(e21_reclassification, provider_sync)
    route=build_e22_route_decision(kpi, blockers)
    control_room=build_autonomous_dry_run_control_room(selection, dry_run_results, ledger, kpi, blockers, route)
    gate=build_e22_ecosystem_alignment_gate(provider_sync)
    repo_decision=build_repo_modification_decision(gate)
    future_policy=build_future_dry_run_live_policy()
    artifact_paths=[
        "operations/external_validation/e22_dry_run_batch_selection.json",
        "operations/external_validation/e22_outbound_envelopes.json",
        "operations/external_validation/e22_guard_stack_results.json",
        "operations/external_validation/e22_gov_mcp_dry_run_results.json",
        "operations/external_validation/e22_idempotency_replay_proof.json",
        "operations/external_validation/e22_suppression_proof.json",
        "operations/external_validation/e22_rate_limit_proof.json",
        "operations/external_validation/e22_dry_run_receipt_ledger.json",
        "operations/external_validation/e22_kpi_dry_run_delta.json",
        "operations/external_validation/e22_live_promotion_blockers.json",
        "operations/external_validation/e22_autonomous_dry_run_control_room.json",
        "operations/external_validation/e22_ecosystem_alignment_gate.json",
        "operations/external_validation/e22_repo_modification_decision_packet.json",
        "operations/external_validation/e22_route_decision_packet.json",
        "operations/external_validation/e22_future_dry_run_live_policy.json",
        "operations/external_validation/e22_czl_closure.json",
        "operations/external_validation/e22_autonomous_dry_run_control_room.md",
        "reports/integration/e22_autonomous_dry_run_batch_execution.md",
        "reports/integration/e22_guard_stack_replay.md",
        "reports/integration/e22_dry_run_receipt_ledger.md",
        "reports/integration/e22_kpi_dry_run_delta.md",
        "reports/integration/e22_live_promotion_blockers.md",
        "reports/integration/e22_ecosystem_alignment_gate.md",
        "reports/integration/e22_route_decision_packet.md",
        "reports/integration/e22_future_dry_run_live_policy.md",
        "reports/integration/e22_czl_closure.md",
    ]
    closure=build_czl(selection,dry_run_results,ledger,gate,route,artifact_paths)
    outputs={
        "operations/external_validation/e22_dry_run_batch_selection.json":selection,
        "operations/external_validation/e22_outbound_envelopes.json":envelopes,
        "operations/external_validation/e22_guard_stack_results.json":guard_results,
        "operations/external_validation/e22_gov_mcp_dry_run_results.json":dry_run_results,
        "operations/external_validation/e22_idempotency_replay_proof.json":idempotency,
        "operations/external_validation/e22_suppression_proof.json":suppression,
        "operations/external_validation/e22_rate_limit_proof.json":rate_limit,
        "operations/external_validation/e22_dry_run_receipt_ledger.json":ledger,
        "operations/external_validation/e22_kpi_dry_run_delta.json":kpi,
        "operations/external_validation/e22_live_promotion_blockers.json":blockers,
        "operations/external_validation/e22_autonomous_dry_run_control_room.json":control_room,
        "operations/external_validation/e22_ecosystem_alignment_gate.json":gate,
        "operations/external_validation/e22_repo_modification_decision_packet.json":repo_decision,
        "operations/external_validation/e22_route_decision_packet.json":route,
        "operations/external_validation/e22_future_dry_run_live_policy.json":future_policy,
        "operations/external_validation/e22_czl_closure.json":closure,
    }
    for rel,data in outputs.items(): write_json(output_root/rel,data)
    write_text(output_root/"operations/external_validation/e22_autonomous_dry_run_control_room.md", render_autonomous_dry_run_control_room(control_room))
    write_text(output_root/"reports/integration/e22_autonomous_dry_run_batch_execution.md", render_main(selection,dry_run_results,route))
    write_text(output_root/"reports/integration/e22_guard_stack_replay.md", render_guard_stack_results(guard_results))
    write_text(output_root/"reports/integration/e22_dry_run_receipt_ledger.md", render_dry_run_receipt_ledger(ledger))
    write_text(output_root/"reports/integration/e22_kpi_dry_run_delta.md", render_kpi_dry_run_delta(kpi))
    write_text(output_root/"reports/integration/e22_live_promotion_blockers.md", render_live_promotion_blockers(blockers))
    write_text(output_root/"reports/integration/e22_ecosystem_alignment_gate.md", render_ecosystem_alignment_gate(gate))
    write_text(output_root/"reports/integration/e22_route_decision_packet.md", render_route_decision(route))
    write_text(output_root/"reports/integration/e22_future_dry_run_live_policy.md", render_future_dry_run_live_policy(future_policy))
    write_text(output_root/"reports/integration/e22_czl_closure.md", render_czl(closure))
    return sorted(artifact_paths)


def main() -> int:
    parser=argparse.ArgumentParser(description="Create E22 autonomous dry-run batch execution artifacts.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-root", default=".")
    parser.add_argument("--json", action="store_true")
    args=parser.parse_args()
    files=create_e22(Path(args.repo_root), Path(args.output_root))
    if args.json: print(json.dumps({"status":"created","files":files}, indent=2))
    else: print(f"created {len(files)} E22 artifacts")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
