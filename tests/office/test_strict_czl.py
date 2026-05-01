from office.mission_command.strict_czl import build_strict_czl_state, strict_czl_is_blocked, strict_czl_is_complete


def test_blocked_status_full_rt1_nonzero():
    state = build_strict_czl_state(
        mission_id="m",
        y_star=["internal_done", "live_external_evidence_available"],
        xt={},
        u=["internal work"],
        y_t1={"internal_done": True, "live_external_evidence_available": False},
        feasible_criteria=["internal_done"],
        full_criteria=["internal_done", "live_external_evidence_available"],
        blocked_reason="missing live config",
        exact_unblock_action=["approve Tier 1 research"],
    )
    assert strict_czl_is_blocked(state)
    assert state.feasible_internal_rt1_score == 0
    assert state.full_mission_rt1_score > 0
    assert not strict_czl_is_complete(state)


def test_feasible_internal_rt1_can_be_zero_while_full_rt1_nonzero():
    state = build_strict_czl_state(
        mission_id="m",
        y_star=["internal_done", "live_external_evidence_available"],
        xt={},
        u=[],
        y_t1={"internal_done": True, "live_external_evidence_available": False},
        feasible_criteria=["internal_done"],
        full_criteria=["internal_done", "live_external_evidence_available"],
        blocked_reason="live evidence missing",
    )
    assert state.feasible_internal_rt1_score == 0
    assert "live_external_evidence_available" in state.full_mission_residuals
