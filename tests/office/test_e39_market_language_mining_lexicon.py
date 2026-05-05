from office.mission_command.e39_market_language_mining_lexicon import build_market_language_lexicon


def test_market_language_lexicon_has_real_terms_and_usage_boundaries():
    lexicon = build_market_language_lexicon()
    assert lexicon["term_count"] >= 30
    assert lexicon["expert_review_facing_candidates"]
    for term in lexicon["terms"]:
        assert term["language_type"] in {"market language observed in sources", "Y* internal language", "invented language", "overclaim language"}
        assert term["recommended_usage"] in {"owner-facing", "expert-review-facing", "buyer-facing later", "internal only", "avoid"}
    assert lexicon["customer_validation_claimed"] is False
    assert lexicon["paid_signal_claimed"] is False
