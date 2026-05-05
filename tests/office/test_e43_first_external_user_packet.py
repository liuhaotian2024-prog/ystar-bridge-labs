from office.mission_command.e35_one_brain_integration_guard import get_artifact


def test_e43_first_external_user_packet_is_unsent_and_persona_only():
    artifact = get_artifact("e43_first_external_user_packet")
    assert artifact["status"] == "owner_ready_unsent_unpublished"
    assert artifact["no_real_people_identified"] is True
    assert artifact["customer_contact_occurred"] is False
    assert artifact["publication_occurred"] is False
    assert artifact["customer_validation_claimed"] is False
