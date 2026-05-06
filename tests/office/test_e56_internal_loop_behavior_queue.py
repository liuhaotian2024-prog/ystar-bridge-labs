from office.mission_command.e56_internal_loop_behavior_queue import build_internal_loop_behavior_queue


def test_behavior_queue_receives_selected_action_and_blocks_external():
    data = build_internal_loop_behavior_queue()
    assert data["queue_status"] == "valid"
    assert data["selected_action_queued"] is True
    assert data["external_first_user_review_denied"] is True
    assert data["owner_decision_status"] == "pending_owner_decision"

