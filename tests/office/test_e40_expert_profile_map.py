from office.mission_command.e40_expert_profile_map import build_expert_profile_map


def test_profile_map_has_no_real_people_or_contact_info():
    profiles = build_expert_profile_map()
    assert profiles["profile_count"] >= 7
    assert profiles["real_individuals_identified"] is False
    assert profiles["personal_contact_info_scraped"] is False
    for profile in profiles["profiles"]:
        assert profile["owner_approval_required_before_contact"] is True
        assert "customer validation" in profile["what_they_cannot_validate"]
