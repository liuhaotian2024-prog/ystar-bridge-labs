from office.mission_command.e35_one_brain_integration_guard import get_artifact


def test_e43_selects_one_concrete_first_value_path():
    artifact = get_artifact("e43_selected_first_value_path")
    assert artifact["selected_path"] == "gov-mcp + Y-star-gov governed execution in 5 minutes"
    assert artifact["exact_install_command_documented"] == "pip install gov-mcp"
    assert "gov-mcp status" in artifact["exact_first_commands_to_run"]
    assert artifact["not_final_product_selection"] is True
