from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_DIRS = ['office/mission_command', 'operations/external_validation', 'operations/knowledge_graph', 'reports/integration', 'reports/insights', 'reports/daily', 'reports/autonomous', 'governance', 'knowledge', 'memory', 'scripts', 'tests', 'sales', 'marketing', 'content', 'finance', '.claude']
CAPABILITY_TERMS = ['article_11', 'forgetguard', 'forget_guard', 'stop', 'hook', 'governance_watcher', 'working_memory', 'lrs', 'wisdom', 'telegram', 'notification', 'daily', 'directive', 'operations', 'board', 'cfo', 'ledger', 'sales', 'marketing', 'commercial', 'plugin', 'mcpb', 'bug bounty', 'workflow resale', 'revenue', 'pricing', 'first user', 'install', 'jsonl', 'recovery', 'k9', 'cieu', 'czl', 'gov_order', 'active_agent', 'identity', 'memory', 'brain', 'kg', 'cognition', 'imagination', 'innovation', 'opportunity', 'evidence', 'route', 'execution', 'governance', 'audit']
MISLEADING_NAME_TERMS = ['engine', 'runtime', 'generator', 'planner', 'selector', 'protocol', 'model', 'cognition', 'imagination', 'innovation']

def _read(path: Path, limit: int = 60000) -> str:
    try:
        if not path.exists() or path.is_dir() or path.stat().st_size > 2_000_000:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""

def _py_info(text: str) -> dict[str, Any]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {"callables": [], "real_computation": False}
    callables = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    real = len(callables) > 0 and (len([n for n in ast.walk(tree) if isinstance(n, ast.Call)]) > 4 or any(term in text for term in ["sqlite3", "subprocess", "TfidfVectorizer", "cosine_similarity", "urllib", "hashlib", "argparse"]))
    return {"callables": callables[:30], "real_computation": real}

def is_pure_get_artifact_accessor(path: str, text: str) -> bool:
    if not path.endswith(".py") or "get_artifact(" not in text:
        return False
    triple_single = chr(39) * 3
    non_comment_lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#") and not line.strip().startswith('"""') and not line.strip().startswith(triple_single)]
    return len(non_comment_lines) <= 12 or ("return get_artifact(" in text and "for " not in text and "if " not in text and "class " not in text)

def capability_family(path: str, text: str) -> str:
    lower = f"{path}\n{text[:12000]}".lower()
    if any(k in lower for k in ["article_11", "forgetguard", "forget_guard", "governance_watcher", "stop hook", "pre_tool", "active_agent", "hook"]):
        return "live_runtime_enforcement"
    if any(k in lower for k in ["working_memory", "lrs", "session_recovery", "boot", "snapshot"]):
        return "session_lifecycle_memory"
    if any(k in lower for k in ["wisdom", "who_i_am", "m_triangle", "work_methodology", "imagination", "cognition", "innovation"]):
        return "ceo_wisdom_and_cognition"
    if any(k in lower for k in ["sales", "marketing", "pricing", "revenue", "first user", "install guide", "show hn", "bug bounty", "workflow resale", "plugin", "mcpb", "commercial"]):
        return "commercial_and_value_production"
    if any(k in lower for k in ["gov_order", "repository_delivery", "jsonl", "recovery", "execution", "delivery"]):
        return "execution_and_delivery"
    if any(k in lower for k in ["cieu", "czl", "k9", "audit", "governance"]):
        return "governance_and_audit"
    if any(k in lower for k in ["telegram", "notification", "daily", "board_pending", "board reporting", "directive_tracker"]):
        return "notification_and_board_loop"
    return "unknown"

def build_full_history_runtime_archaeology() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for directory in SCAN_DIRS:
        base = REPO_ROOT / directory
        if not base.exists():
            continue
        for file in sorted(base.rglob("*")):
            if not file.is_file() or ".git" in file.parts:
                continue
            if file.suffix.lower() not in {".py", ".md", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".txt"}:
                continue
            rel = str(file.relative_to(REPO_ROOT))
            if rel in seen:
                continue
            seen.add(rel)
            text = _read(file)
            lower = f"{rel}\n{text[:12000]}".lower()
            if not any(term.replace("_", " ") in lower or term in lower for term in CAPABILITY_TERMS) and not re.search(r"e(3[1-9]|4[0-4][a-z]?)", rel.lower()):
                continue
            info = _py_info(text) if rel.endswith(".py") else {"callables": [], "real_computation": False}
            accessor = is_pure_get_artifact_accessor(rel, text)
            family = capability_family(rel, text)
            milestone = re.search(r"(e\d+[a-z]?)", rel.lower())
            e_milestone = milestone.group(1).upper() if milestone else ""
            rows.append({
                "resource_id": re.sub(r"[^a-zA-Z0-9]+", "_", rel).strip("_").lower()[:180],
                "path": rel,
                "capability_family": family,
                "milestone": e_milestone,
                "implemented_before_E31": not e_milestone or bool(re.match(r"E([0-2]\d|30)$", e_milestone)),
                "still_callable_now": rel.endswith(".py") and bool(info["callables"]),
                "callable_function_names": info["callables"],
                "real_task_specific_computation": info["real_computation"] and not accessor,
                "artifact_accessor_only": accessor,
                "misleading_runtime_name": rel.endswith(".py") and accessor and any(term in Path(rel).stem.lower() for term in MISLEADING_NAME_TERMS),
                "bypassed_by_E_series": (not e_milestone) and family != "unknown",
                "covered_by_later_artifact_line": (not e_milestone) and family in {"ceo_wisdom_and_cognition", "session_lifecycle_memory", "commercial_and_value_production", "notification_and_board_loop"},
                "reconnection_action": family,
            })
    return {"artifact_id": "e44a_full_history_runtime_archaeology", "resources": rows, "resource_count": len(rows)}
