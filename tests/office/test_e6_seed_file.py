from pathlib import Path

from office.mission_command.public_source_seed_model import load_public_source_seed_file, validate_public_source_seed
from office.mission_command.safe_public_page_reader import PublicPageReadResult, reject_unsafe_public_url, stop_reason_from_text
from office.mission_command.source_seeded_research_provider import SourceSeededPublicResearchProvider
from office.mission_command.tier1_public_research import Tier1ResearchBudget, Tier1ResearchRequest


ROOT = Path(__file__).resolve().parents[2]


def test_e6_seed_file_has_at_least_10_owner_approved_public_urls():
    plan = load_public_source_seed_file(ROOT)
    assert len(plan.seeds) >= 10
    assert all(seed.owner_approved for seed in plan.seeds)
    assert all(seed.url.startswith("https://") for seed in plan.seeds)


def test_e6_seed_file_covers_at_least_8_opportunity_families():
    plan = load_public_source_seed_file(ROOT)
    assert len({seed.opportunity_family for seed in plan.seeds}) >= 8


def test_e6_seed_file_does_not_authorize_customer_contact():
    plan = load_public_source_seed_file(ROOT)
    assert "customer_contact" in plan.forbidden_actions
    assert "does not authorize customer contact" in plan.approval_boundary


def test_e6_seed_validation_rejects_non_http_url():
    seed = load_public_source_seed_file(ROOT).seeds[0]
    bad = type(seed)(**{**seed.to_dict(), "url": "file:///tmp/secret"})
    assert "non_http_url" in validate_public_source_seed(bad)


def test_e6_seed_validation_rejects_localhost_or_private_url():
    seed = load_public_source_seed_file(ROOT).seeds[0]
    bad = type(seed)(**{**seed.to_dict(), "url": "http://localhost/private"})
    assert "private_or_local_url" in validate_public_source_seed(bad)
    assert reject_unsafe_public_url("http://10.0.0.1/page")


def test_e6_page_reader_skips_login_or_payment_indicator():
    assert stop_reason_from_text("sign in to continue") == "blocked_login_indicator"
    assert stop_reason_from_text("submit payment with credit card") == "blocked_payment_indicator"


class FailingReader:
    def available(self):
        return True

    def read(self, url):
        return PublicPageReadResult(
            url=url,
            domain="example.com",
            status=200,
            retrieved_at="2026-05-01T00:00:00Z",
            title="Blocked",
            text_excerpt="",
            safety_errors=[],
            blocked_reason="blocked_login_indicator",
            bytes_read=0,
            external_action_executed=False,
        )


def test_e6_research_writes_receipt_even_when_pages_fail(tmp_path):
    plan = load_public_source_seed_file(ROOT)
    request = Tier1ResearchRequest(
        mission_id="e6_source_seeded_market_evidence_run",
        allowed_source_categories=["public docs"],
        query_plan=[],
        page_read_plan=[],
        budget=Tier1ResearchBudget(max_pages_read=2, max_domains=2),
        stop_conditions=["stop"],
    )
    bundle = SourceSeededPublicResearchProvider(FailingReader()).run(
        tmp_path,
        request,
        plan,
        receipt_name="e6_tier1_research_budget_receipt.md",
        summaries_name="e6_external_source_summaries.md",
    )
    assert bundle.validated_live is False
    assert (tmp_path / "reports" / "integration" / "e6_tier1_research_budget_receipt.md").exists()
