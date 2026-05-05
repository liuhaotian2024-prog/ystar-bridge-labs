from office.mission_command.e42_internal_resource_inventory import build_internal_resource_inventory


def test_internal_resource_inventory_indexes_real_resources_and_layers():
    inventory = build_internal_resource_inventory(max_files_per_repo=5000)
    assert inventory["derived_from_real_files"] is True
    assert inventory["recent_milestones_only"] is False
    assert inventory["resource_count"] > 200
    paths = {item["path"] for item in inventory["resources"] if item["repo"] == "ystar-bridge-labs"}
    assert "scripts/gov_order.py" in paths
    assert "scripts/k9_audit_v3.py" in paths
    assert "operations/external_validation/e41_frontier_capability_import_loop.json" in paths
    owners = inventory["cross_repo_capability_ownership_index"]
    assert "bridge_labs_strategy" in owners
    assert "gov_mcp_execution_boundary" in owners
