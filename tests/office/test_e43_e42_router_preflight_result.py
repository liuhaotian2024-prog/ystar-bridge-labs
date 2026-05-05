from office.mission_command.e35_one_brain_integration_guard import get_artifact


def test_e43_starts_with_e42_router_and_cites_new_files():
    artifact = get_artifact("e43_e42_router_preflight_result")
    assert artifact["E42_router_called"] is True
    assert artifact["relevant_existing_resources"]
    assert "Direct reuse was insufficient" in artifact["new_file_citation"]
    assert "duplicate governance kernel" in artifact["forbidden_duplicate_work"]
