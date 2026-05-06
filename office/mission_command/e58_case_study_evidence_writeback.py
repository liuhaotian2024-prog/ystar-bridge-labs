from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e58_case_study_boundary import BRIDGE_ROOT, CASE_STUDY_ID, NEAREST_ALTERNATIVE, NEXT_MILESTONE, SELECTED_ROUTE, write_json, write_md


def write_case_study_evidence_writeback(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    brain = {
        "artifact_id": "e58_ceo_brain_case_study_update",
        "case_study_status": "AI_agent_company_runtime_harness_case_study_packaged",
        "case_study_id": CASE_STUDY_ID,
        "selected_route_from_E57": SELECTED_ROUTE,
        "nearest_alternative_from_E57": NEAREST_ALTERNATIVE,
        "external_intelligence_gap_declared": True,
        "E59_required_before_market_contact": True,
        "owner_decision_status": "pending_owner_decision",
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "real_mcp_transport_claimed": False,
        "external_intelligence_L5_claimed_complete": False,
        "next_recommended_milestone": NEXT_MILESTONE,
        "no_external_action": True,
    }
    czl = {
        "artifact_id": "e58_czl_closure",
        "closure_status": "AI_agent_company_runtime_harness_case_study_packaged",
        "case_study_id": CASE_STUDY_ID,
        "next_milestone": NEXT_MILESTONE,
        "external_action_allowed": False,
        "no_external_action": True,
    }
    cieu = {
        "artifact_id": "e58_cieu_residual_summary",
        "previous_residual": "E57 selected the case study route, but it was not yet packaged as owner-reviewable material.",
        "intervention": "E58 packaged the AI Agent Company Runtime Harness Case Study and declared the E59 external intelligence gap.",
        "expected_residual_after_E58": "owner can review internal L5 case study; E59 must close external intelligence L5 before market contact.",
        "remaining_residual": ["external intelligence L5 not complete", "owner decision pending", "real MCP transport not claimed", "no customer validation or paid signal"],
        "external_action_allowed": False,
        "no_external_action": True,
    }
    kg = {
        "artifact_id": "e58_ceo_kg_read_model_update",
        "nodes_added": ["e58_case_study", "e58_external_intelligence_gap", NEXT_MILESTONE],
        "case_study_id": CASE_STUDY_ID,
        "selected_route": SELECTED_ROUTE,
        "selected_next_milestone": NEXT_MILESTONE,
        "external_action_allowed": False,
        "no_external_action": True,
    }
    evidence = {
        "artifact_id": "e58_cross_repo_evidence_packet",
        "case_study_id": CASE_STUDY_ID,
        "source_artifacts": [
            "products/ai_agent_company_runtime_harness_case_study/case_study.json",
            "operations/external_validation/e57_post_l5_commercial_route_decision_packet.json",
            "operations/external_validation/e56_internal_company_loop_l5_readiness_gate_result.json",
            "operations/external_validation/e55_behavior_center_l5_readiness_gate_result.json",
            "operations/external_validation/e54_ceo_brain_l5_readiness_gate_result.json",
        ],
        "KG_update": "operations/knowledge_graph/e58_ceo_kg_read_model_update.json",
        "CZL_closure": "operations/external_validation/e58_czl_closure.json",
        "CIEU_residual": "operations/external_validation/e58_cieu_residual_summary.json",
        "no_customer_validation_claimed": True,
        "no_paid_signal_claimed": True,
        "no_real_mcp_transport_claimed": True,
        "external_intelligence_L5_claimed_complete": False,
        "external_action_allowed": False,
        "no_external_action": True,
    }
    nodes = [
        {"node_id": "e58_case_study", "node_type": "owner_reviewable_case_study", "status": "packaged"},
        {"node_id": "e58_external_intelligence_gap", "node_type": "capability_gap", "status": "declared"},
        {"node_id": NEXT_MILESTONE, "node_type": "next_milestone", "status": "recommended"},
    ]
    edges = [
        {"from": "E57_post_L5_money_route", "to": "e58_case_study", "edge": "selects_and_packages"},
        {"from": "e58_case_study", "to": "CEO_brain", "edge": "readback"},
        {"from": "e58_external_intelligence_gap", "to": NEXT_MILESTONE, "edge": "requires"},
    ]
    write_json(root, "operations/external_validation/e58_ceo_brain_case_study_update.json", brain)
    write_json(root, "operations/external_validation/e58_czl_closure.json", czl)
    write_json(root, "operations/external_validation/e58_cieu_residual_summary.json", cieu)
    write_json(root, "operations/knowledge_graph/e58_ceo_kg_read_model_update.json", kg)
    write_json(root, "operations/external_validation/e58_cross_repo_evidence_packet.json", evidence)
    (root / "operations/knowledge_graph").mkdir(parents=True, exist_ok=True)
    (root / "operations/knowledge_graph/e58_ceo_kg_nodes_delta.jsonl").write_text("".join(json.dumps(n, ensure_ascii=False) + "\n" for n in nodes), encoding="utf-8")
    (root / "operations/knowledge_graph/e58_ceo_kg_edges_delta.jsonl").write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in edges), encoding="utf-8")
    write_md(root, "reports/integration/e58_cross_repo_evidence_packet.md", "E58 Cross-Repo Evidence Packet", [
        f"Case study id: `{CASE_STUDY_ID}`",
        f"Next milestone: `{NEXT_MILESTONE}`",
        "No external action or overclaim.",
    ])
    return evidence

