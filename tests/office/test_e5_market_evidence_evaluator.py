from pathlib import Path

from office.mission_command.e5_market_evidence_evaluator import evaluate_e5_market_evidence
from office.mission_command.evidence_provenance import EvidenceProviderMode, build_evidence_run_bundle


ROOT = Path(__file__).resolve().parents[2]


def _source(source_id, domain, opportunity_id="opp_partner_channel_enablement"):
    return {
        "source_id": source_id,
        "url_or_public_identifier": f"https://{domain}/public",
        "domain": domain,
        "source_category": "public service page",
        "retrieved_at": "2026-05-01T00:00:00Z",
        "evidence_type": "live_public_read_only",
        "relevant_opportunity_ids": [opportunity_id],
        "summary": "Public source describes partner enablement package, buyer pain, pricing plan, and consulting alternatives.",
        "buyer_pain_signal": "AI consultants need partner enablement.",
        "pricing_signal": "$3000 package",
        "competitor_signal": "AI consultant service",
        "substitute_signal": "DIY guide",
        "budget_signal": "consulting services budget",
        "confidence": "test",
        "limitations": ["unit test"],
    }


def _bundle(mode=EvidenceProviderMode.SOURCE_SEED_LIVE_PUBLIC_READ_ONLY, fixture=False):
    sources = [_source("s1", "a.example.com"), _source("s2", "b.example.org")]
    receipt = {
        "mission_id": "e5_market_backed_first_revenue",
        "live_research_executed": True,
        "provider_name": "test_provider",
        "started_at": "2026-05-01T00:00:00Z",
        "completed_at": "2026-05-01T00:00:01Z",
        "queries_used": [],
        "pages_read": [source["url_or_public_identifier"] for source in sources],
        "domains_touched": [source["domain"] for source in sources],
        "stopped_reason": "complete",
        "safety_boundary": {"no_customer_contact": True},
        "external_action_executed": False,
        "errors": [],
        "source_summary_paths": ["reports/integration/test_summaries.md"],
    }
    return build_evidence_run_bundle(
        run_id="test",
        mission_id="e5_market_backed_first_revenue",
        provider_name="test_provider",
        provider_mode=mode,
        receipt=receipt,
        sources=sources,
        source_summary_paths=["reports/integration/test_summaries.md"],
        fixture_only=fixture,
    )


def test_evaluator_internal_only_without_valid_bundle():
    evaluation = evaluate_e5_market_evidence(ROOT)
    assert evaluation["bundle_valid"] is False
    assert evaluation["default_is_market_backed"] is False
    assert evaluation["default_recommendation"] == "obtain_validated_public_evidence_bundle"


def test_evaluator_market_backed_with_two_independent_live_sources():
    evaluation = evaluate_e5_market_evidence(ROOT, _bundle())
    target = next(row for row in evaluation["rows"] if row["opportunity"]["opportunity_id"] == "opp_partner_channel_enablement")
    assert evaluation["bundle_valid"] is True
    assert target["market_backed"] is True
    assert target["score"]["source_independence"] == 2


def test_evaluator_rejects_fixture_evidence_as_market_backing():
    evaluation = evaluate_e5_market_evidence(ROOT, _bundle(EvidenceProviderMode.FIXTURE_ONLY, fixture=True))
    assert evaluation["bundle_valid"] is False
    assert all(not row["market_backed"] for row in evaluation["rows"])


def test_evaluator_applies_narrowness_penalty_without_external_evidence():
    evaluation = evaluate_e5_market_evidence(ROOT)
    penalized = [row for row in evaluation["rows"] if row["score"]["narrowness_penalty"] > 0]
    assert penalized
    assert all(row["evidence_mode"] == "internal_hypothesis_only" for row in penalized)
