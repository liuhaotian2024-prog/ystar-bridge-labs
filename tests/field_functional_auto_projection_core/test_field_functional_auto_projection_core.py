from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[2]
BUILDER = (
    ROOT
    / "field_functional_auto_projection_core"
    / "tools"
    / "build_field_functional_auto_projection_core.py"
)

REQUIRED_FILES = [
    "field_functional_auto_projection_core/README.md",
    "field_functional_auto_projection_core/tools/build_field_functional_auto_projection_core.py",
    "field_functional_auto_projection_core/field_projection_operator_contract.json",
    "field_functional_auto_projection_core/field_projection_operator_policy.json",
    "field_functional_auto_projection_core/field_projection_input_fixture.json",
    "field_functional_auto_projection_core/field_projection_algorithm_v0.md",
    "field_functional_auto_projection_core/field_projection_operator_summary.json",
    "field_functional_auto_projection_core/field_projection_operator_report.md",
    "mission_to_behavior_y_star_projection/mission_y_star_input.json",
    "mission_to_behavior_y_star_projection/projection_context_field_fixture.json",
    "mission_to_behavior_y_star_projection/mission_to_company_y_star.json",
    "mission_to_behavior_y_star_projection/company_to_milestone_y_star.json",
    "mission_to_behavior_y_star_projection/milestone_to_session_y_star.json",
    "mission_to_behavior_y_star_projection/session_to_task_y_star.json",
    "mission_to_behavior_y_star_projection/task_to_behavior_y_star.json",
    "mission_to_behavior_y_star_projection/mission_to_behavior_projection_trace.json",
    "mission_to_behavior_y_star_projection/y_star_inheritance_map.json",
    "mission_to_behavior_y_star_projection/y_star_contraction_map.json",
    "mission_to_behavior_y_star_projection/context_binding_map.json",
    "mission_to_behavior_y_star_projection/unresolved_projection_gap_map.json",
    "mission_to_behavior_y_star_projection/behavior_level_y_star_candidate.json",
    "mission_to_behavior_y_star_projection/mission_to_behavior_projection_summary.json",
    "mission_to_behavior_y_star_projection/mission_to_behavior_projection_report.md",
    "behavior_y_star_to_pre_u_candidate/behavior_to_pre_u_mapping.json",
    "behavior_y_star_to_pre_u_candidate/pre_u_packet_candidate_from_behavior_y_star.json",
    "behavior_y_star_to_pre_u_candidate/pre_u_candidate_gap_report.md",
    "behavior_y_star_to_pre_u_candidate/pre_u_candidate_summary.json",
    "projection_behavior_residual_loop_fixture/projected_behavior_expected_outcome.json",
    "projection_behavior_residual_loop_fixture/mock_behavior_actual_outcome.json",
    "projection_behavior_residual_loop_fixture/behavior_projection_residual_delta.json",
    "projection_behavior_residual_loop_fixture/projection_learning_candidate_stub.json",
    "projection_behavior_residual_loop_fixture/projection_residual_loop_summary.json",
    "projection_behavior_residual_loop_fixture/projection_residual_loop_report.md",
    "field_projection_cycle_readiness/field_projection_cycle_readiness.json",
    "field_projection_cycle_readiness/field_projection_cycle_readiness.md",
    "field_projection_cycle_readiness/l5_3_recommended_next_step.json",
]

JSON_FILES = [path for path in REQUIRED_FILES if path.endswith(".json")]

LAYER_FILES = [
    "mission_to_behavior_y_star_projection/mission_to_company_y_star.json",
    "mission_to_behavior_y_star_projection/company_to_milestone_y_star.json",
    "mission_to_behavior_y_star_projection/milestone_to_session_y_star.json",
    "mission_to_behavior_y_star_projection/session_to_task_y_star.json",
    "mission_to_behavior_y_star_projection/task_to_behavior_y_star.json",
]

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
    "semantic_truth_scoring_enabled",
    "raw_runtime_artifact_reading_enabled",
    "behavior_execution_enabled",
    "live_behavior_authorized",
    "eligible_for_direct_execution",
    "eligible_for_brain_writeback",
    "eligible_for_memory_ingestion",
    "live_execution_authorized",
    "external_action_authorized",
    "production_ready",
    "real_behavior_executed",
    "eligible_for_direct_brain_writeback",
    "eligible_for_direct_memory_ingestion",
    "eligible_for_candidate_auto_approval",
    "live_learning_enabled",
    "approved",
}


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
def generated_field_projection_core() -> None:
    result = run_command(["python3", str(BUILDER.relative_to(ROOT))])
    assert result.returncode == 0, result.stdout + result.stderr


def load_json(relative_path: str) -> Any:
    path = ROOT / relative_path
    assert path.exists(), f"missing file: {relative_path}"
    return json.loads(path.read_text(encoding="utf-8"))


def walk_json(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def test_required_l5_2_files_exist_and_json_parses() -> None:
    for relative_path in REQUIRED_FILES:
        assert (ROOT / relative_path).exists(), f"missing file: {relative_path}"
    for relative_path in JSON_FILES:
        load_json(relative_path)


def test_operator_contract_defines_layers_rules_sources_and_false_flags() -> None:
    contract = load_json("field_functional_auto_projection_core/field_projection_operator_contract.json")
    for field in [
        "y_star_definition",
        "projection_layers",
        "inheritance_rules",
        "contraction_rules",
        "context_binding_rules",
        "forbidden_projection_sources",
        "safety_flags",
    ]:
        assert field in contract

    assert contract["projection_layers"] == [
        "mission",
        "company",
        "milestone",
        "session",
        "task",
        "behavior",
    ]
    assert "raw_db_contents" in contract["forbidden_projection_sources"]
    assert "semantic_truth_scoring" in contract["forbidden_projection_sources"]
    for value in contract["safety_flags"].values():
        assert value is False


def test_mission_input_and_context_fixture_keep_revenue_discovery_disabled() -> None:
    mission = load_json("mission_to_behavior_y_star_projection/mission_y_star_input.json")
    context = load_json("mission_to_behavior_y_star_projection/projection_context_field_fixture.json")

    assert mission["declared_mission_y_star"]
    assert "revenue execution" in mission["non_goals"]
    disabled = context["future_revenue_opportunity_context_disabled"]
    assert disabled["reserved_for_future"] is True
    assert disabled["enabled"] is False
    assert disabled["network_scans_enabled"] is False
    assert disabled["bounty_rfp_grant_market_source_scans_enabled"] is False


def test_each_layer_projection_has_required_projection_shape() -> None:
    for relative_path in LAYER_FILES:
        layer = load_json(relative_path)
        for field in [
            "projected_y_star",
            "inherited_obligations",
            "contracted_obligations",
            "context_bound_obligations",
            "unresolved_gaps",
            "evidence_refs",
            "safety_flags",
        ]:
            assert field in layer, f"{relative_path} missing {field}"
        assert layer["projected_y_star"]
        assert layer["evidence_refs"]
        for value in layer["safety_flags"].values():
            assert value is False


def test_trace_and_projection_maps_link_all_transitions() -> None:
    trace = load_json("mission_to_behavior_y_star_projection/mission_to_behavior_projection_trace.json")
    inheritance = load_json("mission_to_behavior_y_star_projection/y_star_inheritance_map.json")
    contraction = load_json("mission_to_behavior_y_star_projection/y_star_contraction_map.json")

    assert trace["projection_layers"] == [
        "mission",
        "company",
        "milestone",
        "session",
        "task",
        "behavior",
    ]
    assert [(edge["from_layer"], edge["to_layer"]) for edge in trace["transitions"]] == [
        ("mission", "company"),
        ("company", "milestone"),
        ("milestone", "session"),
        ("session", "task"),
        ("task", "behavior"),
    ]
    assert inheritance["inheritance_edges"]
    assert contraction["contractions"]


def test_behavior_level_y_star_candidate_is_projection_only_and_pre_u_eligible() -> None:
    candidate = load_json("mission_to_behavior_y_star_projection/behavior_level_y_star_candidate.json")

    assert candidate["required_pre_u_validation"] is True
    assert candidate["execution_status"] == "projection_only"
    assert candidate["live_behavior_authorized"] is False
    assert candidate["behavior_execution_enabled"] is False
    assert candidate["eligible_for_pre_u_packet_candidate"] is True
    assert candidate["eligible_for_direct_execution"] is False
    assert candidate["eligible_for_brain_writeback"] is False
    assert candidate["eligible_for_memory_ingestion"] is False


def test_pre_u_packet_candidate_from_behavior_y_star_is_dry_run_only() -> None:
    packet = load_json("behavior_y_star_to_pre_u_candidate/pre_u_packet_candidate_from_behavior_y_star.json")
    mapping = load_json("behavior_y_star_to_pre_u_candidate/behavior_to_pre_u_mapping.json")

    assert packet["dry_run_only"] is True
    assert packet["production_ready"] is False
    assert packet["requires_y_star_gov_validation_before_execution"] is True
    assert packet["live_execution_authorized"] is False
    assert packet["external_action_authorized"] is False
    assert packet["declared_Y_star"]
    assert packet["candidate_U"]
    assert packet["execution_boundary"]["behavior_execution_enabled"] is False
    assert mapping["y_star_gov_imported"] is False
    assert mapping["live_hooks_called"] is False


def test_residual_loop_and_learning_stub_do_not_claim_execution_or_writeback() -> None:
    actual = load_json("projection_behavior_residual_loop_fixture/mock_behavior_actual_outcome.json")
    delta = load_json("projection_behavior_residual_loop_fixture/behavior_projection_residual_delta.json")
    learning = load_json("projection_behavior_residual_loop_fixture/projection_learning_candidate_stub.json")

    assert actual["synthetic_dry_run_only"] is True
    assert actual["real_behavior_executed"] is False
    assert delta["real_behavior_executed"] is False
    assert delta["no_execution_residual"]
    assert learning["eligible_for_review_queue"] is True
    assert learning["eligible_for_direct_brain_writeback"] is False
    assert learning["eligible_for_direct_memory_ingestion"] is False
    assert learning["eligible_for_candidate_auto_approval"] is False
    assert learning["requires_human_or_governance_review"] is True
    assert learning["learning_target"] == "projection_policy_only"
    assert learning["live_learning_enabled"] is False


def test_cycle_readiness_requires_artifacts_and_blocked_safety_flags() -> None:
    readiness = load_json("field_projection_cycle_readiness/field_projection_cycle_readiness.json")

    assert readiness["mission_y_star_defined"] is True
    assert readiness["projection_operator_defined"] is True
    assert readiness["mission_to_behavior_trace_generated"] is True
    assert readiness["behavior_level_y_star_candidate_generated"] is True
    assert readiness["pre_u_packet_candidate_generated"] is True
    assert readiness["residual_delta_fixture_generated"] is True
    assert readiness["learning_candidate_stub_generated"] is True
    assert readiness["live_execution_still_blocked"] is True
    assert readiness["writeback_still_blocked"] is True
    assert readiness["external_action_still_blocked"] is True
    assert readiness["ready_for_l5_3_projection_checked_autonomous_cycle"] is True
    assert readiness["next_required_milestone"] == "L5.3 Projection-Checked Autonomous Work Cycle v0"


def test_no_live_external_network_scheduler_daemon_writeback_or_scoring_flags_enabled() -> None:
    for relative_path in JSON_FILES:
        payload = load_json(relative_path)
        for node in walk_json(payload):
            for field in FALSE_FLAG_FIELDS:
                if field in node:
                    assert node[field] is False, f"{relative_path}: {field} must be false"


def test_console_read_model_integration_passes() -> None:
    loader = run_command(["python3", "console_read_model/loader/build_team_console_snapshot.py"])
    assert loader.returncode == 0, loader.stdout + loader.stderr

    summary = load_json("console_read_model/generated/field_projection_summary.json")
    assert summary["field_functional_auto_projection_core_defined"] is True
    assert summary["mission_to_behavior_projection_generated"] is True
    assert summary["behavior_execution_enabled"] is False
    assert summary["ready_for_l5_3_projection_checked_autonomous_cycle"] is True

    cli = run_command(["python3", "console_read_model/cli/team_console.py", "field-projection"])
    assert cli.returncode == 0, cli.stdout + cli.stderr
    assert "Field Functional Auto-Projection Core" in cli.stdout

    validator = run_command(["python3", "console_read_model/validation/validate_team_read_model.py"])
    assert validator.returncode == 0, validator.stdout + validator.stderr


def test_builder_source_is_static_and_non_runtime() -> None:
    source = BUILDER.read_text(encoding="utf-8")
    assert "shell=True" not in source
    assert "import sqlite3" not in source
    assert "subprocess.run" not in source
    assert "requests." not in source
    assert "urllib.request" not in source
    assert ".db-wal" not in source
    assert ".db-shm" not in source
    assert ".sqlite3" not in source
    assert "scripts/.logs" not in source
