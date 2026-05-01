import json

from office.mission_command.public_source_seed_model import (
    SEED_FILE_RELATIVE,
    PublicSourceSeed,
    PublicSourceSeedPlan,
    load_public_source_seed_file,
    render_owner_public_source_seed_request,
    validate_public_source_seed,
    validate_public_source_seed_plan,
)


def test_missing_seed_file_writes_owner_seed_request(tmp_path):
    plan = load_public_source_seed_file(tmp_path)
    request = render_owner_public_source_seed_request(plan)
    assert plan.seeds == []
    assert "10-20 public, no-login URLs" in request
    assert str(SEED_FILE_RELATIVE) in request
    assert "do not authorize customer contact" in request


def test_valid_seed_plan_loads_owner_approved_public_urls(tmp_path):
    path = tmp_path / SEED_FILE_RELATIVE
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "mission_id": "e5_market_backed_first_revenue",
                "required_seed_count": 1,
                "seeds": [
                    {
                        "seed_id": "seed_1",
                        "url": "https://example.com/public",
                        "opportunity_family": "partner enablement",
                        "relevant_opportunity_ids": ["opp_partner_channel_enablement"],
                        "source_category": "public service page",
                        "evidence_sought": ["buyer pain", "pricing"],
                        "owner_approved": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    plan = load_public_source_seed_file(tmp_path)
    assert len(plan.seeds) == 1
    assert validate_public_source_seed_plan(plan) == []


def test_private_or_unapproved_seed_rejected():
    seed = PublicSourceSeed(
        seed_id="bad",
        url="http://localhost/private",
        opportunity_family="AI workflow bottleneck",
        relevant_opportunity_ids=["opp_external_pain_agent_bottleneck"],
        source_category="public page",
        evidence_sought=["pain"],
        owner_approved=False,
    )
    errors = validate_public_source_seed(seed)
    assert "private_or_local_url" in errors
    assert "seed_not_owner_approved" in errors


def test_seed_plan_requires_enough_seeds():
    plan = PublicSourceSeedPlan(
        mission_id="e5",
        seeds=[],
        required_seed_count=1,
        missing_families=[],
        approval_boundary="read only",
        forbidden_actions=[],
    )
    assert "missing_required_seed_count" in validate_public_source_seed_plan(plan)
