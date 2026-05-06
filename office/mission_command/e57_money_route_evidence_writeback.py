from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e57_commercial_route_candidates import BRIDGE_ROOT, NEAREST_ALTERNATIVE, NEXT_MILESTONE, SELECTED_ROUTE, write_json, write_md
from .e57_commercial_route_decision import run_commercial_route_decision
from .e57_selected_route_behavior_authorization import run_selected_route_behavior_authorization


def write_money_route_evidence_writeback(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    decision = run_commercial_route_decision()
    auth = run_selected_route_behavior_authorization()
    brain = {
        "artifact_id": "e57_ceo_brain_money_route_update",
        "money_route_status": "post_l5_money_route_retest_closed",
        "selected_route": decision["selected_route"],
        "nearest_alternative": decision["nearest_alternative"],
        "selected_next_action": decision["allowed_next_action"],
        "behavior_authorization": auth["authorization_outcome"],
        "owner_decision_status": "pending_owner_decision",
        "owner_approval_required_before_external_action": True,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "real_mcp_transport_claimed": False,
        "next_recommended_milestone": NEXT_MILESTONE,
        "no_external_action": True,
    }
    czl = {
        "artifact_id": "e57_czl_closure",
        "closure_status": "post_l5_money_route_retest_closed",
        "selected_route": SELECTED_ROUTE,
        "nearest_alternative": NEAREST_ALTERNATIVE,
        "external_action_allowed": False,
        "next_milestone": NEXT_MILESTONE,
        "no_external_action": True,
    }
    cieu = {
        "artifact_id": "e57_cieu_residual_summary",
        "previous_residual": "money route had not been retested after CEO brain, behavior center, and internal loop reached L5.",
        "intervention": "E57 post-L5 capability delta, route candidates, counterfactual scoring, decision, authorization, readback, and governance gates.",
        "expected_residual_after_E57": "next internal route is selected without external action or overclaiming.",
        "remaining_residual": ["owner decision remains pending", "real MCP transport remains unclaimed", "customer validation and paid signal remain absent"],
        "external_action_allowed": False,
        "no_external_action": True,
    }
    kg = {
        "artifact_id": "e57_ceo_kg_read_model_update",
        "nodes_added": ["e57_post_l5_money_route_decision", SELECTED_ROUTE, NEAREST_ALTERNATIVE, NEXT_MILESTONE],
        "selected_route": SELECTED_ROUTE,
        "nearest_alternative": NEAREST_ALTERNATIVE,
        "selected_next_milestone": NEXT_MILESTONE,
        "owner_decision_status": "pending_owner_decision",
        "external_action_allowed": False,
        "no_external_action": True,
    }
    evidence = {
        "artifact_id": "e57_cross_repo_evidence_packet",
        "selected_route": SELECTED_ROUTE,
        "nearest_alternative": NEAREST_ALTERNATIVE,
        "source_artifacts": [
            "operations/external_validation/e54_ceo_brain_l5_readiness_gate_result.json",
            "operations/external_validation/e55_behavior_center_l5_readiness_gate_result.json",
            "operations/external_validation/e56_internal_company_loop_l5_readiness_gate_result.json",
            "operations/external_validation/e57_post_l5_commercial_route_decision_packet.json",
        ],
        "KG_update": "operations/knowledge_graph/e57_ceo_kg_read_model_update.json",
        "CZL_closure": "operations/external_validation/e57_czl_closure.json",
        "CIEU_residual": "operations/external_validation/e57_cieu_residual_summary.json",
        "no_customer_validation_claimed": True,
        "no_paid_signal_claimed": True,
        "no_real_mcp_transport_claimed": True,
        "external_action_allowed": False,
        "no_external_action": True,
    }
    nodes = [
        {"node_id": "e57_post_l5_money_route_decision", "node_type": "commercial_decision_packet", "status": "closed"},
        {"node_id": SELECTED_ROUTE, "node_type": "selected_route", "status": "selected"},
        {"node_id": NEAREST_ALTERNATIVE, "node_type": "nearest_alternative", "status": "deferred"},
        {"node_id": NEXT_MILESTONE, "node_type": "next_milestone", "status": "recommended"},
    ]
    edges = [
        {"from": "E56_internal_company_loop_L5", "to": "e57_post_l5_money_route_decision", "edge": "enables"},
        {"from": "e57_post_l5_money_route_decision", "to": SELECTED_ROUTE, "edge": "selects"},
        {"from": "e57_post_l5_money_route_decision", "to": NEAREST_ALTERNATIVE, "edge": "defers"},
        {"from": "e57_cross_repo_evidence_packet", "to": "CEO_brain", "edge": "readback"},
    ]
    write_json(root, "operations/external_validation/e57_ceo_brain_money_route_update.json", brain)
    write_json(root, "operations/external_validation/e57_czl_closure.json", czl)
    write_json(root, "operations/external_validation/e57_cieu_residual_summary.json", cieu)
    write_json(root, "operations/knowledge_graph/e57_ceo_kg_read_model_update.json", kg)
    write_json(root, "operations/external_validation/e57_cross_repo_evidence_packet.json", evidence)
    (root / "operations/knowledge_graph").mkdir(parents=True, exist_ok=True)
    (root / "operations/knowledge_graph/e57_ceo_kg_nodes_delta.jsonl").write_text("".join(json.dumps(n, ensure_ascii=False) + "\n" for n in nodes), encoding="utf-8")
    (root / "operations/knowledge_graph/e57_ceo_kg_edges_delta.jsonl").write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in edges), encoding="utf-8")
    write_md(root, "reports/integration/e57_cross_repo_evidence_packet.md", "E57 Cross-Repo Evidence Packet", [
        f"Selected route: `{SELECTED_ROUTE}`",
        f"Nearest alternative: `{NEAREST_ALTERNATIVE}`",
        "No external action, customer validation claim, paid signal claim, or real MCP transport claim.",
    ])
    return evidence

