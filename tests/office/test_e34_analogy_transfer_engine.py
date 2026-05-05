from office.mission_command.e34_analogy_transfer_engine import build_analogy_transfer_engine


def test_analogy_transfer_engine_supports_mature_trust_domains():
    artifact = build_analogy_transfer_engine()
    domains = set(artifact["analogy_domains_supported"])
    assert "aviation black box" in domains
    assert "financial audit" in domains
    assert "insurance underwriting" in domains
    assert "GitHub PR review" in domains
    assert artifact["analogy_domains_supported_count"] >= 15
    assert "financial audit" in artifact["most_productive_analogy"]
