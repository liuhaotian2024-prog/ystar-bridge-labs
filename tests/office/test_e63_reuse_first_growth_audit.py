from office.mission_command.e63_reuse_first_growth_audit import run_reuse_first_growth_audit


def test_e63_reuse_first_audit_blocks_duplicate_capabilities():
    data = run_reuse_first_growth_audit()
    assert data["passed"] is True
    assert data["duplicate_capability_created_without_justification"] is False
    assert data["duplicate_capability_risks_checked"]["public_read_adapter_rebuilt"] is False
    assert data["duplicate_capability_risks_checked"]["first_cash_selector_rebuilt"] is False
    assert data["connected_to_existing_E54_E62_runtime_assets"] is True
