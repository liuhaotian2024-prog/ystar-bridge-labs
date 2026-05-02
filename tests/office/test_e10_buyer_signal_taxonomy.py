from office.mission_command.e10_buyer_signal_taxonomy import (
    BuyerSignalType,
    REQUIRED_BUYER_SIGNAL_TYPES,
    classify_buyer_signal,
    score_signal_strength,
)


def test_buyer_signal_taxonomy_has_required_signal_types():
    for signal_type in [
        BuyerSignalType.PAIN,
        BuyerSignalType.BUDGET,
        BuyerSignalType.URGENCY,
        BuyerSignalType.TOOL_STACK_COMPLEXITY,
        BuyerSignalType.GOVERNANCE_SAFETY,
        BuyerSignalType.HIRING_JOB,
        BuyerSignalType.IMPLEMENTATION_BURDEN,
        BuyerSignalType.EXISTING_ALTERNATIVE,
        BuyerSignalType.CONTACTABILITY,
        BuyerSignalType.TRUST_GAP,
        BuyerSignalType.DISCONFIRMING,
    ]:
        assert signal_type in REQUIRED_BUYER_SIGNAL_TYPES


def test_classify_buyer_signal_scores_public_budget_signal():
    signal = classify_buyer_signal(
        "Enterprise pricing plans and paid support indicate a visible budget proxy.",
        {"source_id": "src_test", "source_url": "https://example.com", "source_domain": "example.com"},
    )
    assert signal.signal_type == BuyerSignalType.BUDGET
    assert score_signal_strength(signal) >= 1
