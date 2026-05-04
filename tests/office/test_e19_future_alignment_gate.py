import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_future_alignment_gate_requires_ecosystem_proof():
    data = json.loads((ROOT / "operations/external_validation/e19_future_milestone_alignment_gate.json").read_text())
    required = set(data["required_for_future_large_milestones"])
    assert "ecosystem_alignment_scanner_result" in required
    assert "cross_repo_impact_matrix" in required
    assert "repo_modification_decision_packet" in required
    assert "bridge_delivery_closure" in required
    assert data["per_milestone_bootstrap_allowed"] is False
