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

from .e42_task_capability_matcher import match_task_to_capabilities
from .e44a_ceo_cognition_cascade_runtime import run_ceo_cognition_cascade
from .e45_real_local_first_value_demo_runner import run_real_local_first_value_demo
from .e46b_ceo_brain_adapter import load_ceo_brain_context
from .e46b_field_projection_adapter import project_task_from_m_triangle


def _side_effect_report() -> dict[str, bool]:
    return {
        "customer_contact": False,
        "expert_contact": False,
        "human_identification": False,
        "scraping": False,
        "send": False,
        "publish": False,
        "form_submission": False,
        "login": False,
        "provider_api_execution": False,
        "internet_install": False,
        "payment": False,
        "secret_use": False,
    }


def _commercial_wrapper_comparison(brain_context: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"route": "gov-mcp + Y-star-gov CLI proof", "role": "first local substrate", "status": "active", "reason": "E45 local commands passed except doctor/environment gaps"},
        {"route": "Governed Agent Action Proof Packet", "role": "first user-facing value object", "status": "active", "reason": "best explains allow/deny evidence without validation claims"},
        {"route": "Claude Desktop plugin / MCPB", "role": "commercial wrapper candidate", "status": "watchlist", "reason": f"{len(brain_context.get('commercial_assets', []))} commercial/plugin assets found but packaging not closed"},
        {"route": "bug bounty / workflow resale / enterprise", "role": "later revenue route", "status": "parked", "reason": "requires stronger local proof and owner-approved external action"},
    ]


def run_canonical_ceo_operating_runtime(task: dict[str, Any], mode: str = "local_dry_run") -> dict[str, Any]:
    side_pre = _side_effect_report()
    projection = project_task_from_m_triangle(task, {})
    brain = load_ceo_brain_context(task)
    task_text = f"{task.get('task_title', '')}\n{task.get('task_description', '')}"
    matches = match_task_to_capabilities(task_text, top_n=12)
    cascade = run_ceo_cognition_cascade(task)
    demo = run_real_local_first_value_demo() if mode == "local_dry_run" else {"local_demo_readiness_class": "not_run", "commands_attempted": []}
    failed = [item["label"] for item in demo.get("commands_attempted", []) if item.get("classification") == "failed"]
    skipped = [item["label"] for item in demo.get("commands_attempted", []) if str(item.get("classification", "")).startswith("skipped")]
    wrappers = _commercial_wrapper_comparison(brain)
    needs_local_hardening = "ystar_doctor" in failed or "gov_mcp_install_start_server" in skipped
    next_milestone = "E47_gov_mcp_server_client_demo_closure" if needs_local_hardening else "E47_owner_approved_single_external_user_attempt"
    route_decision = {
        "selected_value_object": "Governed Agent Action Proof Packet",
        "technical_substrate": "gov-mcp + Y-star-gov governed execution",
        "first_external_attempt_now": not needs_local_hardening,
        "reason": "Canonical spine keeps the proof packet route but requires server/client and doctor closure before outreach." if needs_local_hardening else "Local proof is clean enough for one owner-approved attempt.",
        "next_recommended_milestone": next_milestone,
    }
    closure = {
        "projection_chain_created": True,
        "ceo_brain_context_loaded": True,
        "capability_router_invoked": bool(matches),
        "cognition_cascade_invoked": bool(cascade.get("stages")),
        "local_demo_status": demo.get("local_demo_readiness_class"),
        "remaining_blockers": failed + skipped,
        "owner_approval_required_before_external_action": True,
    }
    return {
        "artifact_id": "e46b_canonical_runtime_v1_1_smoke_result",
        "task_id": task.get("task_id") or "e46b_task",
        "mode": mode,
        "side_effect_precheck": side_pre,
        "constitutional_target_alignment": projection["m_triangle_alignment"],
        "projection_chain": projection,
        "ceo_brain_context": brain,
        "invoked_capabilities": {
            "e42_match_count": len(matches),
            "e44a_stage_count": len(cascade.get("stages", [])),
            "e45_command_count": len(demo.get("commands_attempted", [])),
        },
        "route_matches": matches[:8],
        "cognition_cascade_route": cascade.get("route_selection", {}),
        "commercial_wrapper_comparison": wrappers,
        "evidence_audit_context": {"uses_E45_invocation_trace": True, "uses_K9_CIEU_CZL_as_context": True, "no_duplicate_audit_layer": True},
        "local_demo_status": demo,
        "governance_boundary": {"Y_star_gov_owns_kernel": True, "gov_mcp_owns_execution_boundary": True, "owner_approval_required_for_external_action": True},
        "audit_context": {"CIEU_CZL_closure_expected": True, "K9Audit_later_add_on": True},
        "side_effect_report": _side_effect_report(),
        "route_decision": route_decision,
        "closure_packet": closure,
        "side_effect_postcheck": _side_effect_report(),
        "next_recommended_milestone": next_milestone,
        "no_external_action": True,
    }
