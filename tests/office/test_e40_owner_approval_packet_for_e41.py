from office.mission_command.e40_owner_approval_packet_for_e41 import build_owner_approval_packet_for_e41


def test_owner_packet_requires_explicit_approval_for_future_contact():
    packet = build_owner_approval_packet_for_e41()
    assert len(packet["choices"]) == 6
    assert packet["final_product_selected"] is False
    assert packet["customer_validation_claimed"] is False
    assert packet["paid_signal_claimed"] is False
    assert "explicit owner approval" in packet["future_contact_requirements"]
    contact_choice = next(choice for choice in packet["choices"] if choice["choice"] == "B")
    assert contact_choice["external_side_effect"] is True
    assert contact_choice["owner_approval_needed"] is True
