from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "mission_field_projection_contract" / "tools" / "build_mission_field_projection_harness.py"

REQUIRED_FILES = [
    "mission_field_projection_contract/README.md",
    "mission_field_projection_contract/projection_contract_v0.json",
    "mission_field_projection_contract/projection_input_fixture.json",
    "mission_field_projection_contract/projection_policy_v0.json",
    "mission_field_projection_contract/projection_contract_summary.json",
    "mission_field_projection_contract/projection_contract_report.md",
    "layered_y_star_projection_trace/layered_projection_trace.json",
    "layered_y_star_projection_trace/layered_projection_trace.md",
    "layered_y_star_projection_trace/field_source_map.json",
    "layered_y_star_projection_trace/contraction_map.json",
    "layered_y_star_projection_trace/unresolved_gap_map.json",
    "layered_y_star_projection_trace/projection_trace_summary.json",
    "projection_to_pre_u_packet_adapter/pre_u_packet_candidate.json",
    "projection_to_pre_u_packet_adapter/pre_u_adapter_mapping.json",
    "projection_to_pre_u_packet_adapter/pre_u_adapter_gap_report.md",
    "projection_to_pre_u_packet_adapter/pre_u_adapter_summary.json",
    "projection_residual_delta_fixture/projection_predicted_outcome.json",
    "projection_residual_delta_fixture/projection_mock_actual_outcome.json",
    "projection_residual_delta_fixture/projection_residual_delta_fixture.json",
    "projection_residual_delta_fixture/projection_residual_delta_summary.json",
    "projection_residual_delta_fixture/projection_residual_delta_report.md",
]

JSON_FILES = [path for path in REQUIRED_FILES if path.endswith(".json")]

FALSE_FLAG_FIELDS = {
    "live_execution_enabled",
    "external_action_enabled",
    "network_enabled",
    "scheduler_enabled",
    "daemon_enabled",
    "cieu_persistence_enabled",
    "brain_writeback_enabled",
    "memory_ingestion_enabled",
    "candidate_auto_approval_enabled",
    "live_action_authorized",
    "real_action_executed",
    "external_action_executed",
}

FORBIDDEN_SOURCE_MARKERS = [
    ".db-wal",
    ".db-shm",
    ".sqlite",
    ".sqlite3",
    "scripts/.logs",
    "active-agent",
]


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


@pytest.fixture(scope="module", autouse=True)
def generated_projection_harness() -> None:
    result = run_command(["python3", str(BUILDER.relative_to(ROOT))])
    assert result.returncode == 0, result.stdout + result.stderr


def load_json(relative_path: str) -> Any:
    path = ROOT / relative_path
    assert path.exists(), f"missing generated file: {relative_path}"
    return json.loads(path.read_text(encoding="utf-8"))


def walk_json(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def test_required_l5_1_files_exist_and_json_parses() -> None:
    for relative_path in REQUIRED_FILES:
        assert (ROOT / relative_path).exists(), f"missing file: {relative_path}"
    for relative_path in JSON_FILES:
        load_json(relative_path)


def test_projection_contract_declares_required_inputs_outputs_and_safety() -> None:
    contract = load_json("mission_field_projection_contract/projection_contract_v0.json")
    required_inputs = {
        "mission_y_star",
        "xt_observation_summary",
        "agent_role",
        "tool_context",
        "risk_boundary",
        "residual_history_summary",
        "governance_policy_summary",
        "archaeology_evidence_refs",
    }
    required_outputs = {
        "layered_y_star_projection",
        "projection_trace",
        "field_source_map",
        "contraction_map",
        "unresolved_gap_map",
        "pre_u_adapter_candidate",
        "residual_delta_fixture_candidate",
    }

    assert set(contract["supported_projection_layers"]) == {
        "mission",
        "company",
        "milestone",
        "session",
        "task",
        "action",
    }
    assert required_inputs.issubset(set(contract["allowed_input_fields"]))
    assert required_outputs.issubset(set(contract["output_requirements"]))
    assert "raw DB contents" in contract["forbidden_inputs"]
    for value in contract["safety_flags"].values():
        assert value is False


def test_layered_projection_has_all_layers_with_evidence_and_action_contract_only() -> None:
    trace = load_json("layered_y_star_projection_trace/layered_projection_trace.json")
    layers = {layer["layer_name"]: layer for layer in trace["projection_layers"]}
    assert list(layers) == ["mission", "company", "milestone", "session", "task", "action"]

    for layer in layers.values():
        assert layer["evidence_refs"]
        assert layer["safety_flags"]
        for value in layer["safety_flags"].values():
            assert value is False

    action = layers["action"]
    assert action["projection_only"] is True
    assert action["live_action_authorized"] is False
    assert action["requires_pre_u_validation"] is True
    assert action["action_field_execution_status"] == "not_implemented_future_work"


def test_pre_u_packet_candidate_maps_projection_to_packet_shape() -> None:
    packet = load_json("projection_to_pre_u_packet_adapter/pre_u_packet_candidate.json")
    mapping = load_json("projection_to_pre_u_packet_adapter/pre_u_adapter_mapping.json")
    summary = load_json("projection_to_pre_u_packet_adapter/pre_u_adapter_summary.json")

    assert packet["adapter_status"] == "candidate_only_not_production_ready"
    assert packet["declared_Y_star"]["Y_star_id"] == "action-y-star-pre-u-candidate-v0"
    assert packet["Xt"]["source_kind"] == "generated_read_model_summary"
    assert packet["candidate_U"]["execution_mode"] == "dry_run_projection_only"
    assert packet["execution_boundary"]["network_enabled"] is False
    assert packet["production_ready"] is False
    assert mapping["not_mapped_to_live_validator"] is True
    assert summary["pre_u_adapter_candidate_generated"] is True
    assert summary["y_star_gov_called"] is False


def test_residual_delta_fixture_blocks_direct_writeback_and_ingestion() -> None:
    predicted = load_json("projection_residual_delta_fixture/projection_predicted_outcome.json")
    actual = load_json("projection_residual_delta_fixture/projection_mock_actual_outcome.json")
    delta = load_json("projection_residual_delta_fixture/projection_residual_delta_fixture.json")
    summary = load_json("projection_residual_delta_fixture/projection_residual_delta_summary.json")

    assert predicted["derived_from"] == "layered_y_star_projection_trace/layered_projection_trace.json"
    assert actual["synthetic_dry_run_only"] is True
    learning = delta["residual_delta"]["learning_eligibility"]
    assert learning["eligible_for_review_queue"] is True
    assert learning["eligible_for_direct_brain_writeback"] is False
    assert learning["eligible_for_direct_memory_ingestion"] is False
    assert learning["requires_human_or_governance_review"] is True
    assert delta["direct_brain_writeback_allowed"] is False
    assert delta["direct_memory_ingestion_allowed"] is False
    assert summary["eligible_for_direct_brain_writeback"] is False
    assert summary["eligible_for_direct_memory_ingestion"] is False


def test_all_live_external_network_scheduler_daemon_writeback_flags_are_false() -> None:
    for relative_path in JSON_FILES:
        payload = load_json(relative_path)
        for node in walk_json(payload):
            for field in FALSE_FLAG_FIELDS:
                if field in node:
                    assert node[field] is False, f"{relative_path}: {field} must be false"


def test_no_unsafe_runtime_sources_are_referenced_as_inputs() -> None:
    fixture = load_json("mission_field_projection_contract/projection_input_fixture.json")
    rendered = json.dumps(fixture, ensure_ascii=False).lower()
    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in rendered


def test_console_read_model_integration_passes() -> None:
    loader = run_command(["python3", "console_read_model/loader/build_team_console_snapshot.py"])
    assert loader.returncode == 0, loader.stdout + loader.stderr

    summary = load_json("console_read_model/generated/mission_projection_summary.json")
    assert summary["l5_1_projection_contract_defined"] is True
    assert summary["ready_for_L5_2_deep_xt_observation_model"] is True
    assert summary["network_enabled"] is False

    validator = run_command(["python3", "console_read_model/validation/validate_team_read_model.py"])
    assert validator.returncode == 0, validator.stdout + validator.stderr


def test_builder_source_is_static_and_non_runtime() -> None:
    source = BUILDER.read_text(encoding="utf-8")
    assert "shell=True" not in source
    assert "import sqlite3" not in source
    assert "subprocess.run" not in source
    assert "requests." not in source
    assert "urllib.request" not in source
    assert "scripts/.logs" not in source
    assert ".db-wal" not in source
    assert ".db-shm" not in source
    assert ".sqlite3" not in source
