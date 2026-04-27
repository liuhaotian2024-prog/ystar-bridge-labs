#!/usr/bin/env python3
"""Read-only CLI for generated team console snapshots."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

SNAPSHOT = "console_read_model/generated/team_console_snapshot.json"
CARDS = "console_read_model/generated/agent_cards_compiled.json"
READINESS = "console_read_model/generated/readiness_summary.json"
MANIFEST = "console_read_model/generated/generation_manifest.json"
QUARANTINE = "console_read_model/generated/quarantine_summary.json"
MINING = "console_read_model/generated/safe_mining_summary.json"
REQUIRED_AGENTS = ["Aiden-CEO", "Ethan-CTO", "Samantha-Secretary"]
UNSAFE_MARKERS = [
    ".db",
    ".db-wal",
    ".db-shm",
    "scripts/.logs",
    "__pycache__",
    "active-agent",
    ".pid",
    "daemon",
    "reports/ceo/brain_dream_diffs",
    "reports/escalation",
    "reports/drift_hourly",
]


def usage() -> str:
    return (
        "Usage: python3 console_read_model/cli/team_console.py "
        "{summary|agents|agent <agent_id>|readiness|capabilities|governance|quarantine|mining-candidates|gaps|sources|warnings|validate-local}"
    )


def ensure_safe_path(relative_path: str) -> Path:
    lowered = relative_path.lower()
    for marker in UNSAFE_MARKERS:
        m = marker.lower()
        if m in {".db", ".db-wal", ".db-shm"}:
            if lowered.endswith(m):
                raise ValueError(f"Refusing unsafe source: {relative_path}")
        elif m in lowered:
            raise ValueError(f"Refusing unsafe source: {relative_path}")
    path = ROOT / relative_path
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"Refusing path outside repo: {relative_path}") from exc
    return path


def load_json(relative_path: str) -> Any:
    path = ensure_safe_path(relative_path)
    if not path.exists():
        raise FileNotFoundError(f"Required snapshot missing: {relative_path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_all() -> dict[str, Any]:
    return {
        "snapshot": load_json(SNAPSHOT),
        "cards": load_json(CARDS),
        "readiness": load_json(READINESS),
        "manifest": load_json(MANIFEST),
        "quarantine": load_json(QUARANTINE),
        "mining": load_json(MINING),
    }


def bullet_list(items: list[Any]) -> None:
    for item in items:
        print(f"- {item}")


def cmd_summary(data: dict[str, Any]) -> None:
    snapshot = data["snapshot"]
    readiness = data["readiness"]
    print("# Team Brain Console Snapshot")
    print()
    print(f"model_status: {snapshot.get('schema_name')} / {snapshot.get('schema_version')}")
    print()
    print("Agents included:")
    for agent in snapshot.get("agents", []):
        print(f"- {agent['agent_id']} ({agent.get('readiness_level')})")
    print()
    print("Ready now:")
    bullet_list(readiness.get("ready_now", []))
    print()
    print("Governance:")
    print(snapshot.get("governance_summary", {}).get("principle", "not recorded"))
    print()
    print("Warnings:")
    warnings = snapshot.get("warnings", [])
    bullet_list(warnings or ["none"])


def cmd_agents(data: dict[str, Any]) -> None:
    print("# Agents")
    for agent in data["snapshot"].get("agents", []):
        print()
        print(f"## {agent['agent_id']}")
        print(f"- role: {agent.get('role_type')}")
        print(f"- readiness: {agent.get('readiness_level')} / {agent.get('card_status')}")
        print(f"- focus: {agent.get('focus')}")


def card_by_id(data: dict[str, Any], agent_id: str) -> dict[str, Any] | None:
    for card in data["cards"].get("cards", []):
        if card.get("card_id") == agent_id:
            return card
    return None


def cmd_agent(data: dict[str, Any], agent_id: str) -> int:
    card = card_by_id(data, agent_id)
    if not card:
        print(f"Unknown agent: {agent_id}")
        return 1
    print(f"# {agent_id}")
    print(f"display_name: {card.get('display_name')}")
    print(f"role: {card.get('role')}")
    print(f"status: {card.get('status')}")
    print()
    print("primary_focus:")
    bullet_list(card.get("primary_focus", []))
    print()
    print("capabilities:")
    bullet_list(card.get("capabilities", []))
    print()
    print("limitations:")
    bullet_list(card.get("limitations", []))
    print()
    print("next_actions:")
    bullet_list(card.get("next_actions", []))
    print()
    print("warnings:")
    bullet_list(card.get("warnings", []) or ["none"])
    return 0


def cmd_readiness(data: dict[str, Any]) -> None:
    readiness = data["readiness"]
    print("# Readiness")
    for key in ["ready_now", "not_ready", "recommended_next_steps", "blockers", "safety_boundaries"]:
        print()
        print(f"## {key}")
        bullet_list(readiness.get(key, []))


def cmd_capabilities(data: dict[str, Any]) -> None:
    matrix = data["snapshot"].get("capabilities", {})
    print("# Capabilities")
    print()
    print("Agents:")
    bullet_list(matrix.get("agents", []))
    print()
    print("Matrix:")
    for capability, values in matrix.get("matrix", {}).items():
        rendered = ", ".join(f"{agent}={status}" for agent, status in values.items())
        print(f"- {capability}: {rendered}")


def cmd_governance(data: dict[str, Any]) -> None:
    print("# Governance")
    print("- labs thinks")
    print("- Y-star-gov judges")
    print("- hook enforces")
    print("- CIEU records/teaches")
    print("- brain learns")
    print("- console reads curated snapshots only")
    print()
    summary = data["snapshot"].get("governance_summary", {})
    for key, value in summary.items():
        print(f"- {key}: {value}")


def cmd_quarantine(data: dict[str, Any]) -> None:
    quarantine = data["quarantine"]
    print("# Runtime Artifact Quarantine Summary")
    print()
    print(f"framework_status: {quarantine.get('framework_status')}")
    print(f"current_mining_level: {quarantine.get('current_mining_level')}")
    print(f"artifacts_classified: {quarantine.get('artifacts_classified')}")
    print(f"unsafe_artifacts_count: {quarantine.get('unsafe_artifacts_count')}")
    print()
    print("classes_seen:")
    for class_name, count in sorted(quarantine.get("classes_seen", {}).items()):
        print(f"- {class_name}: {count}")
    print()
    print("forbidden_direct_reads:")
    bullet_list(quarantine.get("forbidden_direct_reads", []))
    print()
    print("future_adapter_candidates:")
    bullet_list(quarantine.get("future_adapter_candidates", []))
    print()
    print(f"generated_manifest_ref: {quarantine.get('generated_manifest_ref')}")
    print(f"warning: {quarantine.get('safety_warning')}")


def cmd_mining_candidates(data: dict[str, Any]) -> None:
    mining = data["mining"]
    print("# Runtime Artifact Safe Mining Candidates")
    print()
    print(f"candidate_count: {mining.get('candidate_count')}")
    print(f"safety_level: {mining.get('safety_level')}")
    print(f"ingestion_status: {mining.get('ingestion_status')}")
    print(f"generated_candidate_index: {mining.get('generated_candidate_index')}")
    print()
    print("classes_seen:")
    for class_name, count in sorted(mining.get("classes_seen", {}).items()):
        print(f"- {class_name}: {count}")
    print()
    print(f"allowed_next_step: {mining.get('allowed_next_step')}")
    print(f"forbidden_next_step: {mining.get('forbidden_next_step')}")
    print(f"warning: {mining.get('warning')}")


def cmd_gaps(data: dict[str, Any]) -> None:
    print("# Gaps")
    bullet_list(data["snapshot"].get("open_gaps", []))
    for item in data["readiness"].get("blockers", []):
        print(f"- blocker: {item}")


def cmd_sources(data: dict[str, Any]) -> None:
    manifest = data["manifest"]
    print("# Sources")
    print()
    print("Source files:")
    bullet_list(manifest.get("source_files", []))
    print()
    print("Unsafe sources not read:")
    bullet_list(manifest.get("unsafe_sources_not_read", []))
    quarantine = data.get("quarantine", {})
    if quarantine:
        print()
        print("Quarantine manifest:")
        print(f"- {quarantine.get('generated_manifest_ref')}")
    mining = data.get("mining", {})
    if mining:
        print()
        print("Safe mining candidate index:")
        print(f"- {mining.get('generated_candidate_index')}")


def cmd_warnings(data: dict[str, Any]) -> None:
    print("# Warnings")
    bullet_list(data["snapshot"].get("warnings", []) or ["none"])


def source_has_unsafe_marker(source: str) -> str | None:
    lowered = source.lower()
    for marker in UNSAFE_MARKERS:
        m = marker.lower()
        if m in {".db", ".db-wal", ".db-shm"}:
            if lowered.endswith(m):
                return marker
        elif m in lowered:
            return marker
    return None


def cmd_validate_local() -> int:
    failures: list[str] = []
    inspected: list[str] = []
    loaded: dict[str, Any] = {}
    for rel in [SNAPSHOT, CARDS, READINESS, MANIFEST, QUARANTINE, MINING]:
        try:
            loaded[rel] = load_json(rel)
            inspected.append(rel)
        except Exception as exc:
            failures.append(str(exc))

    snapshot = loaded.get(SNAPSHOT)
    if snapshot:
        agents = {agent.get("agent_id") for agent in snapshot.get("agents", [])}
        for agent_id in REQUIRED_AGENTS:
            if agent_id not in agents:
                failures.append(f"required agent missing from snapshot: {agent_id}")
        if "quarantine_summary" not in snapshot:
            failures.append("quarantine_summary missing from team console snapshot")
        if "safe_mining_summary" not in snapshot:
            failures.append("safe_mining_summary missing from team console snapshot")

    manifest = loaded.get(MANIFEST)
    if manifest:
        for source in manifest.get("source_files", []):
            marker = source_has_unsafe_marker(str(source))
            if marker:
                failures.append(f"unsafe source in manifest: {source} ({marker})")

    quarantine = loaded.get(QUARANTINE)
    if quarantine:
        required_fields = [
            "framework_status",
            "current_mining_level",
            "artifacts_classified",
            "unsafe_artifacts_count",
            "classes_seen",
            "generated_manifest_ref",
            "forbidden_direct_reads",
            "future_adapter_candidates",
            "safety_warning",
        ]
        for field in required_fields:
            if field not in quarantine:
                failures.append(f"quarantine summary missing field: {field}")

    mining = loaded.get(MINING)
    if mining:
        required_fields = [
            "candidate_count",
            "classes_seen",
            "generated_candidate_index",
            "safety_level",
            "ingestion_status",
            "allowed_next_step",
            "forbidden_next_step",
            "warning",
        ]
        for field in required_fields:
            if field not in mining:
                failures.append(f"safe mining summary missing field: {field}")
        if mining.get("ingestion_status") != "candidate_only":
            failures.append("safe mining summary must remain candidate_only")
        if mining.get("forbidden_next_step") != "direct_brain_writeback":
            failures.append("safe mining summary must forbid direct brain writeback")

    print(f"Team Console CLI validate-local: {'PASS' if not failures else 'FAIL'}")
    print(f"Generated JSON files inspected: {len(inspected)}")
    print(f"Required agents: {', '.join(REQUIRED_AGENTS)}")
    if failures:
        print()
        print("Failures:")
        bullet_list(failures)
        return 1
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(usage())
        return 1

    command = argv[1]
    if command == "validate-local":
        return cmd_validate_local()

    try:
        data = load_all()
    except Exception as exc:
        print(f"Failed to load generated snapshots: {exc}")
        return 1

    if command == "summary":
        cmd_summary(data)
    elif command == "agents":
        cmd_agents(data)
    elif command == "agent":
        if len(argv) != 3:
            print("Usage: agent <agent_id>")
            return 1
        return cmd_agent(data, argv[2])
    elif command == "readiness":
        cmd_readiness(data)
    elif command == "capabilities":
        cmd_capabilities(data)
    elif command == "governance":
        cmd_governance(data)
    elif command == "quarantine":
        cmd_quarantine(data)
    elif command == "mining-candidates":
        cmd_mining_candidates(data)
    elif command == "gaps":
        cmd_gaps(data)
    elif command == "sources":
        cmd_sources(data)
    elif command == "warnings":
        cmd_warnings(data)
    else:
        print(f"Invalid command: {command}")
        print(usage())
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
