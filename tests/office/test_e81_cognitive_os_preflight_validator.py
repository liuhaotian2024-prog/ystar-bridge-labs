from pathlib import Path

from office.mission_command.e81_ceo_cognitive_os_preflight_validator import (
    build_valid_pre_action_packet,
    validate_post_action_residual,
    validate_pre_action_packet,
)


ROOT = Path(__file__).resolve().parents[2]


def test_e81_validator_allows_valid_packet():
    packet = build_valid_pre_action_packet(ROOT)
    result = validate_pre_action_packet(packet, ROOT)

    assert result["decision"] == "ALLOW"
    assert result["CIEU_validation_record"]["Y_t_plus_1"]["decision"] == "ALLOW"


def test_e81_validator_denies_missing_counterfactual_and_cieu_prediction():
    packet = build_valid_pre_action_packet(ROOT)
    packet["counterfactual_comparison"] = []
    assert validate_pre_action_packet(packet, ROOT)["decision"] == "DENY"

    packet = build_valid_pre_action_packet(ROOT)
    packet["predicted_CIEU_records"] = []
    result = validate_pre_action_packet(packet, ROOT)
    assert result["decision"] == "DENY"
    assert result["failed_stage"] == "pre_action_CIEU_residual_prediction"


def test_e81_validator_denies_l4_without_approval_and_unverified_runtime_claim():
    packet = build_valid_pre_action_packet(ROOT)
    packet["action_class"] = "L4_external_feedback_execution"
    packet["owner_approval_state"] = "pending_owner_decision"
    assert validate_pre_action_packet(packet, ROOT)["decision"] == "DENY"

    packet = build_valid_pre_action_packet(ROOT)
    packet["discovered_capabilities_consulted"].append({"capability_id": "cap_fake_runtime", "evidence_paths": ["prompt_only"], "claimed_runtime_active": True})
    result = validate_pre_action_packet(packet, ROOT)
    assert result["decision"] == "DENY"
    assert result["failed_stage"] == "repository_evidence"


def test_e81_post_action_residual_validator_checks_cieu_and_overclaim():
    residual = {
        "packet_id": "post",
        "linked_pre_action_packet_id": "pre",
        "action_taken": "internal",
        "expected_outcome": "validated",
        "actual_output": "validated",
        "CIEU_record": {"X_t": "x", "U_t": "u", "Y_star_t": "ys", "Y_t_plus_1": "y", "R_t_plus_1": "r"},
        "residuals": [],
        "unexpected_failures": [],
        "overclaim_check": {"customer_validation_claim": False},
        "no_new_wheel_check": {"passed": True},
        "owner_usefulness_check": {"passed": True},
        "intelligence_gate_result": {"passed": True},
        "capability_state_updates": [],
        "learning_candidates": [],
        "YstarGov_sync_status": "pending",
        "next_action_recommendation": "next",
        "what_not_to_do_next": [],
    }
    assert validate_post_action_residual(residual, ROOT)["decision"] == "ALLOW"
    residual["overclaim_check"]["customer_validation_claim"] = True
    assert validate_post_action_residual(residual, ROOT)["decision"] == "DENY"
