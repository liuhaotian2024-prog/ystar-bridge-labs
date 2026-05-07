import json
from pathlib import Path

from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
from office.mission_command.e84_readback import (
    REQUIRED_ARTIFACTS,
    build_cieu_log_terminology_correction,
    build_e83_correctness_audit,
    build_runtime_wiring_design,
    generate_e84_artifacts,
    load_e84_runtime_interface_state_for_brain,
)
from office.mission_command.e84_ystar_gov_ceo_cognitive_os_call_adapter import (
    build_sample_pre_action_packet,
    build_sample_post_action_residual,
    validate_post_action_with_ystar_gov,
    validate_pre_action_with_ystar_gov,
)


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_e84_required_artifacts_exist_and_generate():
    generate_e84_artifacts()

    for rel in REQUIRED_ARTIFACTS:
        assert (ROOT / rel).exists(), rel


def test_cieu_log_terminology_correction_blocks_invented_trace_language():
    correction = build_cieu_log_terminology_correction()

    assert correction["E83_validator_output"] == "CIEU_validation_record_candidate"
    assert correction["formal_CIEU_log_write_status"] == "CIEU_log_write_deferred"
    assert "CIEU-style trace" in correction["forbidden_terms"]

    for rel in REQUIRED_ARTIFACTS:
        if rel.endswith("e84_cieu_log_terminology_correction.json"):
            continue
        if rel.startswith("operations/external_validation/e84_"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            assert "CIEU-style trace" not in text


def test_bridge_adapter_calls_ystar_gov_validator_and_routes_allow():
    result = validate_pre_action_with_ystar_gov(build_sample_pre_action_packet())

    assert result["YstarGov_import_status"] == "direct_YstarGov_import_used"
    assert result["YstarGov_decision"] == "ALLOW"
    assert result["route"]["route"] == "continue_to_approved_next_step_without_external_execution"
    assert result["route"]["execution_allowed_by_adapter"] is False
    assert result["formal_CIEU_log_written"] is False
    assert result["formal_CIEU_log_status"] == "CIEU_log_write_deferred"


def test_bridge_adapter_routes_require_revision_guidance():
    packet = build_sample_pre_action_packet()
    packet["counterfactual_comparison"] = []

    result = validate_pre_action_with_ystar_gov(packet)

    assert result["YstarGov_decision"] == "REQUIRE_REVISION"
    assert result["route"]["ceo_revision_required"] is True
    assert result["route"]["block_execution"] is True
    assert result["YstarGov_guidance"]["guidance_type"] == "require_revision"
    assert result["YstarGov_correct_path"]


def test_bridge_adapter_routes_escalate_to_owner_decision_path():
    packet = build_sample_pre_action_packet(action_class="L4_external_feedback_execution")

    result = validate_pre_action_with_ystar_gov(packet)

    assert result["YstarGov_decision"] == "ESCALATE"
    assert result["route"]["owner_decision_packet_required"] is True
    assert result["route"]["execution_allowed_by_adapter"] is False
    assert result["YstarGov_requires_owner_decision"] is True


def test_bridge_adapter_routes_deny_for_forbidden_claims():
    packet = build_sample_pre_action_packet()
    packet["overclaim_boundary"]["customer_validation_claim"] = True

    result = validate_pre_action_with_ystar_gov(packet)

    assert result["YstarGov_decision"] == "DENY"
    assert result["route"]["block_execution"] is True
    assert "customer_validation_claim" in result["YstarGov_reason"]


def test_post_action_residual_validation_is_candidate_not_log_write():
    result = validate_post_action_with_ystar_gov(build_sample_post_action_residual())

    assert result["YstarGov_decision"] == "ALLOW"
    assert result["CIEU_validation_record_candidate"]
    assert result["formal_CIEU_log_written"] is False
    assert result["formal_CIEU_log_status"] == "CIEU_log_write_deferred"


def test_e83_correctness_and_runtime_design_choose_call_adapter_not_fake_log():
    audit = build_e83_correctness_audit()
    design = build_runtime_wiring_design()

    assert audit["decision"] == "correct_but_needs_bridge_labs_call_adapter"
    assert audit["answers"]["bridge_labs_called_YstarGov_before_E84"] is False
    assert audit["answers"]["bridge_labs_calls_YstarGov_after_E84"] is True
    assert design["routing"]["REQUIRE_REVISION"] == "return_correct_path_guidance_to_CEO"
    assert design["formal_CIEU_log_write_status"] == "CIEU_log_write_deferred"


def test_e84_completion_report_has_no_external_action_or_overclaim():
    generate_e84_artifacts()
    completion = _load("operations/external_validation/e84_completion_report.json")
    safety = completion["safety_statement"]

    assert completion["gov_mcp_availability"] == "available_read_only"
    assert completion["formal_CIEU_log_write_status"] == "CIEU_log_write_deferred"
    assert completion["validator_output_remains_CIEU_validation_record_only"] is True
    assert completion["patch_result"]["patch_type"] == "bridge_labs_call_adapter"
    assert safety["no_external_action"] is True
    assert safety["no_customer_validation_claim"] is True
    assert safety["no_paid_signal_claim"] is True
    assert safety["no_pricing_validation_claim"] is True
    assert safety["no_compliance_legal_claim"] is True
    assert safety["no_production_deployment_claim"] is True
    assert safety["no_L4_execution_claim"] is True
    assert safety["no_L5_readiness_claim"] is True
    assert safety["gov_mcp_mutated"] is False


def test_ceo_brain_readback_reports_e84_runtime_interface_state():
    generate_e84_artifacts()
    readback = load_e84_runtime_interface_state_for_brain()
    context = load_ceo_brain_context({"task_title": "E84 readback", "task_description": "runtime interface"})

    assert readback["bridge_labs_call_adapter_active"] is True
    assert context["current_e84_bridge_labs_call_adapter_active"] is True
    assert context["current_e84_formal_CIEU_log_write_status"] == "CIEU_log_write_deferred"
    assert context["current_e84_external_action_allowed"] is False
    assert context["current_e84_L4_execution_authorized"] is False
    assert context["current_e84_L5_ready"] is False
