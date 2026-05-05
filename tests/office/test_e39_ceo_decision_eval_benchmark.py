from office.mission_command.e39_ceo_decision_eval_benchmark import build_ceo_decision_eval_benchmark


def test_decision_eval_benchmark_scores_prior_decisions_without_validation_claims():
    benchmark = build_ceo_decision_eval_benchmark()
    assert benchmark["decisions_evaluated"] >= 5
    assert benchmark["strongest_decision"] == "E38 public evidence ranking"
    assert benchmark["weakest_decision"] == "E32 Black Box selection"
    assert len(benchmark["dimensions"]) == 12
    for decision in benchmark["decisions"]:
        assert set(benchmark["dimensions"]) == set(decision["benchmark_score_by_dimension"])
    assert benchmark["customer_validation_claimed"] is False
    assert benchmark["paid_signal_claimed"] is False
