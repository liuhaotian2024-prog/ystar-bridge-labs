from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
from office.mission_command.e69_ceo_next_action_planner_readback import (
    explain_next_action_selection,
    get_ceo_candidate_actions,
    get_ceo_next_action_scoring,
    get_ceo_selected_next_action,
    get_owner_decision_packet,
)


def test_e69_readback_exposes_next_action_planner_to_ceo_brain():
    assert get_ceo_candidate_actions()["candidate_count"] >= 10
    assert get_ceo_next_action_scoring()["top_candidate"] == "integrate_CIEU_audit_log_module_into_governed_business_operations_blueprint_no_execution"
    assert get_ceo_selected_next_action()["selection_made_by_CEO_planning_model"] is True
    assert get_owner_decision_packet()["not_owner_approval"] is True
    assert explain_next_action_selection()["external_action_allowed"] is False
    context = load_ceo_brain_context({"task_title": "e69 readback", "task_description": "CEO next action planner"})
    assert context["current_ceo_generated_candidate_count"] >= 10
    assert context["current_ceo_selected_next_action"] == "integrate_CIEU_audit_log_module_into_governed_business_operations_blueprint_no_execution"
    assert context["current_ceo_next_action_external_action_allowed"] is False

