from office.mission_command.e84_ystar_gov_ceo_cognitive_os_call_adapter import (
    build_sample_pre_action_packet,
    validate_pre_action_with_ystar_gov,
)
from office.mission_command.e85_ceo_cognitive_os_runtime_bridge import (
    assess_formal_cieu_log_insertion,
    build_ceo_major_action_runtime_envelope,
    build_provider_tool_ceo_major_action_runtime_envelope,
    build_l5_runtime_readiness_gate,
    route_provider_tool_action_through_runtime_nervous_system,
    route_ceo_major_action_through_ystar_gov_runtime,
    run_runtime_bridge_smoke,
    write_e85_artifacts,
)


def test_runtime_bridge_calls_ystar_gov_hook_and_maps_allow():
    result = route_ceo_major_action_through_ystar_gov_runtime(
        build_ceo_major_action_runtime_envelope()
    )

    assert result["YstarGov_import_status"] == "direct_YstarGov_runtime_hook_import_used"
    assert result["YstarGov_runtime_decision"] == "ALLOW"
    assert result["bridge_labs_route"]["route"] == "approved_next_step_pending_execution_boundary"
    assert result["bridge_labs_route"]["external_execution_allowed"] is False
    assert result["external_action_executed"] is False
    assert result["provider_live_execution"] is False


def test_e84_direct_call_adapter_remains_compatible():
    result = validate_pre_action_with_ystar_gov(build_sample_pre_action_packet())

    assert result["YstarGov_import_status"] == "direct_YstarGov_import_used"
    assert result["YstarGov_decision"] == "ALLOW"
    assert result["route"]["route"] == "continue_to_approved_next_step_without_external_execution"
    assert result["route"]["execution_allowed_by_adapter"] is False


def test_runtime_bridge_maps_require_revision_with_correct_path():
    packet = build_sample_pre_action_packet()
    packet["counterfactual_comparison"] = []

    result = route_ceo_major_action_through_ystar_gov_runtime(
        build_ceo_major_action_runtime_envelope(packet=packet)
    )

    assert result["YstarGov_runtime_decision"] == "REQUIRE_REVISION"
    assert result["bridge_labs_route"]["route"] == "ceo_revision_required_with_correct_path"
    assert result["bridge_labs_route"]["ceo_revision_required"] is True
    assert result["YstarGov_correct_path"]


def test_runtime_bridge_maps_escalate_to_owner_decision_no_execution():
    packet = build_sample_pre_action_packet(action_class="L4_external_feedback_execution")

    result = route_ceo_major_action_through_ystar_gov_runtime(
        build_ceo_major_action_runtime_envelope(
            packet=packet,
            objective="prepare L4 external feedback owner decision without execution",
            externality_level="external_feedback",
            owner_approval_status="pending_owner_decision",
        )
    )

    assert result["YstarGov_runtime_decision"] == "ESCALATE"
    assert result["bridge_labs_route"]["route"] == "owner_decision_packet_required_no_execution"
    assert result["bridge_labs_route"]["owner_decision_packet_required"] is True
    assert result["external_action_executed"] is False


def test_runtime_bridge_maps_deny_to_blocked_residual_candidate():
    envelope = build_ceo_major_action_runtime_envelope()
    envelope["bypass_attempt"] = True

    result = route_ceo_major_action_through_ystar_gov_runtime(envelope)

    assert result["YstarGov_runtime_decision"] == "DENY"
    assert result["bridge_labs_route"]["route"] == "execution_blocked_with_residual_candidate"
    assert result["bridge_labs_route"]["execution_blocked"] is True
    assert result["CIEU_validation_record_candidate"]


def test_runtime_bridge_requires_post_action_residual_for_closure():
    envelope = build_ceo_major_action_runtime_envelope(action_phase="completed")

    result = route_ceo_major_action_through_ystar_gov_runtime(envelope)

    assert result["YstarGov_runtime_decision"] == "REQUIRE_REVISION"
    assert result["YstarGov_post_action_residual_required"] is True
    assert result["bridge_labs_route"]["route"] == "ceo_revision_required_with_correct_path"


def test_formal_cieu_log_is_deferred_candidate_only():
    cieu = assess_formal_cieu_log_insertion()

    assert cieu["formal_CIEU_log_written"] is False
    assert cieu["formal_CIEU_log_status"] == "CIEU_log_write_deferred"
    assert cieu["validator_output_status"] == "CIEU_validation_record_candidate_only"


def test_l5_readiness_gate_claims_foundation_not_business_completion():
    gate = build_l5_runtime_readiness_gate()

    assert gate["status"]["L5_runtime_foundation"] is True
    assert gate["status"]["L5_business_loop_complete"] is False
    assert gate["status"]["L5_revenue_loop_complete"] is False
    assert gate["status"]["L5_external_feedback_loop_complete"] is False
    assert gate["still_pending"]["gov_mcp_provider_tool_execution_envelope_integration"] is True


def test_provider_tool_action_routes_to_gov_mcp_dry_run_only_after_allow():
    result = route_provider_tool_action_through_runtime_nervous_system(
        build_provider_tool_ceo_major_action_runtime_envelope()
    )

    receipt = result["gov_mcp_receipt"]
    assert result["YstarGov_route"]["YstarGov_runtime_decision"] == "ALLOW"
    assert result["gov_mcp_dry_run_invoked"] is True
    assert receipt["execution_mode_boundary"] == "dry_run_only"
    assert receipt["provider_action_executed"] is False
    assert receipt["external_side_effect"] is False
    assert receipt["external_provider_called"] is False
    assert receipt["no_send_invariant"] is True
    assert receipt["receipt_id"]


def test_provider_tool_action_does_not_call_gov_mcp_when_revision_required():
    packet = build_sample_pre_action_packet(action_class="provider_tool_execution")
    packet["counterfactual_comparison"] = []

    result = route_provider_tool_action_through_runtime_nervous_system(
        build_provider_tool_ceo_major_action_runtime_envelope(packet=packet)
    )

    assert result["YstarGov_route"]["YstarGov_runtime_decision"] == "REQUIRE_REVISION"
    assert result["gov_mcp_dry_run_invoked"] is False
    assert result["gov_mcp_receipt"] == {}
    assert result["external_side_effect"] is False


def test_runtime_bridge_smoke_covers_all_decision_routes():
    smoke = run_runtime_bridge_smoke()

    assert smoke["valid_internal_major_action"]["YstarGov_runtime_decision"] == "ALLOW"
    assert smoke["repairable_missing_counterfactual"]["YstarGov_runtime_decision"] == "REQUIRE_REVISION"
    assert smoke["owner_decision_boundary"]["YstarGov_runtime_decision"] == "ESCALATE"
    assert smoke["hard_boundary_bypass"]["YstarGov_runtime_decision"] == "DENY"
    assert smoke["post_action_residual"]["YstarGov_runtime_decision"] == "ALLOW"


def test_e85_artifacts_are_generated_without_external_action(tmp_path):
    report = write_e85_artifacts(tmp_path)

    assert report["L5_status"]["L5_runtime_foundation"] is True
    assert report["L5_status"]["L5_business_loop_complete"] is False
    assert report["runtime_nervous_system_chain"]["provider_route_fixture"]["gov_mcp_dry_run_invoked"] is True
    assert report["formal_CIEU_log_status"]["formal_CIEU_log_written"] is False
    assert report["formal_CIEU_log_status"]["formal_CIEU_log_status"] == "CIEU_log_write_deferred"
    assert report["safety_statement"]["no_external_action"] is True
    assert (tmp_path / "office/mission_command/e85_ceo_nervous_system_l5_runtime_foundation_report.json").exists()
    assert (tmp_path / "office/mission_command/e85r_canonical_delivery_and_runtime_nervous_system_report.json").exists()
    assert (tmp_path / "operations/external_validation/e85_l5_runtime_readiness_gate.json").exists()
