from __future__ import annotations

import json
import os
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
K9_ROOT = Path(os.environ.get("K9AUDIT_ROOT", "/Users/haotianliu/.openclaw/workspace/K9Audit"))
COMPANY_ROOT = Path(os.environ.get("YSTAR_COMPANY_ROOT", "/Users/haotianliu/.openclaw/workspace/ystar-company"))


def _read(path: Path, limit: int = 120000) -> str:
    try:
        if not path.exists() or path.is_dir() or path.stat().st_size > 2_000_000:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""


def _json(path: Path) -> Any:
    try:
        return json.loads(_read(path, 2_000_000))
    except Exception:
        return None


def _run(command: list[str], cwd: Path = BRIDGE_ROOT, timeout: int = 20) -> dict[str, Any]:
    try:
        completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=timeout, check=False)
        return {"command": command, "cwd": str(cwd), "returncode": completed.returncode, "stdout": (completed.stdout or "")[:4000], "stderr": (completed.stderr or "")[:4000], "timed_out": False}
    except subprocess.TimeoutExpired as exc:
        return {"command": command, "cwd": str(cwd), "returncode": None, "stdout": (exc.stdout or "")[:4000] if isinstance(exc.stdout, str) else "", "stderr": (exc.stderr or "")[:4000] if isinstance(exc.stderr, str) else "", "timed_out": True}
    except Exception as exc:
        return {"command": command, "cwd": str(cwd), "returncode": None, "stdout": "", "stderr": str(exc), "timed_out": False}


def _lines(path: Path, terms: list[str], limit: int = 8) -> list[str]:
    rows: list[str] = []
    body = _read(path, 120000)
    for line in body.splitlines():
        lower = line.lower()
        if any(term.lower() in lower for term in terms):
            rows.append(line.strip()[:240])
        if len(rows) >= limit:
            break
    return rows


def _latest_existing(paths: list[str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for rel in paths:
        path = BRIDGE_ROOT / rel
        if path.exists():
            result[rel] = _json(path) if path.suffix in {".json", ".jsonl"} else _read(path, 20000)
    return result


def _commercial_assets(limit: int = 12) -> list[dict[str, Any]]:
    terms = ["first user", "revenue", "pricing", "plugin", "mcpb", "marketplace", "enterprise", "bug bounty", "workflow resale", "paid"]
    assets: list[dict[str, Any]] = []
    for directory in ["sales", "marketing", "content", "finance", "reports/autonomous", "knowledge/cso", "knowledge/cfo"]:
        base = BRIDGE_ROOT / directory
        if not base.exists():
            continue
        for file in sorted(base.rglob("*")):
            if not file.is_file() or file.suffix.lower() not in {".md", ".json", ".txt", ".yaml", ".yml"}:
                continue
            body = f"{file.name}\n{_read(file, 40000)}".lower()
            matched = [term for term in terms if term in body]
            if matched:
                assets.append({"path": str(file.relative_to(BRIDGE_ROOT)), "matched_terms": matched[:8], "snippets": _lines(file, matched[:6], limit=3), "score": len(matched)})
    return sorted(assets, key=lambda item: (-item["score"], item["path"]))[:limit]



E50B_CURRENT_STATE_PATHS = {
    "brain_update": "operations/external_validation/e50b_ceo_brain_counterfactual_update.json",
    "commercial_decision_packet": "operations/external_validation/e50b_ceo_commercial_decision_packet.json",
    "counterfactual_money_route_retest": "operations/external_validation/e50b_counterfactual_money_route_retest.json",
    "counterfactual_money_route_matrix": "operations/external_validation/e50b_counterfactual_money_route_matrix.json",
    "kg_read_model_update": "operations/knowledge_graph/e50b_ceo_kg_read_model_update.json",
    "czl_closure": "operations/external_validation/e50b_czl_closure.json",
    "cieu_residual_summary": "operations/external_validation/e50b_cieu_residual_summary.json",
    "e50a_mcp_client_blocker_update": "operations/external_validation/e50a_mcp_client_blocker_update.json",
}


def _route_id(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("route_id") or value.get("selected_route") or "")
    if isinstance(value, str):
        return value
    return ""


def _artifact_or_unavailable(rel: str) -> dict[str, Any]:
    path = BRIDGE_ROOT / rel
    if not path.exists():
        return {"available": False, "path": rel, "data": None, "status": "unavailable_nonfatal"}
    return {"available": True, "path": rel, "data": _json(path), "status": "loaded"}


def _load_e50b_current_state() -> dict[str, Any]:
    artifacts = {name: _artifact_or_unavailable(rel) for name, rel in E50B_CURRENT_STATE_PATHS.items()}
    packet = artifacts["commercial_decision_packet"].get("data") or {}
    retest = artifacts["counterfactual_money_route_retest"].get("data") or {}
    matrix = artifacts["counterfactual_money_route_matrix"].get("data") or {}
    kg = artifacts["kg_read_model_update"].get("data") or {}
    czl = artifacts["czl_closure"].get("data") or {}
    cieu = artifacts["cieu_residual_summary"].get("data") or {}
    e50a = artifacts["e50a_mcp_client_blocker_update"].get("data") or {}

    selected_route = _route_id(packet.get("selected_route")) or _route_id(retest.get("selected_route")) or _route_id(matrix.get("selected_route")) or _route_id(kg.get("selected_route"))
    nearest_alternative = _route_id(packet.get("nearest_rejected_or_deferred_alternative")) or _route_id(retest.get("nearest_rejected_or_deferred_route")) or _route_id(matrix.get("nearest_rejected_or_deferred_route")) or _route_id(kg.get("nearest_counterfactual_alternative"))
    selected_route_payload = packet.get("selected_route") if isinstance(packet.get("selected_route"), dict) else retest.get("selected_route", {})
    blocker_state = selected_route_payload.get("blocker_state") if isinstance(selected_route_payload, dict) else ""
    residuals = cieu.get("residuals", []) if isinstance(cieu.get("residuals", []), list) else []
    if residuals:
        blocker_state = blocker_state or "; ".join(str(item) for item in residuals)
    current_next = packet.get("next_executable_milestone") or kg.get("next_decision_horizon") or ""
    e50b_status = packet.get("final_status") or czl.get("external_observation_status") or "unavailable_nonfatal"
    current_no_go_boundaries = {
        "no_outreach": True,
        "no_publication": True,
        "no_customer_validation_claim": True,
        "no_paid_signal_claim": True,
        "no_expert_feedback_claim": True,
        "no_contact_scraping": True,
        "no_login": True,
        "no_provider_private_api": True,
        "no_payment_or_secret_use": True,
        "owner_approval_required_before_external_action": True,
        "brain_may_not_bypass_governance": True,
    }
    matrix_routes = matrix.get("routes", []) if isinstance(matrix.get("routes"), list) else []
    counterfactual_summary = {
        "available": artifacts["counterfactual_money_route_matrix"]["available"],
        "selected_route": _route_id(matrix.get("selected_route")),
        "nearest_rejected_or_deferred_route": _route_id(matrix.get("nearest_rejected_or_deferred_route")),
        "route_count": len(matrix_routes),
        "validation": matrix.get("validation", {}),
    }
    centerline_connected = all([
        selected_route == "package_governed_agent_action_proof_packet",
        nearest_alternative == "external_commercial_observation_now",
        current_next == "E51_package_governed_agent_action_proof_packet_for_first_user_review",
        "real_mcp_transport_not_closed" in str(blocker_state or ""),
        e50a.get("new_status") == "tool_layer_allow_deny_closed",
    ])
    return {
        "current_decision_horizon": "E51 first-user-review proof packet packaging",
        "current_selected_route": selected_route or "unavailable_nonfatal",
        "current_nearest_alternative": nearest_alternative or "unavailable_nonfatal",
        "current_counterfactual_matrix_summary": counterfactual_summary,
        "current_commercial_decision_packet": packet if packet else {"available": False, "status": "unavailable_nonfatal"},
        "current_blocker_state": blocker_state or "unavailable_nonfatal",
        "current_no_go_boundaries": current_no_go_boundaries,
        "current_next_milestone": current_next or "unavailable_nonfatal",
        "current_e50a_status": e50a.get("new_status") or e50a.get("final_status") or "unavailable_nonfatal",
        "current_e50b_status": e50b_status,
        "current_czl_closure": czl if czl else {"available": False, "status": "unavailable_nonfatal"},
        "current_cieu_residual_summary": cieu if cieu else {"available": False, "status": "unavailable_nonfatal"},
        "current_kg_read_model_update": kg if kg else {"available": False, "status": "unavailable_nonfatal"},
        "brain_centerline_status": "ceo_brain_centerline_connected" if centerline_connected else "e50b_current_state_unavailable_nonfatal",
        "e50b_artifacts_loaded": {name: item["available"] for name, item in artifacts.items()},
    }



E52_PROOF_PACKET_CURRENT_STATE_PATHS = {
    "proof_packet": "products/governed_agent_action_proof_packet/proof_packet.json",
    "packet_validation": "products/governed_agent_action_proof_packet/packet_validation_result.json",
    "owner_checklist": "products/governed_agent_action_proof_packet/owner_approval_checklist.md",
    "no_go_boundary_manifest": "products/governed_agent_action_proof_packet/no_go_boundary_manifest.json",
    "completion_gate": "operations/external_validation/e52_completion_gate_result.json",
    "czl_closure": "operations/external_validation/e52_czl_closure.json",
    "cieu_residual_summary": "operations/external_validation/e52_cieu_residual_summary.json",
    "kg_read_model_update": "operations/knowledge_graph/e52_ceo_kg_read_model_update.json",
}


def _load_latest_proof_packet_current_state() -> dict[str, Any]:
    artifacts = {name: _artifact_or_unavailable(rel) for name, rel in E52_PROOF_PACKET_CURRENT_STATE_PATHS.items()}
    packet = artifacts["proof_packet"].get("data") or {}
    validation = artifacts["packet_validation"].get("data") or {}
    completion = artifacts["completion_gate"].get("data") or {}
    no_go = artifacts["no_go_boundary_manifest"].get("data") or {}
    kg = artifacts["kg_read_model_update"].get("data") or {}
    packet_exists = artifacts["proof_packet"]["available"]
    next_milestone = packet.get("next_recommended_milestone") or completion.get("recommended_next_milestone") or kg.get("next_recommended_milestone") or "unavailable_nonfatal"
    return {
        "proof_packet_available": packet_exists,
        "packet_id": packet.get("packet_id") or "unavailable_nonfatal",
        "packet_status": "owner_reviewable_only" if packet_exists else "unavailable_nonfatal",
        "selected_route": packet.get("selected_route") or "unavailable_nonfatal",
        "proof_level": packet.get("proof_level") or "unavailable_nonfatal",
        "real_mcp_transport_claimed": bool(packet.get("real_mcp_transport_claimed", False)),
        "customer_validation_claimed": bool(packet.get("customer_validation_claimed", False)),
        "paid_signal_claimed": bool(packet.get("paid_signal_claimed", False)),
        "outreach_status": packet.get("outreach_status") or "not_contacted",
        "publication_status": packet.get("publication_status") or "not_published",
        "owner_approval_required_before": packet.get("owner_approval_required_before") or ["external contact", "publication"],
        "no_go_boundaries": no_go or packet.get("no_go_boundaries", {}),
        "packet_validation_passed": validation.get("passed") if isinstance(validation, dict) else None,
        "completion_gate_passed": completion.get("gate_passed") if isinstance(completion, dict) else None,
        "next_recommended_milestone": next_milestone,
        "artifacts_loaded": {name: item["available"] for name, item in artifacts.items()},
        "read_model_role": "latest owner-review proof packet state; never authorizes outreach or publication",
    }


E53_OWNER_REVIEW_CURRENT_STATE_PATHS = {
    "owner_review_packet": "products/governed_agent_action_proof_packet/e53_owner_review_packet.json",
    "approval_placeholder": "operations/external_validation/e53_owner_approval_record_placeholder.json",
    "approval_validation": "operations/external_validation/e53_owner_approval_validation_result.json",
    "risk_gate": "operations/external_validation/e53_first_user_review_risk_gate_result.json",
    "non_sent_template": "products/governed_agent_action_proof_packet/e53_non_sent_review_request_template.json",
    "protocol": "products/governed_agent_action_proof_packet/e53_single_first_user_review_protocol.json",
    "completion_gate": "operations/external_validation/e53_completion_gate_result.json",
    "czl_closure": "operations/external_validation/e53_czl_closure.json",
    "cieu_residual_summary": "operations/external_validation/e53_cieu_residual_summary.json",
    "kg_read_model_update": "operations/knowledge_graph/e53_ceo_kg_read_model_update.json",
}


def _load_latest_owner_review_current_state() -> dict[str, Any]:
    artifacts = {name: _artifact_or_unavailable(rel) for name, rel in E53_OWNER_REVIEW_CURRENT_STATE_PATHS.items()}
    packet = artifacts["owner_review_packet"].get("data") or {}
    placeholder = artifacts["approval_placeholder"].get("data") or {}
    validation = artifacts["approval_validation"].get("data") or {}
    risk = artifacts["risk_gate"].get("data") or {}
    template = artifacts["non_sent_template"].get("data") or {}
    completion = artifacts["completion_gate"].get("data") or {}
    kg = artifacts["kg_read_model_update"].get("data") or {}
    owner_status = validation.get("owner_decision_status") or placeholder.get("owner_decision_status") or packet.get("owner_decision_status") or "pending_owner_decision"
    next_milestone = completion.get("recommended_next_milestone") or risk.get("recommended_next_milestone") or packet.get("next_recommended_milestone") or kg.get("next_recommended_milestone") or "E54_owner_decision_or_controlled_first_user_review_plan"
    return {
        "owner_review_packet_available": artifacts["owner_review_packet"]["available"],
        "owner_review_packet_id": packet.get("review_packet_id") or "unavailable_nonfatal",
        "owner_decision_status": owner_status,
        "approval_validation_status": validation.get("status") or owner_status,
        "external_action_allowed": bool(risk.get("external_action_allowed", False)),
        "risk_gate_status": risk.get("gate_status") or "blocked_pending_owner_decision",
        "non_sent_template_sent": bool(template.get("sent", False)),
        "real_reviewer_identified": bool(packet.get("real_reviewer_identified", False) or template.get("contact_identified", False)),
        "contact_info_collected": bool(template.get("contact_info_collected", False)),
        "customer_validation_claimed": bool(packet.get("customer_validation_claimed", False)),
        "paid_signal_claimed": bool(packet.get("paid_signal_claimed", False)),
        "real_mcp_transport_claimed": bool(packet.get("real_mcp_transport_claimed", False)),
        "no_go_boundaries": packet.get("no_go_boundaries") or risk.get("no_go_boundaries") or {},
        "next_recommended_milestone": next_milestone,
        "artifacts_loaded": {name: item["available"] for name, item in artifacts.items()},
        "read_model_role": "latest owner-review approval gate state; blocks external action until explicit owner approval evidence exists",
    }


def load_ceo_brain_context(task: dict[str, Any]) -> dict[str, Any]:
    query = f"{task.get('task_title', '')} {task.get('task_description', '')} M Triangle value production"
    wisdom = _run(["python3", "scripts/wisdom_search.py", "--top", "3", "--json", query])
    memory = _run(["python3", "scripts/working_memory_snapshot.py", "load-latest"])
    latest = _latest_existing([
        "operations/external_validation/e45_full_history_actual_invocation_trace.json",
        "operations/external_validation/e45_real_local_first_value_demo_run.json",
        "operations/external_validation/e45_first_value_demo_bundle.json",
        "operations/external_validation/e44a_full_history_runtime_capability_map.json",
        "operations/external_validation/e42_ceo_runtime_reuse_router_integration.json",
        "operations/knowledge_graph/e45_ceo_kg_read_model_update.json",
        "operations/external_validation/e45_ceo_brain_first_value_demo_update.json",
        "operations/external_validation/e50b_ceo_brain_counterfactual_update.json",
        "operations/external_validation/e50b_ceo_commercial_decision_packet.json",
        "operations/external_validation/e50b_counterfactual_money_route_retest.json",
        "operations/external_validation/e50b_counterfactual_money_route_matrix.json",
        "operations/knowledge_graph/e50b_ceo_kg_read_model_update.json",
        "operations/external_validation/e50b_czl_closure.json",
        "operations/external_validation/e50b_cieu_residual_summary.json",
        "operations/external_validation/e50a_mcp_client_blocker_update.json",
    ])
    e50b_current_state = _load_e50b_current_state()
    proof_packet_state = _load_latest_proof_packet_current_state()
    owner_review_state = _load_latest_owner_review_current_state()
    try:
        from office.mission_command.e54_ceo_brain_current_state_registry import resolve_current_state
        e54_current_state_registry_resolution = resolve_current_state()
    except Exception as exc:
        e54_current_state_registry_resolution = {'registry_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_approval_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e55_behavior_center_readback_smoke import load_behavior_center_state_for_brain
        e55_behavior_center_state = load_behavior_center_state_for_brain()
    except Exception as exc:
        e55_behavior_center_state = {'behavior_center_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e56_internal_loop_readback_smoke import load_internal_loop_state_for_brain
        e56_internal_company_loop_state = load_internal_loop_state_for_brain()
    except Exception as exc:
        e56_internal_company_loop_state = {'internal_company_loop_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e57_ceo_brain_readback_smoke import load_money_route_state_for_brain
        e57_money_route_state = load_money_route_state_for_brain()
    except Exception as exc:
        e57_money_route_state = {'money_route_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e58_ceo_brain_readback_smoke import load_case_study_state_for_brain
        e58_case_study_state = load_case_study_state_for_brain()
    except Exception as exc:
        e58_case_study_state = {'case_study_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e59_ceo_brain_readback_smoke import load_e59_state_for_brain
        e59_external_intelligence_state = load_e59_state_for_brain()
    except Exception as exc:
        e59_external_intelligence_state = {'external_intelligence_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e60_ceo_brain_readback_smoke import load_e60_state_for_brain
        e60_market_readiness_state = load_e60_state_for_brain()
    except Exception as exc:
        e60_market_readiness_state = {'market_readiness_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e61_ceo_brain_readback_smoke import load_e61_state_for_brain
        e61_live_public_read_state = load_e61_state_for_brain()
    except Exception as exc:
        e61_live_public_read_state = {'live_public_read_final_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e62_ceo_brain_readback_smoke import load_e62_state_for_brain
        e62_revenue_runtime_state = load_e62_state_for_brain()
    except Exception as exc:
        e62_revenue_runtime_state = {'revenue_runtime_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e63_ceo_brain_readback_smoke import load_e63_state_for_brain
        e63_revenue_opportunity_state = load_e63_state_for_brain()
    except Exception as exc:
        e63_revenue_opportunity_state = {'opportunity_discovery_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e64_ceo_brain_readback_smoke import load_e64_state_for_brain
        e64_dual_axis_revenue_state = load_e64_state_for_brain()
    except Exception as exc:
        e64_dual_axis_revenue_state = {'dual_axis_retest_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e65_ceo_market_dynamics_readback import load_e65_market_dynamics_state_for_brain
        e65_market_dynamics_state = load_e65_market_dynamics_state_for_brain()
    except Exception as exc:
        e65_market_dynamics_state = {'market_model_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e66_ceo_brain_readback_smoke import load_e66_state_for_brain
        e66_model_driven_offer_state = load_e66_state_for_brain()
    except Exception as exc:
        e66_model_driven_offer_state = {'model_driven_offer_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e67_ceo_external_validation_readback import load_e67_external_validation_state_for_brain
        e67_external_validation_state = load_e67_external_validation_state_for_brain()
    except Exception as exc:
        e67_external_validation_state = {'external_validation_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e68_ceo_cieu_route_readback import load_e68_cieu_route_state_for_brain
        e68_cieu_route_state = load_e68_cieu_route_state_for_brain()
    except Exception as exc:
        e68_cieu_route_state = {'cieu_route_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e69_ceo_next_action_planner_readback import load_e69_next_action_state_for_brain
        e69_next_action_planning_state = load_e69_next_action_state_for_brain()
    except Exception as exc:
        e69_next_action_planning_state = {'planning_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e70_ceo_self_bootstrap_readback import load_e70_self_bootstrap_state_for_brain
        e70_self_bootstrap_state = load_e70_self_bootstrap_state_for_brain()
    except Exception as exc:
        e70_self_bootstrap_state = {'self_bootstrap_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e71_legacy_asset_readback import load_e71_legacy_asset_resurrection_state_for_brain
        e71_legacy_asset_resurrection_state = load_e71_legacy_asset_resurrection_state_for_brain()
    except Exception as exc:
        e71_legacy_asset_resurrection_state = {'legacy_asset_resurrection_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e72_cieu_audit_module_readback import load_e72_cieu_audit_module_state_for_brain
        e72_cieu_audit_module_state = load_e72_cieu_audit_module_state_for_brain()
    except Exception as exc:
        e72_cieu_audit_module_state = {'cieu_audit_module_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e73_readback import load_e73_boundary_state_for_brain
        e73_ecosystem_boundary_lock_state = load_e73_boundary_state_for_brain()
    except Exception as exc:
        e73_ecosystem_boundary_lock_state = {'ecosystem_boundary_lock_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e74_ceo_l2_readback import load_e74_l2_work_state_for_brain
        e74_l2_internal_work_state = load_e74_l2_work_state_for_brain()
    except Exception as exc:
        e74_l2_internal_work_state = {'L2_work_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e75_readback import load_e75_owner_decision_state_for_brain
        e75_l3_owner_decision_state = load_e75_owner_decision_state_for_brain()
    except Exception as exc:
        e75_l3_owner_decision_state = {'E75_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_approval_status': 'pending_owner_decision'}
    try:
        from office.mission_command.e76_e77_readback import load_e76_e77_state_for_brain
        e76_e77_l3_lineage_decision_state = load_e76_e77_state_for_brain()
    except Exception as exc:
        e76_e77_l3_lineage_decision_state = {'E76_E77_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision', 'did_execute_L3': False}
    try:
        from office.mission_command.e78_readback import load_e78_l3_research_state_for_brain
        e78_l3_research_state = load_e78_l3_research_state_for_brain()
    except Exception as exc:
        e78_l3_research_state = {'E78_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'owner_decision_status': 'pending_owner_decision', 'did_execute_L3': False}
    try:
        from office.mission_command.e79_readback import load_e79_strategic_judgment_state_for_brain
        e79_strategic_judgment_state = load_e79_strategic_judgment_state_for_brain()
    except Exception as exc:
        e79_strategic_judgment_state = {'E79_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'L4_execution_authorized': False, 'quality_gate_passed': False}
    try:
        from office.mission_command.e80_readback import load_e80_cognitive_activation_state_for_brain
        e80_cognitive_activation_state = load_e80_cognitive_activation_state_for_brain()
    except Exception as exc:
        e80_cognitive_activation_state = {'E80_R2_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'L4_execution_authorized': False, 'L5_ready': False}
    try:
        from office.mission_command.e81_readback import load_e81_cognitive_os_state_for_brain
        e81_cognitive_os_state = load_e81_cognitive_os_state_for_brain()
    except Exception as exc:
        e81_cognitive_os_state = {'E81_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'L4_execution_authorized': False, 'L5_ready': False, 'bypass_allowed': True}
    try:
        from office.mission_command.e82_ystar_gov_sync_readback import load_e82_cognitive_os_sync_state_for_brain
        e82_cognitive_os_sync_state = load_e82_cognitive_os_sync_state_for_brain()
    except Exception as exc:
        e82_cognitive_os_sync_state = {'E82_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'L4_execution_authorized': False, 'L5_ready': False, 'YstarGov_synced': False}
    try:
        from office.mission_command.e83_autoguidance_semantics_readback import load_e83_autoguidance_state_for_brain
        e83_autoguidance_state = load_e83_autoguidance_state_for_brain()
    except Exception as exc:
        e83_autoguidance_state = {'E83_status': 'unavailable_nonfatal', 'error': str(exc), 'external_action_allowed': False, 'L4_execution_authorized': False, 'L5_ready': False, 'Y_star_gov_validator_supports_correct_path_guidance': False}
    try:
        wisdom_results = json.loads(wisdom.get("stdout") or "[]") if wisdom.get("returncode") == 0 else []
    except Exception:
        wisdom_results = []
    return {
        "artifact_id": "e46b_ceo_brain_context",
        "active_task_time_source": "e46b_ceo_brain_adapter.load_ceo_brain_context",
        "task": task,
        "wisdom_search": {"invoked": True, "returncode": wisdom.get("returncode"), "top_results": wisdom_results[:3]},
        "working_memory": {"invoked": True, "returncode": memory.get("returncode"), "status": "loaded" if memory.get("returncode") == 0 else "unavailable_nonfatal", "stdout": memory.get("stdout", "")[:1000], "stderr": memory.get("stderr", "")[:1000]},
        "constitutional_sources": {
            "M_TRIANGLE": _lines(BRIDGE_ROOT / "knowledge/ceo/wisdom/M_TRIANGLE.md", ["value", "production", "triangle", "real"]),
            "WORK_METHODOLOGY": _lines(BRIDGE_ROOT / "knowledge/ceo/wisdom/WORK_METHODOLOGY.md", ["task", "execution", "user", "value"]),
            "DIRECTIVE_TRACKER": _lines(BRIDGE_ROOT / "DIRECTIVE_TRACKER.md", ["first", "user", "revenue", "pmf", "install", "customer"]),
            "OPERATIONS": _lines(BRIDGE_ROOT / "OPERATIONS.md", ["first", "user", "revenue", "pmf", "install", "customer"]),
        },
        "latest_runtime_artifacts": latest,
        "current_decision_horizon": e50b_current_state["current_decision_horizon"],
        "current_selected_route": e50b_current_state["current_selected_route"],
        "current_nearest_alternative": e50b_current_state["current_nearest_alternative"],
        "current_counterfactual_matrix_summary": e50b_current_state["current_counterfactual_matrix_summary"],
        "current_commercial_decision_packet": e50b_current_state["current_commercial_decision_packet"],
        "current_blocker_state": e50b_current_state["current_blocker_state"],
        "current_no_go_boundaries": e50b_current_state["current_no_go_boundaries"],
        "current_next_milestone": e50b_current_state["current_next_milestone"],
        "current_e50a_status": e50b_current_state["current_e50a_status"],
        "current_e50b_status": e50b_current_state["current_e50b_status"],
        "current_czl_closure": e50b_current_state["current_czl_closure"],
        "current_cieu_residual_summary": e50b_current_state["current_cieu_residual_summary"],
        "current_kg_read_model_update": e50b_current_state["current_kg_read_model_update"],
        "brain_centerline_status": e50b_current_state["brain_centerline_status"],
        "e50b_artifacts_loaded": e50b_current_state["e50b_artifacts_loaded"],
        "latest_proof_packet_state": proof_packet_state,
        "current_proof_packet_status": proof_packet_state.get("packet_status"),
        "current_proof_packet_next_milestone": proof_packet_state.get("next_recommended_milestone"),
        "latest_owner_review_state": owner_review_state,
        "current_owner_review_status": "owner_review_gate_ready" if owner_review_state.get("owner_review_packet_available") else "unavailable_nonfatal",
        "current_owner_approval_status": owner_review_state.get("owner_decision_status"),
        "current_external_action_allowed": owner_review_state.get("external_action_allowed"),
        "current_owner_review_next_milestone": owner_review_state.get("next_recommended_milestone"),
        "latest_current_state_registry_resolution": e54_current_state_registry_resolution,
        "current_state_registry_status": e54_current_state_registry_resolution.get("registry_status"),
        "current_l5_brain_next_action": e54_current_state_registry_resolution.get("next_milestone"),
        "current_l5_external_action_allowed": e54_current_state_registry_resolution.get("external_action_allowed"),
        "latest_behavior_center_state": e55_behavior_center_state,
        "current_behavior_center_status": e55_behavior_center_state.get("behavior_center_status"),
        "current_behavior_queue_status": e55_behavior_center_state.get("behavior_queue_status"),
        "current_behavior_authorization_status": e55_behavior_center_state.get("authorization_gate_status"),
        "current_behavior_external_action_allowed": e55_behavior_center_state.get("external_action_allowed"),
        "current_behavior_next_milestone": e55_behavior_center_state.get("next_recommended_milestone"),
        "latest_internal_company_loop_state": e56_internal_company_loop_state,
        "current_internal_company_loop_status": e56_internal_company_loop_state.get("internal_company_loop_status"),
        "current_internal_loop_selected_action": e56_internal_company_loop_state.get("selected_action"),
        "current_internal_loop_authorization_result": e56_internal_company_loop_state.get("authorization_result"),
        "current_internal_loop_dry_run_result": e56_internal_company_loop_state.get("dry_run_result"),
        "current_internal_loop_external_action_allowed": e56_internal_company_loop_state.get("external_action_allowed"),
        "current_internal_loop_next_milestone": e56_internal_company_loop_state.get("next_recommended_milestone"),
        "latest_money_route_state": e57_money_route_state,
        "current_money_route_status": e57_money_route_state.get("money_route_status"),
        "current_money_route_selected_route": e57_money_route_state.get("selected_route"),
        "current_money_route_nearest_alternative": e57_money_route_state.get("nearest_alternative"),
        "current_money_route_external_action_allowed": e57_money_route_state.get("external_action_allowed"),
        "current_money_route_next_milestone": e57_money_route_state.get("next_recommended_milestone"),
        "latest_case_study_state": e58_case_study_state,
        "current_case_study_status": e58_case_study_state.get("case_study_status"),
        "current_case_study_id": e58_case_study_state.get("case_study_id"),
        "current_case_study_external_intelligence_gap": e58_case_study_state.get("external_intelligence_gap_declared"),
        "current_case_study_external_action_allowed": e58_case_study_state.get("external_action_allowed"),
        "current_case_study_next_milestone": e58_case_study_state.get("next_recommended_milestone"),
        "latest_external_intelligence_state": e59_external_intelligence_state,
        "current_external_intelligence_status": e59_external_intelligence_state.get("external_intelligence_status"),
        "current_external_intelligence_receipt_count": e59_external_intelligence_state.get("source_receipt_count"),
        "current_external_intelligence_evidence_atom_count": e59_external_intelligence_state.get("evidence_atom_count"),
        "current_external_intelligence_live_public_read_status": e59_external_intelligence_state.get("live_public_read_status"),
        "current_external_intelligence_external_action_allowed": e59_external_intelligence_state.get("external_action_allowed"),
        "current_external_intelligence_next_milestone": e59_external_intelligence_state.get("next_recommended_milestone"),
        "latest_market_readiness_state": e60_market_readiness_state,
        "current_market_readiness_status": e60_market_readiness_state.get("market_readiness_status"),
        "current_market_entry_readiness_level": e60_market_readiness_state.get("current_readiness_level"),
        "current_market_readiness_selected_next_milestone": e60_market_readiness_state.get("selected_next_milestone"),
        "current_market_readiness_nearest_alternative": e60_market_readiness_state.get("nearest_alternative"),
        "current_market_readiness_live_public_read_status": e60_market_readiness_state.get("live_public_read_status"),
        "current_market_readiness_fixture_only_evidence_treated_as_live_market_freshness": e60_market_readiness_state.get("fixture_only_evidence_treated_as_live_market_freshness"),
        "current_market_readiness_external_action_allowed": e60_market_readiness_state.get("external_action_allowed"),
        "latest_live_public_read_state": e61_live_public_read_state,
        "current_live_public_read_final_status": e61_live_public_read_state.get("live_public_read_final_status"),
        "current_live_public_read_smoke_probe_passed": e61_live_public_read_state.get("controlled_public_read_smoke_probe_passed"),
        "current_live_public_read_recommended_next_milestone": e61_live_public_read_state.get("recommended_next_milestone"),
        "current_live_public_read_external_action_allowed": e61_live_public_read_state.get("external_action_allowed"),
        "latest_autonomous_revenue_runtime_state": e62_revenue_runtime_state,
        "current_autonomous_revenue_runtime_status": e62_revenue_runtime_state.get("revenue_runtime_status"),
        "current_autonomous_revenue_runtime_primary_objective": e62_revenue_runtime_state.get("primary_objective"),
        "current_autonomous_revenue_runtime_first_cash_path": e62_revenue_runtime_state.get("selected_first_cash_path"),
        "current_autonomous_revenue_runtime_public_read_blocker": e62_revenue_runtime_state.get("public_read_blocker_status"),
        "current_autonomous_revenue_runtime_next_milestone": e62_revenue_runtime_state.get("recommended_next_milestone"),
        "current_autonomous_revenue_runtime_external_action_allowed": e62_revenue_runtime_state.get("external_action_allowed"),
        "latest_revenue_opportunity_discovery_state": e63_revenue_opportunity_state,
        "current_revenue_opportunity_discovery_status": e63_revenue_opportunity_state.get("opportunity_discovery_status"),
        "current_revenue_opportunity_first_cash_path": e63_revenue_opportunity_state.get("refined_first_cash_path"),
        "current_revenue_opportunity_source_receipt_count": e63_revenue_opportunity_state.get("source_receipt_count"),
        "current_revenue_opportunity_evidence_atom_count": e63_revenue_opportunity_state.get("evidence_atom_count"),
        "current_revenue_opportunity_offer_package": e63_revenue_opportunity_state.get("offer_package_hypothesis"),
        "current_revenue_opportunity_next_milestone": e63_revenue_opportunity_state.get("recommended_next_milestone"),
        "current_revenue_opportunity_external_action_allowed": e63_revenue_opportunity_state.get("external_action_allowed"),
        "latest_dual_axis_revenue_state": e64_dual_axis_revenue_state,
        "current_dual_axis_revenue_status": e64_dual_axis_revenue_state.get("dual_axis_retest_status"),
        "current_dual_axis_best_market_optimal_path": e64_dual_axis_revenue_state.get("best_market_optimal_path"),
        "current_dual_axis_best_ybridge_unique_path": e64_dual_axis_revenue_state.get("best_YBridge_unique_path"),
        "current_dual_axis_selected_first_cash_path": e64_dual_axis_revenue_state.get("selected_final_first_cash_path"),
        "current_dual_axis_top3_offers": e64_dual_axis_revenue_state.get("top3_offer_names"),
        "current_dual_axis_next_milestone": e64_dual_axis_revenue_state.get("recommended_next_milestone"),
        "current_dual_axis_external_action_allowed": e64_dual_axis_revenue_state.get("external_action_allowed"),
        "latest_market_dynamics_model_state": e65_market_dynamics_state,
        "current_market_dynamics_primary_route": e65_market_dynamics_state.get("primary_route"),
        "current_market_dynamics_first_cash_wedge": e65_market_dynamics_state.get("first_cash_wedge"),
        "current_market_dynamics_fallback_route": e65_market_dynamics_state.get("fallback_route"),
        "current_market_dynamics_decision_stability": e65_market_dynamics_state.get("decision_stability"),
        "current_market_dynamics_evidence_quality": e65_market_dynamics_state.get("evidence_quality_limits"),
        "current_market_dynamics_update_triggers": e65_market_dynamics_state.get("update_triggers"),
        "current_market_dynamics_next_milestone": e65_market_dynamics_state.get("next_recommended_milestone"),
        "current_market_dynamics_external_action_allowed": e65_market_dynamics_state.get("external_action_allowed"),
        "latest_model_driven_offer_state": e66_model_driven_offer_state,
        "current_model_driven_offer_status": e66_model_driven_offer_state.get("model_driven_offer_status"),
        "current_model_driven_offer_selected_route": e66_model_driven_offer_state.get("selected_route"),
        "current_model_driven_offer_name": e66_model_driven_offer_state.get("offer_name"),
        "current_model_driven_offer_decision_stability": e66_model_driven_offer_state.get("decision_stability_score"),
        "current_model_driven_offer_evidence_quality": e66_model_driven_offer_state.get("evidence_quality_tier"),
        "current_model_driven_offer_next_milestone": e66_model_driven_offer_state.get("next_recommended_milestone"),
        "current_model_driven_offer_external_action_allowed": e66_model_driven_offer_state.get("external_action_allowed"),
        "latest_external_validation_state": e67_external_validation_state,
        "current_external_validation_primary_route_score": e67_external_validation_state.get("primary_route_external_validation_score"),
        "current_external_validation_highest_EV_level": e67_external_validation_state.get("highest_EV_level"),
        "current_external_validation_non_contact_confidence": e67_external_validation_state.get("non_contact_confidence"),
        "current_external_validation_missing_evidence": e67_external_validation_state.get("missing_evidence"),
        "current_external_validation_owner_gated_next_steps": e67_external_validation_state.get("owner_gated_next_steps"),
        "current_external_validation_next_milestone": e67_external_validation_state.get("next_recommended_milestone"),
        "current_external_validation_external_action_allowed": e67_external_validation_state.get("external_action_allowed"),
        "latest_cieu_route_state": e68_cieu_route_state,
        "current_cieu_route_score": e68_cieu_route_state.get("CIEU_route_score"),
        "current_cieu_highest_EV_level": e68_cieu_route_state.get("CIEU_EV_level"),
        "current_cieu_portfolio_role": e68_cieu_route_state.get("portfolio_role"),
        "current_cieu_product_wedge": e68_cieu_route_state.get("product_wedge_hypothesis"),
        "current_cieu_no_overclaim_policy": e68_cieu_route_state.get("no_overclaim_policy"),
        "current_cieu_next_milestone": e68_cieu_route_state.get("next_recommended_milestone"),
        "current_cieu_external_action_allowed": e68_cieu_route_state.get("external_action_allowed"),
        "latest_ceo_next_action_planning_state": e69_next_action_planning_state,
        "current_ceo_generated_candidate_count": e69_next_action_planning_state.get("generated_candidate_count"),
        "current_ceo_selected_next_action": e69_next_action_planning_state.get("selected_next_action"),
        "current_ceo_next_action_nearest_alternative": e69_next_action_planning_state.get("nearest_alternative"),
        "current_ceo_owner_decision_packet_status": e69_next_action_planning_state.get("owner_decision_packet_status"),
        "current_ceo_next_action_requires_owner_approval": e69_next_action_planning_state.get("requires_owner_approval_for_selected_internal_action"),
        "current_ceo_next_action_external_action_allowed": e69_next_action_planning_state.get("external_action_allowed"),
        "current_ceo_next_action_next_milestone": e69_next_action_planning_state.get("next_recommended_milestone"),
        "latest_ceo_self_bootstrap_state": e70_self_bootstrap_state,
        "current_ceo_capability_gap_count": e70_self_bootstrap_state.get("capability_gap_count"),
        "current_ceo_selected_self_improvement_action": e70_self_bootstrap_state.get("selected_self_bootstrap_action"),
        "current_ceo_generated_codex_job_proposal_id": e70_self_bootstrap_state.get("generated_Codex_job_proposal_id"),
        "current_ceo_can_generate_codex_job_proposals": e70_self_bootstrap_state.get("Codex_job_proposal_schema_status") == "created",
        "current_ceo_can_propose_skill_discovery": e70_self_bootstrap_state.get("skill_boundary_status") == "created_no_install",
        "current_ceo_skill_installation_requires_owner_approval": True,
        "current_ceo_self_bootstrap_use_case_status": e70_self_bootstrap_state.get("L5_use_case_status"),
        "current_ceo_capability_growth_next_milestone": e70_self_bootstrap_state.get("next_recommended_milestone"),
        "current_ceo_self_bootstrap_external_action_allowed": e70_self_bootstrap_state.get("external_action_allowed"),
        "latest_legacy_asset_resurrection_state": e71_legacy_asset_resurrection_state,
        "current_legacy_asset_promoted_count": e71_legacy_asset_resurrection_state.get("promoted_count"),
        "current_legacy_asset_quarantined_count": e71_legacy_asset_resurrection_state.get("quarantined_count"),
        "current_legacy_asset_top_clusters": e71_legacy_asset_resurrection_state.get("top_clusters"),
        "current_legacy_asset_market_model_inputs": e71_legacy_asset_resurrection_state.get("market_model_inputs"),
        "current_legacy_asset_CIEU_module_inputs": e71_legacy_asset_resurrection_state.get("CIEU_module_inputs"),
        "current_legacy_asset_pricing_inputs": e71_legacy_asset_resurrection_state.get("pricing_inputs"),
        "current_legacy_asset_self_bootstrap_inputs": e71_legacy_asset_resurrection_state.get("self_bootstrap_inputs"),
        "current_legacy_asset_provider_promotion_inputs": e71_legacy_asset_resurrection_state.get("provider_promotion_inputs"),
        "current_legacy_asset_next_recommended_milestone": e71_legacy_asset_resurrection_state.get("next_recommended_milestone"),
        "current_legacy_asset_external_action_allowed": e71_legacy_asset_resurrection_state.get("external_action_allowed"),
        "latest_cieu_audit_module_hash_chain_state": e72_cieu_audit_module_state,
        "current_cieu_audit_module_status": e72_cieu_audit_module_state.get("cieu_audit_module_status"),
        "current_cieu_audit_module_k9_context_bound": e72_cieu_audit_module_state.get("K9_CIEU_hash_chain_context_bound"),
        "current_cieu_audit_module_e71_assets_consumed": e72_cieu_audit_module_state.get("E71_promoted_assets_consumed"),
        "current_cieu_audit_module_product_binding_status": e72_cieu_audit_module_state.get("CIEU_Audit_Module_integrated_into_governed_business_operations_blueprint"),
        "current_cieu_audit_module_production_ready": e72_cieu_audit_module_state.get("production_ready"),
        "current_cieu_audit_module_forbidden_claims": e72_cieu_audit_module_state.get("forbidden_claims"),
        "current_cieu_audit_module_residual_gaps": e72_cieu_audit_module_state.get("residual_gaps"),
        "current_cieu_audit_module_next_milestone": e72_cieu_audit_module_state.get("next_recommended_milestone"),
        "current_cieu_audit_module_external_action_allowed": e72_cieu_audit_module_state.get("external_action_allowed"),
        "latest_ecosystem_boundary_lock_state": e73_ecosystem_boundary_lock_state,
        "current_ceo_real_work_highest_ready_level": e73_ecosystem_boundary_lock_state.get("highest_ready_CEO_work_level"),
        "current_ceo_next_allowed_work_class": e73_ecosystem_boundary_lock_state.get("next_allowed_work_class"),
        "current_ceo_L2_readiness_decision": e73_ecosystem_boundary_lock_state.get("L2_readiness_decision"),
        "current_ceo_L3_readiness_decision": e73_ecosystem_boundary_lock_state.get("L3_readiness_decision"),
        "current_ceo_L4_readiness_decision": e73_ecosystem_boundary_lock_state.get("L4_readiness_decision"),
        "current_ceo_L5_readiness_decision": e73_ecosystem_boundary_lock_state.get("L5_readiness_decision"),
        "current_ceo_must_not_rebuild": e73_ecosystem_boundary_lock_state.get("must_not_rebuild"),
        "current_ceo_boundary_lock_e72_proposal_decision": e73_ecosystem_boundary_lock_state.get("E72_proposal_decision"),
        "current_ceo_real_work_next_recommended_milestone": e73_ecosystem_boundary_lock_state.get("next_recommended_milestone"),
        "current_ceo_real_work_external_action_allowed": e73_ecosystem_boundary_lock_state.get("external_action_allowed"),
        "latest_ceo_l2_internal_work_state": e74_l2_internal_work_state,
        "current_ceo_l2_work_status": e74_l2_internal_work_state.get("L2_work_status"),
        "current_ceo_l2_work_deliverable": e74_l2_internal_work_state.get("deliverable_produced"),
        "current_ceo_l2_work_owner_packet_status": e74_l2_internal_work_state.get("owner_facing_packet_status"),
        "current_ceo_l2_work_no_new_wheel_compliance": e74_l2_internal_work_state.get("no_new_wheel_compliance"),
        "current_ceo_l2_work_readiness_movement": e74_l2_internal_work_state.get("readiness_movement"),
        "current_ceo_l2_work_l3_status": e74_l2_internal_work_state.get("L3_status_after_E74"),
        "current_ceo_l2_work_next_recommended_milestone": e74_l2_internal_work_state.get("next_recommended_milestone"),
        "current_ceo_l2_work_external_action_allowed": e74_l2_internal_work_state.get("external_action_allowed"),
        "latest_l3_owner_decision_packet_state": e75_l3_owner_decision_state,
        "current_l3_owner_decision_packet_status": e75_l3_owner_decision_state.get("E75_status"),
        "current_l3_owner_decision_packet_l3_executed": e75_l3_owner_decision_state.get("L3_executed"),
        "current_l3_owner_decision_packet_owner_approval_status": e75_l3_owner_decision_state.get("owner_approval_status"),
        "current_l3_owner_decision_packet_source_categories": e75_l3_owner_decision_state.get("proposed_source_categories"),
        "current_l3_owner_decision_packet_forbidden_actions": e75_l3_owner_decision_state.get("forbidden_actions"),
        "current_l3_owner_decision_requested": e75_l3_owner_decision_state.get("decision_requested_from_owner"),
        "current_l3_owner_decision_if_owner_approves": e75_l3_owner_decision_state.get("if_owner_approves"),
        "current_l3_owner_decision_L4_ready": e75_l3_owner_decision_state.get("L4_ready"),
        "current_l3_owner_decision_L5_ready": e75_l3_owner_decision_state.get("L5_ready"),
        "current_l3_owner_decision_next_milestone": e75_l3_owner_decision_state.get("next_recommended_milestone"),
        "current_l3_owner_decision_external_action_allowed": e75_l3_owner_decision_state.get("external_action_allowed"),
        "latest_e76_e77_l3_lineage_decision_state": e76_e77_l3_lineage_decision_state,
        "current_e76_e77_status": e76_e77_l3_lineage_decision_state.get("E76_E77_status"),
        "current_e76_e77_phase_b_authorized": e76_e77_l3_lineage_decision_state.get("phase_B_execution_authorized"),
        "current_e76_e77_l3_executed": e76_e77_l3_lineage_decision_state.get("did_execute_L3"),
        "current_e76_e77_owner_decision_status": e76_e77_l3_lineage_decision_state.get("owner_decision_status"),
        "current_e76_e77_prior_public_read_lineage_count": e76_e77_l3_lineage_decision_state.get("prior_public_read_lineage_count"),
        "current_e76_e77_lineage_correction": e76_e77_l3_lineage_decision_state.get("why_not_first_external_read_only_research"),
        "current_e76_e77_new_after_E73_E74_E75": e76_e77_l3_lineage_decision_state.get("what_is_genuinely_new_after_E73_E74_E75"),
        "current_e76_e77_next_milestone": e76_e77_l3_lineage_decision_state.get("next_milestone"),
        "current_e76_e77_L4_ready": e76_e77_l3_lineage_decision_state.get("L4_ready"),
        "current_e76_e77_L5_ready": e76_e77_l3_lineage_decision_state.get("L5_ready"),
        "current_e76_e77_external_action_allowed": e76_e77_l3_lineage_decision_state.get("external_action_allowed"),
        "latest_e78_l3_research_state": e78_l3_research_state,
        "current_e78_l3_research_status": e78_l3_research_state.get("E78_status"),
        "current_e78_l3_executed": e78_l3_research_state.get("did_execute_L3"),
        "current_e78_owner_approval_explicit": e78_l3_research_state.get("owner_approval_explicit"),
        "current_e78_public_read_source_count": e78_l3_research_state.get("source_count"),
        "current_e78_source_categories_used": e78_l3_research_state.get("source_categories_used"),
        "current_e78_buyer_problem_finding": e78_l3_research_state.get("buyer_problem_finding"),
        "current_e78_product_offer_finding": e78_l3_research_state.get("product_offer_finding"),
        "current_e78_CIEU_audit_module_finding": e78_l3_research_state.get("CIEU_audit_module_finding"),
        "current_e78_pricing_packaging_finding": e78_l3_research_state.get("pricing_packaging_finding"),
        "current_e78_L4_owner_decision_packet_preparation_justified": e78_l3_research_state.get("L4_owner_decision_packet_preparation_justified"),
        "current_e78_L4_execution_ready": e78_l3_research_state.get("L4_execution_ready"),
        "current_e78_L5_ready": e78_l3_research_state.get("L5_ready"),
        "current_e78_next_recommended_milestone": e78_l3_research_state.get("next_recommended_milestone"),
        "current_e78_external_action_allowed": e78_l3_research_state.get("external_action_allowed"),
        "latest_e79_strategic_judgment_state": e79_strategic_judgment_state,
        "current_e79_status": e79_strategic_judgment_state.get("E79_status"),
        "current_e79_selected_strategic_thesis": e79_strategic_judgment_state.get("selected_strategic_thesis"),
        "current_e79_backup_thesis_id": e79_strategic_judgment_state.get("backup_thesis_id"),
        "current_e79_target_buyer": e79_strategic_judgment_state.get("target_buyer"),
        "current_e79_trigger_event": e79_strategic_judgment_state.get("trigger_event"),
        "current_e79_frontstage_message": e79_strategic_judgment_state.get("frontstage_message"),
        "current_e79_backstage_CIEU_role": e79_strategic_judgment_state.get("backstage_CIEU_role"),
        "current_e79_quality_gate_passed": e79_strategic_judgment_state.get("quality_gate_passed"),
        "current_e79_L4_packet_status": e79_strategic_judgment_state.get("L4_packet_status"),
        "current_e79_L4_execution_authorized": e79_strategic_judgment_state.get("L4_execution_authorized"),
        "current_e79_next_recommended_milestone": e79_strategic_judgment_state.get("next_recommended_milestone"),
        "current_e79_external_action_allowed": e79_strategic_judgment_state.get("external_action_allowed"),
        "latest_e80_discovery_first_cognitive_activation_state": e80_cognitive_activation_state,
        "current_e80_status": e80_cognitive_activation_state.get("E80_R2_status"),
        "current_e80_files_inventoried": e80_cognitive_activation_state.get("files_inventoried"),
        "current_e80_generated_artifacts_indexed": e80_cognitive_activation_state.get("generated_artifacts_indexed"),
        "current_e80_python_symbols_indexed": e80_cognitive_activation_state.get("python_symbols_indexed"),
        "current_e80_tests_indexed": e80_cognitive_activation_state.get("tests_indexed"),
        "current_e80_capabilities_discovered": e80_cognitive_activation_state.get("capabilities_discovered"),
        "current_e80_repository_discovered_not_prompt_hinted_count": e80_cognitive_activation_state.get("repository_discovered_not_prompt_hinted_count"),
        "current_e80_prompt_hinted_unverified_count": e80_cognitive_activation_state.get("prompt_hinted_unverified_count"),
        "current_e80_activation_state_counts": e80_cognitive_activation_state.get("activation_state_counts"),
        "current_e80_high_value_capabilities_activated": e80_cognitive_activation_state.get("high_value_capabilities_activated"),
        "current_e80_sixD_field_brain_status": e80_cognitive_activation_state.get("sixD_field_brain_status"),
        "current_e80_KG_long_memory_status": e80_cognitive_activation_state.get("KG_long_memory_status"),
        "current_e80_pre_action_CIEU_prediction_status": e80_cognitive_activation_state.get("pre_action_CIEU_prediction_status"),
        "current_e80_counterfactual_comparison_status": e80_cognitive_activation_state.get("counterfactual_comparison_status"),
        "current_e80_legacy_commercial_assets_status": e80_cognitive_activation_state.get("legacy_commercial_assets_status"),
        "current_e80_intelligence_gate_v2_passed": e80_cognitive_activation_state.get("CEO_intelligence_gate_v2_passed"),
        "current_e80_live_cognition_loop_demo_decision": e80_cognitive_activation_state.get("live_cognition_loop_demo_decision"),
        "current_e80_what_not_to_do_next": e80_cognitive_activation_state.get("what_not_to_do_next"),
        "current_e80_next_recommended_milestone": e80_cognitive_activation_state.get("next_recommended_milestone"),
        "current_e80_external_action_allowed": e80_cognitive_activation_state.get("external_action_allowed"),
        "current_e80_L4_execution_authorized": e80_cognitive_activation_state.get("L4_execution_authorized"),
        "current_e80_L5_ready": e80_cognitive_activation_state.get("L5_ready"),
        "latest_e81_ceo_cognitive_os_state": e81_cognitive_os_state,
        "current_e81_status": e81_cognitive_os_state.get("E81_status"),
        "current_e81_cognitive_OS_contract_installed": e81_cognitive_os_state.get("cognitive_OS_contract_installed_in_bridge_labs"),
        "current_e81_mandatory_stage_count": e81_cognitive_os_state.get("mandatory_stage_count"),
        "current_e81_YstarGov_sync_packet_exists": e81_cognitive_os_state.get("YstarGov_sync_packet_exists"),
        "current_e81_YstarGov_mutated": e81_cognitive_os_state.get("YstarGov_mutated"),
        "current_e81_future_CEO_work_requires_pre_action_packet": e81_cognitive_os_state.get("future_CEO_work_requires_pre_action_packet"),
        "current_e81_future_CEO_work_requires_post_action_residual": e81_cognitive_os_state.get("future_CEO_work_requires_post_action_residual"),
        "current_e81_bypass_allowed": e81_cognitive_os_state.get("bypass_allowed"),
        "current_e81_bypass_result": e81_cognitive_os_state.get("bypass_result"),
        "current_e81_enforcement_mode": e81_cognitive_os_state.get("current_enforcement_mode"),
        "current_e81_YstarGov_sync_status": e81_cognitive_os_state.get("YstarGov_sync_status"),
        "current_e81_if_CEO_bypasses_loop": e81_cognitive_os_state.get("if_CEO_bypasses_loop"),
        "current_e81_validator_status": e81_cognitive_os_state.get("validator_status"),
        "current_e81_bypass_fixture_results": e81_cognitive_os_state.get("bypass_fixture_results"),
        "current_e81_live_internal_decision_result": e81_cognitive_os_state.get("live_internal_decision_result"),
        "current_e81_selected_next_action": e81_cognitive_os_state.get("selected_next_action"),
        "current_e81_external_action_allowed": e81_cognitive_os_state.get("external_action_allowed"),
        "current_e81_L4_execution_authorized": e81_cognitive_os_state.get("L4_execution_authorized"),
        "current_e81_L5_ready": e81_cognitive_os_state.get("L5_ready"),
        "latest_e82_ceo_cognitive_os_sync_state": e82_cognitive_os_sync_state,
        "current_e82_status": e82_cognitive_os_sync_state.get("E82_status"),
        "current_e82_enforcement_mode": e82_cognitive_os_sync_state.get("current_enforcement_mode"),
        "current_e82_YstarGov_synced": e82_cognitive_os_sync_state.get("YstarGov_synced"),
        "current_e82_YstarGov_module_path": e82_cognitive_os_sync_state.get("YstarGov_module_path"),
        "current_e82_YstarGov_tests_path": e82_cognitive_os_sync_state.get("YstarGov_tests_path"),
        "current_e82_direct_YstarGov_import_used": e82_cognitive_os_sync_state.get("direct_YstarGov_import_used"),
        "current_e82_bypass_status": e82_cognitive_os_sync_state.get("bypass_status"),
        "current_e82_future_CEO_work_requires_pre_action_packet": e82_cognitive_os_sync_state.get("future_CEO_work_requires_pre_action_packet"),
        "current_e82_future_CEO_work_requires_post_action_residual": e82_cognitive_os_sync_state.get("future_CEO_work_requires_post_action_residual"),
        "current_e82_if_CEO_bypasses_loop": e82_cognitive_os_sync_state.get("if_CEO_bypasses_loop"),
        "current_e82_L4_execution_authorized": e82_cognitive_os_sync_state.get("L4_execution_authorized"),
        "current_e82_L5_ready": e82_cognitive_os_sync_state.get("L5_ready"),
        "current_e82_next_recommended_milestone": e82_cognitive_os_sync_state.get("next_recommended_milestone"),
        "latest_e83_autoguidance_semantics_state": e83_autoguidance_state,
        "current_e83_discovered_auto_guidance_lineage": e83_autoguidance_state.get("discovered_auto_guidance_lineage"),
        "current_e83_actual_decision_vocabulary": e83_autoguidance_state.get("actual_decision_vocabulary"),
        "current_e83_E82_semantics_correction": e83_autoguidance_state.get("E82_semantics_correction"),
        "current_e83_YstarGov_validator_supports_correct_path_guidance": e83_autoguidance_state.get("Y_star_gov_validator_supports_correct_path_guidance"),
        "current_e83_correct_L4_flow": e83_autoguidance_state.get("correct_L4_flow"),
        "current_e83_correct_L5_flow": e83_autoguidance_state.get("correct_L5_flow"),
        "current_e83_next_recommended_milestone": e83_autoguidance_state.get("next_milestone"),
        "current_e83_external_action_allowed": e83_autoguidance_state.get("external_action_allowed"),
        "current_e83_L4_execution_authorized": e83_autoguidance_state.get("L4_execution_authorized"),
        "current_e83_L5_ready": e83_autoguidance_state.get("L5_ready"),
        "commercial_assets": _commercial_assets(),
        "read_model_role": "active read context assembled from wisdom, working memory status, latest KG/brain/read-model artifacts, directives, commercial assets, and E50B current decision state",
        "no_external_action": True,
    }
