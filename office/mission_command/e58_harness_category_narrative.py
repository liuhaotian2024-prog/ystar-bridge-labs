from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .e58_case_study_boundary import BRIDGE_ROOT, PRODUCT_DIR, write_json, write_md


def build_harness_category_narrative() -> dict[str, Any]:
    points = [
        "It is more than a proof packet because it packages a functioning internal L5 company runtime, not only one governed action artifact.",
        "It is more than an agent framework because it includes governance, authorization, evidence closure, and readback centerlines.",
        "It is more than an audit log because it includes decisioning, behavior control, and route selection before evidence capture.",
        "It is more than a guardrail because it models the full cognition -> behavior -> evidence -> governance loop.",
        "It is a runtime harness for AI-agent-operated company behavior because it coordinates CEO brain, behavior center, internal loop, and closure gates.",
        "Y-star-gov supplies generic governance validation; gov-mcp exposes validation as tool boundaries; K9Audit remains audit context.",
        "It does not prove market demand, customer validation, paid signal, real MCP transport, or external intelligence L5.",
        "External intelligence L5 must precede real market contact because latest source discovery, technology capture, and route impact analysis are not yet closed.",
    ]
    return {"artifact_id": "e58_harness_category_narrative", "narrative_points": points, "category_leadership_claimed": False, "market_validation_claimed": False, "customer_demand_claimed": False, "external_action_allowed": False}


def write_harness_category_narrative(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = build_harness_category_narrative()
    write_json(root, "operations/external_validation/e58_harness_category_narrative.json", data)
    write_md(root, "reports/integration/e58_harness_category_narrative.md", "E58 Harness Category Narrative", data["narrative_points"])
    write_md(root, str(PRODUCT_DIR / "category_narrative.md"), "Category Narrative", data["narrative_points"])
    return data

