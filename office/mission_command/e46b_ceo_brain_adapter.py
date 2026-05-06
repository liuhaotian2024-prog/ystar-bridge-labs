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
    ])
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
        "commercial_assets": _commercial_assets(),
        "read_model_role": "active read context assembled from wisdom, working memory status, latest KG/brain/read-model artifacts, directives, and commercial assets",
        "no_external_action": True,
    }
