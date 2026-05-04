#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from office.mission_command.e20_autonomous_control_room import build_autonomous_control_room, render_autonomous_control_room
from office.mission_command.e20_autonomous_execution_eligibility import build_autonomous_execution_eligibility_rules
from office.mission_command.e20_autonomous_outbound_envelope import build_autonomous_outbound_envelope_schema
from office.mission_command.e20_batch_autonomous_reclassification import build_batch_autonomous_reclassification, render_batch_autonomous_reclassification
from office.mission_command.e20_ecosystem_alignment_gate import build_ecosystem_alignment_gate, render_ecosystem_alignment_gate
from office.mission_command.e20_future_outbound_policy import build_future_outbound_policy, render_future_outbound_policy
from office.mission_command.e20_human_intervention_boundary import build_human_intervention_boundary, render_human_intervention_boundary
from office.mission_command.e20_provider_capability_detector import detect_provider_capability, render_provider_capability_detection
from office.mission_command.e20_risk_tier_taxonomy import build_risk_tier_taxonomy
from office.mission_command.e20_route_decision import build_e20_route_decision, render_route_decision


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def render_main_report(taxonomy: Dict[str, Any], control_room: Dict[str, Any], route: Dict[str, Any]) -> str:
    lines = [
        "# E20 Risk-Tiered Autonomous Outbound Execution Control Plane",
        "",
        "E20 replaces owner-manual-send-by-default with risk-tiered autonomous execution policy.",
        "",
        f"- owner_manual_send_is_default: {str(taxonomy['owner_manual_send_is_default']).lower()}",
        f"- provider_capability_status: {control_room['provider_capability_status']}",
        f"- recommended_route: {route['recommended_route']}",
        "- external_action_executed: false",
        "",
        "## Control Room Counts",
        f"- autonomous_now: {len(control_room['actions_agent_can_do_autonomously_now'])}",
        f"- autonomous_after_provider: {len(control_room['actions_agent_could_do_after_provider_implementation'])}",
        f"- owner_approval_required: {len(control_room['actions_requiring_owner_approval'])}",
        f"- provider_missing_override_possible: {len(control_room['actions_owner_may_do_manually_as_override'])}",
    ]
    return "\n".join(lines).rstrip() + "\n"


def build_czl_closure(control_room: Dict[str, Any], route: Dict[str, Any], gate: Dict[str, Any], artifacts: list[str]) -> Dict[str, Any]:
    return {
        "artifact_id": "e20_czl_closure",
        "Y_star": "E20 risk-tiered autonomous outbound execution control plane",
        "Xt": ["E19 control room", "E18 revenue validation batch", "gov-mcp no-send outbound boundary", "Y-star-gov governance semantics"],
        "U": ["risk taxonomy", "autonomous eligibility", "human intervention boundary", "provider capability detector", "autonomous envelopes", "batch reclassification", "autonomous control room", "ecosystem gate", "route decision", "future outbound policy"],
        "Yt_plus_1": "Low-risk outbound can be classified for future autonomous execution; high-risk owner gates remain explicit; live execution stays blocked by provider capability gap.",
        "Rt_plus_1": 0,
        "ecosystem_alignment_status": gate["closure_status"],
        "owner_manual_send_no_longer_default": True,
        "low_risk_autonomous_execution_path_defined": True,
        "high_risk_human_intervention_boundary_defined": True,
        "no_real_external_action_occurred": True,
        "no_customer_contact_occurred": True,
        "no_fake_send_created": True,
        "no_fake_feedback_created": True,
        "no_provider_api_called": True,
        "recommended_route": route["recommended_route"],
        "artifacts": artifacts,
    }


def render_czl_closure(closure: Dict[str, Any]) -> str:
    lines = [
        "# E20 CZL Closure",
        "",
        f"- Y*: {closure['Y_star']}",
        f"- Yt+1: {closure['Yt_plus_1']}",
        f"- Rt+1: {closure['Rt_plus_1']}",
        f"- ecosystem_alignment_status: {closure['ecosystem_alignment_status']}",
        f"- owner_manual_send_no_longer_default: {str(closure['owner_manual_send_no_longer_default']).lower()}",
        f"- low_risk_autonomous_execution_path_defined: {str(closure['low_risk_autonomous_execution_path_defined']).lower()}",
        f"- high_risk_human_intervention_boundary_defined: {str(closure['high_risk_human_intervention_boundary_defined']).lower()}",
        f"- no_real_external_action_occurred: {str(closure['no_real_external_action_occurred']).lower()}",
        f"- no_provider_api_called: {str(closure['no_provider_api_called']).lower()}",
        "",
        "## U",
    ]
    lines.extend(f"- {item}" for item in closure["U"])
    return "\n".join(lines).rstrip() + "\n"


def create_e20(repo_root: Path, output_root: Path) -> list[str]:
    e18_batch = load_json(repo_root / "operations/external_validation/e18_revenue_validation_batch.json")

    taxonomy = build_risk_tier_taxonomy()
    eligibility_rules = build_autonomous_execution_eligibility_rules()
    human_boundary = build_human_intervention_boundary()
    provider_capability = detect_provider_capability()
    envelope_schema = build_autonomous_outbound_envelope_schema()
    reclassification = build_batch_autonomous_reclassification(e18_batch, provider_capability)
    route = build_e20_route_decision(reclassification, provider_capability)
    control_room = build_autonomous_control_room(reclassification, provider_capability, route)
    ecosystem_gate = build_ecosystem_alignment_gate(provider_capability)
    future_policy = build_future_outbound_policy()
    repo_decision = {
        "artifact_id": "e20_repo_modification_decision_packet",
        "cross_repo_mutation_performed": False,
        "decisions": ecosystem_gate["repo_modification_decisions"],
        "bridge_labs_only_delivery": True,
        "external_action_executed": False,
    }

    artifact_paths = [
        "operations/external_validation/e20_risk_tier_taxonomy.json",
        "operations/external_validation/e20_autonomous_execution_eligibility_rules.json",
        "operations/external_validation/e20_human_intervention_boundary.json",
        "operations/external_validation/e20_provider_capability_detection.json",
        "operations/external_validation/e20_autonomous_outbound_envelope_schema.json",
        "operations/external_validation/e20_batch_autonomous_reclassification.json",
        "operations/external_validation/e20_autonomous_control_room.json",
        "operations/external_validation/e20_ecosystem_alignment_gate.json",
        "operations/external_validation/e20_repo_modification_decision_packet.json",
        "operations/external_validation/e20_route_decision_packet.json",
        "operations/external_validation/e20_future_outbound_policy.json",
        "operations/external_validation/e20_czl_closure.json",
        "operations/external_validation/e20_autonomous_control_room.md",
        "reports/integration/e20_risk_tiered_autonomous_outbound_control_plane.md",
        "reports/integration/e20_human_intervention_boundary.md",
        "reports/integration/e20_batch_autonomous_reclassification.md",
        "reports/integration/e20_provider_capability_detection.md",
        "reports/integration/e20_ecosystem_alignment_gate.md",
        "reports/integration/e20_route_decision_packet.md",
        "reports/integration/e20_future_outbound_policy.md",
        "reports/integration/e20_czl_closure.md",
    ]
    closure = build_czl_closure(control_room, route, ecosystem_gate, artifact_paths)
    outputs = {
        "operations/external_validation/e20_risk_tier_taxonomy.json": taxonomy,
        "operations/external_validation/e20_autonomous_execution_eligibility_rules.json": eligibility_rules,
        "operations/external_validation/e20_human_intervention_boundary.json": human_boundary,
        "operations/external_validation/e20_provider_capability_detection.json": provider_capability,
        "operations/external_validation/e20_autonomous_outbound_envelope_schema.json": envelope_schema,
        "operations/external_validation/e20_batch_autonomous_reclassification.json": reclassification,
        "operations/external_validation/e20_autonomous_control_room.json": control_room,
        "operations/external_validation/e20_ecosystem_alignment_gate.json": ecosystem_gate,
        "operations/external_validation/e20_repo_modification_decision_packet.json": repo_decision,
        "operations/external_validation/e20_route_decision_packet.json": route,
        "operations/external_validation/e20_future_outbound_policy.json": future_policy,
        "operations/external_validation/e20_czl_closure.json": closure,
    }
    for rel, data in outputs.items():
        write_json(output_root / rel, data)

    write_text(output_root / "operations/external_validation/e20_autonomous_control_room.md", render_autonomous_control_room(control_room))
    write_text(output_root / "reports/integration/e20_risk_tiered_autonomous_outbound_control_plane.md", render_main_report(taxonomy, control_room, route))
    write_text(output_root / "reports/integration/e20_human_intervention_boundary.md", render_human_intervention_boundary(human_boundary))
    write_text(output_root / "reports/integration/e20_batch_autonomous_reclassification.md", render_batch_autonomous_reclassification(reclassification))
    write_text(output_root / "reports/integration/e20_provider_capability_detection.md", render_provider_capability_detection(provider_capability))
    write_text(output_root / "reports/integration/e20_ecosystem_alignment_gate.md", render_ecosystem_alignment_gate(ecosystem_gate))
    write_text(output_root / "reports/integration/e20_route_decision_packet.md", render_route_decision(route))
    write_text(output_root / "reports/integration/e20_future_outbound_policy.md", render_future_outbound_policy(future_policy))
    write_text(output_root / "reports/integration/e20_czl_closure.md", render_czl_closure(closure))
    return sorted(artifact_paths)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create E20 risk-tiered autonomous outbound execution control plane.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    files = create_e20(Path(args.repo_root), Path(args.output_root))
    if args.json:
        print(json.dumps({"status": "created", "files": files}, indent=2))
    else:
        print(f"created {len(files)} E20 artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
