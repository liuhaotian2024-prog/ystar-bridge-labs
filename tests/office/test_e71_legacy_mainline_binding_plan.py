import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e71_mainline_binding_plan_uses_overlays_not_core_rewrites():
    data = json.loads((ROOT / "operations/external_validation/e71_legacy_mainline_binding_plan.json").read_text())
    targets = {row["target_runtime"] for row in data["bindings"]}
    assert len(data["bindings"]) >= 6
    assert "E65_market_dynamics_model" in targets
    assert "E67_external_validation_model" in targets
    assert "E68_CIEU_route_and_module" in targets
    assert "E70_self_bootstrap_runtime" in targets
    assert data["core_models_rewritten"] is False
    assert all("not validated" in row["no_overclaim_boundary"] for row in data["bindings"])
    assert data["external_action_allowed"] is False

