from office.mission_command.e63_repository_archaeology_inventory import run_repository_archaeology_inventory


def test_e63_archaeology_reuses_existing_runtime_assets():
    data = run_repository_archaeology_inventory()
    assert data["asset_count"] > 0
    assert "office/mission_command/e61_live_public_read_core.py" in data["reusable_discovery_evidence_public_read_assets"]
    assert "operations/external_validation/e62_first_cash_path_selection.json" in data["reusable_revenue_route_assets"]
    assert "safe_public_page_reader" in " ".join(data["what_must_not_be_rebuilt"])
