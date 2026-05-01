from pathlib import Path

from office.mission_command.e5_market_evidence_evaluator import evaluate_e5_market_evidence
from office.mission_command.evidence_provenance import (
    EvidenceProviderMode,
    build_evidence_run_bundle,
    evidence_bundle_is_market_backing_eligible,
    validate_evidence_run_bundle,
)


def _source(source_id="s1", domain="example.com", opportunity_id="opp_partner_channel_enablement"):
    return {
        "source_id": source_id,
        "url_or_public_identifier": f"https://{domain}/evidence",
        "domain": domain,
        "source_category": "public service page",
        "retrieved_at": "2026-05-01T00:00:00Z",
        "evidence_type": "live_public_read_only",
        "relevant_opportunity_ids": [opportunity_id],
        "summary": "Public page describes AI consultant partner enablement pain and pricing.",
        "buyer_pain_signal": "AI consultants need enablement packages.",
        "pricing_signal": "$2500 package",
        "competitor_signal": "consultant service alternative",
        "substitute_signal": "DIY enablement guide",
        "budget_signal": "consulting services budget",
        "confidence": "test",
        "limitations": ["unit test"],
    }


def _receipt(sources, summary_paths=None, live=True):
    paths = ["reports/integration/test_summaries.md"] if summary_paths is None else summary_paths
    return {
        "mission_id": "e5_market_backed_first_revenue",
        "live_research_executed": live,
        "provider_name": "test_live_provider",
        "started_at": "2026-05-01T00:00:00Z",
        "completed_at": "2026-05-01T00:00:01Z",
        "queries_used": [],
        "pages_read": [source["url_or_public_identifier"] for source in sources],
        "domains_touched": [source["domain"] for source in sources],
        "stopped_reason": "complete",
        "safety_boundary": {"no_customer_contact": True},
        "external_action_executed": False,
        "errors": [],
        "source_summary_paths": paths,
    }


def _valid_bundle():
    sources = [_source("s1", "a.example.com"), _source("s2", "b.example.com")]
    return build_evidence_run_bundle(
        run_id="test_run",
        mission_id="e5_market_backed_first_revenue",
        provider_name="test_live_provider",
        provider_mode=EvidenceProviderMode.SOURCE_SEED_LIVE_PUBLIC_READ_ONLY,
        receipt=_receipt(sources),
        sources=sources,
        source_summary_paths=["reports/integration/test_summaries.md"],
    )


def test_raw_source_list_cannot_mark_market_backed():
    evaluation = evaluate_e5_market_evidence(Path("."), {"sources": [_source()]})
    assert evaluation["default_is_market_backed"] is False
    assert evaluation["mode"] == "internal_only_or_blocked"


def test_validated_bundle_required_for_market_backing():
    assert evidence_bundle_is_market_backing_eligible(_valid_bundle()) is True


def test_fixture_provider_cannot_complete_full_mission():
    source = _source()
    bundle = build_evidence_run_bundle(
        run_id="fixture_run",
        mission_id="e5_market_backed_first_revenue",
        provider_name="deterministic_fake_test_provider",
        provider_mode=EvidenceProviderMode.FIXTURE_ONLY,
        receipt=_receipt([source]),
        sources=[source],
        source_summary_paths=["reports/integration/test_summaries.md"],
        fixture_only=True,
    )
    assert evidence_bundle_is_market_backing_eligible(bundle) is False
    assert "receipt_live_true_requires_live_provider_mode" in validate_evidence_run_bundle(bundle)


def test_deterministic_fake_provider_is_fixture_only():
    bundle = build_evidence_run_bundle(
        run_id="fake",
        mission_id="e5_market_backed_first_revenue",
        provider_name="deterministic_fake_test_provider",
        provider_mode=EvidenceProviderMode.FIXTURE_ONLY,
        fixture_only=True,
    )
    assert bundle.fixture_only is True
    assert bundle.validated_live is False


def test_receipt_true_without_summary_paths_fails_bundle_validation():
    source = _source()
    bundle = build_evidence_run_bundle(
        run_id="bad",
        mission_id="e5_market_backed_first_revenue",
        provider_name="test_live_provider",
        provider_mode=EvidenceProviderMode.SOURCE_SEED_LIVE_PUBLIC_READ_ONLY,
        receipt=_receipt([source], summary_paths=[], live=True),
        sources=[source],
        source_summary_paths=[],
    )
    assert "live_research_true_without_source_summary_paths" in validate_evidence_run_bundle(bundle)
    assert evidence_bundle_is_market_backing_eligible(bundle) is False


def test_source_without_public_identifier_fails():
    source = _source()
    source["url_or_public_identifier"] = ""
    assert any("missing_public_identifier" in item for item in validate_evidence_run_bundle(_valid_bundle().to_dict() | {"sources": [source]}))


def test_source_without_domain_fails():
    source = _source()
    source["domain"] = ""
    assert any("missing_domain" in item for item in validate_evidence_run_bundle(_valid_bundle().to_dict() | {"sources": [source]}))


def test_source_without_relevant_opportunity_ids_fails():
    source = _source()
    source["relevant_opportunity_ids"] = []
    assert any("source_missing_relevant_opportunity_ids" in item for item in validate_evidence_run_bundle(_valid_bundle().to_dict() | {"sources": [source]}))
