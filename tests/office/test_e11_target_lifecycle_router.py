from office.mission_command.target_lifecycle_router import route_target_lifecycle


def test_target_lifecycle_blocks_discovered_candidate_contact_if_router_implemented():
    decision = route_target_lifecycle({"candidate_id": "cand_public", "owner_approved_for_contact": False})
    assert decision.contact_allowed is False
    assert decision.blocked_reason == "discovered_candidate_is_not_contact_approval"


def test_target_lifecycle_blocks_proposed_target_seed_contact_if_router_implemented():
    decision = route_target_lifecycle({"target_id": "target_proposed", "proposal_only": True})
    assert decision.contact_allowed is False
    assert decision.blocked_reason == "proposed_target_seed_is_not_approval"


def test_target_lifecycle_allows_owner_approved_target_to_preflight_only_if_router_implemented():
    decision = route_target_lifecycle({"target_id": "target_approved", "owner_approved_for_contact": True})
    assert decision.contact_allowed is False
    assert decision.preflight_allowed is True
    assert decision.execution_allowed is False

