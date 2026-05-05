from office.mission_command.e35_one_brain_integration_guard import get_artifact


def test_e42_czl_closure_flags_and_no_external_actions():
    closure = get_artifact("e42_czl_closure")
    assert closure["internal_resource_inventory_exists"] is True
    assert closure["task_capability_matcher_works"] is True
    assert closure["reuse_first_no_rebuild_gate_works"] is True
    assert closure["customer_contact_occurred"] is False
    assert closure["expert_contact_occurred"] is False
    assert closure["real_human_target_identification_occurred"] is False
    assert closure["personal_contact_scraping_occurred"] is False
    assert closure["provider_api_or_tool_execution_occurred"] is False
    assert closure["payment_occurred"] is False
    assert closure["duplicate_governance_kernel_created"] is False
    assert closure["second_CEO_brain_created"] is False
