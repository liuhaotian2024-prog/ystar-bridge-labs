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

from .e46b_ceo_brain_adapter import load_ceo_brain_context

RELATIONSHIPS = [
    {"name": "CEO brain", "canonical_role": "task-time cognitive context assembled by adapter; not a second brain"},
    {"name": "CEO KG", "canonical_role": "graph/delta memory and read-model input; not direct execution"},
    {"name": "memory/LRS", "canonical_role": "session continuity and recent state"},
    {"name": "wisdom corpus", "canonical_role": "cross-domain recall and M Triangle grounding"},
    {"name": "daily/directive reports", "canonical_role": "operating memory and Board loop context"},
    {"name": "E34-E45 artifacts", "canonical_role": "capability lenses/read-models invoked through canonical runtime"},
]


def build_ceo_brain_canonical_model() -> dict[str, Any]:
    task = {"task_title": "canonical model smoke", "task_description": "load CEO brain context for first value runtime spine"}
    context = load_ceo_brain_context(task)
    written_but_not_read_prior = _json(BRIDGE_ROOT / "operations/external_validation/e44a_full_history_breakage_counts.json") or {}
    return {
        "artifact_id": "e46b_ceo_brain_canonical_model",
        "active_task_time_ceo_brain_source": "e46b_ceo_brain_adapter.load_ceo_brain_context",
        "historical_memory_role": "memory/, daily reports, prior closures, and LRS are read inputs, not competing brains",
        "wisdom_role": "wisdom_search and wisdom corpus provide M Triangle/cross-domain recall",
        "kg_role": "CEO KG deltas/read-models are structured graph memory inputs and closure outputs",
        "read_model_role": "latest summarized state read by canonical runtime before route decision",
        "daily_operational_memory_role": "directive/operations/daily reports supply Board and operating context",
        "relationships": RELATIONSHIPS,
        "context_smoke": {"wisdom_results": len(context["wisdom_search"].get("top_results", [])), "commercial_assets": len(context["commercial_assets"]), "latest_runtime_artifacts": len(context["latest_runtime_artifacts"])},
        "prior_written_but_not_read_reference": written_but_not_read_prior,
        "no_second_ceo_brain": True,
        "no_second_ceo_kg": True,
    }


def build_ceo_brain_operationalization_gap_matrix() -> dict[str, Any]:
    model = build_ceo_brain_canonical_model()
    rows = [
        {"source": "working_memory_snapshot/LRS", "before": "not always read before E42/E43", "after_E46B": "read by e46b_ceo_brain_adapter", "remaining_gap": "load may be unavailable; capture remains explicit/nonfatal"},
        {"source": "wisdom_search", "before": "not part of E43 route", "after_E46B": "queried for task-time context", "remaining_gap": "semantic depth remains TF-IDF"},
        {"source": "CEO KG/read-model", "before": "many deltas written", "after_E46B": "latest read-models included in context", "remaining_gap": "full graph query still future"},
        {"source": "commercial/revenue assets", "before": "disconnected from first-user loop", "after_E46B": "commercial assets included in route comparison", "remaining_gap": "pricing/revenue proof still unvalidated"},
    ]
    return {"artifact_id": "e46b_ceo_brain_operationalization_gap_matrix", "rows": rows, "active_task_time_source": model["active_task_time_ceo_brain_source"], "no_external_action": True}
