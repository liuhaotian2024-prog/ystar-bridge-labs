from office.mission_command.e9_suppression_registry import E9SuppressionRegistry, suppression_blocks_target


def test_suppression_registry_blocks_opted_out_target():
    registry = E9SuppressionRegistry(opted_out_target_ids=["t1"])
    assert "target_opted_out" in suppression_blocks_target(registry, "t1")


def test_suppression_registry_blocks_duplicate_over_limit():
    registry = E9SuppressionRegistry(sent_counts_by_target_id={"t1": 1}, max_duplicate_contacts=1)
    assert "duplicate_contact_limit_reached" in suppression_blocks_target(registry, "t1")
