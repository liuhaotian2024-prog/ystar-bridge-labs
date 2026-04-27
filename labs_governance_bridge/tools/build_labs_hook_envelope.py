#!/usr/bin/env python3
"""Build a Y-star-gov-compatible hook envelope from curated labs inputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SAMPLE_TASK = "labs_governance_bridge/samples/sample_labs_task.json"
AIDEN_PROFILE = "agent_brains/Aiden-CEO/brain_profile.json"
HINT_ROUTING = "runtime_artifact_quarantine/evidence_review/generated/hint_routing_index.json"
GENERATED_ENVELOPE = "labs_governance_bridge/generated/sample_hook_envelope.json"
GENERATED_MANIFEST = "labs_governance_bridge/generated/envelope_manifest.json"
MAX_HINT_REFS = 5

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


class BridgeBuildError(Exception):
    """Raised when the bridge envelope cannot be built safely."""


def repo_path(relative_path: str) -> Path:
    path = ROOT / relative_path
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise BridgeBuildError(f"Refusing path outside repo: {relative_path}") from exc
    lowered = relative_path.lower()
    for marker in FORBIDDEN_SOURCE_MARKERS:
        if marker in lowered:
            raise BridgeBuildError(f"Refusing unsafe bridge source path: {relative_path}")
    return path


def load_json(relative_path: str) -> Any:
    path = repo_path(relative_path)
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(relative_path: str, payload: Any) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")


def build_hint_refs(hint_routing: dict[str, Any]) -> list[dict[str, Any]]:
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


def build_envelope() -> tuple[dict[str, Any], dict[str, Any]]:
    task = load_json(SAMPLE_TASK)
    profile = load_json(AIDEN_PROFILE)
    hint_routing = load_json(HINT_ROUTING)

    if task.get("agent_id") != profile.get("agent_id"):
        raise BridgeBuildError("Sample task agent_id does not match Aiden profile agent_id.")

    hint_refs = build_hint_refs(hint_routing)
    task_hint_refs = task.get("evidence_hint_refs") or []
    evidence_hint_refs = task_hint_refs + hint_refs

    envelope = {
        "hook_event_id": f"labs-gov-bridge-{task['task_id']}",
        "agent_id": task["agent_id"],
        "agent_capsule_ref": "agent_brains/Aiden-CEO/brain_profile.json",
        "packet_id": f"preu-{task['task_id']}",
        "task_id": task["task_id"],
        "risk_tier": task.get("risk_tier", "normal"),
        "declared_Y_star": task["declared_objective"],
        "Xt": {
            "context": task.get("context", {}),
            "role": task.get("role"),
            "evidence_hint_refs": evidence_hint_refs,
        },
        "m_functor": {
            "summary": "Map curated labs evidence hints into a dry-run governance envelope.",
            "source": "labs_governance_bridge",
            "non_execution_boundary": True,
        },
        "candidate_U": [normalize_candidate(action) for action in task.get("candidate_actions", [])],
        "selected_U_id": task["selected_action_id"],
        "why_min_residual": task["why_min_residual"],
        "governance_expectations": task["governance_expectations"],
        "cieu_link_policy": task["cieu_link_policy"],
    }

    manifest = {
        "schema_name": "ystar.labs_governance_bridge.envelope_manifest",
        "schema_version": "v0",
        "generated_envelope": GENERATED_ENVELOPE,
        "source_files": [
            SAMPLE_TASK,
            AIDEN_PROFILE,
            HINT_ROUTING,
        ],
        "hint_refs_included": len(evidence_hint_refs),
        "dry_run_only": True,
        "action_execution_allowed": False,
        "cieu_write_allowed": False,
        "brain_writeback_allowed": False,
        "memory_ingestion_allowed": False,
        "warning": "Generated envelope is for Y-star-gov dry-run judgment only.",
    }
    return envelope, manifest


def print_report(envelope: dict[str, Any], manifest: dict[str, Any]) -> None:
    print("Labs Hook Envelope Builder: PASS")
    print(f"agent_id: {envelope.get('agent_id')}")
    print(f"packet_id: {envelope.get('packet_id')}")
    print(f"selected_U_id: {envelope.get('selected_U_id')}")
    print(f"hint_refs_included: {manifest.get('hint_refs_included')}")
    print("Generated files:")
    print(f"- {GENERATED_ENVELOPE}")
    print(f"- {GENERATED_MANIFEST}")
    print("Safety note: envelope generation does not call Y-star-gov or execute actions.")


def main() -> int:
    try:
        envelope, manifest = build_envelope()
        write_json(GENERATED_ENVELOPE, envelope)
        write_json(GENERATED_MANIFEST, manifest)
    except Exception as exc:
        print("Labs Hook Envelope Builder: FAIL")
        print(f"Error: {exc}")
        return 1
    print_report(envelope, manifest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
