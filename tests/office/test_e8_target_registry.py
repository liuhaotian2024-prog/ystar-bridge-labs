from office.mission_command.e8_target_registry import E8ValidationTarget, target_allows_action, validate_e8_target


def test_target_registry_rejects_scraped_or_unapproved_contact():
    target = E8ValidationTarget("t1", "known_contact", "Someone", "email", "x@example.com", "scraped from web", "relevant", False, 1, False, "")
    errors = validate_e8_target(target)
    assert "scraped_contact_not_allowed" in errors
    assert "target_not_approved_for_contact" in errors


def test_target_registry_allows_internal_benchmark_proxy():
    target = E8ValidationTarget("b1", "internal_benchmark_proxy", "Benchmark", "internal", "", "no contact", "test", False, 0, False, "")
    assert not validate_e8_target(target)


def test_target_registry_blocks_opted_out_target():
    target = E8ValidationTarget("t1", "known_contact", "Someone", "email", "x@example.com", "known", "relevant", True, 1, True, "")
    assert "target_opted_out" in validate_e8_target(target)
    assert not target_allows_action(target, {"target_id": "t1", "channel": "email"})
