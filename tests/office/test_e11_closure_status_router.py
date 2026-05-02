from office.mission_command.closure_status_router import ClosureStatusFamily, route_closure_status


def test_closure_status_router_distinguishes_discovery_complete_from_validation_complete_if_router_implemented():
    discovery = route_closure_status(ClosureStatusFamily.DISCOVERY_COMPLETE, has_target_candidates=True)
    validation = route_closure_status(ClosureStatusFamily.VALIDATION_COMPLETE, has_target_candidates=True)
    assert discovery.allowed is True
    assert validation.allowed is False
    assert validation.status_boundary == "validation_is_not_paid_signal"


def test_closure_status_router_distinguishes_validation_complete_from_paid_signal_complete_if_router_implemented():
    validation = route_closure_status(ClosureStatusFamily.VALIDATION_COMPLETE, has_feedback_events=True)
    paid_signal = route_closure_status(ClosureStatusFamily.PAID_SIGNAL_COMPLETE, has_feedback_events=True)
    assert validation.allowed is True
    assert paid_signal.allowed is False
    assert paid_signal.required_evidence == "paid_signal"

