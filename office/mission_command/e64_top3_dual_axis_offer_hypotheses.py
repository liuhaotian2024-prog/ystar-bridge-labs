from __future__ import annotations

from pathlib import Path

from . import e64_dual_axis_revenue_core as core


def run_e64_top3_dual_axis_offer_hypotheses(root: Path | None = None) -> dict:
    return core.build_top3_dual_axis_offer_hypotheses(root or core.BRIDGE_ROOT)


def write_e64_top3_dual_axis_offer_hypotheses(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_e64_top3_dual_axis_offer_hypotheses(root)
    core.write_json(root, "operations/external_validation/e64_top3_dual_axis_offer_hypotheses.json", data)
    return data
