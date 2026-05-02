from office.mission_command.e12_target_preflight import validate_e12_target_seed
from office.mission_command.target_lifecycle_router import route_target_lifecycle


def _approved_target():
    return {
        "target_id": "cand_alicelabs_alicelabs",
        "approval_state": "owner_approved",
        "owner_approved_for_contact": True,
        "proposal_only": False,
        "contact_handle_or_address": "owner_approved_public_general_channel",
        "allowed_message_count": 1,
        "opt_out_state": False,
    }


def test_proposed_target_cannot_be_contacted():
    target = {"target_id": "cand_a", "proposal_only": True, "owner_approved_for_contact": False}
    assert "proposed_target_seed_is_not_approval" in validate_e12_target_seed(target)
    assert route_target_lifecycle(target).contact_allowed is False


def test_owner_approved_target_can_be_preflighted():
    target = _approved_target()
    assert validate_e12_target_seed(target, ["cand_alicelabs_alicelabs"]) == []
    routed = route_target_lifecycle(target)
    assert routed.preflight_allowed is True
    assert routed.execution_allowed is False


def test_target_preflight_rejects_scraped_contact_and_opt_out():
    target = _approved_target()
    target["contact_handle_or_address"] = "scraped:person@example.com"
    target["opt_out_state"] = "opted_out"
    errors = validate_e12_target_seed(target)
    assert "scraped_personal_contact_blocked" in errors
    assert "target_opted_out_or_suppressed" in errors

