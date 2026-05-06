from office.mission_command.e63_completion_gate import run_e63_completion_gate


def test_e63_completion_gate_passes_with_truthful_public_read_status():
    data = run_e63_completion_gate()
    assert data["gate_passed"] is True
    assert data["final_status"] in {
        "e63_public_read_opportunity_discovery_completed",
        "e63_public_read_blocked_but_revenue_opportunity_plan_created",
        "e63_opportunity_discovery_partial_with_blocker",
    }
    assert data["planned_source_count"] >= data["source_receipt_count"] >= 1
    assert data["recommended_next_milestone"].startswith("E64_")
