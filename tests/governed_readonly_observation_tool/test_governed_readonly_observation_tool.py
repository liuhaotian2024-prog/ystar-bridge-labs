from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "governed_readonly_observation_tool"
GENERATED = PACK / "generated"
BUILDER = PACK / "tools" / "build_readonly_observation_tool_artifacts.py"
RUNNER = PACK / "tools" / "run_readonly_observation_tool.py"

JSON_OUTPUTS = [
    "tool_contract.json",
    "allowed_source_registry.json",
    "sample_tool_invocation.json",
    "sample_tool_result.json",
    "rejected_unsafe_invocation.json",
    "tool_invocation_trace.json",
    "tool_cieu_event.json",
    "tool_readiness_summary.json",
]

FORBIDDEN_GENERATED_STRINGS = [
    ".db",
    ".db-wal",
    ".db-shm",
    ".sqlite",
    ".sqlite3",
    "scripts/.logs",
    "active-agent",
]


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["python3", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result


def run_builder() -> None:
    run_script(str(BUILDER.relative_to(ROOT)))


def load_json(name: str) -> dict:
    path = GENERATED / name
    assert path.exists(), f"missing generated file: {name}"
    return json.loads(path.read_text(encoding="utf-8"))


def load_runner_module():
    spec = importlib.util.spec_from_file_location("readonly_runner", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_tool_artifacts_are_valid() -> None:
    run_builder()

    for name in JSON_OUTPUTS:
        load_json(name)

    contract = load_json("tool_contract.json")
    registry = load_json("allowed_source_registry.json")
    invocation = load_json("sample_tool_invocation.json")
    result = load_json("sample_tool_result.json")
    readiness = load_json("tool_readiness_summary.json")

    assert contract["tool_id"] == "governed_readonly_observation_tool_v0"
    assert contract["tool_category"] == "read_only_observation"
    assert contract["input_contract_required"] is True
    assert contract["output_contract_required"] is True
    assert contract["requires_y_star_gov"] is True
    assert contract["requires_operator_approval"] is False
    assert contract["requires_cieu_event"] is True
    assert contract["live_enabled"] is False
    assert contract["external_action_enabled"] is False
    assert contract["network_enabled"] is False
    assert contract["cieu_persistence_enabled"] is False
    assert contract["brain_writeback_enabled"] is False
    assert contract["memory_ingestion_enabled"] is False

    assert registry["source_count"] == len(registry["sources"])
    assert registry["source_count"] >= 8
    assert invocation["requested_sources"]
    assert result["status"] == "success"
    assert readiness["first_governed_tool_wrapper_created"] is True


def test_allowed_source_registry_is_safe_read_only() -> None:
    run_builder()

    registry = load_json("allowed_source_registry.json")
    for source in registry["sources"]:
        assert source["safe_to_read_now"] is True
        assert source["raw_runtime_artifact"] is False
        assert source["requires_network"] is False
        assert source["requires_credentials"] is False
        assert source["read_mode"] == "json_summary"
        source_path = ROOT / source["source_path"]
        assert source_path.exists()
        assert source_path.suffix == ".json"


def test_runner_succeeds_for_sample_invocation() -> None:
    run_builder()

    run_script(
        str(RUNNER.relative_to(ROOT)),
        "--input",
        "governed_readonly_observation_tool/generated/sample_tool_invocation.json",
        "--output",
        "governed_readonly_observation_tool/generated/sample_tool_result.json",
    )
    result = load_json("sample_tool_result.json")

    assert result["status"] == "success"
    assert result["read_sources"]
    assert result["blocked_sources"] == []
    assert result["real_action_executed"] is False
    assert result["external_action_executed"] is False
    assert result["live_action_enabled"] is False
    assert result["cieu_persistence_enabled"] is False
    assert result["brain_writeback_enabled"] is False
    assert result["memory_ingestion_enabled"] is False


def test_runner_rejects_unsafe_invocation_without_reading_sources() -> None:
    run_builder()

    runner = load_runner_module()
    unsafe_invocation = load_json("rejected_unsafe_invocation.json")
    result = runner.run_invocation(unsafe_invocation)

    assert result["status"] == "rejected"
    assert result["read_sources"] == []
    assert result["blocked_sources"]
    assert result["real_action_executed"] is False
    assert result["external_action_executed"] is False
    assert result["live_action_enabled"] is False


def test_tool_cieu_event_is_dry_run_only() -> None:
    run_builder()

    event = load_json("tool_cieu_event.json")
    assert event["dry_run_only"] is True
    assert event["persistence_enabled"] is False
    assert event["learning_eligibility"] is False
    assert event["curation_required"] is True
    assert event["direct_brain_writeback_allowed"] is False
    assert event["direct_memory_ingestion_allowed"] is False
    assert event["raw_artifact_ingestion_allowed"] is False


def test_readiness_summary_keeps_live_behavior_disabled() -> None:
    run_builder()

    summary = load_json("tool_readiness_summary.json")
    for field in [
        "governed_readonly_observation_tool_defined",
        "tool_contract_defined",
        "allowed_source_registry_defined",
        "sample_invocation_defined",
        "sample_result_defined",
        "unsafe_invocation_rejected",
        "tool_cieu_event_defined",
        "local_readonly_dry_run_callable",
        "mission_bounded_autonomy_supported",
        "step_by_step_human_prompting_reduced",
        "first_governed_tool_wrapper_created",
    ]:
        assert summary[field] is True

    for field in [
        "real_action_executed",
        "external_action_executed",
        "live_action_enabled",
        "network_enabled",
        "git_push_enabled",
        "daemon_control_enabled",
        "cieu_persistence_enabled",
        "brain_writeback_enabled",
        "memory_ingestion_enabled",
        "email_or_external_communication_enabled",
    ]:
        assert summary[field] is False

    assert summary["next_required_milestone"] == "L4.5 Governed Tool Invocation Through Pre-U Bridge v0"


def test_generated_outputs_do_not_depend_on_forbidden_runtime_paths() -> None:
    run_builder()

    for path in GENERATED.iterdir():
        if path.suffix not in {".json", ".md"}:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for marker in FORBIDDEN_GENERATED_STRINGS:
            assert marker not in text, f"{marker} appeared in {path.name}"


def test_builder_and_runner_sources_are_non_runtime() -> None:
    for path in [BUILDER, RUNNER]:
        source = path.read_text(encoding="utf-8")
        assert "shell=True" not in source
        assert "import sqlite3" not in source
        assert "requests." not in source
        assert "urllib.request" not in source

