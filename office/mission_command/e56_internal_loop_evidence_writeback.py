from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e56_internal_company_loop_model import BRIDGE_ROOT, E56_CYCLE_ID, NEXT_MILESTONE, SELECTED_ACTION, write_json, write_md
from .e56_internal_loop_authorization import run_internal_loop_authorization
from .e56_internal_loop_dry_run_executor import run_internal_loop_dry_run_executor


def build_internal_loop_evidence_packet() -> dict[str, Any]:
    auth = run_internal_loop_authorization()
    dry = run_internal_loop_dry_run_executor()
    return {
        "artifact_id": "e56_internal_loop_evidence_packet",
        "cycle_id": E56_CYCLE_ID,
        "selected_action": SELECTED_ACTION,
        "authorization_result": auth["authorization_status"],
        "dry_run_result": dry["executor_status"],
        "denied_external_action_evidence": auth["external_action_authorization"],
        "no_go_boundary_evidence": {"pending_owner_decision_not_approval": True, "external_action_allowed": False},
        "KG_update": "operations/knowledge_graph/e56_ceo_kg_read_model_update.json",
        "CZL_closure": "operations/external_validation/e56_czl_closure.json",
        "CIEU_residual": "operations/external_validation/e56_cieu_residual_summary.json",
        "no_external_action_statement": "E56 executed internal dry-run artifacts only.",
        "next_milestone_proposal": NEXT_MILESTONE,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_internal_loop_evidence_writeback(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = build_internal_loop_evidence_packet()
    write_json(root, "operations/external_validation/e56_internal_loop_evidence_packet.json", data)
    czl = {
        "artifact_id": "e56_czl_closure",
        "closure_status": "internal_company_operating_loop_l5_ready",
        "cycle_id": E56_CYCLE_ID,
        "selected_action": SELECTED_ACTION,
        "external_action_allowed": False,
        "next_milestone": NEXT_MILESTONE,
        "no_external_action": True,
    }
    cieu = {
        "artifact_id": "e56_cieu_residual_summary",
        "previous_residual": "CEO brain L5 and behavior center L5 existed but had not yet completed one full internal operating cycle.",
        "intervention": "E56 internal cycle scenario, counterfactual selection, behavior queue, authorization, dry-run execution, evidence, KG/CZL/CIEU, readback, and self-evaluation.",
        "expected_residual_after_E56": "future money-route retest can inherit an internally proven operating loop.",
        "remaining_residual": ["real MCP transport remains unclaimed", "external review remains pending owner decision", "money route needs post-L5 retest"],
        "external_action_allowed": False,
        "no_external_action": True,
    }
    brain_update = {
        "artifact_id": "e56_ceo_brain_internal_loop_update",
        "internal_company_loop_status": "internal_company_operating_loop_l5_ready",
        "cycle_id": E56_CYCLE_ID,
        "selected_action": SELECTED_ACTION,
        "authorization_result": data["authorization_result"],
        "dry_run_result": data["dry_run_result"],
        "external_action_denied": True,
        "evidence_packet": "operations/external_validation/e56_internal_loop_evidence_packet.json",
        "KG_update": data["KG_update"],
        "CZL_closure": data["CZL_closure"],
        "CIEU_residual": data["CIEU_residual"],
        "next_recommended_milestone": NEXT_MILESTONE,
        "owner_decision_status": "pending_owner_decision",
        "external_action_allowed": False,
        "no_external_action": True,
    }
    kg = {
        "artifact_id": "e56_ceo_kg_read_model_update",
        "nodes_added": ["e56_internal_company_loop", "e56_internal_self_test_action", "e56_internal_loop_evidence", NEXT_MILESTONE],
        "cycle_id": E56_CYCLE_ID,
        "selected_action": SELECTED_ACTION,
        "selected_next_milestone": NEXT_MILESTONE,
        "owner_decision_status": "pending_owner_decision",
        "external_action_allowed": False,
        "no_external_action": True,
    }
    nodes = [
        {"node_id": "e56_internal_company_loop", "node_type": "internal_company_cycle", "status": "L5_ready"},
        {"node_id": SELECTED_ACTION, "node_type": "internal_action", "status": "dry_run_completed"},
        {"node_id": "e56_external_first_user_review_now", "node_type": "external_action", "status": "denied_pending_owner_decision"},
        {"node_id": NEXT_MILESTONE, "node_type": "next_milestone", "status": "recommended"},
    ]
    edges = [
        {"from": "CEO_brain_L5", "to": SELECTED_ACTION, "edge": "proposes"},
        {"from": SELECTED_ACTION, "to": "E55_behavior_control_center", "edge": "authorized_by"},
        {"from": "E55_behavior_control_center", "to": "e56_internal_loop_evidence", "edge": "dry_run_evidenced"},
        {"from": "e56_internal_loop_evidence", "to": "CEO_brain", "edge": "readback"},
    ]
    write_json(root, "operations/external_validation/e56_czl_closure.json", czl)
    write_json(root, "operations/external_validation/e56_cieu_residual_summary.json", cieu)
    write_json(root, "operations/external_validation/e56_ceo_brain_internal_loop_update.json", brain_update)
    write_json(root, "operations/knowledge_graph/e56_ceo_kg_read_model_update.json", kg)
    (root / "operations/knowledge_graph").mkdir(parents=True, exist_ok=True)
    (root / "operations/knowledge_graph/e56_ceo_kg_nodes_delta.jsonl").write_text("".join(json.dumps(n, ensure_ascii=False) + "\n" for n in nodes), encoding="utf-8")
    (root / "operations/knowledge_graph/e56_ceo_kg_edges_delta.jsonl").write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in edges), encoding="utf-8")
    write_md(root, "reports/integration/e56_internal_loop_evidence_packet.md", "E56 Internal Loop Evidence Packet", [
        f"Cycle id: `{data['cycle_id']}`",
        f"Selected action: `{data['selected_action']}`",
        f"Next milestone proposal: `{data['next_milestone_proposal']}`",
    ])
    return data

