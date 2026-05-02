from office.mission_command.e8_autonomy_budget import render_e8_autonomy_budget_template
from office.mission_command.e8_risk_controlled_action_model import ActionType
from office.mission_command.e9_validation_manifest import E9ExternalValidationManifest, e9_manifest_allows_action, render_e9_manifest_template, validate_e9_validation_manifest


def _manifest():
    return E9ExternalValidationManifest(
        manifest_id="m1",
        approved_by="Haotian Liu",
        approved_at="2026-05-01T00:00:00Z",
        top_offer="48h AI Ops Operating Room Blueprint",
        validation_mode="contact_validation",
        autonomy_budget=render_e8_autonomy_budget_template(),
        approved_draft_ids=["d1"],
        approved_draft_hashes={"d1": "h1"},
        approved_target_seed_ids=["t1"],
        approved_channels=["email"],
        allowed_action_types=[ActionType.SEND_VALIDATION_MESSAGE],
    )


def test_e9_manifest_template_not_treated_as_approval():
    assert "OWNER_TO_FILL" in render_e9_manifest_template()


def test_e9_manifest_rejects_placeholders():
    errors = validate_e9_validation_manifest(E9ExternalValidationManifest(manifest_id="OWNER_TO_FILL"))
    assert any("placeholder" in error for error in errors)


def test_e9_manifest_rejects_vague_approval():
    errors = validate_e9_validation_manifest(E9ExternalValidationManifest(approved_by="TBD"))
    assert "placeholder_approved_by" in errors or "missing_approved_by" in errors


def test_e9_manifest_requires_exact_draft_hash():
    manifest = _manifest()
    bad = E9ExternalValidationManifest(**{**manifest.to_dict(), "approved_draft_hashes": {}})
    assert "missing_exact_draft_hash" in validate_e9_validation_manifest(bad)
    assert e9_manifest_allows_action(manifest, {"action_type": ActionType.SEND_VALIDATION_MESSAGE, "target_id": "t1", "channel": "email", "draft_id": "d1", "draft_hash": "h1"})
