from __future__ import annotations

from pathlib import Path

from . import e65_market_dynamics_model as model


def load_e65_market_dynamics_state_for_brain(root: Path | None = None) -> dict:
    return model.load_e65_market_dynamics_state_for_brain(root or model.BRIDGE_ROOT)


def get_market_dynamics_model(root: Path | None = None) -> dict:
    return model.get_market_dynamics_model(root or model.BRIDGE_ROOT)


def rank_routes_by_profile(profile_name: str, root: Path | None = None) -> dict:
    return model.rank_routes_by_profile(profile_name, root or model.BRIDGE_ROOT)


def get_route_evidence(route_id: str, root: Path | None = None) -> dict:
    return model.get_route_evidence(route_id, root or model.BRIDGE_ROOT)


def get_decision_stability(root: Path | None = None) -> dict:
    return model.get_decision_stability(root or model.BRIDGE_ROOT)


def get_recommended_market_portfolio(root: Path | None = None) -> dict:
    return model.get_recommended_market_portfolio(root or model.BRIDGE_ROOT)


def explain_route_selection(route_id: str, root: Path | None = None) -> dict:
    return model.explain_route_selection(route_id, root or model.BRIDGE_ROOT)


def list_update_triggers(root: Path | None = None) -> dict:
    return model.list_update_triggers(root or model.BRIDGE_ROOT)


def run_ceo_market_dynamics_readback_smoke(root: Path | None = None) -> dict:
    return model.build_ceo_market_dynamics_readback_smoke(root or model.BRIDGE_ROOT)


def write_ceo_market_dynamics_readback_smoke(output_root: Path | None = None) -> dict:
    root = output_root or model.BRIDGE_ROOT
    data = run_ceo_market_dynamics_readback_smoke(root)
    model.write_json(root, "operations/external_validation/e65_ceo_market_dynamics_readback_smoke_result.json", data)
    return data
