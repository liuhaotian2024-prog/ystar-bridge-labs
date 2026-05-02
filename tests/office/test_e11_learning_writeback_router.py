from office.mission_command.learning_writeback_router import LearningDestination, LearningSource, route_learning_writeback


def test_learning_writeback_router_blocks_report_direct_brain_writeback_if_router_implemented():
    decision = route_learning_writeback(LearningSource.REPORT_ONLY_LEARNING, LearningDestination.BRAIN_GRAPH)
    assert decision.allowed is False
    assert decision.requires_cieu_delta is True


def test_learning_writeback_router_requires_cieu_delta_for_brain_writeback_if_router_implemented():
    blocked = route_learning_writeback(LearningSource.CIEU_PREDICTION_DELTA, LearningDestination.BRAIN_GRAPH)
    allowed = route_learning_writeback(
        LearningSource.CIEU_PREDICTION_DELTA,
        LearningDestination.BRAIN_GRAPH,
        has_cieu_delta=True,
        explicit_gate=True,
    )
    assert blocked.allowed is False
    assert allowed.allowed is True

