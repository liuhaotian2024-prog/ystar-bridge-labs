from office.mission_command.e68_cieu_route_evaluation_model import write_all_e68_artifacts


def test_e68_artifacts_generate_end_to_end_with_truthful_public_read_status():
    gate = write_all_e68_artifacts()
    assert gate["gate_passed"] is True
    assert gate["final_status"] in {
        "e68_cieu_route_promising_as_high_defensibility_vertical",
        "e68_cieu_route_deferred_due_to_evidence_or_sales_cycle_risk",
    }

