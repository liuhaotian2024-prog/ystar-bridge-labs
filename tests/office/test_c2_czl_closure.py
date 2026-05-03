from __future__ import annotations

import json
from pathlib import Path

from office.mission_command.c2_action_queue import build_c2_action_queue
from office.mission_command.c2_constitutional_activation import build_c2_activation_packet
from office.mission_command.c2_czl_closure import build_c2_czl_closure, validate_c2_czl_closure
from office.mission_command.c2_feedback_loop import build_c2_feedback_ingestion_template, validate_c2_feedback_template
from office.mission_command.c2_owner_handoff_capsule import build_c2_owner_handoff_capsule


ROOT = Path(__file__).resolve().parents[2]


def test_c2_czl_closes_local_control_loop_without_external_action() -> None:
    activation = build_c2_activation_packet(ROOT).to_dict()
    queue = build_c2_action_queue(ROOT, activation)
    capsule = build_c2_owner_handoff_capsule(queue).to_dict()
    template = build_c2_feedback_ingestion_template()
    closure = build_c2_czl_closure(
        base_head="27f96e969e688422761d3e18572a3c5008298ba9",
        activation_packet=activation,
        action_queue=queue,
        handoff_capsule=capsule,
        feedback_template_valid=validate_c2_feedback_template(template) == [],
    )
    assert validate_c2_czl_closure(closure) == []
    assert closure.r_t1 == 0
    assert all(value is False for value in closure.no_external_side_effects.values())


def test_c2_generated_artifacts_exist_after_generation() -> None:
    for rel in [
        "operations/external_validation/c2_constitutional_activation_packet.json",
        "operations/external_validation/c2_ygov_decision_envelopes.json",
        "operations/external_validation/c2_gov_mcp_execution_contracts.json",
        "operations/external_validation/c2_governed_action_queue.json",
        "operations/external_validation/c2_owner_handoff_execution_capsule.md",
        "operations/external_validation/c2_feedback_ingestion_template.json",
        "operations/external_validation/c2_signal_loop_fixture.json",
        "reports/integration/c2_governed_first_action_activation_loop.md",
        "reports/integration/c2_y_gov_gov_mcp_execution_control.md",
        "reports/integration/c2_owner_handoff_and_feedback_loop.md",
        "reports/integration/c2_czl_closure.md",
        "operations/repository_delivery/delivery_requests/c2_governed_first_action_activation_loop_delivery.json",
    ]:
        assert (ROOT / rel).exists(), rel


def test_c2_delivery_request_uses_host_side_runner_contract() -> None:
    request = json.loads((ROOT / "operations/repository_delivery/delivery_requests/c2_governed_first_action_activation_loop_delivery.json").read_text(encoding="utf-8"))
    assert request["remote_confirmation_required"] is True
    assert request["expected_base_head"] == "27f96e969e688422761d3e18572a3c5008298ba9"
    assert "host_delivery_runner" in request["safety_boundary"]
    assert "tests/office/test_c2_czl_closure.py" in request["allowed_files"]
