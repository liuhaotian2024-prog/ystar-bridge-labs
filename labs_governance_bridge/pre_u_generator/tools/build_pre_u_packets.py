#!/usr/bin/env python3
"""Build dry-run Pre-U packets from curated role task envelopes."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
HINT_ROUTING = "runtime_artifact_quarantine/evidence_review/generated/hint_routing_index.json"
GENERATED_DIR = "labs_governance_bridge/pre_u_generator/generated"
MAX_HINT_REFS = 5

ROLE_CONFIG = {
    "Aiden-CEO": {
        "slug": "aiden",
        "sample": "labs_governance_bridge/pre_u_generator/samples/aiden_task_envelope.json",
        "profile": "agent_brains/Aiden-CEO/brain_profile.json",
        "packet": f"{GENERATED_DIR}/aiden_pre_u_packet.json",
    },
    "Ethan-CTO": {
        "slug": "ethan",
        "sample": "labs_governance_bridge/pre_u_generator/samples/ethan_task_envelope.json",
        "profile": "agent_brains/Ethan-CTO/brain_profile.json",
        "packet": f"{GENERATED_DIR}/ethan_pre_u_packet.json",
    },
    "Samantha-Secretary": {
        "slug": "samantha",
        "sample": "labs_governance_bridge/pre_u_generator/samples/samantha_task_envelope.json",
        "profile": "agent_brains/Samantha-Secretary/brain_profile.json",
        "packet": f"{GENERATED_DIR}/samantha_pre_u_packet.json",
    },
}

MANIFEST = f"{GENERATED_DIR}/pre_u_packet_manifest.json"
SUMMARY = f"{GENERATED_DIR}/pre_u_packet_summary.md"

FORBIDDEN_SOURCE_MARKERS = [
    ".db",
    ".db-wal",
    ".db-shm",
    "scripts/.logs",
    "active_agent",
    ".ystar_active_agent",
    ".pid",
    "daemon",
]


class PacketBuildError(Exception):
    """Raised when a Pre-U packet cannot be safely generated."""


def repo_path(relative_path: str) -> Path:
    lowered = relative_path.lower()
    for marker in FORBIDDEN_SOURCE_MARKERS:
        if marker in lowered:
            raise PacketBuildError(f"Refusing unsafe source path: {relative_path}")
    path = ROOT / relative_path
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise PacketBuildError(f"Refusing path outside repo: {relative_path}") from exc
    return path


def load_json(relative_path: str) -> Any:
    with repo_path(relative_path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(relative_path: str, payload: Any) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")


def write_text(relative_path: str, text: str) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(text)


def build_hint_refs(hint_routing: dict[str, Any], agent_id: str) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for route in hint_routing.get("routes", []):
        if len(refs) >= MAX_HINT_REFS:
            break
        refs.append(
            {
                "route": route.get("route"),
                "candidate_id": route.get("candidate_id"),
                "review_id": route.get("review_id"),
                "evidence_id": route.get("evidence_id"),
                "readiness": route.get("readiness"),
                "status": route.get("status"),
                "ingestion_status": route.get("ingestion_status"),
                "agent_scope": agent_id,
            }
        )
    return refs


def normalize_candidate(action: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": action.get("id"),
        "action_type": action.get("action_type"),
        "description": action.get("description"),
        "predicted_Yt_plus_1": action.get("predicted_Yt_plus_1"),
        "predicted_Rt_plus_1": action.get("predicted_Rt_plus_1"),
    }


def selected_candidate(task: dict[str, Any]) -> dict[str, Any]:
    selected_id = task.get("selected_action_id")
    for action in task.get("candidate_actions", []):
        if action.get("id") == selected_id:
            return action
    raise PacketBuildError(f"selected_action_id not present in candidate_actions: {selected_id}")


def build_packet(agent_id: str, config: dict[str, str], hint_routing: dict[str, Any]) -> dict[str, Any]:
    task = load_json(config["sample"])
    profile = load_json(config["profile"])
    if task.get("agent_id") != agent_id or profile.get("agent_id") != agent_id:
        raise PacketBuildError(f"Agent identity mismatch while building packet for {agent_id}")

    selected = selected_candidate(task)
    evidence_hint_refs = (task.get("evidence_hint_refs") or []) + build_hint_refs(hint_routing, agent_id)

    return {
        "schema_name": "ystar.labs_governance_bridge.pre_u_packet",
        "schema_version": "v0",
        "packet_id": f"preu-{task['task_id']}",
        "task_id": task["task_id"],
        "agent_id": agent_id,
        "role": task["role"],
        "agent_capsule_ref": config["profile"],
        "declared_Y_star": task["declared_objective"],
        "Xt": {
            "context": task.get("context", {}),
            "role_specific_focus": profile.get("role_specific_focus", []),
            "evidence_hint_refs": evidence_hint_refs,
        },
        "m_functor": {
            "summary": f"Map {agent_id} curated task envelope into dry-run governance packet.",
            "source": "labs_governance_bridge/pre_u_generator",
            "non_execution_boundary": True,
        },
        "candidate_U": [normalize_candidate(action) for action in task.get("candidate_actions", [])],
        "selected_U": {
            "selected_candidate_id": task["selected_action_id"],
            "selected_action": normalize_candidate(selected),
        },
        "predicted_Yt_plus_1": selected.get("predicted_Yt_plus_1") or task.get("predicted_outcome"),
        "predicted_Rt_plus_1": selected.get("predicted_Rt_plus_1") or task.get("predicted_residual"),
        "why_min_residual": task["why_min_residual"],
        "risk_tier": task.get("risk_tier", "normal"),
        "governance_expectations": task["governance_expectations"],
        "cieu_link_policy": task["cieu_link_policy"],
        "evidence_hint_refs": evidence_hint_refs,
        "packet_status": "generated_dry_run_only",
        "action_executed": False,
        "brain_writeback_allowed": False,
        "memory_ingestion_allowed": False,
        "cieu_write_allowed": False,
    }


def build_all_packets() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    hint_routing = load_json(HINT_ROUTING)
    packets: list[dict[str, Any]] = []
    for agent_id, config in ROLE_CONFIG.items():
        packet = build_packet(agent_id, config, hint_routing)
        write_json(config["packet"], packet)
        packets.append(packet)

    manifest = {
        "schema_name": "ystar.labs_governance_bridge.pre_u_packet_manifest",
        "schema_version": "v0",
        "generated_packets": [config["packet"] for config in ROLE_CONFIG.values()],
        "source_files": [HINT_ROUTING]
        + [config["sample"] for config in ROLE_CONFIG.values()]
        + [config["profile"] for config in ROLE_CONFIG.values()],
        "roles_covered": list(ROLE_CONFIG),
        "packets_generated": len(packets),
        "dry_run_only": True,
        "action_execution_allowed": False,
        "cieu_write_allowed": False,
        "brain_writeback_allowed": False,
        "memory_ingestion_allowed": False,
        "warning": "Generated Pre-U packets are dry-run only and are not runtime actions.",
    }
    write_json(MANIFEST, manifest)
    write_text(SUMMARY, render_summary(packets, manifest))
    return packets, manifest


def render_summary(packets: list[dict[str, Any]], manifest: dict[str, Any]) -> str:
    lines = [
        "# Pre-U Packet Summary",
        "",
        f"- Packets generated: {manifest['packets_generated']}",
        "- Roles covered:",
    ]
    for packet in packets:
        lines.append(f"  - {packet['agent_id']}: {packet['packet_id']}")
    lines.extend(
        [
            "",
            "Safety: packets are dry-run only and do not execute actions, write CIEU, ingest memory, or write brain state.",
            "",
        ]
    )
    return "\n".join(lines)


def print_report(packets: list[dict[str, Any]]) -> None:
    print("Pre-U Packet Builder: PASS")
    print(f"Packets generated: {len(packets)}")
    print("Roles covered:")
    for packet in packets:
        print(f"- {packet['agent_id']}: {packet['packet_id']}")
    print("Generated files:")
    for config in ROLE_CONFIG.values():
        print(f"- {config['packet']}")
    print(f"- {MANIFEST}")
    print(f"- {SUMMARY}")
    print("Safety note: generated packets are dry-run only.")


def main() -> int:
    try:
        packets, _manifest = build_all_packets()
    except Exception as exc:
        print("Pre-U Packet Builder: FAIL")
        print(f"Error: {exc}")
        return 1
    print_report(packets)
    return 0


if __name__ == "__main__":
    sys.exit(main())
