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


def _snippets() -> dict[str, list[str]]:
    terms = ["m triangle", "mission", "first user", "revenue", "pmf", "real value", "customer", "execution"]
    return {
        "DIRECTIVE_TRACKER": _lines(BRIDGE_ROOT / "DIRECTIVE_TRACKER.md", terms),
        "OPERATIONS": _lines(BRIDGE_ROOT / "OPERATIONS.md", terms),
        "M_TRIANGLE": _lines(BRIDGE_ROOT / "knowledge/ceo/wisdom/M_TRIANGLE.md", ["value", "production", "triangle", "real"]),
        "WORK_METHODOLOGY": _lines(BRIDGE_ROOT / "knowledge/ceo/wisdom/WORK_METHODOLOGY.md", ["task", "execution", "user", "value"]),
    }


def project_task_from_m_triangle(task: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    text = f"{task.get('task_title', '')}\n{task.get('task_description', '')}".lower()
    value_task = any(term in text for term in ["user", "value", "commercial", "revenue", "install", "demo"])
    snippets = _snippets()
    return {
        "artifact_id": "e46b_field_projection_adapter_result",
        "task_id": task.get("task_id") or task.get("task_title") or "task",
        "m_triangle_alignment": "value production before claim expansion; learning must close through CIEU/CZL" if value_task else "maintain Board/M Triangle alignment before execution",
        "board_directive_link": snippets["DIRECTIVE_TRACKER"][:4] or snippets["OPERATIONS"][:4],
        "company_objective": "prove governed agent action is understandable and locally demonstrable without external claims",
        "milestone_objective": "E46B canonical spine turns prior runtime/projection/brain/capability assets into one task-time flow",
        "session_objective": "produce local dry-run route decision with no external side effects",
        "task_objective": task.get("task_description", ""),
        "action_candidates": ["run canonical dry-run", "reuse E45 local demo", "close gov-mcp server/client demo gap", "prepare owner-approved external attempt only after blockers"],
        "behavior_constraints": ["no contact", "no send", "no provider/API", "no internet install", "no duplicate governance/execution/audit/brain/KG"],
        "y_star_candidate": "Governed Agent Action Proof Packet over gov-mcp + Y-star-gov substrate",
        "governance_gate_needed": True,
        "cieu_closure_expectation": "record local proof, failures, route decision, owner approval boundary, and next projection",
        "residual_learning_expectation": "doctor/server-client gaps become residual learning candidates, not canonical learning until reviewed",
        "projection_maturity": "partial_adapter",
        "source_snippets": snippets,
        "no_external_action": True,
    }
