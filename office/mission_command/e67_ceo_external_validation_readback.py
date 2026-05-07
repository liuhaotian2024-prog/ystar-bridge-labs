from __future__ import annotations

from pathlib import Path

from . import e67_external_validation_model as model


def load_e67_external_validation_state_for_brain(root: Path | None = None) -> dict:
    return model.load_e67_external_validation_state_for_brain(root or model.BRIDGE_ROOT)


def get_external_validation_ladder(root: Path | None = None) -> dict:
    return model.get_external_validation_ladder(root or model.BRIDGE_ROOT)


def get_route_external_validation_score(route_id: str, root: Path | None = None) -> dict:
    return model.get_route_external_validation_score(route_id, root or model.BRIDGE_ROOT)


def get_non_contact_validation_portfolio(root: Path | None = None) -> dict:
    return model.get_non_contact_validation_portfolio(root or model.BRIDGE_ROOT)


def explain_validation_limits(route_id: str, root: Path | None = None) -> dict:
    return model.explain_validation_limits(route_id, root or model.BRIDGE_ROOT)


def list_owner_gated_validation_next_steps(root: Path | None = None) -> dict:
    return model.list_owner_gated_validation_next_steps(root or model.BRIDGE_ROOT)


def run_ceo_external_validation_readback_smoke(root: Path | None = None) -> dict:
    return model.build_ceo_external_validation_readback_smoke(root or model.BRIDGE_ROOT)


def write_ceo_external_validation_readback_smoke(output_root: Path | None = None) -> dict:
    root = output_root or model.BRIDGE_ROOT
    data = run_ceo_external_validation_readback_smoke(root)
    model.write_json(root, "operations/external_validation/e67_ceo_external_validation_readback_smoke_result.json", data)
    return data
