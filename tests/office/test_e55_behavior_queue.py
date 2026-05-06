from office.mission_command.e55_behavior_queue import produce_queue_snapshot

def test_behavior_queue_blocks_external_and_prioritizes_internal():
    data = produce_queue_snapshot()
    assert data["queue_status"] == "valid"
    assert "e55_validate_behavior_action_model" in data["dry_run_only_actions"]
    assert "e53_e54_external_review_track" in data["blocked_actions"]
    assert data["pending_owner_decision_not_approval"] is True
