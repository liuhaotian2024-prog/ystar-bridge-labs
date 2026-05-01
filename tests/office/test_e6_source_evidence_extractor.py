from office.mission_command.source_evidence_extractor import (
    extract_source_evidence_signals,
    source_supports_market_backing,
)


def test_e6_extractor_detects_pricing_language_from_excerpt():
    signals = extract_source_evidence_signals(
        text_excerpt="Enterprise pricing plans include paid subscription tiers for AI workflow teams.",
        title="Pricing",
        domain="example.com",
        source_category="public pricing pages",
        evidence_sought=["pricing"],
    )
    assert signals.pricing_signal
    assert signals.budget_signal


def test_e6_extractor_detects_contact_sales_or_enterprise_buying_process():
    signals = extract_source_evidence_signals(
        text_excerpt="Contact sales for enterprise plans and billing details.",
        title="Plans",
        domain="example.com",
        source_category="public pricing pages",
        evidence_sought=["buying process"],
    )
    assert signals.buying_process_signal


def test_e6_extractor_records_trust_gap_and_limitations():
    signals = extract_source_evidence_signals(
        text_excerpt="Security, privacy, governance, and authorization controls are important.",
        title="Security",
        domain="example.com",
        source_category="public docs",
        evidence_sought=["trust gap"],
    )
    assert signals.trust_gap_signal
    assert signals.limitation_notes


def test_e6_extractor_market_backing_support_requires_real_signals():
    signals = extract_source_evidence_signals(
        text_excerpt="AI workflow pricing plans show a paid enterprise category.",
        title="Pricing",
        domain="example.com",
        source_category="public pricing pages",
        evidence_sought=["pricing"],
    )
    assert source_supports_market_backing(signals) is True
