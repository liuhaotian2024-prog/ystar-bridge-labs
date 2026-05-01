from pathlib import Path

from office.mission_command.e6_market_evidence_evaluator import evaluate_e6_market_evidence
from office.mission_command.evidence_provenance import EvidenceProviderMode, build_evidence_run_bundle


ROOT = Path(__file__).resolve().parents[2]


def _source(source_id, domain, opportunity_id):
    return {
        "source_id": source_id,
        "url_or_public_identifier": f"https://{domain}/pricing",
        "domain": domain,
        "source_category": "public pricing pages",
        "retrieved_at": "2026-05-01T00:00:00Z",
        "evidence_type": "live_public_read_only",
        "relevant_opportunity_ids": [opportunity_id],
        "summary": "Public pricing page shows enterprise AI workflow implementation category.",
        "buyer_pain_signal": "AI workflow implementation pain.",
        "pricing_signal": "enterprise pricing plan",
        "competitor_signal": "public product/service alternative",
        "substitute_signal": "DIY platform alternative",
        "budget_signal": "paid plan budget proxy",
        "confidence": "test",
        "limitations": ["unit test"],
    }


def _bundle(opportunity_id="opp_integration_implementation_ai_ops_room", single=False, fixture=False):
    sources = [_source("s1", "a.example.com", opportunity_id)]
    if not single:
        sources.append(_source("s2", "b.example.org", opportunity_id))
    receipt = {
        "mission_id": "e6_source_seeded_market_evidence_run",
        "live_research_executed": True,
        "provider_name": "source_seeded_public_page_read",
        "started_at": "2026-05-01T00:00:00Z",
        "completed_at": "2026-05-01T00:00:01Z",
        "queries_used": [],
        "pages_read": [source["url_or_public_identifier"] for source in sources],
        "domains_touched": [source["domain"] for source in sources],
        "stopped_reason": "complete",
        "safety_boundary": {"no_customer_contact": True},
        "external_action_executed": False,
        "errors": [],
        "source_summary_paths": ["reports/integration/e6_external_source_summaries.md"],
    }
    return build_evidence_run_bundle(
        run_id="e6_test",
        mission_id="e6_source_seeded_market_evidence_run",
        provider_name="source_seeded_public_page_read",
        provider_mode=EvidenceProviderMode.FIXTURE_ONLY if fixture else EvidenceProviderMode.SOURCE_SEED_LIVE_PUBLIC_READ_ONLY,
        receipt=receipt,
        sources=sources,
        source_summary_paths=["reports/integration/e6_external_source_summaries.md"],
        fixture_only=fixture,
    )


def test_e6_evaluator_requires_valid_bundle_for_market_backed():
    assert evaluate_e6_market_evidence(ROOT)["default_is_market_backed"] is False


def test_e6_evaluator_requires_independent_source_support_for_top_offer():
    evaluation = evaluate_e6_market_evidence(ROOT, _bundle(single=True))
    assert evaluation["default_is_market_backed"] is False


def test_e6_evaluator_can_change_top_path_based_on_sources():
    evaluation = evaluate_e6_market_evidence(ROOT, _bundle("opp_integration_implementation_ai_ops_room"))
    assert evaluation["top_path"] == "AI Ops Operating Room Implementation Support"
    assert evaluation["default_is_market_backed"] is True


def test_e6_evaluator_does_not_hardcode_agent_workflow_or_mcp():
    evaluation = evaluate_e6_market_evidence(ROOT, _bundle("opp_partner_channel_enablement"))
    assert evaluation["top_path"] not in {"Agent Workflow Bottleneck Diagnosis", "MCP / Tool-Use Boundary Review"}


def test_e6_fixture_or_fake_evidence_cannot_complete_full_mission():
    evaluation = evaluate_e6_market_evidence(ROOT, _bundle(fixture=True))
    assert evaluation["bundle_valid"] is False
    assert evaluation["default_is_market_backed"] is False
