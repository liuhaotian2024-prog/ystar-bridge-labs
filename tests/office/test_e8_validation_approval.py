from office.mission_command.e8_autonomy_budget import render_e8_autonomy_budget_template
from office.mission_command.e8_risk_controlled_action_model import ActionType
from office.mission_command.e8_validation_approval import E8ExternalValidationManifest, validate_e8_external_validation_manifest


def _manifest(**overrides):
    data = {
        "manifest_id": "m1",
        "approved_by": "Haotian",
        "approved_at": "2026-05-01T00:00:00Z",
        "top_offer": "48h AI Ops Operating Room Blueprint",
        "validation_mode": "contact_validation",
        "autonomy_budget": render_e8_autonomy_budget_template(),
        "approved_draft_ids": ["draft1"],
        "approved_target_seed_ids": ["target1"],
        "approved_channels": ["owner_selected_email"],
        "allowed_action_types": [ActionType.SEND_VALIDATION_MESSAGE],
        "forbidden_action_types": [ActionType.COLLECT_PAYMENT],
    }
    data.update(overrides)
    return E8ExternalValidationManifest(**data)


def test_manifest_rejects_vague_outreach_approval():
    errors = validate_e8_external_validation_manifest(_manifest(approved_by="owner"))
    assert "missing_specific_approver" in errors


def test_manifest_requires_draft_target_channel_count():
    budget = render_e8_autonomy_budget_template()
    budget["max_external_messages"] = 0
    errors = validate_e8_external_validation_manifest(_manifest(approved_draft_ids=[], approved_target_seed_ids=[], approved_channels=[], autonomy_budget=budget))
    assert "missing_approved_draft_ids" in errors
    assert "missing_approved_target_seed_ids" in errors
    assert "missing_approved_channels" in errors
    assert "missing_external_action_count" in errors
