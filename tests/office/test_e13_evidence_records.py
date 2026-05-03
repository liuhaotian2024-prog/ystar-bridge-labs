from office.mission_command.e13_evidence_records import (
    E13EvidenceQuality,
    build_evidence_record,
    classify_evidence_quality,
    validate_evidence_record,
)


def test_e13_evidence_records_require_source_claim_quality_limitations():
    record = build_evidence_record(
        "ev1",
        "Agent Workflow Bottleneck Diagnosis",
        "https://example.com",
        "public_forum_or_community",
        "Teams describe agent workflow bottleneck and manual governance pain.",
    )
    assert validate_evidence_record(record) == []
    data = record.to_dict()
    assert data["source_url_or_ref"]
    assert data["claim_supported"]
    assert data["evidence_quality"]
    assert data["limitations"]


def test_e13_rejects_fake_evidence():
    record = build_evidence_record(
        "ev1",
        "Agent Workflow Bottleneck Diagnosis",
        "fake:source",
        "public_web_page",
        "fake",
    )
    errors = validate_evidence_record(record)
    assert "fake_evidence_source_rejected" in errors
    assert "unsupported_or_fake_claim_rejected" in errors


def test_e13_distinguishes_direct_buyer_pain_from_indirect_market_evidence():
    direct = classify_evidence_quality("public_forum_or_community", "workflow bottleneck and governance pain")
    indirect = classify_evidence_quality("public_blog_post", "AI adoption is growing across teams")
    assert direct == E13EvidenceQuality.DIRECT_BUYER_PAIN
    assert indirect == E13EvidenceQuality.INDIRECT_MARKET_EVIDENCE
