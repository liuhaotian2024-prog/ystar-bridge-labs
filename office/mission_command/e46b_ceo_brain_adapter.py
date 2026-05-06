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
        "commercial_assets": _commercial_assets(),
        "read_model_role": "active read context assembled from wisdom, working memory status, latest KG/brain/read-model artifacts, directives, commercial assets, and E50B current decision state",
        "no_external_action": True,
    }
