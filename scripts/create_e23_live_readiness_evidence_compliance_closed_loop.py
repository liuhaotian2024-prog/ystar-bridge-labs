#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from office.mission_command.e23_batch_reclassification import build_batch_reclassification, render_batch_reclassification
from office.mission_command.e23_candidate_evidence_dossier import build_candidate_evidence_dossiers
from office.mission_command.e23_compliance_registry import build_compliance_registry, render_suppression_compliance
from office.mission_command.e23_ecosystem_alignment_gate import build_e23_ecosystem_alignment_gate, render_ecosystem_alignment_gate
from office.mission_command.e23_evidence_tightening_evaluator import evaluate_evidence_tightening, render_evidence_tightening
from office.mission_command.e23_future_live_readiness_policy import build_future_live_readiness_policy, render_future_live_readiness_policy
from office.mission_command.e23_kpi_update import build_kpi_update, render_kpi_update
from office.mission_command.e23_live_provider_enablement_plan import build_live_provider_enablement_plan, render_live_provider_enablement_plan
from office.mission_command.e23_live_readiness_control_room import build_live_readiness_control_room, render_live_readiness_control_room
from office.mission_command.e23_optional_dry_run_iteration import build_optional_dry_run_iteration
from office.mission_command.e23_promotion_readiness_gate import build_promotion_readiness_gate, render_promotion_readiness_gate
from office.mission_command.e23_route_decision import build_e23_route_decision, render_route_decision
from office.mission_command.e23_suppression_registry import build_suppression_registry, build_suppression_registry_schema


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_repo_modification_decision(gate: Dict[str, Any]) -> Dict[str, Any]:
    return {"artifact_id":"e23_repo_modification_decision_packet","decision":"bridge_labs_update_only_gov_mcp_contract_sufficient","gov_mcp_read_only":gate["gov_mcp_read_only"],"gov_mcp_modified":gate["gov_mcp_modified"],"bridge_labs_modified_and_delivered":True,"Y_star_gov_immediate_mutation_needed":False,"ystar_company_future_migration_followup":True,"external_action_executed":False}


def build_czl(evaluation: Dict[str, Any], suppression: Dict[str, Any], compliance: Dict[str, Any], promotion: Dict[str, Any], gate: Dict[str, Any], route: Dict[str, Any], artifacts: list[str]) -> Dict[str, Any]:
    return {"artifact_id":"e23_czl_closure","Y_star":"E23 live-readiness evidence and compliance hardening closed loop","Xt":["E22 autonomous dry-run results","E21 provider foundation","E18/E20 batch artifacts","four-repo ecosystem scan"],"U":["evidence tightening","candidate dossiers","suppression registry","compliance registry","live provider enablement plan","promotion readiness gate","batch reclassification","optional dry-run iteration decision","KPI update","live-readiness control room","ecosystem gate","route decision","future live-readiness policy"],"Yt_plus_1":"Live-readiness blockers are explicit: live provider disabled, live tests/config/persistence missing, one target suppressed, one target source-blocked.","Rt_plus_1":0,"evidence_required_before":evaluation["evidence_required_before"],"promoted_to_dry_run_available":evaluation["promoted_to_dry_run_available"],"suppressed_or_rejected":evaluation["suppressed_or_rejected"],"production_suppressed_target_count":suppression["production_suppressed_target_count"],"compliance_blocked_count":compliance["compliance_blocked_count"],"live_ready_count":promotion["counts"]["live_ready"],"live_blocked_provider_disabled":promotion["counts"]["live_blocked_provider_disabled"],"ecosystem_alignment_status":gate["closure_status"],"no_real_external_action_occurred":True,"no_provider_api_called":True,"no_message_sent":True,"no_live_receipt_created":True,"no_fake_evidence_created":True,"no_fake_suppression_evidence_created":True,"no_fake_feedback_created":True,"live_provider_honestly_reported":"live_provider_scaffolded_but_disabled","suppression_compliance_gates_defined":True,"owner_manual_send_is_not_default":True,"recommended_route":route["recommended_route"],"artifacts":artifacts}


def render_main(evaluation: Dict[str, Any], kpi: Dict[str, Any], route: Dict[str, Any]) -> str:
    return "\n".join(["# E23 Live-Readiness Evidence & Compliance Hardening Closed Loop","",f"- evidence_required_before: {evaluation['evidence_required_before']}",f"- promoted_to_dry_run_available: {evaluation['promoted_to_dry_run_available']}",f"- still_evidence_required: {evaluation['still_evidence_required']}",f"- previous_dry_run_executed: {kpi['previous_dry_run_executed']}",f"- live_send_count: {kpi['live_send_count']}",f"- recommended_route: {route['recommended_route']}","- external_action_executed: false"]).rstrip()+"\n"


def render_czl(closure: Dict[str, Any]) -> str:
    lines=["# E23 CZL Closure","",f"- Y*: {closure['Y_star']}",f"- Yt+1: {closure['Yt_plus_1']}",f"- Rt+1: {closure['Rt_plus_1']}",f"- ecosystem_alignment_status: {closure['ecosystem_alignment_status']}",f"- no_real_external_action_occurred: {str(closure['no_real_external_action_occurred']).lower()}",f"- no_provider_api_called: {str(closure['no_provider_api_called']).lower()}",f"- no_message_sent: {str(closure['no_message_sent']).lower()}",f"- no_live_receipt_created: {str(closure['no_live_receipt_created']).lower()}",f"- no_fake_evidence_created: {str(closure['no_fake_evidence_created']).lower()}","","## U"]
    lines.extend(f"- {item}" for item in closure["U"])
    return "\n".join(lines).rstrip()+"\n"


def create_e23(repo_root: Path, output_root: Path) -> list[str]:
    e22_selection=load_json(repo_root/"operations/external_validation/e22_dry_run_batch_selection.json")
    e22_kpi=load_json(repo_root/"operations/external_validation/e22_kpi_dry_run_delta.json")
    e21_reclassification=load_json(repo_root/"operations/external_validation/e21_batch_provider_reclassification.json")
    provider_sync=load_json(repo_root/"operations/external_validation/e21_provider_capability_sync.json")
    e18_batch=load_json(repo_root/"operations/external_validation/e18_revenue_validation_batch.json")
    evaluation=evaluate_evidence_tightening(e22_selection,e18_batch)
    dossiers=build_candidate_evidence_dossiers(evaluation)
    suppression_schema=build_suppression_registry_schema()
    suppression=build_suppression_registry(dossiers)
    compliance=build_compliance_registry()
    plan=build_live_provider_enablement_plan(provider_sync)
    promotion=build_promotion_readiness_gate(e21_reclassification,suppression,compliance,provider_sync,evaluation)
    batch=build_batch_reclassification(e21_reclassification,evaluation,suppression,compliance,promotion,e22_kpi)
    optional=build_optional_dry_run_iteration(batch)
    kpi=build_kpi_update(e22_kpi,batch,optional)
    route=build_e23_route_decision(kpi,promotion,provider_sync)
    control=build_live_readiness_control_room(evaluation,suppression,compliance,promotion,batch,kpi,route)
    gate=build_e23_ecosystem_alignment_gate(provider_sync)
    repo_decision=build_repo_modification_decision(gate)
    future=build_future_live_readiness_policy()
    artifact_paths=[
        "operations/external_validation/e23_evidence_tightening_evaluation.json","operations/external_validation/e23_candidate_evidence_dossiers.json","operations/external_validation/e23_suppression_registry_schema.json","operations/external_validation/e23_suppression_registry.json","operations/external_validation/e23_compliance_registry.json","operations/external_validation/e23_live_provider_enablement_plan.json","operations/external_validation/e23_promotion_readiness_gate.json","operations/external_validation/e23_batch_reclassification.json","operations/external_validation/e23_optional_dry_run_iteration.json","operations/external_validation/e23_kpi_update.json","operations/external_validation/e23_live_readiness_control_room.json","operations/external_validation/e23_ecosystem_alignment_gate.json","operations/external_validation/e23_repo_modification_decision_packet.json","operations/external_validation/e23_route_decision_packet.json","operations/external_validation/e23_future_live_readiness_policy.json","operations/external_validation/e23_czl_closure.json","operations/external_validation/e23_live_readiness_control_room.md","reports/integration/e23_live_readiness_evidence_compliance_closed_loop.md","reports/integration/e23_evidence_tightening.md","reports/integration/e23_suppression_compliance_registry.md","reports/integration/e23_live_provider_enablement_plan.md","reports/integration/e23_promotion_readiness_gate.md","reports/integration/e23_batch_reclassification.md","reports/integration/e23_kpi_update.md","reports/integration/e23_ecosystem_alignment_gate.md","reports/integration/e23_route_decision_packet.md","reports/integration/e23_future_live_readiness_policy.md","reports/integration/e23_czl_closure.md"]
    closure=build_czl(evaluation,suppression,compliance,promotion,gate,route,artifact_paths)
    outputs={"operations/external_validation/e23_evidence_tightening_evaluation.json":evaluation,"operations/external_validation/e23_candidate_evidence_dossiers.json":dossiers,"operations/external_validation/e23_suppression_registry_schema.json":suppression_schema,"operations/external_validation/e23_suppression_registry.json":suppression,"operations/external_validation/e23_compliance_registry.json":compliance,"operations/external_validation/e23_live_provider_enablement_plan.json":plan,"operations/external_validation/e23_promotion_readiness_gate.json":promotion,"operations/external_validation/e23_batch_reclassification.json":batch,"operations/external_validation/e23_optional_dry_run_iteration.json":optional,"operations/external_validation/e23_kpi_update.json":kpi,"operations/external_validation/e23_live_readiness_control_room.json":control,"operations/external_validation/e23_ecosystem_alignment_gate.json":gate,"operations/external_validation/e23_repo_modification_decision_packet.json":repo_decision,"operations/external_validation/e23_route_decision_packet.json":route,"operations/external_validation/e23_future_live_readiness_policy.json":future,"operations/external_validation/e23_czl_closure.json":closure}
    for rel,data in outputs.items(): write_json(output_root/rel,data)
    write_text(output_root/"operations/external_validation/e23_live_readiness_control_room.md", render_live_readiness_control_room(control))
    write_text(output_root/"reports/integration/e23_live_readiness_evidence_compliance_closed_loop.md", render_main(evaluation,kpi,route))
    write_text(output_root/"reports/integration/e23_evidence_tightening.md", render_evidence_tightening(evaluation))
    write_text(output_root/"reports/integration/e23_suppression_compliance_registry.md", render_suppression_compliance(suppression,compliance))
    write_text(output_root/"reports/integration/e23_live_provider_enablement_plan.md", render_live_provider_enablement_plan(plan))
    write_text(output_root/"reports/integration/e23_promotion_readiness_gate.md", render_promotion_readiness_gate(promotion))
    write_text(output_root/"reports/integration/e23_batch_reclassification.md", render_batch_reclassification(batch))
    write_text(output_root/"reports/integration/e23_kpi_update.md", render_kpi_update(kpi))
    write_text(output_root/"reports/integration/e23_ecosystem_alignment_gate.md", render_ecosystem_alignment_gate(gate))
    write_text(output_root/"reports/integration/e23_route_decision_packet.md", render_route_decision(route))
    write_text(output_root/"reports/integration/e23_future_live_readiness_policy.md", render_future_live_readiness_policy(future))
    write_text(output_root/"reports/integration/e23_czl_closure.md", render_czl(closure))
    return sorted(artifact_paths)


def main() -> int:
    parser=argparse.ArgumentParser(description="Create E23 live-readiness evidence and compliance hardening loop.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-root", default=".")
    parser.add_argument("--json", action="store_true")
    args=parser.parse_args()
    files=create_e23(Path(args.repo_root), Path(args.output_root))
    if args.json: print(json.dumps({"status":"created","files":files}, indent=2))
    else: print(f"created {len(files)} E23 artifacts")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
