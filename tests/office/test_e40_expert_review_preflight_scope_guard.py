from office.mission_command.e40_expert_review_preflight_scope_guard import build_expert_review_preflight_scope_guard


def test_scope_guard_forbids_external_action_and_validation_claims():
    guard = build_expert_review_preflight_scope_guard()
    assert "expert profile generation" in guard["allowed"]
    assert "send" in guard["forbidden"]
    assert "provider/API/tool execution" in guard["forbidden"]
    assert guard["any_artifact_implies_review_occurred"] is False
    assert guard["message_drafts_unsent"] is True
    assert guard["final_product_selected"] is False
    assert guard["customer_validation_claimed"] is False
    assert guard["paid_signal_claimed"] is False
