from office.mission_command.public_source_seed_model import PublicSourceSeed, PublicSourceSeedPlan
from office.mission_command.safe_public_page_reader import PublicPageReadResult
from office.mission_command.source_seeded_research_provider import SourceSeededPublicResearchProvider
from office.mission_command.tier1_public_research import Tier1ResearchBudget, Tier1ResearchRequest


class FakePageReader:
    def available(self):
        return True

    def read(self, url):
        return PublicPageReadResult(
            url=url,
            domain="example.com" if "example.com" in url else "alt.example.org",
            status=200,
            retrieved_at="2026-05-01T00:00:00Z",
            title="Public Service",
            text_excerpt="Public pricing plan for AI consultant enablement. Buyers use guides and checklists when blocked.",
            safety_errors=[],
            blocked_reason="",
            bytes_read=100,
            external_action_executed=False,
        )


def _request(max_pages=4):
    return Tier1ResearchRequest(
        mission_id="e5_market_backed_first_revenue",
        allowed_source_categories=["public service page"],
        query_plan=[],
        page_read_plan=[],
        budget=Tier1ResearchBudget(max_pages_read=max_pages, max_domains=4),
        stop_conditions=["stop on budget"],
    )


def _seed(seed_id="seed_1", url="https://example.com/public"):
    return PublicSourceSeed(
        seed_id=seed_id,
        url=url,
        opportunity_family="partner enablement",
        relevant_opportunity_ids=["opp_partner_channel_enablement"],
        source_category="public service page",
        evidence_sought=["buyer pain", "pricing"],
        owner_approved=True,
    )


def _plan(seeds):
    return PublicSourceSeedPlan(
        mission_id="e5_market_backed_first_revenue",
        seeds=seeds,
        required_seed_count=1,
        missing_families=[],
        approval_boundary="read-only public pages only",
        forbidden_actions=[],
    )


def test_source_seeded_provider_writes_receipt_and_summaries_with_fake_page_reader(tmp_path):
    provider = SourceSeededPublicResearchProvider(FakePageReader())
    bundle = provider.run(tmp_path, _request(), _plan([_seed()]))
    assert bundle.live_public_read_only is True
    assert bundle.external_action_executed is False
    assert (tmp_path / "reports" / "integration" / "e5_tier1_research_budget_receipt.md").exists()
    assert (tmp_path / "reports" / "integration" / "e5_external_source_summaries.md").exists()


def test_source_seeded_provider_does_not_require_search_provider(tmp_path):
    provider = SourceSeededPublicResearchProvider(FakePageReader())
    bundle = provider.run(tmp_path, _request(), _plan([_seed()]))
    assert bundle.receipt["queries_used"] == []
    assert bundle.sources


def test_budget_blocks_excess_seed_urls(tmp_path):
    provider = SourceSeededPublicResearchProvider(FakePageReader())
    bundle = provider.run(tmp_path, _request(max_pages=0), _plan([_seed()]))
    assert bundle.live_public_read_only is False
    assert bundle.validated_live is False


def test_missing_seed_file_equivalent_blocks_with_exact_action(tmp_path):
    provider = SourceSeededPublicResearchProvider(FakePageReader())
    bundle = provider.run(tmp_path, _request(), _plan([]))
    assert bundle.provider_mode == "blocked_missing_source_seeds"
    assert "Add 10-20 owner-approved" in " ".join(bundle.exact_unblock_action)
