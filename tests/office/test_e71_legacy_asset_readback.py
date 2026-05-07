from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
from office.mission_command.e71_legacy_asset_readback import (
    load_e71_legacy_asset_resurrection_state_for_brain,
    run_legacy_asset_readback_smoke,
)


def test_e71_readback_exposes_legacy_resurrection_state_to_ceo_brain():
    state = load_e71_legacy_asset_resurrection_state_for_brain()
    assert state["legacy_asset_resurrection_status"] == "ready_internal_no_external_action"
    assert state["promoted_count"] > 0
    assert state["external_action_allowed"] is False
    assert run_legacy_asset_readback_smoke()["passes"] is True
    context = load_ceo_brain_context({"task_title": "e71 readback", "task_description": "legacy asset resurrection"})
    assert context["current_legacy_asset_promoted_count"] == state["promoted_count"]
    assert context["current_legacy_asset_quarantined_count"] == state["quarantined_count"]
    assert context["current_legacy_asset_next_recommended_milestone"] == "E72_integrate_K9_CIEU_hash_chain_context_into_CIEU_audit_module"
    assert context["current_legacy_asset_external_action_allowed"] is False

