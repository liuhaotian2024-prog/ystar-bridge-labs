from office.mission_command.e35_one_brain_integration_guard import get_artifact


def test_e39_czl_closure_flags_are_safe():
    closure = get_artifact("e39_czl_closure")
    assert closure["claim_graph_created"] is True
    assert closure["contradiction_graph_created"] is True
    assert closure["unsupported_claim_downgrader_created"] is True
    assert closure["durable_research_threads_created"] is True
    assert closure["market_language_lexicon_created"] is True
    assert closure["CEO_decision_eval_benchmark_created"] is True
    assert closure["provider_API_or_tool_execution_occurred"] is False
    assert closure["external_integration_occurred"] is False
    assert closure["customer_validation_claimed"] is False
    assert closure["paid_signal_claimed"] is False
    assert closure["second_CEO_brain_created"] is False
    assert closure["second_CEO_KG_created"] is False
