from __future__ import annotations

from pathlib import Path

from .e59_external_intelligence_core import BRIDGE_ROOT, build_competitor_comparison, write_json, write_md


def run_competitor_adjacent_technology_comparison() -> dict:
    return build_competitor_comparison()


def write_competitor_adjacent_technology_comparison(output_root: Path | None = None) -> dict:
    root = output_root or BRIDGE_ROOT
    data = run_competitor_adjacent_technology_comparison()
    write_json(root, "operations/external_validation/e59_competitor_adjacent_technology_comparison.json", data)
    write_md(root, "reports/integration/e59_competitor_adjacent_technology_comparison.md", "E59 Competitor / Adjacent Technology Comparison", [
        f"Categories compared: `{data['comparison_count']}`",
        "Uncertain claims are marked unverified; no superiority overclaim is made.",
    ])
    return data

