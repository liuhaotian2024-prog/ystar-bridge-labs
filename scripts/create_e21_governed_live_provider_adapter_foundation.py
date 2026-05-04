#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from office.mission_command.e21_autonomous_provider_control_room import build_autonomous_provider_control_room, render_autonomous_provider_control_room
from office.mission_command.e21_batch_provider_reclassification import build_batch_provider_reclassification, render_batch_provider_reclassification
from office.mission_command.e21_ecosystem_alignment_gate import build_e21_ecosystem_alignment_gate, render_ecosystem_alignment_gate
from office.mission_command.e21_future_provider_policy import build_future_provider_policy, render_future_provider_policy
from office.mission_command.e21_provider_capability_sync import build_provider_capability_sync, render_provider_capability_sync
from office.mission_command.e21_provider_promotion_gate import build_provider_promotion_gate, render_provider_promotion_gate
from office.mission_command.e21_route_decision import build_e21_route_decision, render_route_decision


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_czl(provider_sync: Dict[str, Any], gate: Dict[str, Any], route: Dict[str, Any], artifacts: list[str]) -> Dict[str, Any]:
    return {
        "artifact_id": "e21_czl_closure",
        "Y_star": "E21 governed live provider adapter foundation",
        "Xt": ["E20 autonomous outbound control plane", "gov-mcp provider adapter foundation", "four-repo ecosystem scan"],
        "U": ["provider capability sync", "batch provider reclassification", "autonomous provider control room", "promotion gate", "ecosystem alignment gate", "route decision", "future provider policy"],
        "Yt_plus_1": "Low-risk outbound can now be dry-run through a canonical provider foundation; live send remains blocked until provider is live_ready and promotion gates pass.",
        "Rt_plus_1": 0,
        "ecosystem_alignment_status": gate["closure_status"],
        "no_real_external_action_occurred": True,
        "no_provider_api_called": True,
        "no_message_sent": True,
        "no_live_receipt_created": True,
        "dry_run_and_live_receipts_remain_distinct": provider_sync["dry_run_and_live_receipts_distinct"],
        "live_provider_capability_honestly_reported": provider_sync["capability_status"],
        "owner_manual_send_is_not_default": True,
        "high_risk_human_intervention_boundary_intact": True,
        "recommended_route": route["recommended_route"],
        "artifacts": artifacts,
    }


def render_czl(closure: Dict[str, Any]) -> str:
    lines = [
        "# E21 CZL Closure",
        "",
        f"- Y*: {closure['Y_star']}",
        f"- Yt+1: {closure['Yt_plus_1']}",
        f"- Rt+1: {closure['Rt_plus_1']}",
        f"- ecosystem_alignment_status: {closure['ecosystem_alignment_status']}",
        f"- no_real_external_action_occurred: {str(closure['no_real_external_action_occurred']).lower()}",
        f"- no_provider_api_called: {str(closure['no_provider_api_called']).lower()}",
        f"- no_message_sent: {str(closure['no_message_sent']).lower()}",
        f"- no_live_receipt_created: {str(closure['no_live_receipt_created']).lower()}",
        f"- owner_manual_send_is_not_default: {str(closure['owner_manual_send_is_not_default']).lower()}",
        "",
        "## U",
    ]
    lines.extend(f"- {item}" for item in closure["U"])
    return "\n".join(lines).rstrip() + "\n"


def render_main(provider_sync: Dict[str, Any], control_room: Dict[str, Any], route: Dict[str, Any]) -> str:
    return "\n".join([
        "# E21 Governed Live Provider Adapter Foundation",
        "",
        "E21 adds the provider substrate for future governed autonomous outbound execution without enabling live sends.",
        "",
        f"- provider_capability_status: {provider_sync['capability_status']}",
        f"- dry_run_available_actions: {len(control_room['dry_run_available_actions'])}",
        f"- live_scaffolded_but_disabled_actions: {len(control_room['live_scaffolded_but_disabled_actions'])}",
        f"- live_ready_actions: {len(control_room['live_ready_actions'])}",
        f"- recommended_route: {route['recommended_route']}",
        "- external_action_executed: false",
    ]).rstrip() + "\n"


def create_e21(repo_root: Path, output_root: Path) -> list[str]:
    e20_reclassification = load_json(repo_root / "operations/external_validation/e20_batch_autonomous_reclassification.json")
    provider_sync = build_provider_capability_sync()
    batch_reclassification = build_batch_provider_reclassification(e20_reclassification, provider_sync)
    promotion_gate = build_provider_promotion_gate(provider_sync, batch_reclassification)
    route = build_e21_route_decision(provider_sync, batch_reclassification, promotion_gate)
    control_room = build_autonomous_provider_control_room(provider_sync, batch_reclassification, promotion_gate, route)
    ecosystem_gate = build_e21_ecosystem_alignment_gate(provider_sync)
    repo_decision = {
        "artifact_id": "e21_repo_modification_decision_packet",
        "gov_mcp_modified_and_delivered": True,
        "bridge_labs_modified_and_delivered": True,
        "decisions": ecosystem_gate["repo_modification_decisions"],
        "cross_repo_mutation_hidden": False,
        "external_action_executed": False,
    }
    future_policy = build_future_provider_policy()
    artifact_paths = [
        "operations/external_validation/e21_provider_capability_sync.json",
        "operations/external_validation/e21_batch_provider_reclassification.json",
        "operations/external_validation/e21_autonomous_provider_control_room.json",
        "operations/external_validation/e21_provider_promotion_gate.json",
        "operations/external_validation/e21_ecosystem_alignment_gate.json",
        "operations/external_validation/e21_repo_modification_decision_packet.json",
        "operations/external_validation/e21_route_decision_packet.json",
        "operations/external_validation/e21_future_provider_policy.json",
        "operations/external_validation/e21_czl_closure.json",
        "operations/external_validation/e21_autonomous_provider_control_room.md",
        "reports/integration/e21_governed_live_provider_adapter_foundation.md",
        "reports/integration/e21_provider_capability_sync.md",
        "reports/integration/e21_batch_provider_reclassification.md",
        "reports/integration/e21_provider_promotion_gate.md",
        "reports/integration/e21_ecosystem_alignment_gate.md",
        "reports/integration/e21_route_decision_packet.md",
        "reports/integration/e21_future_provider_policy.md",
        "reports/integration/e21_czl_closure.md",
    ]
    closure = build_czl(provider_sync, ecosystem_gate, route, artifact_paths)
    outputs = {
        "operations/external_validation/e21_provider_capability_sync.json": provider_sync,
        "operations/external_validation/e21_batch_provider_reclassification.json": batch_reclassification,
        "operations/external_validation/e21_autonomous_provider_control_room.json": control_room,
        "operations/external_validation/e21_provider_promotion_gate.json": promotion_gate,
        "operations/external_validation/e21_ecosystem_alignment_gate.json": ecosystem_gate,
        "operations/external_validation/e21_repo_modification_decision_packet.json": repo_decision,
        "operations/external_validation/e21_route_decision_packet.json": route,
        "operations/external_validation/e21_future_provider_policy.json": future_policy,
        "operations/external_validation/e21_czl_closure.json": closure,
    }
    for rel, data in outputs.items():
        write_json(output_root / rel, data)
    write_text(output_root / "operations/external_validation/e21_autonomous_provider_control_room.md", render_autonomous_provider_control_room(control_room))
    write_text(output_root / "reports/integration/e21_governed_live_provider_adapter_foundation.md", render_main(provider_sync, control_room, route))
    write_text(output_root / "reports/integration/e21_provider_capability_sync.md", render_provider_capability_sync(provider_sync))
    write_text(output_root / "reports/integration/e21_batch_provider_reclassification.md", render_batch_provider_reclassification(batch_reclassification))
    write_text(output_root / "reports/integration/e21_provider_promotion_gate.md", render_provider_promotion_gate(promotion_gate))
    write_text(output_root / "reports/integration/e21_ecosystem_alignment_gate.md", render_ecosystem_alignment_gate(ecosystem_gate))
    write_text(output_root / "reports/integration/e21_route_decision_packet.md", render_route_decision(route))
    write_text(output_root / "reports/integration/e21_future_provider_policy.md", render_future_provider_policy(future_policy))
    write_text(output_root / "reports/integration/e21_czl_closure.md", render_czl(closure))
    return sorted(artifact_paths)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create E21 governed live provider adapter foundation alignment artifacts.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    files = create_e21(Path(args.repo_root), Path(args.output_root))
    if args.json:
        print(json.dumps({"status": "created", "files": files}, indent=2))
    else:
        print(f"created {len(files)} E21 artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
