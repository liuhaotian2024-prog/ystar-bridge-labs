from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports" / "integration"


def test_cross_repo_backflow_plan_mentions_formal_and_incubation_repos():
    text = (REPORTS / "e11_cross_repo_backflow_plan.md").read_text(encoding="utf-8")
    assert "Y-star-gov" in text
    assert "gov-mcp" in text
    assert "ystar-company" in text


def test_ownership_map_declares_canonical_and_adapter_owners():
    text = (REPORTS / "e11_canonical_ownership_map.md").read_text(encoding="utf-8")
    assert "canonical_owner:" in text
    assert "adapter_owner:" in text
    assert "gateway_owner:" in text


def test_field_brain_cieu_map_mentions_brain_activation_phi_and_cieu_writeback_policy():
    text = (REPORTS / "e11_field_brain_cieu_integration_map.md").read_text(encoding="utf-8")
    assert "activation" in text.lower()
    assert "phi" in text.lower() or "Φ" in text
    assert "brain_writeback_policy" in text

