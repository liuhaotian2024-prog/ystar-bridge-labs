#!/usr/bin/env python3
"""Build a static team console snapshot from curated read-model files only."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "console_read_model" / "generated"
GENERATOR_VERSION = "v0"

CURATED_SOURCES = [
    "console_read_model/team_brain_read_model.json",
    "console_read_model/agent_cards.json",
    "console_read_model/capability_matrix.json",
    "agent_brains/team_capsule_map.json",
    "agent_brains/Aiden-CEO/brain_profile.json",
    "agent_brains/Ethan-CTO/brain_profile.json",
    "agent_brains/Samantha-Secretary/brain_profile.json",
    "agent_brains/Ethan-CTO/execution_channels.json",
    "runtime_artifact_quarantine/quarantine_index.json",
    "runtime_artifact_quarantine/generated/runtime_artifact_manifest.json",
    "runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.json",
]

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


class BuildError(Exception):
    """Raised when the static snapshot cannot be built safely."""


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def assert_safe_source(path: Path) -> None:
    try:
        relative = rel(path)
    except ValueError as exc:
        raise BuildError(f"Refusing path outside repo: {path}") from exc

    lowered = relative.lower()
    for marker in UNSAFE_MARKERS:
        m = marker.lower()
        if m in {".db", ".db-wal", ".db-shm"}:
            if lowered.endswith(m):
                raise BuildError(f"Refusing unsafe source: {relative}")
        elif m in lowered:
            raise BuildError(f"Refusing unsafe source: {relative}")


def load_json(relative_path: str, files_read: list[str]) -> Any:
    path = ROOT / relative_path
    assert_safe_source(path)
    if not path.exists():
        raise BuildError(f"Missing curated source: {relative_path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    files_read.append(relative_path)
    return data


def write_json(relative_path: str, payload: Any, generated_files: list[str]) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
    generated_files.append(relative_path)


def write_text(relative_path: str, text: str, generated_files: list[str]) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)
    generated_files.append(relative_path)


def build_quarantine_summary(
    quarantine_index: dict[str, Any],
    quarantine_manifest: dict[str, Any],
) -> dict[str, Any]:
    artifacts = quarantine_manifest.get("artifacts", [])
    future_adapter_candidates = sorted(
        {
            artifact.get("future_adapter_candidate")
            for artifact in artifacts
            if artifact.get("future_adapter_candidate")
            and artifact.get("future_adapter_candidate") not in {"none", "none_or_metadata_only"}
        }
    )
    if not future_adapter_candidates:
        future_adapter_candidates = quarantine_index.get("future_adapters", [])

    return {
        "schema_name": "ystar.console_read_model.generated.quarantine_summary",
        "schema_version": "v0",
        "framework_status": quarantine_index.get("framework_status"),
        "current_mining_level": quarantine_index.get("current_mining_level"),
        "artifacts_classified": quarantine_manifest.get("artifacts_classified", 0),
        "unsafe_artifacts_count": quarantine_manifest.get("unsafe_artifacts_count", 0),
        "classes_seen": quarantine_manifest.get("classes_seen", {}),
        "generated_manifest_ref": quarantine_index.get(
            "generated_manifest_ref",
            "runtime_artifact_quarantine/generated/runtime_artifact_manifest.json",
        ),
        "forbidden_direct_reads": quarantine_index.get("forbidden_direct_reads", []),
        "future_adapter_candidates": future_adapter_candidates,
        "safety_warning": (
            "Console displays only curated path-level quarantine summary. "
            "No artifact contents were read."
        ),
    }


def build_safe_mining_summary(candidate_index: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.console_read_model.generated.safe_mining_summary",
        "schema_version": "v0",
        "candidate_count": candidate_index.get("candidate_count", 0),
        "classes_seen": candidate_index.get("classes_seen", {}),
        "generated_candidate_index": (
            "runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.json"
        ),
        "mining_manifest_ref": "runtime_artifact_quarantine/safe_mining/generated/mining_manifest.json",
        "safety_level": candidate_index.get("safety_level", "bounded_markdown_candidate"),
        "ingestion_status": candidate_index.get("ingestion_status", "candidate_only"),
        "allowed_next_step": candidate_index.get("allowed_next_step", "human_review_or_curated_queue"),
        "forbidden_next_step": candidate_index.get("forbidden_next_step", "direct_brain_writeback"),
        "allowed_artifact_classes": candidate_index.get("allowed_artifact_classes", []),
        "bounds": candidate_index.get("bounds", {}),
        "warning": (
            "Safe mining candidates are bounded review assets only. They are not brain memory, "
            "CIEU records, or approved writeback."
        ),
    }


def build() -> tuple[list[str], list[str], list[str], list[str]]:
    files_read: list[str] = []
    generated_files: list[str] = []
    warnings: list[str] = []

    team_model = load_json("console_read_model/team_brain_read_model.json", files_read)
    agent_cards = load_json("console_read_model/agent_cards.json", files_read)
    capability_matrix = load_json("console_read_model/capability_matrix.json", files_read)
    team_capsules = load_json("agent_brains/team_capsule_map.json", files_read)
    quarantine_index = load_json("runtime_artifact_quarantine/quarantine_index.json", files_read)
    quarantine_manifest = load_json(
        "runtime_artifact_quarantine/generated/runtime_artifact_manifest.json",
        files_read,
    )
    safe_mining_candidates = load_json(
        "runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.json",
        files_read,
    )
    quarantine_summary = build_quarantine_summary(quarantine_index, quarantine_manifest)
    safe_mining_summary = build_safe_mining_summary(safe_mining_candidates)

    profiles = {
        "Aiden-CEO": load_json("agent_brains/Aiden-CEO/brain_profile.json", files_read),
        "Ethan-CTO": load_json("agent_brains/Ethan-CTO/brain_profile.json", files_read),
        "Samantha-Secretary": load_json("agent_brains/Samantha-Secretary/brain_profile.json", files_read),
    }

    ethan_execution = None
    ethan_execution_path = ROOT / "agent_brains/Ethan-CTO/execution_channels.json"
    if ethan_execution_path.exists():
        ethan_execution = load_json("agent_brains/Ethan-CTO/execution_channels.json", files_read)
    else:
        warnings.append("Ethan execution channel map not present.")

    cards_by_id = {card["card_id"]: card for card in agent_cards.get("cards", [])}
    agents = []
    for agent in team_model.get("agents", []):
        agent_id = agent["agent_id"]
        profile = profiles.get(agent_id, {})
        card = cards_by_id.get(agent_id, {})
        agents.append(
            {
                "agent_id": agent_id,
                "canonical_name": agent.get("canonical_name") or profile.get("canonical_name"),
                "role_type": agent.get("role_type") or profile.get("role_type"),
                "capsule_path": agent.get("capsule_path"),
                "readiness_level": agent.get("readiness_level"),
                "focus": agent.get("focus"),
                "card_status": card.get("status"),
                "capabilities": card.get("capabilities", []),
                "limitations": card.get("limitations", []),
                "next_actions": card.get("next_actions", []),
                "has_pre_u_packet": agent.get("has_pre_u_packet", False),
                "has_chain_review": agent.get("has_chain_review", False),
                "has_execution_channels": agent.get("has_execution_channels", False),
            }
        )

    if ethan_execution:
        warnings.append("Ethan execution channels are present as reference-only boundaries, not runtime launchers.")

    readiness = team_model.get("readiness", {})
    governance_summary = {
        "principle": "labs thinks; Y-star-gov judges; hook enforces; CIEU records and teaches; brain learns",
        "pre_u_packet_validator_spec": team_model.get("governance_interfaces", {}).get("pre_u_packet_validator_spec"),
        "boundary_docs": team_model.get("governance_interfaces", {}).get("boundary_docs"),
        "hook_role": team_model.get("governance_interfaces", {}).get("hook_role"),
        "cieu_role": team_model.get("governance_interfaces", {}).get("cieu_role"),
    }

    open_gaps = [
        "Static console loader exists; no frontend UI yet." if gap == "No static console loader." else gap
        for gap in team_model.get("open_gaps", [])
    ]
    if "Snapshot-only CLI exists; no interactive UI or live refresh yet." not in open_gaps:
        open_gaps.append("Snapshot-only CLI exists; no interactive UI or live refresh yet.")
    if "Runtime artifact quarantine is visible as a path-only summary; full artifact mining is not implemented." not in open_gaps:
        open_gaps.append("Runtime artifact quarantine is visible as a path-only summary; full artifact mining is not implemented.")
    if "Safe mining v0 produces candidate-only Markdown report snippets; no brain or CIEU ingestion exists." not in open_gaps:
        open_gaps.append("Safe mining v0 produces candidate-only Markdown report snippets; no brain or CIEU ingestion exists.")

    snapshot = {
        "schema_name": "ystar.console_read_model.generated.team_console_snapshot",
        "schema_version": "v0",
        "generated_by": "console_read_model/loader/build_team_console_snapshot.py",
        "source_files": files_read,
        "agents": agents,
        "capabilities": capability_matrix,
        "readiness": readiness,
        "governance_summary": governance_summary,
        "data_safety": team_model.get("data_safety", {}),
        "quarantine_summary": quarantine_summary,
        "safe_mining_summary": safe_mining_summary,
        "open_gaps": open_gaps,
        "warnings": warnings,
    }

    compiled_cards = {
        "schema_name": "ystar.console_read_model.generated.agent_cards_compiled",
        "schema_version": "v0",
        "source_files": [
            "console_read_model/agent_cards.json",
            "agent_brains/team_capsule_map.json",
        ],
        "cards": [
            {
                **card,
                "capsule_map_entry": next(
                    (entry for entry in team_capsules.get("agents", []) if entry.get("agent_id") == card.get("card_id")),
                    None,
                ),
            }
            for card in agent_cards.get("cards", [])
        ],
    }

    readiness_summary = {
        "schema_name": "ystar.console_read_model.generated.readiness_summary",
        "schema_version": "v0",
        "ready_now": [
            "reference docs",
            "team read model",
            "capsule schema",
            "Aiden capsule chain",
            "Ethan/Samantha base capsules",
            "Y-star-gov validator interface spec",
            "static read-model validation utility",
            "static snapshot generator",
            "snapshot-only team console CLI",
            "path-only runtime artifact quarantine summary",
            "bounded Markdown safe-mining candidate index",
        ],
        "not_ready": [
            "runtime generator",
            "hook enforcement",
            "validator implementation",
            "CIEU delta schema",
            "brain writeback integration validation",
            "DB-safe query adapter",
            "frontend console",
            "live team-state refresh",
            "CI wiring for validator/generator",
            "CLI integration packaging",
            "semantic validation against live runtime",
            "full runtime artifact mining or curation adapters",
            "brain/CIEU ingestion from safe-mining candidates",
        ],
        "recommended_next_steps": [
            "wire static validator and loader into CI",
            "build a frontend that reads generated snapshots only",
            "create Y-star-gov validator skeleton",
            "define CIEU prediction-delta schema",
            "add Ethan/Samantha Pre-U packet variants",
            "design safe adapters for quarantine-to-CIEU review",
            "add human review queue for safe-mining candidates",
        ],
        "blockers": [
            "no DB-safe adapter",
            "no live validator implementation",
            "no hook enforcement",
            "no semantic runtime truth guarantee",
        ],
        "safety_boundaries": [
            "no DB reads",
            "no log reads",
            "no daemon/runtime state reads",
            "no hook/governance execution",
            "curated read-model files only",
            "quarantine summary is path-level only",
            "safe-mining candidates are bounded Markdown snippets only",
        ],
    }

    manifest = {
        "schema_name": "ystar.console_read_model.generated.generation_manifest",
        "schema_version": "v0",
        "generated_files": [
            "console_read_model/generated/README.md",
            "console_read_model/generated/team_console_snapshot.json",
            "console_read_model/generated/team_console_snapshot.md",
            "console_read_model/generated/agent_cards_compiled.json",
            "console_read_model/generated/readiness_summary.json",
            "console_read_model/generated/quarantine_summary.json",
            "console_read_model/generated/safe_mining_summary.json",
            "console_read_model/generated/generation_manifest.json",
        ],
        "source_files": files_read,
        "unsafe_sources_not_read": [
            "*.db",
            "*.db-wal",
            "*.db-shm",
            "scripts/.logs/*",
            "active-agent markers",
            "daemon pid/state files",
            "__pycache__",
            "raw runtime report directories",
        ],
        "generator_version": GENERATOR_VERSION,
        "validation_recommendation": "Run console_read_model/validation/validate_team_read_model.py after generation.",
        "generated_at_policy": "static_snapshot_no_runtime_clock_required",
    }

    snapshot_md = render_snapshot_markdown(snapshot, readiness_summary)

    write_text(
        "console_read_model/generated/README.md",
        "# Generated Console Snapshots\n\n"
        "These files are derived artifacts from curated read-model inputs only.\n"
        "They do not contain DB contents, raw logs, daemon state, active-agent state,\n"
        "or live runtime observations.\n\n"
        "`quarantine_summary.json` is derived from the runtime artifact quarantine\n"
        "path-only manifest. It summarizes classes/counts only and does not include\n"
        "artifact contents.\n\n"
        "`safe_mining_summary.json` is derived from bounded Markdown report candidate\n"
        "indexes. It summarizes candidate counts/classes only; candidates remain\n"
        "review assets, not brain memory.\n\n"
        "`console_read_model/cli/team_console.py` consumes these generated files as its\n"
        "only data source.\n",
        generated_files,
    )
    write_json("console_read_model/generated/team_console_snapshot.json", snapshot, generated_files)
    write_text("console_read_model/generated/team_console_snapshot.md", snapshot_md, generated_files)
    write_json("console_read_model/generated/agent_cards_compiled.json", compiled_cards, generated_files)
    write_json("console_read_model/generated/readiness_summary.json", readiness_summary, generated_files)
    write_json("console_read_model/generated/quarantine_summary.json", quarantine_summary, generated_files)
    write_json("console_read_model/generated/safe_mining_summary.json", safe_mining_summary, generated_files)
    write_json("console_read_model/generated/generation_manifest.json", manifest, generated_files)

    return files_read, generated_files, [agent["agent_id"] for agent in agents], warnings


def render_snapshot_markdown(snapshot: dict[str, Any], readiness: dict[str, Any]) -> str:
    lines = [
        "# Team Brain Console Snapshot",
        "",
        "This snapshot is generated from curated read-model files only.",
        "",
        "## Agents",
        "",
    ]
    for agent in snapshot["agents"]:
        lines.extend(
            [
                f"### {agent['agent_id']}",
                "",
                f"- Name: {agent['canonical_name']}",
                f"- Role type: {agent['role_type']}",
                f"- Readiness: {agent['readiness_level']}",
                f"- Focus: {agent['focus']}",
                f"- Pre-U packet: {agent['has_pre_u_packet']}",
                f"- Execution channels: {agent['has_execution_channels']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Capability Matrix Summary",
            "",
            "See `capability_matrix.json` and generated snapshot JSON for the full matrix.",
            "",
            "## Readiness Summary",
            "",
            "Ready now:",
        ]
    )
    lines.extend([f"- {item}" for item in readiness["ready_now"]])
    lines.extend(["", "Not ready:"])
    lines.extend([f"- {item}" for item in readiness["not_ready"]])
    quarantine = snapshot.get("quarantine_summary", {})
    safe_mining = snapshot.get("safe_mining_summary", {})
    lines.extend(
        [
            "",
            "## Runtime Artifact Quarantine Summary",
            "",
            f"- Framework status: {quarantine.get('framework_status')}",
            f"- Current mining level: {quarantine.get('current_mining_level')}",
            f"- Artifacts classified: {quarantine.get('artifacts_classified')}",
            f"- Unsafe artifacts count: {quarantine.get('unsafe_artifacts_count')}",
            "- Classes seen:",
        ]
    )
    for class_name, count in sorted(quarantine.get("classes_seen", {}).items()):
        lines.append(f"  - {class_name}: {count}")
    lines.extend(
        [
            f"- Generated manifest ref: {quarantine.get('generated_manifest_ref')}",
            f"- Warning: {quarantine.get('safety_warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Runtime Artifact Safe Mining Candidates",
            "",
            f"- Candidate count: {safe_mining.get('candidate_count')}",
            f"- Safety level: {safe_mining.get('safety_level')}",
            f"- Ingestion status: {safe_mining.get('ingestion_status')}",
            f"- Generated candidate index: {safe_mining.get('generated_candidate_index')}",
            "- Classes seen:",
        ]
    )
    for class_name, count in sorted(safe_mining.get("classes_seen", {}).items()):
        lines.append(f"  - {class_name}: {count}")
    lines.extend(
        [
            f"- Warning: {safe_mining.get('warning')}",
        ]
    )
    lines.extend(
        [
            "",
            "## Governance Boundary",
            "",
            snapshot["governance_summary"]["principle"],
            "",
            "## Data Safety Boundary",
            "",
            "Console reads curated read-model files only. It must not read DBs, logs, active-agent markers, daemon state, or raw runtime state directly.",
            "",
            "## Next Recommended Steps",
            "",
        ]
    )
    lines.extend([f"- {item}" for item in readiness["recommended_next_steps"]])
    lines.extend(["", "## Warnings / Gaps", ""])
    for item in snapshot["warnings"] + snapshot["open_gaps"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def print_report(status: str, files_read: list[str], generated_files: list[str], agents: list[str], warnings: list[str]) -> None:
    print(f"Team Console Snapshot Loader: {status}")
    print(f"Files read: {len(files_read)}")
    print(f"Files generated: {len(generated_files)}")
    print(f"Agents included: {', '.join(agents)}")
    print(f"Warnings: {len(warnings)}")
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")
    print("\nFiles read:")
    for item in files_read:
        print(f"- {item}")
    print("\nFiles generated:")
    for item in generated_files:
        print(f"- {item}")


def main() -> int:
    try:
        files_read, generated_files, agents, warnings = build()
    except Exception as exc:
        print(f"Team Console Snapshot Loader: FAIL")
        print(f"Error: {exc}")
        return 1
    print_report("PASS", files_read, generated_files, agents, warnings)
    return 0


if __name__ == "__main__":
    sys.exit(main())
