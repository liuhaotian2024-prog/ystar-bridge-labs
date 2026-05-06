from __future__ import annotations

from pathlib import Path

from .e61_live_public_read_core import BRIDGE_ROOT, load_e61_state_for_brain, run_ceo_brain_readback_smoke, write_json, write_md


def write_ceo_brain_readback_smoke(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_ceo_brain_readback_smoke(root)
    write_json(root, "operations/external_validation/e61_ceo_brain_readback_smoke_result.json", data)
    write_md(root, "reports/integration/e61_ceo_brain_readback_smoke_result.md", "E61 CEO Brain Readback Smoke", [f"Passes: `{data['passes']}`"])
    return data
