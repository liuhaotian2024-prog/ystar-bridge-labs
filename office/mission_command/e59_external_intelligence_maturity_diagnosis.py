from __future__ import annotations

from pathlib import Path

from .e59_external_intelligence_core import BRIDGE_ROOT, build_maturity_diagnosis, write_json, write_md


def run_external_intelligence_maturity_diagnosis() -> dict:
    return build_maturity_diagnosis()


def write_external_intelligence_maturity_diagnosis(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_external_intelligence_maturity_diagnosis()
    write_json(root, "operations/external_validation/e59_external_intelligence_maturity_diagnosis.json", data)
    write_md(root, "reports/integration/e59_external_intelligence_maturity_diagnosis.md", "E59 External Intelligence Maturity Diagnosis", [
        f"Current level: `{data['current_overall_external_intelligence_level']}`",
        "Target level: `L5`.",
        "E57 blocker is explicitly in the L5 blocker list.",
    ])
    return data

