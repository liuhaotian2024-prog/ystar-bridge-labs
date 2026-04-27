from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "governed_tool_invocation_bridge"
GENERATED = PACK / "generated"
BUILDER = PACK / "tools" / "build_tool_invocation_bridge.py"
RUNNER = PACK / "tools" / "run_governed_tool_bridge.py"

JSON_OUTPUTS = [
    "bridge_contract.json",
    "agent_tool_request.json",
    "pre_u_tool_packet.json",
    "governance_decision_envelope.json",
    "bridge_authorization.json",
    "bridge_invocation_trace.json",
    "bridged_tool_result.json",
    "bridge_cieu_event.json",
    "bridge_residual_delta.json",
    "rejected_direct_tool_invocation.json",
    "rejected_unsafe_bridge_request.json",
    "tool_bridge_readiness_summary.json",
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


def assert_disabled(payload: dict, fields: list[str]) -> None:
    for field in fields:
        assert payload[field] is False, f"{field} should remain false"


def test_bridge_artifacts_are_valid_and_contract_first() -> None:
    run_builder()

    for name in JSON_OUTPUTS:
        load_json(name)

    contract = load_json("bridge_contract.json")
    assert contract["bridge_id"] == "governed_tool_invocation_bridge_v0"
    assert contract["supported_tool_id"] == "governed_readonly_observation_tool_v0"
    assert contract["agent_direct_tool_invocation_allowed"] is False
    assert contract["pre_u_packet_required"] is True
    assert contract["governance_decision_required"] is True
    assert contract["bridge_authorization_required"] is True
    assert contract["cieu_event_required"] is True
    assert contract["residual_delta_required"] is True
    assert "allow_local_readonly_tool_invocation" in contract["allowed_decisions"]
    assert_disabled(
        contract,
        [
            "live_enabled",
            "external_action_enabled",
            "network_enabled",
            "git_push_enabled",
            "daemon_control_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "email_or_external_communication_enabled",
        ],
    )


def test_agent_request_pre_u_packet_and_decision_are_safe() -> None:
    run_builder()

    request = load_json("agent_tool_request.json")
    packet = load_json("pre_u_tool_packet.json")
    decision = load_json("governance_decision_envelope.json")
    authorization = load_json("bridge_authorization.json")

    assert request["requesting_agent"] == "Aiden-CEO"
    assert request["supporting_agent"] == "Samantha-Secretary"
    assert request["tool_id"] == "governed_readonly_observation_tool_v0"
    assert request["risk_tier"] == "low"
    assert_disabled(
        request,
        [
            "live_action_requested",
            "external_action_requested",
            "brain_writeback_requested",
            "memory_ingestion_requested",
            "cieu_persistence_requested",
        ],
    )

    assert packet["tool_id"] == request["tool_id"]
    assert packet["request_id"] == request["request_id"]
    assert len(packet["candidate_U"]) >= 3
    assert packet["selected_U"]["u_id"] == "U1"
    assert packet["governance_expectations"]["agent_direct_tool_invocation_allowed"] is False
    assert packet["cieu_link_policy"]["persistence_enabled"] is False

    assert decision["decision"] == "allow_local_readonly_tool_invocation"
    assert decision["allowed_only_as_local_readonly_dry_run"] is True
    assert decision["agent_direct_tool_invocation_allowed"] is False
    assert_disabled(
        decision,
        [
            "live_action_allowed",
            "external_action_allowed",
            "cieu_persistence_allowed",
            "brain_writeback_allowed",
            "memory_ingestion_allowed",
        ],
    )

    assert authorization["authorized"] is True
    assert authorization["authorized_only_for_local_readonly_dry_run"] is True
    assert authorization["agent_direct_tool_invocation_allowed"] is False
    assert authorization["allowed_sources"]
    assert authorization["denied_sources"] == []


def test_runner_invokes_l4_4_tool_only_through_bridge() -> None:
    run_builder()

    run_script(
        str(RUNNER.relative_to(ROOT)),
        "--request",
        "governed_tool_invocation_bridge/generated/agent_tool_request.json",
        "--output-dir",
        "governed_tool_invocation_bridge/generated",
    )

    result = load_json("bridged_tool_result.json")
    trace = load_json("bridge_invocation_trace.json")
    readiness = load_json("tool_bridge_readiness_summary.json")

    assert result["status"] == "success"
    assert result["pre_u_packet_ref"].endswith("pre_u_tool_packet.json")
    assert result["governance_decision_ref"].endswith("governance_decision_envelope.json")
    assert result["bridge_authorization_ref"].endswith("bridge_authorization.json")
    assert result["read_sources"]
    assert result["normalized_observation"]
    assert result["agent_direct_tool_invocation_allowed"] is False
    assert_disabled(
        result,
        [
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
        ],
    )

    assert trace["tool_invoked_through_bridge"] is True
    assert trace["direct_tool_invocation_rejected"] is True
    assert trace["unsafe_bridge_request_rejected"] is True
    assert readiness["tool_invoked_through_bridge"] is True
    assert readiness["first_governed_tool_invocation_chain_created"] is True


def test_rejection_fixtures_fail_closed_without_reads() -> None:
    run_builder()

    direct = load_json("rejected_direct_tool_invocation.json")
    unsafe = load_json("rejected_unsafe_bridge_request.json")

    assert direct["status"] == "rejected"
    assert direct["reason"] == "agent_direct_tool_invocation_disallowed_pre_u_bridge_required"
    assert direct["agent_direct_tool_invocation_allowed"] is False
    assert direct["tool_invoked"] is False
    assert unsafe["status"] == "rejected"
    assert unsafe["tool_invoked"] is False
    assert unsafe["read_sources"] == []
    assert "source_not_in_allowed_registry" in unsafe["blocked_reasons"]
    assert "live_action_requested_forbidden" in unsafe["blocked_reasons"]


def test_bridge_cieu_event_and_residual_delta_are_dry_run_only() -> None:
    run_builder()

    event = load_json("bridge_cieu_event.json")
    delta = load_json("bridge_residual_delta.json")

    assert event["dry_run_only"] is True
    assert event["persistence_enabled"] is False
    assert event["learning_eligibility"] is False
    assert event["curation_required"] is True
    assert event["direct_brain_writeback_allowed"] is False
    assert event["direct_memory_ingestion_allowed"] is False
    assert event["raw_artifact_ingestion_allowed"] is False
    assert delta["curation_required"] is True
    assert delta["direct_brain_writeback_allowed"] is False
    assert delta["direct_memory_ingestion_allowed"] is False
    assert delta["next_review_required"] is True


def test_readiness_summary_keeps_all_live_behavior_disabled() -> None:
    run_builder()

    summary = load_json("tool_bridge_readiness_summary.json")
    for field in [
        "governed_tool_invocation_bridge_defined",
        "bridge_contract_defined",
        "agent_tool_request_defined",
        "pre_u_tool_packet_defined",
        "governance_decision_defined",
        "bridge_authorization_defined",
        "tool_invoked_through_bridge",
        "direct_tool_invocation_rejected",
        "unsafe_bridge_request_rejected",
        "bridge_cieu_event_defined",
        "bridge_residual_delta_defined",
        "mission_bounded_autonomy_supported",
        "step_by_step_human_prompting_reduced",
        "first_governed_tool_invocation_chain_created",
    ]:
        assert summary[field] is True

    assert_disabled(
        summary,
        [
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
        ],
    )
    assert summary["next_required_milestone"] == "L4.6 Agent Team Work Proposal to Governed Tool Invocation v0"


def test_generated_files_do_not_contain_raw_runtime_dependency_strings() -> None:
    run_builder()

    forbidden = [
        ".db-wal",
        ".db-shm",
        ".sqlite",
        ".sqlite3",
        "scripts/.logs/",
    ]
    for path in GENERATED.iterdir():
        if path.suffix not in {".json", ".md"}:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for marker in forbidden:
            assert marker not in text, f"{marker} appeared in {path.name}"


def test_builder_and_runner_sources_are_non_runtime() -> None:
    for path in [BUILDER, RUNNER]:
        source = path.read_text(encoding="utf-8")
        assert "shell=True" not in source
        assert "import sqlite3" not in source
        assert "requests." not in source
        assert "urllib.request" not in source
