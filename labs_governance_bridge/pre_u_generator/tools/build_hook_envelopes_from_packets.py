#!/usr/bin/env python3
"""Convert generated Pre-U packets into Y-star-gov hook envelopes."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
GENERATED_DIR = "labs_governance_bridge/pre_u_generator/generated"
PACKET_FILES = {
    "Aiden-CEO": f"{GENERATED_DIR}/aiden_pre_u_packet.json",
    "Ethan-CTO": f"{GENERATED_DIR}/ethan_pre_u_packet.json",
    "Samantha-Secretary": f"{GENERATED_DIR}/samantha_pre_u_packet.json",
}
ENVELOPE_FILES = {
    "Aiden-CEO": f"{GENERATED_DIR}/aiden_hook_envelope.json",
    "Ethan-CTO": f"{GENERATED_DIR}/ethan_hook_envelope.json",
    "Samantha-Secretary": f"{GENERATED_DIR}/samantha_hook_envelope.json",
}
MANIFEST = f"{GENERATED_DIR}/hook_envelope_manifest.json"


class EnvelopeBuildError(Exception):
    """Raised when a hook envelope cannot be built safely."""


def load_json(relative_path: str) -> Any:
    path = ROOT / relative_path
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(relative_path: str, payload: Any) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")


def normalize_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": candidate.get("id"),
        "action_type": candidate.get("action_type"),
        "description": candidate.get("description"),
        "predicted_Yt_plus_1": candidate.get("predicted_Yt_plus_1"),
        "predicted_Rt_plus_1": candidate.get("predicted_Rt_plus_1"),
    }


def build_envelope(packet: dict[str, Any]) -> dict[str, Any]:
    selected = packet.get("selected_U", {})
    selected_id = selected.get("selected_candidate_id")
    if not selected_id:
        raise EnvelopeBuildError(f"packet missing selected_U.selected_candidate_id: {packet.get('packet_id')}")

    return {
        "hook_event_id": f"preu-governance-{packet['task_id']}",
        "agent_id": packet["agent_id"],
        "agent_capsule_ref": packet.get("agent_capsule_ref"),
        "packet_id": packet["packet_id"],
        "task_id": packet["task_id"],
        "risk_tier": packet.get("risk_tier", "normal"),
        "declared_Y_star": packet["declared_Y_star"],
        "Xt": packet["Xt"],
        "m_functor": packet["m_functor"],
        "candidate_U": [normalize_candidate(candidate) for candidate in packet.get("candidate_U", [])],
        "selected_U_id": selected_id,
        "why_min_residual": packet["why_min_residual"],
        "governance_expectations": packet["governance_expectations"],
        "cieu_link_policy": packet["cieu_link_policy"],
    }


def build_all_envelopes() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    envelopes: list[dict[str, Any]] = []
    for agent_id, packet_file in PACKET_FILES.items():
        packet = load_json(packet_file)
        envelope = build_envelope(packet)
        write_json(ENVELOPE_FILES[agent_id], envelope)
        envelopes.append(envelope)

    manifest = {
        "schema_name": "ystar.labs_governance_bridge.hook_envelope_manifest",
        "schema_version": "v0",
        "source_packets": list(PACKET_FILES.values()),
        "generated_envelopes": list(ENVELOPE_FILES.values()),
        "roles_covered": list(PACKET_FILES),
        "envelopes_generated": len(envelopes),
        "dry_run_only": True,
        "action_execution_allowed": False,
        "cieu_write_allowed": False,
        "brain_writeback_allowed": False,
        "memory_ingestion_allowed": False,
        "warning": "Hook envelopes are for Y-star-gov dry-run judgment only.",
    }
    write_json(MANIFEST, manifest)
    return envelopes, manifest


def print_report(envelopes: list[dict[str, Any]]) -> None:
    print("Pre-U Hook Envelope Builder: PASS")
    print(f"Envelopes generated: {len(envelopes)}")
    for envelope in envelopes:
        print(f"- {envelope['agent_id']}: {envelope['packet_id']}")
    print("Generated files:")
    for path in ENVELOPE_FILES.values():
        print(f"- {path}")
    print(f"- {MANIFEST}")
    print("Safety note: envelope generation does not call Y-star-gov or execute actions.")


def main() -> int:
    try:
        envelopes, _manifest = build_all_envelopes()
    except Exception as exc:
        print("Pre-U Hook Envelope Builder: FAIL")
        print(f"Error: {exc}")
        return 1
    print_report(envelopes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
