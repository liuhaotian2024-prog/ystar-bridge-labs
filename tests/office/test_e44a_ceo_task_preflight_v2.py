from office.mission_command.e44a_ceo_task_preflight_v2 import run_ceo_task_preflight_v2, validate_preflight_v2_result

TASK = {
    "task_title": "Real company task",
    "task_description": "Prepare first user business route with customer empathy and commercial proof.",
}

def test_preflight_v2_runs_router_and_cascade():
    result = run_ceo_task_preflight_v2(TASK)
    assert result["router_matches"]
    assert result["cognition_cascade"]["route_selection"]
    assert result["valid"] is True
    assert result["external_action_occurred"] is False

def test_preflight_v2_blocks_router_only_and_report_pile():
    router_only = validate_preflight_v2_result({"serious_ceo_task": True, "cognition_registry": {"capabilities": []}, "output_mode": "runtime_plus_packet"})
    assert router_only["valid"] is False
    report_pile = validate_preflight_v2_result({"serious_ceo_task": False, "cognition_cascade": {}, "cognition_registry": {"capabilities": []}, "output_mode": "report_pile_only"})
    assert report_pile["valid"] is False
    external = validate_preflight_v2_result({"serious_ceo_task": False, "cognition_cascade": {}, "cognition_registry": {"capabilities": []}, "external_action_requested": True})
    assert external["valid"] is False
