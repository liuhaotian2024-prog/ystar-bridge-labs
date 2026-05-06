from office.mission_command.e61_live_public_read_capability_inventory import run_live_public_read_capability_inventory


def test_e61_inventory_finds_existing_adapters_and_e60_blocker():
    data = run_live_public_read_capability_inventory()
    paths = {item["path"] for item in data["discovered_components"]}
    assert "office/mission_command/safe_public_page_reader.py" in paths
    assert "office/mission_command/e59_controlled_public_page_read_adapter.py" in paths
    assert data["E57_blocker"] == "external_page_read_adapter_unavailable"
    assert data["E59_adapter_status"] == "fixture_only_network_unavailable"
    assert "adapter_disconnected" in data["failure_appears_to_be"]
    assert data["fixture_mode_only"] is True
