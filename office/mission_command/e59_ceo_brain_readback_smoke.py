from __future__ import annotations

from pathlib import Path

from .e59_external_intelligence_core import BRIDGE_ROOT, build_readback, load_e59_state_for_brain, write_json, write_md


def run_ceo_brain_readback_smoke() -> dict:
    return build_readback()


def write_ceo_brain_readback_smoke(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_ceo_brain_readback_smoke()
    write_json(root, "operations/external_validation/e59_ceo_brain_readback_smoke_result.json", data)
    write_md(root, "reports/integration/e59_ceo_brain_readback_smoke_result.md", "E59 CEO Brain Readback Smoke", [
        f"Passes: `{data['passes']}`",
        f"Next milestone: `{data['state'].get('next_recommended_milestone')}`",
        "External action remains blocked.",
    ])
    return data

