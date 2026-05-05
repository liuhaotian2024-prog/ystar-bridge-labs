from office.mission_command.e44a_full_history_preflight_v2 import run_full_history_preflight_v2

def test_full_history_preflight_wraps_base_and_replay():
    result = run_full_history_preflight_v2({"task_title": "first user", "task_description": "first user commercial route"})
    assert result["base_E44A_preflight"]["valid"] is True
    assert result["valid"] is True
    assert len(result["required_pre_E31_families_invoked"]) >= 7
    assert result["external_action_occurred"] is False
