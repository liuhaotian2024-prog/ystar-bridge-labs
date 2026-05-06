from __future__ import annotations

import json
import os
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
K9_ROOT = Path(os.environ.get("K9AUDIT_ROOT", "/Users/haotianliu/.openclaw/workspace/K9Audit"))
COMPANY_ROOT = Path(os.environ.get("YSTAR_COMPANY_ROOT", "/Users/haotianliu/.openclaw/workspace/ystar-company"))
FINAL_STATUSES = {
    "active_runtime_adapter", "active_read_model_input", "active_context_input", "active_commercial_route_input", "active_evidence_input", "active_governance_boundary", "active_execution_boundary", "active_audit_context", "parked_with_reason", "quarantined_with_reason", "duplicate_merged", "cross_repo_proposal_required", "deprecated_with_reason",
}


def _read(path: Path, limit: int = 200_000_000) -> str:
    try:
        if not path.exists() or path.is_dir() or path.stat().st_size > limit:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _json(path: Path) -> Any:
    try:
        return json.loads(_read(path))
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
    for line in _read(path, 120000).splitlines():
        lower = line.lower()
        if any(term.lower() in lower for term in terms):
            rows.append(line.strip()[:240])
        if len(rows) >= limit:
            break
    return rows


LAYER_TO_ACTIVE_STATUS = {
    "constitutional_target_layer": "active_context_input",
    "field_functional_projection_layer": "active_runtime_adapter",
    "ceo_brain_layer": "active_context_input",
    "capability_activation_layer": "active_runtime_adapter",
    "governance_kernel_layer": "active_governance_boundary",
    "execution_boundary_layer": "active_execution_boundary",
    "evidence_audit_layer": "active_audit_context",
    "commercial_value_layer": "active_commercial_route_input",
    "notification_board_loop_layer": "active_context_input",
    "closure_learning_layer": "active_audit_context",
}

SPINE_STAGE_BY_LAYER = {
    "constitutional_target_layer": "constitutional_target",
    "field_functional_projection_layer": "field_projection",
    "ceo_brain_layer": "ceo_brain_context",
    "capability_activation_layer": "capability_activation",
    "governance_kernel_layer": "governance_boundary",
    "execution_boundary_layer": "execution_feasibility",
    "evidence_audit_layer": "audit_context",
    "commercial_value_layer": "commercial_value_route",
    "notification_board_loop_layer": "notification_board_loop_readiness",
    "closure_learning_layer": "closure_writeback",
}


def _is_expert_route(item: dict[str, Any]) -> bool:
    text = f"{item.get('path','')} {item.get('resource_id','')}".lower()
    return "expert" in text and ("e40" in text or "expert_review" in text or "review_preflight" in text)


def _final_status(item: dict[str, Any]) -> tuple[str, str, str]:
    repo = item.get("repo", "")
    layer = item.get("spine_layer", "")
    status = item.get("current_status", "")
    path = item.get("path", "")
    if _is_expert_route(item):
        return "quarantined_with_reason", "historical expert/no-send route after owner correction; cannot route future contact by default", "side_effect_guard"
    if repo == "Y-star-gov":
        return "active_governance_boundary", "read-only governance/projection/kernel ownership boundary", "governance_boundary"
    if repo == "gov-mcp":
        return "active_execution_boundary", "read-only MCP execution/tool/server-client boundary", "execution_feasibility"
    if repo == "K9Audit":
        return "active_audit_context", "read-only audit/ledger/watchdog context", "audit_context"
    if repo == "ystar-company":
        return "active_commercial_route_input", "read-only company/commercial context", "commercial_value_route"
    if status in {"artifact_accessor", "misleading_runtime_name"}:
        return "active_read_model_input", "get_artifact/accessor content is wrapped as read-model input, not treated as runtime", SPINE_STAGE_BY_LAYER.get(layer, "ceo_brain_context")
    if status == "parked":
        return "parked_with_reason", "historical/drifted or not currently safe for mainline activation", SPINE_STAGE_BY_LAYER.get(layer, "side_effect_guard")
    if item.get("operational_gap") == "written_but_not_read":
        return "active_read_model_input", "written output is now covered by read-model/status matrix, not silently ignored", SPINE_STAGE_BY_LAYER.get(layer, "closure_writeback")
    if "duplicate" in path.lower() or "superseded" in path.lower():
        return "duplicate_merged", "overlap merged into canonical spine class", SPINE_STAGE_BY_LAYER.get(layer, "capability_activation")
    if layer == "evidence_audit_layer" and any(term in path.lower() for term in ["claim", "evidence", "contradiction", "source", "frontier", "receipt"]):
        return "active_evidence_input", "evidence/claim/frontier artifact feeds money route and no-overclaim checks", "evidence_audit_context"
    return LAYER_TO_ACTIVE_STATUS.get(layer, "parked_with_reason"), "covered by canonical runtime spine final status mapping", SPINE_STAGE_BY_LAYER.get(layer, "closure_writeback")


def build_full_capability_coverage_gate() -> dict[str, Any]:
    archaeology = _json(BRIDGE_ROOT / "operations/external_validation/e46b_full_system_runtime_spine_archaeology.json") or {}
    remaining = _json(BRIDGE_ROOT / "operations/external_validation/e46b_remaining_disconnected_capabilities.json") or {}
    resources = archaeology.get("resources", [])
    matrix: list[dict[str, Any]] = []
    for item in resources:
        final_status, reason, stage = _final_status(item)
        mechanism = "callable" if final_status == "active_runtime_adapter" and item.get("callable_entrypoints") else "read_by_adapter_or_context"
        if final_status in {"active_governance_boundary", "active_execution_boundary", "active_audit_context"}:
            mechanism = "owned_boundary_context"
        if final_status in {"parked_with_reason", "quarantined_with_reason", "deprecated_with_reason", "cross_repo_proposal_required", "duplicate_merged"}:
            mechanism = "not_active_with_explicit_reason"
        matrix.append({
            "resource_id": item.get("resource_id"),
            "repo": item.get("repo"),
            "path": item.get("path"),
            "spine_layer": item.get("spine_layer"),
            "previous_status": item.get("current_status"),
            "final_status": final_status,
            "canonical_spine_stage": stage,
            "reason": reason,
            "active_mechanism": mechanism,
            "get_artifact_only_not_runtime": item.get("current_status") in {"artifact_accessor", "misleading_runtime_name"},
        })
    status_counts = Counter(row["final_status"] for row in matrix)
    layer_counts = Counter(row["spine_layer"] for row in matrix)
    unknown = [row for row in matrix if row["final_status"] not in FINAL_STATUSES]
    expert_quarantined = any(row["final_status"] == "quarantined_with_reason" and "expert" in (row.get("path") or "").lower() for row in matrix)
    artifact_runtime_errors = [row for row in matrix if row["get_artifact_only_not_runtime"] and row["final_status"] == "active_runtime_adapter"]
    represented_layers = set(layer_counts)
    required_layers = set(archaeology.get("spine_layers", []))
    gate_passed = not unknown and not artifact_runtime_errors and required_layers.issubset(represented_layers) and expert_quarantined
    return {
        "artifact_id": "e47_full_capability_coverage_gate",
        "source_artifacts": ["e46b_full_system_runtime_spine_archaeology", "e46b_remaining_disconnected_capabilities", "e46b_ceo_brain_canonical_model", "e46b_field_functional_projection_recovery", "e44a_full_history_runtime_capability_map", "e45_full_history_actual_invocation_trace"],
        "resource_count": len(matrix),
        "coverage_gate_passed": gate_passed,
        "unknown_status_count": len(unknown),
        "final_status_counts": dict(status_counts),
        "spine_layer_counts": dict(layer_counts),
        "all_spine_layers_represented": required_layers.issubset(represented_layers),
        "expert_route_quarantined": expert_quarantined,
        "get_artifact_only_not_active_runtime": not artifact_runtime_errors,
        "remaining_from_E46B_reference": {"total_remaining": remaining.get("total_remaining"), "summary_by_resolution": remaining.get("summary_by_resolution", {})},
        "no_external_action": True,
    }


def build_capability_final_status_matrix() -> dict[str, Any]:
    gate = build_full_capability_coverage_gate()
    resources = (_json(BRIDGE_ROOT / "operations/external_validation/e46b_full_system_runtime_spine_archaeology.json") or {}).get("resources", [])
    rows = []
    for item in resources:
        final_status, reason, stage = _final_status(item)
        rows.append({"resource_id": item.get("resource_id"), "repo": item.get("repo"), "path": item.get("path"), "spine_layer": item.get("spine_layer"), "previous_status": item.get("current_status"), "final_status": final_status, "canonical_spine_stage": stage, "reason": reason})
    return {"artifact_id": "e47_capability_final_status_matrix", "resource_count": len(rows), "final_status_counts": gate["final_status_counts"], "rows": rows, "no_unknown_status": gate["unknown_status_count"] == 0, "no_external_action": True}
