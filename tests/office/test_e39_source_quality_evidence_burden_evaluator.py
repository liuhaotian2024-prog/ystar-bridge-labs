from office.mission_command.e39_source_quality_evidence_burden_evaluator import build_source_quality_evidence_burden_evaluator


def test_source_quality_and_evidence_burden_evaluator_routes_clusters():
    evaluator = build_source_quality_evidence_burden_evaluator()
    assert evaluator["source_count"] == 27
    assert evaluator["source_quality_distribution"]
    assert "enterprise / professional AI transformation" in evaluator["clusters_ready_for_expert_preflight"]
    assert "AI productivity / workflow / toolchain" in evaluator["clusters_ready_for_expert_preflight"]
    assert evaluator["clusters_needing_more_public_evidence"]
    assert evaluator["clusters_needing_simulation_or_park"]
    assert evaluator["customer_validation_claimed"] is False
    assert evaluator["paid_signal_claimed"] is False
