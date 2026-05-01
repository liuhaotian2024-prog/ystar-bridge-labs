from pathlib import Path

from office.mission_command.e7_evidence_quality import (
    assess_source_quality,
    build_e7_evidence_quality_table,
    detect_noise_flags,
    parse_e6_external_source_summaries,
)


ROOT = Path(__file__).resolve().parents[2]


def test_e7_inspection_report_exists():
    assert (ROOT / "reports" / "integration" / "e7_implementation_inspection.md").exists()


def test_evidence_quality_detects_js_css_json_noise():
    raw = 'window.dataLayer = []; @font-face{font-family:x} {"@context":"https://schema.org"}'
    flags = detect_noise_flags(raw)
    assert "javascript_noise" in flags
    assert "css_or_style_noise" in flags
    assert "json_or_schema_noise" in flags


def test_evidence_quality_marks_noisy_source_not_customer_facing_usable():
    assessment = assess_source_quality(
        {
            "source_id": "noisy",
            "domain": "example.com",
            "source_category": "public pricing pages",
            "relevant_opportunity_ids": ["opp_integration_implementation_ai_ops_room"],
            "summary": "Pricing !function(){window.dataLayer=[];} {css:true}",
            "pricing_signal": "Pricing plan",
            "buyer_pain_signal": "workflow pain",
            "competitor_signal": "vendor",
            "substitute_signal": "DIY",
            "budget_signal": "budget proxy",
            "limitations": ["test"],
        }
    )
    assert assessment.noise_flags
    assert assessment.usable_for_customer_facing_packet is False


def test_evidence_quality_preserves_useful_source_as_internal_evidence():
    assessment = assess_source_quality(
        {
            "source_id": "clean",
            "domain": "example.com",
            "source_category": "public pricing pages",
            "relevant_opportunity_ids": ["opp_integration_implementation_ai_ops_room"],
            "summary": "The page describes enterprise AI workflow pricing and implementation support for teams.",
            "pricing_signal": "enterprise plan pricing",
            "buyer_pain_signal": "teams need implementation support",
            "competitor_signal": "vendor alternative",
            "substitute_signal": "DIY platform",
            "budget_signal": "subscription budget proxy",
            "limitations": ["test"],
        }
    )
    assert assessment.claim_type == "directly_supported"
    assert assessment.usable_for_customer_facing_packet is True


def test_evidence_quality_distinguishes_claim_types():
    buyer_only = assess_source_quality(
        {
            "source_id": "buyer",
            "domain": "example.com",
            "source_category": "public article",
            "summary": "A founder says AI workflow coordination is painful.",
            "buyer_pain_signal": "AI workflow coordination is painful",
        }
    )
    weak = assess_source_quality({"source_id": "weak", "domain": "example.com", "summary": ""})
    assert buyer_only.claim_type == "requires_validation"
    assert weak.claim_type == "internal_hypothesis"


def test_cleaned_evidence_table_contains_source_ids_domains_roles_limitations():
    sources = parse_e6_external_source_summaries(ROOT / "reports" / "integration" / "e6_external_source_summaries.md")
    rows = build_e7_evidence_quality_table(sources)
    report = (ROOT / "reports" / "integration" / "e7_cleaned_evidence_table.md").read_text(encoding="utf-8")
    assert rows
    assert "Source ID" in report
    assert "Domain" in report
    assert "Role" in report
    assert "Limitations" in report
    assert rows[0]["source_id"] in report
