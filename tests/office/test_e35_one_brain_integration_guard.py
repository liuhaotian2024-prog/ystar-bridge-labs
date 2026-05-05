from office.mission_command.e35_one_brain_integration_guard import build_one_brain_integration_guard


def test_one_brain_guard_blocks_parallel_cognition_systems():
    guard = build_one_brain_integration_guard()
    assert guard["guard_status"] == "passed"
    assert guard["second_ceo_brain_created"] is False
    assert guard["second_kg_created"] is False
    assert guard["second_route_registry_created"] is False
    assert guard["examples_are_probes_not_routes"] is True
    assert guard["hardcoded_product_selector_detected"] is False
