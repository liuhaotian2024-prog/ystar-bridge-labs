from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TRIAGE_BUILDER = ROOT / "legacy_asset_triage" / "tools" / "build_legacy_asset_triage.py"
BUILDER = ROOT / "governed_observation_loop" / "tools" / "build_governed_observation_loop.py"
GENERATED = ROOT / "governed_observation_loop" / "generated"

JSON_OUTPUTS = [
    "observation_source_registry.json",
    "observation_tick_001.json",
    "mission_dashboard_snapshot.json",
    "company_state_digest.json",
    "observation_to_work_item_candidates.json",
    "governed_observation_loop_summary.json",
]


def run_script(path: Path) -> None:
    result = subprocess.run(
        ["python3", str(path.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def run_builders() -> None:
    run_script(TRIAGE_BUILDER)
    run_script(BUILDER)


def load_json(name: str) -> dict:
    path = GENERATED / name
    assert path.exists(), f"missing generated file: {name}"
    return json.loads(path.read_text(encoding="utf-8"))


def test_observation_loop_outputs_and_summary() -> None:
    run_builders()

    for name in JSON_OUTPUTS:
        load_json(name)

    summary = load_json("governed_observation_loop_summary.json")
    for field in [
        "governed_observation_loop_defined",
        "read_only_observation_loop_defined",
        "observation_source_registry_defined",
        "observation_tick_generated",
        "mission_dashboard_snapshot_defined",
        "company_state_digest_defined",
        "observation_to_work_item_candidates_defined",
        "mission_bounded_autonomy_supported",
        "step_by_step_human_prompting_reduced",
    ]:
        assert summary[field] is True

    for field in [
        "real_action_executed",
        "external_action_executed",
        "live_action_enabled",
        "git_push_enabled",
        "daemon_control_enabled",
        "cieu_persistence_enabled",
        "brain_writeback_enabled",
        "memory_ingestion_enabled",
        "email_or_external_communication_enabled",
    ]:
        assert summary[field] is False

    assert summary["next_required_milestone"] == "L4.4 First Governed Read-Only Observation Tool Wrapper v0"


def test_observation_sources_are_safe_read_only() -> None:
    run_builders()

    registry = load_json("observation_source_registry.json")
    assert registry["sources"]
    for source in registry["sources"]:
        assert source["safe_to_read_now"] is True
        assert source["raw_runtime_artifact"] is False
        assert source["requires_network"] is False
        assert source["requires_credentials"] is False


def test_tick_dashboard_digest_and_candidates_are_non_runtime() -> None:
    run_builders()

    tick = load_json("observation_tick_001.json")
    dashboard = load_json("mission_dashboard_snapshot.json")
    digest = load_json("company_state_digest.json")
    candidates = load_json("observation_to_work_item_candidates.json")

    assert tick["real_action_executed"] is False
    assert tick["external_action_executed"] is False
    assert dashboard["observation_loop_status"]["read_only_observation_loop_defined"] is True
    assert dashboard["observation_loop_status"]["real_action_executed"] is False
    assert digest["live_enabled"] is False
    assert digest["network_used"] is False

    assert candidates["candidate_count"] >= 3
    for candidate in candidates["candidates"]:
        assert candidate["live_enabled"] is False


def test_builder_source_is_non_runtime() -> None:
    source = BUILDER.read_text(encoding="utf-8")
    assert "shell=True" not in source
    assert "import subprocess" not in source
    assert "import sqlite3" not in source
    assert "scripts/.logs" not in source
    assert ".db-wal" not in source
    assert ".db-shm" not in source
