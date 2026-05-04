#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from office.mission_command.e19_commercial_route_decision import build_commercial_route_decision, render_commercial_route_decision
from office.mission_command.e19_cross_repo_impact_matrix import build_cross_repo_impact_matrix, render_cross_repo_impact_matrix
from office.mission_command.e19_ecosystem_alignment_scanner import build_ecosystem_alignment_scan, render_ecosystem_alignment_scan
from office.mission_command.e19_ecosystem_drift_register import build_ecosystem_drift_register, render_ecosystem_drift_register
from office.mission_command.e19_feedback_import_control_path import build_feedback_import_control_path, render_feedback_import_control_path
from office.mission_command.e19_future_alignment_gate import build_future_alignment_gate, render_future_alignment_gate
from office.mission_command.e19_owner_action_model import build_owner_action_model
from office.mission_command.e19_repo_modification_decision import build_repo_modification_decision_packet, render_repo_modification_decision_packet
from office.mission_command.e19_revenue_validation_control_room import build_revenue_validation_control_room, render_revenue_validation_control_room


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_czl_closure(scan: Dict[str, Any], route: Dict[str, Any], repo_decision: Dict[str, Any], artifacts: list[str]) -> Dict[str, Any]:
    return {
        "artifact_id": "e19_czl_closure",
        "Y_star": "E19 ecosystem-aligned revenue validation control room",
        "Xt": ["E18 revenue validation runtime", "gov-mcp outbound no-send boundary", "Y-star-gov governance kernel", "ystar-company historical assets"],
        "U": ["ecosystem alignment scan", "cross-repo impact matrix", "control room", "owner action model", "feedback import path", "drift register", "repo modification decision", "commercial route decision", "future alignment gate"],
        "Yt_plus_1": "Revenue validation batch can be operated from one owner surface while ecosystem boundaries and follow-up repo decisions are explicit.",
        "Rt_plus_1": 0,
        "ecosystem_alignment_status": scan["alignment_status"],
        "repos_checked": [repo["repo_name"] for repo in scan["repos"]],
        "bridge_labs_delivered_only": repo_decision["bridge_labs_only_delivery"],
        "no_real_external_action_occurred": True,
        "no_fake_target_evidence_created": True,
        "no_fake_feedback_created": True,
        "no_provider_api_called": True,
        "no_send_receipt_generated": True,
        "future_cross_repo_actions_routed_not_hidden": True,
        "recommended_route": route["recommended_route"],
        "artifacts": artifacts,
    }


def render_czl_closure(closure: Dict[str, Any]) -> str:
    lines = [
        "# E19 CZL Closure",
        "",
        f"- Y*: {closure['Y_star']}",
        f"- Yt+1: {closure['Yt_plus_1']}",
        f"- Rt+1: {closure['Rt_plus_1']}",
        f"- ecosystem_alignment_status: {closure['ecosystem_alignment_status']}",
        f"- bridge_labs_delivered_only: {str(closure['bridge_labs_delivered_only']).lower()}",
        f"- no_real_external_action_occurred: {str(closure['no_real_external_action_occurred']).lower()}",
        f"- no_fake_target_evidence_created: {str(closure['no_fake_target_evidence_created']).lower()}",
        f"- no_fake_feedback_created: {str(closure['no_fake_feedback_created']).lower()}",
        f"- no_provider_api_called: {str(closure['no_provider_api_called']).lower()}",
        f"- no_send_receipt_generated: {str(closure['no_send_receipt_generated']).lower()}",
        "",
        "## Repos Checked",
    ]
    lines.extend(f"- {repo}" for repo in closure["repos_checked"])
    return "\n".join(lines).rstrip() + "\n"


def create_e19(repo_root: Path, output_root: Path) -> list[str]:
    e18_batch = load_json(repo_root / "operations/external_validation/e18_revenue_validation_batch.json")
    e18_scores = load_json(repo_root / "operations/external_validation/e18_commercial_fit_scores.json")
    e18_console = load_json(repo_root / "operations/external_validation/e18_batch_owner_console.json")
    e18_tracker = load_json(repo_root / "operations/external_validation/e18_manual_send_tracker.json")
    e18_kpi = load_json(repo_root / "operations/external_validation/e18_commercial_kpi_packet.json")
    e18_route = load_json(repo_root / "operations/external_validation/e18_route_decision_packet.json")
    e18_schema = load_json(repo_root / "operations/external_validation/e18_batch_feedback_intake_schema.json")
    e18_empty = load_json(repo_root / "operations/external_validation/e18_batch_feedback_intake_empty.json")

    scan = build_ecosystem_alignment_scan()
    matrix = build_cross_repo_impact_matrix(scan)
    drift = build_ecosystem_drift_register(scan, matrix)
    control_room = build_revenue_validation_control_room(e18_batch, e18_scores, e18_console, e18_tracker, e18_kpi, e18_route, scan, drift)
    owner_action = build_owner_action_model()
    feedback_path = build_feedback_import_control_path(e18_schema, e18_empty)
    repo_decision = build_repo_modification_decision_packet(scan)
    commercial_route = build_commercial_route_decision(control_room, drift)
    future_gate = build_future_alignment_gate()

    artifact_paths = [
        "operations/external_validation/e19_ecosystem_alignment_scan.json",
        "operations/external_validation/e19_cross_repo_impact_matrix.json",
        "operations/external_validation/e19_revenue_validation_control_room.json",
        "operations/external_validation/e19_owner_action_model.json",
        "operations/external_validation/e19_feedback_import_control_path.json",
        "operations/external_validation/e19_ecosystem_drift_register.json",
        "operations/external_validation/e19_repo_modification_decision_packet.json",
        "operations/external_validation/e19_commercial_route_decision_packet.json",
        "operations/external_validation/e19_future_milestone_alignment_gate.json",
        "operations/external_validation/e19_czl_closure.json",
        "operations/external_validation/e19_revenue_validation_control_room.md",
        "reports/integration/e19_ecosystem_alignment_scan.md",
        "reports/integration/e19_cross_repo_impact_matrix.md",
        "reports/integration/e19_revenue_validation_control_room.md",
        "reports/integration/e19_feedback_import_control_path.md",
        "reports/integration/e19_ecosystem_drift_register.md",
        "reports/integration/e19_repo_modification_decision_packet.md",
        "reports/integration/e19_commercial_route_decision_packet.md",
        "reports/integration/e19_future_milestone_alignment_gate.md",
        "reports/integration/e19_czl_closure.md",
    ]
    closure = build_czl_closure(scan, commercial_route, repo_decision, artifact_paths)

    outputs = {
        "operations/external_validation/e19_ecosystem_alignment_scan.json": scan,
        "operations/external_validation/e19_cross_repo_impact_matrix.json": matrix,
        "operations/external_validation/e19_revenue_validation_control_room.json": control_room,
        "operations/external_validation/e19_owner_action_model.json": owner_action,
        "operations/external_validation/e19_feedback_import_control_path.json": feedback_path,
        "operations/external_validation/e19_ecosystem_drift_register.json": drift,
        "operations/external_validation/e19_repo_modification_decision_packet.json": repo_decision,
        "operations/external_validation/e19_commercial_route_decision_packet.json": commercial_route,
        "operations/external_validation/e19_future_milestone_alignment_gate.json": future_gate,
        "operations/external_validation/e19_czl_closure.json": closure,
    }
    for rel, data in outputs.items():
        write_json(output_root / rel, data)

    write_text(output_root / "operations/external_validation/e19_revenue_validation_control_room.md", render_revenue_validation_control_room(control_room))
    write_text(output_root / "reports/integration/e19_ecosystem_alignment_scan.md", render_ecosystem_alignment_scan(scan))
    write_text(output_root / "reports/integration/e19_cross_repo_impact_matrix.md", render_cross_repo_impact_matrix(matrix))
    write_text(output_root / "reports/integration/e19_revenue_validation_control_room.md", render_revenue_validation_control_room(control_room))
    write_text(output_root / "reports/integration/e19_feedback_import_control_path.md", render_feedback_import_control_path(feedback_path))
    write_text(output_root / "reports/integration/e19_ecosystem_drift_register.md", render_ecosystem_drift_register(drift))
    write_text(output_root / "reports/integration/e19_repo_modification_decision_packet.md", render_repo_modification_decision_packet(repo_decision))
    write_text(output_root / "reports/integration/e19_commercial_route_decision_packet.md", render_commercial_route_decision(commercial_route))
    write_text(output_root / "reports/integration/e19_future_milestone_alignment_gate.md", render_future_alignment_gate(future_gate))
    write_text(output_root / "reports/integration/e19_czl_closure.md", render_czl_closure(closure))
    return sorted(artifact_paths)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create E19 ecosystem-aligned revenue validation control room artifacts.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    files = create_e19(Path(args.repo_root), Path(args.output_root))
    if args.json:
        print(json.dumps({"status": "created", "files": files}, indent=2))
    else:
        print(f"created {len(files)} E19 artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
