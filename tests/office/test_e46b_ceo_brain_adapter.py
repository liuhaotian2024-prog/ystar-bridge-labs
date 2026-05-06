from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context


def test_ceo_brain_adapter_loads_task_time_context():
    context = load_ceo_brain_context({"task_title": "first value", "task_description": "governed agent proof"})
    assert context["active_task_time_source"].endswith("load_ceo_brain_context")
    assert context["wisdom_search"]["invoked"] is True
    assert context["working_memory"]["invoked"] is True
    assert context["constitutional_sources"]
    assert "operations/external_validation/e45_first_value_demo_bundle.json" in context["latest_runtime_artifacts"]
    assert context["no_external_action"] is True
