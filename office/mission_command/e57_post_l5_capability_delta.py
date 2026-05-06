from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .e57_commercial_route_candidates import BRIDGE_ROOT, write_json, write_md


def run_post_l5_capability_delta() -> dict[str, Any]:
    rows = [
        ("CEO brain maturity", "counterfactual runtime reconnected but brain readback still emerging", "L5 cognitive state center ready", "large positive", "supports stronger commercial reasoning and state continuity", "boost case-study/harness route"),
        ("behavior control maturity", "canonical runtime existed but action center not L5", "L5 behavior control center ready", "large positive", "actions can be proposed/authorized/dry-run evidenced", "boost internal packageable runtime route"),
        ("internal company loop maturity", "not proven", "L5 internal operating loop ready", "large positive", "company can demonstrate closed internal loop", "new case-study route becomes credible"),
        ("proof packet maturity", "selected for packaging", "packaged owner-reviewable proof packet exists", "positive", "supports review readiness but not validation", "old route remains strong component"),
        ("anti-drift governance", "reconnected in E50B/E50C only", "cross-repo anti-drift gates passed", "positive", "reduces artifact/readback fracture risk", "boost governed stack"),
        ("capability binding governance", "not first-class", "capability centerline gate passed", "positive", "separates cognition/behavior/evidence/boundaries", "boost L5 harness narrative"),
        ("owner-review gate", "not yet built", "owner review pending; external action blocked", "mixed", "safe external gate exists but no approval", "penalize external routes"),
        ("evidence closure", "decision packet artifacts", "KG/CZL/CIEU written through E56", "positive", "evidence chain stronger", "boost case-study/harness route"),
        ("gov-mcp tool-layer proof", "E50A closed", "still closed", "stable positive", "governed tool-layer ALLOW/DENY remains credible", "supports proof packet and stack"),
        ("real MCP transport", "not closed", "still not claimed", "unchanged blocker", "cannot claim production MCP transport", "penalize transport-dependent routes"),
        ("K9Audit write integration", "read-only context", "still future work", "unchanged blocker", "causal audit wedge incomplete", "defer K9-only route"),
        ("external market feedback", "public-read-only evidence only", "no new external feedback", "unchanged blocker", "commercial evidence remains indirect", "penalize outreach/paid routes"),
        ("customer validation", "none", "none", "unchanged blocker", "no validation claim allowed", "deny validation-dependent claims"),
        ("paid signal", "none", "none", "unchanged blocker", "no paid demand claim allowed", "deny paid-signal claims"),
    ]
    return {
        "artifact_id": "e57_post_l5_capability_delta",
        "dimensions": [
            {"dimension": a, "E50B_state": b, "current_state": c, "delta": d, "commercial_effect": e, "route_implication": f}
            for a, b, c, d, e, f in rows
        ],
        "summary": "Post-L5 capability materially improves internal trust/proof and creates a stronger company-runtime harness route, while external-market blockers remain unchanged.",
        "big_improvement_internal_runtime_trust": True,
        "real_mcp_transport_claimed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "owner_decision_status": "pending_owner_decision",
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_post_l5_capability_delta(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_post_l5_capability_delta()
    write_json(root, "operations/external_validation/e57_post_l5_capability_delta.json", data)
    write_md(root, "reports/integration/e57_post_l5_capability_delta.md", "E57 Post-L5 Capability Delta", [
        data["summary"],
        "Real MCP transport claimed: `false`",
        "Customer validation claimed: `false`",
        "Paid signal claimed: `false`",
    ])
    return data

