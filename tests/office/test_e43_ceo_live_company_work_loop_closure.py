from office.mission_command.e35_one_brain_integration_guard import get_artifact


def test_e43_ceo_live_company_work_loop_closes_without_external_action():
    closure = get_artifact("e43_czl_closure")
    assert closure["E42_router_started_loop"] is True
    assert closure["one_concrete_first_value_path_selected"] is True
    assert closure["local_first_value_proof_result_created"] is True
    assert closure["full_CEO_work_loop_closed"] is True
    assert closure["customer_contact_occurred"] is False
    assert closure["real_human_target_identification_occurred"] is False
    assert closure["provider_api_or_tool_execution_occurred"] is False
    assert closure["paid_signal_claimed"] is False
