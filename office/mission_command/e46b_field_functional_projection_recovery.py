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

from .e46b_runtime_spine_archaeology import build_full_system_runtime_spine_archaeology

STAGE_TERMS = {
    "mission": ["mission", "m triangle", "purpose"],
    "company": ["company", "bridge labs", "runtime"],
    "milestone": ["milestone", "e45", "e46"],
    "session": ["session", "working_memory", "lrs"],
    "task": ["task", "preflight", "router"],
    "action": ["action", "tool", "command", "demo"],
    "behavior": ["behavior", "hook", "pretooluse", "governed"],
    "y_star_candidate": ["y*", "y_star", "ystar", "candidate"],
    "pre_u_governance_gate": ["pre-u", "pre_u", "governance", "validator", "contract"],
    "execution": ["execution", "gov-mcp", "mcp", "delivery"],
    "cieu_czl_closure": ["cieu", "czl", "closure"],
    "residual_learning": ["residual", "learning", "writeback"],
}


def _matching(resources: list[dict[str, Any]], terms: list[str]) -> list[dict[str, Any]]:
    rows = []
    for item in resources:
        hay = f"{item['path']} {' '.join(item.get('upstream_dependencies', []))}".lower()
        if any(term in hay for term in terms):
            rows.append(item)
    return rows[:16]


def recover_field_functional_projection() -> dict[str, Any]:
    arch = build_full_system_runtime_spine_archaeology()
    resources = arch["resources"]
    stages = []
    for stage, terms in STAGE_TERMS.items():
        matches = _matching(resources, terms)
        has_runtime = any(item["current_status"] == "active_runtime" for item in matches)
        has_static = any(item["current_status"] in {"static_artifact", "active_read_model", "artifact_accessor", "misleading_runtime_name"} for item in matches)
        if has_runtime:
            maturity = "active_runtime"
        elif has_static:
            maturity = "static_recovered"
        else:
            maturity = "missing"
        stages.append({
            "stage": stage,
            "maturity": maturity,
            "runtime_paths": [item["resource_id"] for item in matches if item["current_status"] == "active_runtime"][:6],
            "static_or_read_model_paths": [item["resource_id"] for item in matches if item["current_status"] != "active_runtime"][:6],
            "gap": "not connected to canonical CEO task runtime" if maturity != "active_runtime" else "needs adapter invocation from canonical spine",
        })
    found = any(stage["maturity"] != "missing" for stage in stages)
    return {
        "artifact_id": "e46b_field_functional_projection_recovery",
        "existing_projection_chain_found": found,
        "projection_stages": stages,
        "current_E42_E44A_E45_runtime_bypasses_projection": True,
        "adapter_needed": "e46b_field_projection_adapter.project_task_from_m_triangle",
        "canonical_spine_action": "recover existing field/residual/Pre-U lines as partial adapter; do not rebuild Y-star-gov projection/governance kernel",
        "no_external_action": True,
    }


def build_projection_chain_gap_matrix() -> dict[str, Any]:
    recovery = recover_field_functional_projection()
    rows = []
    for stage in recovery["projection_stages"]:
        rows.append({
            "stage": stage["stage"],
            "current_maturity": stage["maturity"],
            "gap": stage["gap"],
            "required_adapter_behavior": "read existing runtime/static sources and expose canonical projection field" if stage["maturity"] != "missing" else "mark missing and require future cross-repo proposal if governance-owned",
        })
    return {"artifact_id": "e46b_projection_chain_gap_matrix", "rows": rows, "missing_stage_count": sum(1 for row in rows if row["current_maturity"] == "missing"), "no_external_action": True}
