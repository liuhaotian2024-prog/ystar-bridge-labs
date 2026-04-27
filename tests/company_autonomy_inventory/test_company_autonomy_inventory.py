from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "company_autonomy_inventory" / "tools" / "build_company_autonomy_inventory.py"
GENERATED = ROOT / "company_autonomy_inventory" / "generated"

JSON_OUTPUTS = [
    "repo_discovery_manifest.json",
    "existing_asset_inventory.json",
    "observation_capability_map.json",
    "resource_sensing_map.json",
    "action_capability_map.json",
    "governed_tool_registry_candidates.json",
    "agent_role_capability_matrix.json",
    "company_autonomy_readiness_summary.json",
    "inventory_size_guard.json",
]

GENERATED_OUTPUTS = JSON_OUTPUTS + [
    "dormant_asset_report.md",
    "autonomy_gap_report.md",
    "company_autonomy_report.md",
]

FORBIDDEN_DEPENDENCY_STRINGS = [
    ".db",
    ".db-wal",
    ".db-shm",
    ".sqlite",
    ".sqlite3",
    "scripts/.logs",
    "reports/ceo/brain_dream_diffs",
    "reports/escalation",
    "reports/daily",
    "reports/drift_hourly",
    "active_agent",
    ".ystar_active_agent",
]

REQUIRED_ROLES = {
    "Aiden-CEO",
    "Ethan-CTO",
    "Maya-Governance",
    "Ryan-Platform",
    "Samantha-Secretary",
    "Leo-Kernel",
}

FORBIDDEN_CONTENT_FIELDS = {
    "full_source",
    "source_content",
    "file_content",
    "raw_content",
    "full_text",
    "raw_log",
}


def run_builder() -> None:
    result = subprocess.run(
        ["python3", str(BUILDER.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def load_json(name: str) -> dict:
    path = GENERATED / name
    assert path.exists(), f"missing generated file: {name}"
    return json.loads(path.read_text(encoding="utf-8"))


def test_company_autonomy_inventory_outputs_and_readiness() -> None:
    run_builder()

    for name in JSON_OUTPUTS:
        load_json(name)

    summary = load_json("company_autonomy_readiness_summary.json")
    for field in [
        "company_autonomy_inventory_defined",
        "repo_archaeology_completed",
        "observation_capability_map_defined",
        "resource_sensing_map_defined",
        "action_capability_map_defined",
        "governed_tool_registry_candidates_defined",
        "agent_role_capability_matrix_defined",
        "commercial_agent_company_goal_aligned",
        "requires_manual_enablement",
    ]:
        assert summary[field] is True

    assert summary["governance_only_runtime"] is False
    for field in [
        "live_actions_enabled",
        "external_actions_enabled",
        "brain_writeback_enabled",
        "memory_ingestion_enabled",
        "cieu_persistence_enabled",
        "git_push_enabled",
        "daemon_control_enabled",
        "email_or_external_communication_enabled",
    ]:
        assert summary[field] is False

    assert summary["next_required_milestone"] == "L4.2 Company Autonomous Work Cycle Simulator v0"


def test_inventory_size_guard_prevents_generated_bloat() -> None:
    run_builder()

    guard = load_json("inventory_size_guard.json")
    assert guard["inventory_size_guard_defined"] is True
    assert guard["compaction_applied"] is True
    assert guard["full_source_embedding_allowed"] is False
    assert guard["full_doc_embedding_allowed"] is False
    assert guard["generated_inventory_safe_for_read_model"] is True
    assert guard["oversized_files"] == []
    assert guard["total_generated_inventory_bytes"] <= guard["max_total_generated_inventory_bytes"]

    max_single = guard["max_single_generated_json_bytes"]
    for name in JSON_OUTPUTS:
        path = GENERATED / name
        assert path.stat().st_size <= max_single, f"{name} exceeds size guard"

    inventory = load_json("existing_asset_inventory.json")
    assert inventory["compaction_applied"] is True
    assert inventory["indexed_asset_count"] <= inventory["max_indexed_assets"]
    assert inventory["asset_count"] >= inventory["indexed_asset_count"]

    def walk(value: object) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                assert key not in FORBIDDEN_CONTENT_FIELDS
                walk(nested)
        elif isinstance(value, list):
            for nested in value:
                walk(nested)

    for name in JSON_OUTPUTS:
        walk(load_json(name))


def test_capability_maps_registry_and_roles_are_populated_and_disabled() -> None:
    run_builder()

    observation = load_json("observation_capability_map.json")
    resources = load_json("resource_sensing_map.json")
    actions = load_json("action_capability_map.json")
    tools = load_json("governed_tool_registry_candidates.json")
    matrix = load_json("agent_role_capability_matrix.json")

    assert observation["channels"]
    assert resources["resources"]
    assert actions["actions"]
    assert tools["candidates"]

    roles = {agent["agent_id"] for agent in matrix["agents"]}
    assert roles == REQUIRED_ROLES

    for action in actions["actions"]:
        assert action["live_enabled"] is False

    prohibited = {
        "git_push",
        "brain_writeback",
        "memory_ingestion",
        "cieu_write",
        "daemon_start_stop",
        "external_web_action",
        "email_or_communication",
    }
    action_by_id = {action["action_id"]: action for action in actions["actions"]}
    for action_id in prohibited:
        assert action_by_id[action_id]["live_enabled"] is False
        assert action_by_id[action_id]["current_status"] in {"blocked", "candidate_disabled"}

    for candidate in tools["candidates"]:
        assert candidate["live_enabled"] is False


def test_generated_files_avoid_forbidden_runtime_dependencies() -> None:
    run_builder()

    for name in GENERATED_OUTPUTS:
        path = GENERATED / name
        assert path.exists(), f"missing generated file: {name}"
        text = path.read_text(encoding="utf-8").lower()
        for marker in FORBIDDEN_DEPENDENCY_STRINGS:
            assert marker.lower() not in text, f"{marker} appeared in {name}"


def test_builder_is_source_archaeology_only() -> None:
    source = BUILDER.read_text(encoding="utf-8")
    assert "shell=True" not in source
    assert "import subprocess" not in source
    assert "import sqlite3" not in source

    run_builder()
    manifest = load_json("repo_discovery_manifest.json")
    for root in manifest["scanned_roots"]:
        assert root["write_performed"] is False
