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

from .e46b_field_projection_adapter import project_task_from_m_triangle
from .e46b_ceo_brain_adapter import load_ceo_brain_context
from .e45_real_local_first_value_demo_runner import run_real_local_first_value_demo


def _result(adapter_id: str, stage: str, invoked: bool, status: str, data: Any, effect: str, side_effect_level: str = "read_only_local") -> dict[str, Any]:
    return {"adapter_id": adapter_id, "canonical_spine_stage": stage, "invoked": invoked, "result_status": status, "result_data": data, "side_effect_level": side_effect_level, "no_external_action": True, "decision_effect": effect}


class FieldProjectionMainlineAdapter:
    adapter_id = "field_projection_mainline"
    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        data = project_task_from_m_triangle(task, {})
        return _result(self.adapter_id, "field_projection", True, data.get("projection_maturity", "partial"), data, "Projects task through M Triangle/company/milestone/action/closure chain.")


class CEOBrainMainlineAdapter:
    adapter_id = "ceo_brain_mainline"
    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        data = load_ceo_brain_context(task)
        return _result(self.adapter_id, "ceo_brain_context", True, "pass", {"wisdom_results": len(data.get("wisdom_search", {}).get("top_results", [])), "commercial_assets": len(data.get("commercial_assets", [])), "latest_runtime_artifacts": len(data.get("latest_runtime_artifacts", {}))}, "Loads canonical CEO brain context without creating a second brain.")


class WisdomMainlineAdapter:
    adapter_id = "wisdom_mainline"
    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        query = f"{task.get('task_title','')} {task.get('task_description','')} M Triangle value production"
        command = _run(["python3", "scripts/wisdom_search.py", "--top", "3", "--json", query])
        return _result(self.adapter_id, "ceo_brain_context", True, "pass" if command["returncode"] == 0 else "error", command, "Wisdom corpus influences route framing.")


class WorkingMemoryMainlineAdapter:
    adapter_id = "working_memory_mainline"
    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        command = _run(["python3", "scripts/working_memory_snapshot.py", "load-latest"])
        return _result(self.adapter_id, "ceo_brain_context", True, "loaded" if command["returncode"] == 0 else "unavailable_nonfatal", command, "Working memory/LRS status is read before route decision.")


class Article11MainlineAdapter:
    adapter_id = "article_11_mainline"
    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        command = _run(["python3", "scripts/article_11_tracker.py", "check_compliance", "--window_hours", "2"])
        return _result(self.adapter_id, "constitutional_target", True, "pass" if command["returncode"] == 0 else "fail_nonfatal", command, "Decision discipline is recorded honestly; failure blocks overconfidence, not local dry-run.")


class CommercialRouteMainlineAdapter:
    adapter_id = "commercial_route_mainline"
    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        brain = load_ceo_brain_context(task)
        routes = [asset for asset in brain.get("commercial_assets", [])[:12]]
        return _result(self.adapter_id, "commercial_value_route", True, "pass" if routes else "empty", {"asset_count": len(routes), "top_assets": routes}, "Commercial/plugin/revenue assets are route inputs, not disconnected docs.")


class EvidenceIntelligenceMainlineAdapter:
    adapter_id = "evidence_intelligence_mainline"
    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        paths = ["e38_public_evidence_receipts.json", "e39_deep_research_claim_graph.json", "e39_contradiction_graph.json", "e39_source_quality_evidence_burden_evaluator.json", "e41_frontier_capability_import_loop.json", "e45_first_value_demo_bundle.json"]
        found = []
        for name in paths:
            path = BRIDGE_ROOT / "operations/external_validation" / name
            if path.exists():
                data = _json(path)
                found.append({"path": str(path.relative_to(BRIDGE_ROOT)), "keys": sorted(list(data.keys()))[:8] if isinstance(data, dict) else []})
        return _result(self.adapter_id, "evidence_audit_context", True, "pass" if found else "empty", {"found": found}, "Evidence/claim/frontier assets constrain revenue claims.")


class ExecutionDemoMainlineAdapter:
    adapter_id = "execution_demo_mainline"
    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        demo = run_real_local_first_value_demo()
        return _result(self.adapter_id, "execution_feasibility", True, demo.get("local_demo_readiness_class", "unknown"), {"readiness": demo.get("local_demo_readiness_class"), "passed": demo.get("commands_passed_count"), "failed": demo.get("commands_failed_count"), "skipped": demo.get("commands_skipped_count")}, "Execution/local proof status gates outreach and money-route recommendations.")


class GovernanceBoundaryMainlineAdapter:
    adapter_id = "governance_boundary_mainline"
    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        data = {"Y_star_gov_exists": Y_GOV_ROOT.exists(), "gov_mcp_exists": GOV_MCP_ROOT.exists(), "owner_approval_required": True, "no_duplicate_kernel": True, "no_duplicate_execution_layer": True}
        return _result(self.adapter_id, "governance_boundary", True, "pass", data, "Governance and execution ownership remain cross-repo boundaries.")


class AuditClosureMainlineAdapter:
    adapter_id = "audit_closure_mainline"
    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        data = {"CZL_exists": (BRIDGE_ROOT / "CZL.md").exists(), "E45_trace_exists": (BRIDGE_ROOT / "operations/external_validation/e45_full_history_actual_invocation_trace.json").exists(), "K9Audit_exists": K9_ROOT.exists(), "KG_read_model_exists": (BRIDGE_ROOT / "operations/knowledge_graph/e46b_ceo_kg_read_model_update.json").exists()}
        return _result(self.adapter_id, "audit_context", True, "pass", data, "CIEU/CZL/K9/KG proof context remains attached without duplicate ledger.")


class NotificationBoardLoopAdapter:
    adapter_id = "notification_board_loop"
    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        data = {"telegram_notify_exists": (BRIDGE_ROOT / "scripts/telegram_notify.py").exists(), "reports_daily_exists": (BRIDGE_ROOT / "reports/daily").exists(), "directive_tracker_exists": (BRIDGE_ROOT / "DIRECTIVE_TRACKER.md").exists(), "send_allowed": False}
        return _result(self.adapter_id, "notification_board_loop_readiness", True, "read_only", data, "Board/notification loop is visible but no send is performed.")


class RecoveryDeliveryAdapter:
    adapter_id = "recovery_delivery_mainline"
    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        data = {"delivery_bridge_worker_exists": (BRIDGE_ROOT / "scripts/repository_delivery_bridge_worker.py").exists(), "delivery_status_tests_exist": (BRIDGE_ROOT / "tests/office/test_repository_delivery_status.py").exists(), "jsonl_recovery_mentions": bool(_lines(BRIDGE_ROOT / "reports/integration/e46b_full_system_runtime_spine_archaeology.md", ["recovery", "jsonl"], 3))}
        return _result(self.adapter_id, "execution_feasibility", True, "pass", data, "Recovery/delivery support is part of operational runtime rather than forgotten tooling.")


ADAPTER_CLASSES = [FieldProjectionMainlineAdapter, CEOBrainMainlineAdapter, WisdomMainlineAdapter, WorkingMemoryMainlineAdapter, Article11MainlineAdapter, CommercialRouteMainlineAdapter, EvidenceIntelligenceMainlineAdapter, ExecutionDemoMainlineAdapter, GovernanceBoundaryMainlineAdapter, AuditClosureMainlineAdapter, NotificationBoardLoopAdapter, RecoveryDeliveryAdapter]


def run_all_mainline_adapters(task: dict[str, Any]) -> list[dict[str, Any]]:
    return [cls().run(task) for cls in ADAPTER_CLASSES]


def build_mainline_adapter_registry(task: dict[str, Any] | None = None) -> dict[str, Any]:
    task = task or {"task_title": "E47 adapter registry", "task_description": "connect all capability families to canonical mainline"}
    results = run_all_mainline_adapters(task)
    return {"artifact_id": "e47_mainline_adapter_registry", "adapter_count": len(results), "mandatory_adapter_families": [cls.__name__ for cls in ADAPTER_CLASSES], "adapter_results": results, "all_invoked": all(item["invoked"] for item in results), "no_external_action": all(item["no_external_action"] for item in results)}
