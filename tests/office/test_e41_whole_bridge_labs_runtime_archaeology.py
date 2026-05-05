from office.mission_command.e41_whole_bridge_labs_runtime_archaeology import build_whole_bridge_labs_runtime_archaeology


def test_e41_whole_bridge_labs_runtime_archaeology_contract():
    artifact = build_whole_bridge_labs_runtime_archaeology()
    names = {item["component"] for item in artifact["canonical_runtime_components"]}
    assert "Board/CEO/role governance" in names
    assert "CIEU evidence chain references" in names
    assert "gov-order NL pipeline" in names
    assert artifact["missing_integration_points"]

