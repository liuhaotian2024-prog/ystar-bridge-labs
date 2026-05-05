from office.mission_command.e41_canonical_ceo_runtime_map import build_canonical_ceo_runtime_map


def test_e41_canonical_ceo_runtime_map_contract():
    artifact = build_canonical_ceo_runtime_map()
    components = {item["component"] for item in artifact["components"]}
    for required in ["Board directive intake", "CEO interpretation", "CZL closure", "CIEU evidence", "gov-order NL pipeline", "repository delivery bridge"]:
        assert required in components
    assert "without replacing" in artifact["canonical_rule"]

