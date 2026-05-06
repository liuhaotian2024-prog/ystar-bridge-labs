from __future__ import annotations

from pathlib import Path

from . import e63_opportunity_discovery_core as core


def run_offer_package_hypothesis(root: Path | None = None) -> dict:
    return core.build_offer_package_hypothesis(root or core.BRIDGE_ROOT)


def write_offer_package_hypothesis(output_root: Path | None = None) -> dict:
    root = output_root or core.BRIDGE_ROOT
    data = run_offer_package_hypothesis(root)
    core.write_json(root, "operations/external_validation/e63_offer_package_hypothesis.json", data)
    return data
