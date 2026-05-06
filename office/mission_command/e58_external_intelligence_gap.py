from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .e58_case_study_boundary import BRIDGE_ROOT, NEXT_MILESTONE, PRODUCT_DIR, write_json, write_md


def build_external_intelligence_gap() -> dict[str, Any]:
    requirements = [
        "source discovery",
        "safe public-read-only access",
        "source credibility scoring",
        "freshness tracking",
        "competitor and adjacent technology comparison",
        "latest technology capture",
        "claim extraction",
        "evidence atomization",
        "contradiction and gap detection",
        "learning writeback to CEO brain / KG / CIEU",
        "route impact analysis",
        "Y-star-gov and gov-mcp governance",
        "anti-drift and readback",
        "no login, no contact, no contact scraping, no publication",
    ]
    baseline = [
        "E50B public-read-only observation artifacts",
        "E57 skipped evidence refresh blocker",
        "controlled public page read adapter if present",
        "source receipt builders",
        "external observation manifests",
        "provider availability checks",
        "AI transparency / risk boundary manifests",
        "public-read-only source policies",
        "E6/E8/E9 observation assets if present",
        "E51-E57 anti-drift/capability binding/gov-mcp tooling",
    ]
    return {
        "artifact_id": "e58_external_intelligence_gap",
        "external_world_intelligence_L5_complete": False,
        "technology_capture_market_learning_L5_complete": False,
        "reason": "E57 public-read-only evidence refresh was skipped because external_page_read_adapter_unavailable; internal L5 proof is not latest market intelligence.",
        "E59_required_before_market_contact": True,
        "E59_required_capabilities": requirements,
        "E59_must_inspect_and_reuse_baseline": baseline,
        "E59_baseline_inspection_required": baseline,
        "E59_instruction": "reuse_existing_capabilities_first; inspect baseline assets before building anything new",
        "forbidden_in_E59": ["login", "contact", "contact scraping", "publication", "provider/private API use"],
        "next_recommended_milestone": NEXT_MILESTONE,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_external_intelligence_gap(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = build_external_intelligence_gap()
    write_json(root, "operations/external_validation/e58_external_intelligence_gap.json", data)
    write_md(root, "reports/integration/e58_external_intelligence_gap.md", "E58 External Intelligence Gap", [
        "External World Intelligence / Technology Capture / Market Learning L5 is not complete.",
        "E57 skipped live refresh because `external_page_read_adapter_unavailable`.",
        f"Next required milestone: `{NEXT_MILESTONE}`",
    ])
    write_md(root, str(PRODUCT_DIR / "external_intelligence_gap.md"), "External Intelligence Gap", [
        "External World Intelligence / Technology Capture / Market Learning L5 is not complete.",
        "Internal L5 runtime proof does not equal latest market intelligence.",
        "Real market contact should not begin before E59 closes this capability.",
    ])
    write_md(root, str(PRODUCT_DIR / "e59_requirements_packet.md"), "E59 Requirements Packet", [
        "E59 must first audit current external observation capabilities and reuse existing assets before building anything new.",
        "Required capabilities: " + ", ".join(data["E59_required_capabilities"]) + ".",
        "Baseline inspection must include: " + ", ".join(data["E59_must_inspect_and_reuse_baseline"]) + ".",
    ])
    return data
