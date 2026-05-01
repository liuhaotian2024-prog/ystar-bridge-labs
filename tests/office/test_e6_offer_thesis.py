from pathlib import Path

from office.mission_command.e6_market_evidence_evaluator import evaluate_e6_market_evidence
from office.mission_command.e6_offer_thesis import build_e6_offer_thesis
from office.mission_command.evidence_provenance import EvidenceProviderMode, build_evidence_run_bundle


ROOT = Path(__file__).resolve().parents[2]


def _bundle(valid=True):
    sources = [
        {
            "source_id": "s1",
            "url_or_public_identifier": "https://a.example.com/pricing",
            "domain": "a.example.com",
            "source_category": "public pricing pages",
            "retrieved_at": "2026-05-01T00:00:00Z",
            "evidence_type": "live_public_read_only",
            "relevant_opportunity_ids": ["opp_integration_implementation_ai_ops_room"],
            "summary": "AI ops pricing and implementation buyer pain.",
            "buyer_pain_signal": "AI ops implementation pain",
            "pricing_signal": "$3000",
            "competitor_signal": "vendor",
            "substitute_signal": "DIY platform",
            "budget_signal": "budget proxy",
            "confidence": "test",
            "limitations": ["unit test"],
        },
        {
            "source_id": "s2",
            "url_or_public_identifier": "https://b.example.org/pricing",
            "domain": "b.example.org",
            "source_category": "public pricing pages",
            "retrieved_at": "2026-05-01T00:00:00Z",
            "evidence_type": "live_public_read_only",
            "relevant_opportunity_ids": ["opp_integration_implementation_ai_ops_room"],
            "summary": "AI ops pricing and workflow buyer pain.",
            "buyer_pain_signal": "AI workflow buyer pain",
            "pricing_signal": "$5000",
            "competitor_signal": "vendor",
            "substitute_signal": "DIY platform",
            "budget_signal": "budget proxy",
            "confidence": "test",
            "limitations": ["unit test"],
        },
    ] if valid else []
    receipt = {
        "mission_id": "e6_source_seeded_market_evidence_run",
        "live_research_executed": bool(valid),
        "provider_name": "source_seeded_public_page_read",
        "started_at": "2026-05-01T00:00:00Z",
        "completed_at": "2026-05-01T00:00:01Z",
        "queries_used": [],
        "pages_read": [source["url_or_public_identifier"] for source in sources],
        "domains_touched": [source["domain"] for source in sources],
        "stopped_reason": "complete" if valid else "blocked",
        "safety_boundary": {"no_customer_contact": True},
        "external_action_executed": False,
        "errors": [],
        "source_summary_paths": ["reports/integration/e6_external_source_summaries.md"] if valid else [],
    }
    return build_evidence_run_bundle(
        run_id="e6_test",
        mission_id="e6_source_seeded_market_evidence_run",
        provider_name="source_seeded_public_page_read",
        provider_mode=EvidenceProviderMode.SOURCE_SEED_LIVE_PUBLIC_READ_ONLY,
        receipt=receipt,
        sources=sources,
        source_summary_paths=receipt["source_summary_paths"],
    )


def test_e6_offer_thesis_evidence_backed_only_with_market_eligible_top_path():
    bundle = _bundle(True)
    evaluation = evaluate_e6_market_evidence(ROOT, bundle)
    thesis = build_e6_offer_thesis(evaluation, bundle.to_dict())
    assert thesis["thesis_status"] == "evidence_backed"
    assert thesis["customer_contact_still_blocked"] is True


def test_e6_offer_thesis_blocked_when_evidence_insufficient():
    bundle = _bundle(False)
    evaluation = evaluate_e6_market_evidence(ROOT, bundle)
    thesis = build_e6_offer_thesis(evaluation, bundle.to_dict())
    assert thesis["thesis_status"] == "blocked_insufficient_public_evidence"
    assert thesis["no_customer_contact_recommendation"] is True
