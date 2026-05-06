from __future__ import annotations

from pathlib import Path

from . import e66_model_driven_offer_core as core


def load_e66_state_for_brain(root: Path | None = None) -> dict:
    return core.load_e66_state_for_brain(root or core.BRIDGE_ROOT)


def run_ceo_brain_readback_smoke(root: Path | None = None) -> dict:
    return core.build_ceo_brain_readback_smoke(root or core.BRIDGE_ROOT)


def write_ceo_brain_readback_smoke(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_ceo_brain_readback_smoke(root)
    core.write_json(root, "operations/external_validation/e66_ceo_brain_readback_smoke_result.json", data)
    return data
