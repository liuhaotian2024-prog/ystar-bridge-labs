from office.mission_command.e60_post_e59_capability_synthesis import run_post_e59_capability_synthesis


def test_e60_synthesis_preserves_live_read_limitation_and_no_validation_claims():
    data = run_post_e59_capability_synthesis()
    assert data["fixture_based_external_intelligence_useful_for_architecture_and_pipeline_proof"] is True
    assert data["fixture_based_evidence_is_live_market_freshness"] is False
    assert data["no_customer_expert_paid_validation_exists"] is True
    assert data["external_action_allowed"] is False
    statuses = {row["capability"]: row["status"] for row in data["capabilities"]}
    assert statuses["live public-read evidence availability"] == "live_public_read_unavailable_nonfatal"
