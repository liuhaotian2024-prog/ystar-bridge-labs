from office.mission_command.e39_expert_review_readiness_reassessment import build_expert_review_readiness_reassessment


def test_expert_review_readiness_reassesses_without_sending():
    readiness = build_expert_review_readiness_reassessment()
    assert "enterprise / professional AI transformation" in readiness["ready_clusters"]
    assert "AI productivity / workflow / toolchain" in readiness["ready_clusters"]
    assert readiness["not_ready_clusters"]
    assert "no send" in readiness["recommended_E40_route"] or "preflight" in readiness["recommended_E40_route"]
    assert readiness["customer_validation_claimed"] is False
    assert readiness["paid_signal_claimed"] is False
