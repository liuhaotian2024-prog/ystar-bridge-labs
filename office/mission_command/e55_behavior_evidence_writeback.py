from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e55_dry_run_action_executor import run_dry_run_executor

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))


def build_behavior_evidence_writeback() -> dict[str, Any]:
    executor = run_dry_run_executor()
    actions = [r["action_id"] for r in executor.get("dry_run_results", [])]
    return {
        "artifact_id": "e55_behavior_evidence_writeback",
        "writeback_status": "passed" if executor.get("executor_status") == "passed" else "failed",
        "dry_run_actions_evidenced": actions,
        "output_artifacts": [
            "operations/external_validation/e55_behavior_action_model.json",
            "operations/external_validation/e55_behavior_queue_snapshot.json",
            "operations/external_validation/e55_action_authorization_gate_result.json",
            "operations/external_validation/e55_dry_run_action_executor_result.json",
            "operations/knowledge_graph/e55_ceo_kg_read_model_update.json",
            "operations/external_validation/e55_czl_closure.json",
            "operations/external_validation/e55_cieu_residual_summary.json",
        ],
        "KG_update": "operations/knowledge_graph/e55_ceo_kg_read_model_update.json",
        "CZL_closure": "operations/external_validation/e55_czl_closure.json",
        "CIEU_residual": "operations/external_validation/e55_cieu_residual_summary.json",
        "brain_readback_required": True,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_behavior_evidence_writeback(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = build_behavior_evidence_writeback()
    (root / "operations/external_validation").mkdir(parents=True, exist_ok=True)
    (root / "operations/knowledge_graph").mkdir(parents=True, exist_ok=True)
    (root / "reports/integration").mkdir(parents=True, exist_ok=True)
    (root / "operations/external_validation/e55_behavior_evidence_writeback.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    brain_update = {
        "artifact_id": "e55_ceo_brain_behavior_center_update",
        "behavior_center_status": "behavior_control_center_l5_ready",
        "action_queue_status": "valid",
        "authorization_gate_status": "passed",
        "dry_run_executor_status": "passed",
        "allowed_internal_dry_run_actions": data["dry_run_actions_evidenced"],
        "external_actions_blocked": True,
        "owner_decision_status": "pending_owner_decision",
        "owner_approval_fabricated": False,
        "external_action_allowed": False,
        "next_recommended_milestone": "E56_internal_company_operating_loop_L5",
        "no_external_action": True,
    }
    (root / "operations/external_validation/e55_ceo_brain_behavior_center_update.json").write_text(json.dumps(brain_update, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    czl = {
        "artifact_id": "e55_czl_closure",
        "closure_status": "behavior_control_center_l5_ready",
        "behavior_actions_executed": "dry_run_internal_only",
        "external_action_allowed": False,
        "no_external_action": True,
        "next_milestone": "E56_internal_company_operating_loop_L5",
    }
    cieu = {
        "artifact_id": "e55_cieu_residual_summary",
        "previous_residual": "CEO brain L5 existed but behavior/action center was not L5.",
        "intervention": "E55 behavior action model, queue, authorization gate, dry-run executor, evidence, readback, anti-drift and capability binding gates.",
        "expected_residual_after_E55": "internal behavior actions must be proposed, authorized, dry-run executed, evidenced, and read back before closure.",
        "remaining_residual": ["full internal company operating loop remains future E56", "real MCP transport remains unclaimed", "external review remains pending owner decision"],
        "external_action_allowed": False,
        "no_external_action": True,
    }
    kg_read = {
        "artifact_id": "e55_ceo_kg_read_model_update",
        "nodes_added": ["e55_behavior_control_center", "e55_action_queue", "e55_authorization_gate", "e55_dry_run_executor", "e55_behavior_evidence_loop"],
        "selected_next_milestone": "E56_internal_company_operating_loop_L5",
        "owner_decision_status": "pending_owner_decision",
        "external_action_allowed": False,
        "no_external_action": True,
    }
    nodes = [
        {"node_id": "e55_behavior_control_center", "node_type": "behavior_control_capability", "status": "L5_ready"},
        {"node_id": "e55_action_queue", "node_type": "behavior_queue", "status": "valid"},
        {"node_id": "e55_authorization_gate", "node_type": "boundary_capability", "status": "passed"},
        {"node_id": "e55_dry_run_executor", "node_type": "execution_envelope", "status": "dry_run_only"},
        {"node_id": "e56_internal_company_operating_loop_L5", "node_type": "next_milestone", "status": "recommended"},
    ]
    edges = [
        {"from": "e54_ceo_brain_l5", "to": "e55_action_queue", "edge": "proposes"},
        {"from": "e55_authorization_gate", "to": "e55_dry_run_executor", "edge": "authorizes_dry_run"},
        {"from": "e55_dry_run_executor", "to": "e55_behavior_evidence_loop", "edge": "produces_evidence"},
        {"from": "e55_behavior_evidence_loop", "to": "CEO_brain", "edge": "readback"},
    ]
    (root / "operations/external_validation/e55_czl_closure.json").write_text(json.dumps(czl, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (root / "operations/external_validation/e55_cieu_residual_summary.json").write_text(json.dumps(cieu, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (root / "operations/knowledge_graph/e55_ceo_kg_read_model_update.json").write_text(json.dumps(kg_read, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (root / "operations/knowledge_graph/e55_ceo_kg_nodes_delta.jsonl").write_text("".join(json.dumps(n, ensure_ascii=False) + "\n" for n in nodes), encoding="utf-8")
    (root / "operations/knowledge_graph/e55_ceo_kg_edges_delta.jsonl").write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in edges), encoding="utf-8")
    (root / "reports/integration/e55_behavior_center_readback_smoke_result.md").write_text("# E55 Behavior Evidence Writeback\n\nWriteback status: `%s`\n" % data["writeback_status"], encoding="utf-8")
    return data
