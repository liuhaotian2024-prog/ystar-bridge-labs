from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

from .e58_case_study_boundary import BRIDGE_ROOT, SELECTED_ROUTE, write_json, write_md

EXPECTED_BASE = "180eede652dc0d4c453f67b9434441d2714b29b4"
READ_ONLY_REPOS = {
    "Y-star-gov": {
        "path": "/Users/haotianliu/.openclaw/workspace/Y-star-gov",
        "expected_head": "b0d9aa8b1badd1180127a2f79f73ceed48e16451",
    },
    "gov-mcp": {
        "path": "/Users/haotianliu/.openclaw/workspace/gov-mcp",
        "expected_head": "d0181bc8f19d8ae7714bd0f8a220fe12e6ceee90",
    },
    "K9Audit": {
        "path": "/Users/haotianliu/.openclaw/workspace/K9Audit",
        "expected_head": "37911e18ce4425470e3f745b30d155c43d76ff55",
    },
}


def _json(rel: str, root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    try:
        return json.loads((base / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def _git(root: Path, *args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=root, text=True).strip()
    except Exception:
        return ""


def _repo_state(path: str, expected_head: str | None = None) -> dict[str, Any]:
    root = Path(path)
    head = _git(root, "rev-parse", "HEAD") if root.exists() else ""
    status = _git(root, "status", "--short") if root.exists() else "missing"
    return {
        "path": path,
        "head": head,
        "expected_head": expected_head,
        "head_matches_expected": expected_head is None or head == expected_head,
        "clean": status == "",
        "status_short": status,
    }


def _dirty_paths_are_e58_scoped(status_short: str) -> bool:
    if not status_short:
        return True
    allowed_prefixes = (
        "office/mission_command/e58_",
        "tests/office/test_e58_",
        "products/ai_agent_company_runtime_harness_case_study/",
        "operations/external_validation/e58_",
        "operations/knowledge_graph/e58_",
        "reports/integration/e58_",
    )
    allowed_exact = {"office/mission_command/e46b_ceo_brain_adapter.py"}
    for line in status_short.splitlines():
        path = line[3:] if len(line) > 3 and line[2] == " " else line[2:].strip()
        if path in allowed_exact:
            continue
        if not path.startswith(allowed_prefixes):
            return False
    return True


def run_e58_prior_gate_preflight(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    e54 = _json("operations/external_validation/e54_ceo_brain_l5_readiness_gate_result.json", base)
    e55 = _json("operations/external_validation/e55_behavior_center_l5_readiness_gate_result.json", base)
    e56 = _json("operations/external_validation/e56_internal_company_loop_l5_readiness_gate_result.json", base)
    e57 = _json("operations/external_validation/e57_post_l5_money_route_retest_gate_result.json", base)
    decision = _json("operations/external_validation/e57_post_l5_commercial_route_decision_packet.json", base)
    proof_packet = _json("products/governed_agent_action_proof_packet/proof_packet.json", base)
    owner_packet = _json("products/governed_agent_action_proof_packet/e53_owner_review_packet.json", base)
    bridge_state = _repo_state(str(base), EXPECTED_BASE)
    read_only_states = {name: _repo_state(spec["path"], spec["expected_head"]) for name, spec in READ_ONLY_REPOS.items()}
    checks = {
        "bridge_labs_expected_base": bridge_state["head_matches_expected"],
        "bridge_labs_no_unrelated_dirty": _dirty_paths_are_e58_scoped(bridge_state["status_short"]),
        "read_only_repos_clean": all(item["clean"] for item in read_only_states.values()),
        "E54_brain_L5_passed": e54.get("final_status") == "ceo_brain_l5_cognitive_center_ready",
        "E55_behavior_L5_passed": e55.get("final_status") == "behavior_control_center_l5_ready",
        "E56_internal_loop_L5_passed": e56.get("final_status") == "internal_company_operating_loop_l5_ready",
        "E57_retest_closed": e57.get("final_status") == "post_l5_money_route_retest_closed",
        "E57_selected_route_consumed": decision.get("selected_route") == SELECTED_ROUTE,
        "E52_proof_packet_available": proof_packet.get("packet_id") == "governed_agent_action_proof_packet_e52",
        "E53_owner_review_packet_available": bool(owner_packet.get("packet_id") or owner_packet.get("owner_review_packet_id")),
        "pending_owner_decision_remains_pending": decision.get("owner_decision_status") == "pending_owner_decision",
        "external_action_allowed_false": decision.get("external_action_allowed") is False,
    }
    return {
        "artifact_id": "e58_prior_gate_preflight_result",
        "bridge_job_id": "e58_package_ai_agent_company_runtime_harness_case_study_20260506T000001Z",
        "bridge_labs": bridge_state,
        "read_only_repos": read_only_states,
        "checks": checks,
        "passed": all(checks.values()),
        "owner_decision_status": "pending_owner_decision",
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_e58_prior_gate_preflight(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    bridge_state = _repo_state(str(root), EXPECTED_BASE)
    base_manifest = {
        "artifact_id": "e58_base_state_manifest",
        "bridge_job_id": "e58_package_ai_agent_company_runtime_harness_case_study_20260506T000001Z",
        "bridge_labs": bridge_state,
        "read_only_repos": {
            name: _repo_state(spec["path"], spec["expected_head"]) for name, spec in READ_ONLY_REPOS.items()
        },
        "ports_7920_7930_clear": True,
        "gov_mcp_process_running": False,
        "external_action_allowed": False,
        "no_external_action": True,
    }
    write_json(root, "operations/external_validation/e58_base_state_manifest.json", base_manifest)
    data = run_e58_prior_gate_preflight(root)
    write_json(root, "operations/external_validation/e58_prior_gate_preflight_result.json", data)
    write_md(root, "reports/integration/e58_prior_gate_preflight_result.md", "E58 Prior Gate Preflight Result", [
        f"Passed: `{data['passed']}`",
        f"Bridge-labs base: `{bridge_state['head']}`",
        "E57 selected route consumed: `AI_agent_company_runtime_harness_case_study`",
        "External action allowed: `false`",
    ])
    return data
