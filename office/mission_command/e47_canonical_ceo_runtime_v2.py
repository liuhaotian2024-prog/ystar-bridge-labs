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

from .e42_task_capability_matcher import match_task_to_capabilities
from .e44a_ceo_cognition_cascade_runtime import run_ceo_cognition_cascade
from .e46b_canonical_ceo_operating_runtime import run_canonical_ceo_operating_runtime
from .e47_full_capability_coverage_gate import build_full_capability_coverage_gate
from .e47_mainline_integration_adapters import build_mainline_adapter_registry, run_all_mainline_adapters


def _side_effect_report() -> dict[str, bool]:
    return {"customer_contact": False, "expert_contact": False, "human_identification": False, "scraping": False, "send": False, "publish": False, "form_submission": False, "login": False, "provider_api_execution": False, "internet_install": False, "payment": False, "secret_use": False}


def _route_matrix(runtime: dict[str, Any]) -> list[dict[str, Any]]:
    base = [
        ("gov_mcp_ystar_local_proof", "AI engineer / local MCP user", "gov-mcp + Y-star-gov local proof packet", "trust in agent actions", "help/status/demo/docs", "server/client start and doctor closure", "partial", "hours-days", "not paid by itself", "low", "low", "medium", "low", "medium", "depends on doctor/server blockers", "harden_first"),
        ("governed_agent_action_proof_packet", "AI engineer / agent team", "Governed Agent Action Proof Packet", "make allow/deny governance legible", "E45 bundle + docs + demos", "server/client closure and owner-approved trial script", "ready_for_owner_review", "days", "days-weeks after approval", "low-medium", "low", "medium", "low", "medium", "depends on local blockers", "harden_first"),
        ("claude_desktop_mcpb_packaging", "Claude Desktop / MCP power user", "MCPB/plugin wrapper", "easy install", "plugin/commercial assets", "packaging closure", "not verified", "days-weeks", "weeks", "medium", "medium", "medium", "medium", "medium", "depends on packaging", "package_first"),
        ("ystar_claude_code_plugin_marketplace", "Claude Code user", "Y*gov Claude Code plugin", "governed coding actions", "historical plugin/pricing assets", "marketplace packaging/publish approval", "not verified", "weeks", "weeks", "medium-high", "medium", "medium", "high", "medium", "requires publish/approval", "parked"),
        ("ai_agent_bug_bounty_service", "AI tooling teams", "bug bounty / agent risk service", "find unsafe agent behavior", "sales/bug bounty concepts", "offer/test cases/proof", "not verified", "weeks", "weeks", "medium", "high", "high", "medium", "high", "needs external validation", "parked"),
        ("workflow_resale_n8n_czl", "SMB ops buyer", "workflow resale with CZL", "automated process control", "workflow resale assets", "packaged workflow and proof", "not verified", "weeks", "weeks", "medium", "medium", "medium", "medium", "high", "weak current proof", "parked"),
        ("enterprise_compliance_pilot", "enterprise AI governance buyer", "compliance pilot", "auditability/trust", "enterprise/governance assets", "credible case study and buyer proof", "not verified", "weeks-months", "months", "high", "high", "high", "high", "medium-high", "requires buyer trust", "parked"),
        ("k9audit_causal_audit_proof", "agent platform builder", "K9Audit causal audit proof", "causal traceability", "K9/CIEU context", "integration proof", "read-only context", "weeks", "weeks", "medium", "medium", "medium", "medium", "medium", "K9 integration not active", "parked"),
        ("bridge_labs_agent_company_case_study", "agent-company builder", "Bridge Labs runtime proof/case study", "operating an AI agent company", "E42-E47 artifacts", "readable case packaging", "strong internal proof", "days-weeks", "weeks", "medium", "medium", "medium", "medium", "medium", "publish approval required", "package_first"),
        ("consulting_advisory_proof_packet", "founder / AI ops lead", "paid setup/advisory proof packet", "adopt governed agents", "proof packet + runtime spine", "service scope and owner-approved outreach", "partial", "days", "days-weeks", "low-medium", "medium", "medium", "medium", "medium", "needs exact offer and no-overclaim wording", "package_first"),
        ("paid_setup_implementation_service", "local AI team", "paid implementation setup", "hands-on install/config", "gov-mcp docs + proof packet", "server/client closure", "partial", "days", "days-weeks", "medium", "medium", "medium", "medium", "medium", "depends on server/client proof", "harden_first"),
        ("commercial_asset_surfaced_route", "developer-led growth audience", "developer-led proof bundle", "quick comprehension", "commercial assets from CEO brain", "packaging/pricing", "partial", "days-weeks", "weeks", "medium", "medium", "medium", "medium", "medium", "depends on selected package", "package_first"),
    ]
    rows = []
    for route in base:
        keys = ["route_id", "buyer", "value_object", "pain_solved", "current_assets", "missing_assets", "local_proof_status", "time_to_first_user", "time_to_paid_signal", "execution_complexity", "owner_burden", "evidence_burden", "overclaim_risk", "revenue_potential", "dependency_on_unresolved_local_blockers", "recommended_action"]
        row = dict(zip(keys, route))
        row["credibility_risk"] = "medium" if row["recommended_action"] != "parked" else "high"
        rows.append(row)
    return rows


def run_canonical_ceo_runtime_v2(task: dict[str, Any], mode: str = "local_dry_run") -> dict[str, Any]:
    gate = build_full_capability_coverage_gate()
    adapters = run_all_mainline_adapters(task)
    e46b = run_canonical_ceo_operating_runtime(task, mode=mode)
    matches = match_task_to_capabilities(task.get("task_description", ""), top_n=12)
    cascade = run_ceo_cognition_cascade(task)
    matrix = _route_matrix(e46b)
    selected = next(row for row in matrix if row["route_id"] == "governed_agent_action_proof_packet")
    route_decision = {"selected_route_id": selected["route_id"], "selected_value_object": selected["value_object"], "selected_recommended_action": selected["recommended_action"], "next_recommended_milestone": "E48_gov_mcp_server_client_demo_closure", "why": "Fastest credible revenue-adjacent path is the proof packet service/wedge, but full runtime still sees gov-mcp server/client and Y-star-gov doctor blockers before outreach or paid-signal claims."}
    return {
        "artifact_id": "e47_canonical_runtime_v2_smoke_result",
        "task": task,
        "mode": mode,
        "coverage_gate": {"passed": gate["coverage_gate_passed"], "unknown_status_count": gate["unknown_status_count"], "resource_count": gate["resource_count"]},
        "mandatory_adapter_results": adapters,
        "mandatory_adapter_count": len(adapters),
        "all_mandatory_adapters_invoked": all(item["invoked"] for item in adapters),
        "e46b_runtime_route": e46b.get("route_decision", {}),
        "e42_match_count": len(matches),
        "e44a_cascade_stage_count": len(cascade.get("stages", [])),
        "money_route_matrix": matrix,
        "route_decision": route_decision,
        "side_effect_report": _side_effect_report(),
        "closure_packet": {"coverage_gate_passed": gate["coverage_gate_passed"], "route_decision_produced": True, "owner_approval_required_before_external_action": True, "no_external_action": True},
        "next_projection": "close server/client demo and doctor blockers, then re-evaluate owner-approved external attempt",
        "no_external_action": True,
    }


def build_money_route_retest(task: dict[str, Any] | None = None) -> dict[str, Any]:
    task = task or {"task_title": "E47 money route retest", "task_description": "What is the shortest credible path for Y*Bridge Labs to make real money or obtain the strongest near-term real user / usage / paid signal, using existing assets and without overclaiming?"}
    runtime = run_canonical_ceo_runtime_v2(task)
    matrix = runtime["money_route_matrix"]
    selected = next(row for row in matrix if row["route_id"] == runtime["route_decision"]["selected_route_id"])
    return {"artifact_id": "e47_money_route_runtime_result", "coverage_gate_passed_before_retest": runtime["coverage_gate"]["passed"], "runtime_result": runtime, "route_matrix": matrix, "selected_path": selected, "parked_or_rejected_routes": [row for row in matrix if row["recommended_action"] in {"parked", "rejected"}], "no_external_action": True}
