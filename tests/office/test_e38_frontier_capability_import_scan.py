from office.mission_command.e38_frontier_capability_import_scan import build_frontier_capability_import_scan


def test_frontier_capability_import_scan_covers_required_categories_without_execution():
    scan = build_frontier_capability_import_scan()
    assert scan["category_count"] >= 10
    assert len(scan["categories_inspected"]) >= 10
    assert scan["source_count"] >= 10
    assert scan["external_tool_integration_occurred"] is False
    assert scan["provider_api_execution_occurred"] is False
    assert scan["customer_validation_claimed"] is False
    assert scan["paid_signal_claimed"] is False
    categories = set(scan["categories_inspected"])
    assert "agent protocols and interoperability" in categories
    assert "simulation / synthetic user / market testing" in categories
    for cap in scan["capabilities"]:
        assert cap["source_url"].startswith("https://")
        assert cap["not_customer_validation"] is True
        assert cap["not_paid_signal"] is True
        assert cap["recommended_import_pattern"] in {
            "borrow as method",
            "map as concept",
            "integrate as tool later",
            "propose Y-star-gov primitive",
            "propose gov-mcp adapter",
            "ignore for now",
        }
        assert "relevance_to_Y_star_gov" in cap
        assert "relevance_to_gov_mcp" in cap
        assert "relevance_to_bridge_labs" in cap
