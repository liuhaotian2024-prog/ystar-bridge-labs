from office.mission_command.e35_one_brain_integration_guard import get_artifact


def test_e43_fix_before_real_user_list_is_small_and_practical():
    artifact = get_artifact("e43_fix_before_real_user_list")
    assert artifact["item_count"] <= artifact["max_items"] <= 12
    assert artifact["must_fix_before_contact_count"] >= 1
    assert all(item["fix_type"] in {"docs_fix", "command_fix", "test_fix", "packaging_fix", "demo_fix", "trust_fix"} for item in artifact["items"])
