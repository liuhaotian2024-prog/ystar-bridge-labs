from __future__ import annotations

from pathlib import Path

from .e71_legacy_asset_promotion_gate import (
    build_readback_smoke,
    decide_legacy_asset_disposition,
    explain_legacy_promotion_limits,
    get_mainline_binding_plan,
    get_promoted_legacy_assets,
    get_quarantined_legacy_assets,
    load_e71_legacy_asset_resurrection_state_for_brain,
    load_legacy_asset_registry,
    score_legacy_asset,
    write_json,
    BRIDGE_ROOT,
)


def run_legacy_asset_readback_smoke(root: Path | None = None) -> dict:
    return build_readback_smoke(root or BRIDGE_ROOT)


def write_legacy_asset_readback_smoke(output_root: Path | None = None) -> dict:
    base = output_root or BRIDGE_ROOT
    result = run_legacy_asset_readback_smoke(base)
    write_json(base, "operations/external_validation/e71_ceo_legacy_asset_readback_smoke_result.json", result)
    return result


__all__ = [
    "load_e71_legacy_asset_resurrection_state_for_brain",
    "load_legacy_asset_registry",
    "score_legacy_asset",
    "decide_legacy_asset_disposition",
    "get_promoted_legacy_assets",
    "get_quarantined_legacy_assets",
    "get_mainline_binding_plan",
    "explain_legacy_promotion_limits",
    "run_legacy_asset_readback_smoke",
    "write_legacy_asset_readback_smoke",
]
