from __future__ import annotations

from pathlib import Path

from . import e68_cieu_route_evaluation_model as model


def load_e68_cieu_route_state_for_brain(root: Path | None = None) -> dict:
    return model.load_e68_cieu_route_state_for_brain(root or model.BRIDGE_ROOT)


def get_cieu_route_score(root: Path | None = None) -> dict:
    return model.get_cieu_route_score(root or model.BRIDGE_ROOT)


def get_cieu_external_validation(root: Path | None = None) -> dict:
    return model.get_cieu_external_validation(root or model.BRIDGE_ROOT)


def get_cieu_product_wedge(root: Path | None = None) -> dict:
    return model.get_cieu_product_wedge(root or model.BRIDGE_ROOT)


def get_cieu_portfolio_role(root: Path | None = None) -> dict:
    return model.get_cieu_portfolio_role(root or model.BRIDGE_ROOT)


def explain_cieu_overclaim_limits(root: Path | None = None) -> dict:
    return model.explain_cieu_overclaim_limits(root or model.BRIDGE_ROOT)


def run_ceo_cieu_route_readback_smoke(root: Path | None = None) -> dict:
    return model.build_ceo_cieu_route_readback_smoke(root or model.BRIDGE_ROOT)


def write_ceo_cieu_route_readback_smoke(output_root: Path | None = None) -> dict:
    root = output_root or model.BRIDGE_ROOT
    data = run_ceo_cieu_route_readback_smoke(root)
    model.write_json(root, "operations/external_validation/e68_ceo_cieu_route_readback_smoke_result.json", data)
    return data
