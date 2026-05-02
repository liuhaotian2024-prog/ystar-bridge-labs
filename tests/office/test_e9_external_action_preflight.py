from office.mission_command.e8_autonomy_budget import render_e8_autonomy_budget_template
from office.mission_command.e8_risk_controlled_action_model import ActionType
from office.mission_command.e9_action_plan import build_e9_validation_action_plan
from office.mission_command.e9_draft_binding import E9DraftBinding
from office.mission_command.e9_external_action_preflight import preflight_e9_external_action
from office.mission_command.e9_suppression_registry import E9SuppressionRegistry
from office.mission_command.e9_target_registry import E9ValidationTarget
from office.mission_command.e9_validation_manifest import E9ExternalValidationManifest


def _target():
    return E9ValidationTarget("t1", "known_contact", "Peer", "email", "x@example.com", "owner", "relevant", True, True, 1, False)


def _binding():
    return E9DraftBinding("d1", "h1", "path", "email", True, True, True, [])


def _manifest(action_type=ActionType.SEND_VALIDATION_MESSAGE):
    return E9ExternalValidationManifest(
        "m1",
        "Haotian Liu",
        "2026-05-01T00:00:00Z",
        "48h AI Ops Operating Room Blueprint",
        "contact_validation",
        render_e8_autonomy_budget_template(),
        ["d1"],
        {"d1": "h1"},
        ["t1"],
        ["email"],
        [action_type],
        [],
    )


def test_e9_preflight_blocks_without_manifest_targets():
    plan = build_e9_validation_action_plan(None, [], [_binding()])
    result = preflight_e9_external_action(plan, None, [], [_binding()], E9SuppressionRegistry())
    assert result.blocked is True
    assert "manifest_invalid_or_missing" in result.blocked_reason


def test_e9_preflight_allows_tier2_with_valid_manifest_target_draft():
    manifest = _manifest()
    target = _target()
    binding = _binding()
    plan = build_e9_validation_action_plan(manifest, [target], [binding])
    result = preflight_e9_external_action(plan, manifest, [target], [binding], E9SuppressionRegistry())
    assert result.allowed is True


def test_e9_preflight_blocks_tier3_publication():
    manifest = _manifest(ActionType.PUBLISH_POST)
    target = _target()
    binding = _binding()
    plan = build_e9_validation_action_plan(manifest, [target], [binding])
    object.__setattr__(plan, "planned_action_type", ActionType.PUBLISH_POST)
    result = preflight_e9_external_action(plan, manifest, [target], [binding], E9SuppressionRegistry())
    assert result.blocked is True


def test_e9_preflight_blocks_tier4_actions():
    for action_type in [ActionType.COLLECT_PAYMENT, ActionType.CREATE_ACCOUNT, ActionType.SUBMIT_FORM, ActionType.CORE_WRITEBACK]:
        manifest = _manifest(action_type)
        target = _target()
        binding = _binding()
        plan = build_e9_validation_action_plan(manifest, [target], [binding])
        object.__setattr__(plan, "planned_action_type", action_type)
        result = preflight_e9_external_action(plan, manifest, [target], [binding], E9SuppressionRegistry())
        assert result.blocked is True
