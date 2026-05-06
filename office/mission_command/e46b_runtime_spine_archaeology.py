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


REPO_ROOTS = {
    "ystar-bridge-labs": BRIDGE_ROOT,
    "Y-star-gov": Y_GOV_ROOT,
    "gov-mcp": GOV_MCP_ROOT,
    "K9Audit": K9_ROOT,
    "ystar-company": COMPANY_ROOT,
}

SCAN_DIRS = {
    "ystar-bridge-labs": ["AGENTS.md", "CLAUDE.md", "DIRECTIVE_TRACKER.md", "OPERATIONS.md", "BOARD_PENDING.md", "CZL.md", ".czl_subgoals.json", "knowledge", "memory", "governance", "scripts", "office/mission_command", "operations/external_validation", "operations/knowledge_graph", "reports", "sales", "marketing", "content", "finance", "tests", ".claude"],
    "Y-star-gov": ["README.md", "pyproject.toml", "ystar", "tests", "docs", "domain_packs", "claude-code-integration"],
    "gov-mcp": ["README.md", "pyproject.toml", "gov_mcp", "docs", "tests"],
    "K9Audit": ["README.md", "pyproject.toml", "k9log", "docs", "tests"],
    "ystar-company": ["README.md", "docs", "sales", "marketing", "content", "finance", "reports", "knowledge", "operations"],
}

SPINE_LAYER_TERMS = {
    "constitutional_target_layer": ["m triangle", "m_triangle", "board", "directive", "agents.md", "work_methodology", "who_i_am", "charter", "constitution", "amendment", "mission"],
    "field_functional_projection_layer": ["field functional", "field_functional", "projection", "mission projection", "company projection", "milestone", "session", "task", "action", "behavior", "y* candidate", "pre-u", "pre_u", "residual", "learning", "route registry", "czl subgoal"],
    "ceo_brain_layer": ["ceo brain", "brain", "kg", "knowledge_graph", "memory", "wisdom", "daily", "read_model", "lrs", "working_memory", "directive_tracker"],
    "capability_activation_layer": ["capability", "activation", "registry", "router", "preflight", "cascade", "no-rebuild", "no_rebuild", "reuse", "cognition"],
    "governance_kernel_layer": ["y-star-gov", "ystar", "governance", "pre-u", "pre_u", "intentcontract", "contract", "check", "enforce", "cieu", "kernel", "residual"],
    "execution_boundary_layer": ["gov-mcp", "gov_mcp", "mcp", "execution", "delivery bridge", "repository_delivery", "command", "runner", "demo", "install", "status", "plugin"],
    "evidence_audit_layer": ["k9", "audit", "cieu", "czl", "claim", "evidence", "contradiction", "source quality", "burden", "proof", "ledger"],
    "commercial_value_layer": ["sales", "marketing", "commercial", "content", "finance", "revenue", "customer", "pricing", "pmf", "first user", "plugin", "bug bounty", "enterprise", "paid", "marketplace"],
    "notification_board_loop_layer": ["telegram", "notify", "notification", "daily reminder", "board_pending", "owner packet", "directive_tracker", "reports/daily", "milestone shipped"],
    "closure_learning_layer": ["closure", "czl", "kg", "brain update", "next decision", "decision horizon", "residual learning", "completion matrix", "writeback", "read_model_update"],
}

ALL_TERMS = sorted({term for terms in SPINE_LAYER_TERMS.values() for term in terms})
MISLEADING_NAME_TERMS = ["engine", "runtime", "generator", "planner", "selector", "protocol", "model", "cognition", "imagination", "innovation"]
SKIP_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules", ".venv", "venv"}
VALID_SUFFIXES = {".py", ".md", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".txt"}


def _iter_scan_files(repo: str, root: Path) -> list[Path]:
    files: list[Path] = []
    if not root.exists():
        return files
    for item in SCAN_DIRS.get(repo, []):
        path = root / item
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            for file in path.rglob("*"):
                if not file.is_file() or file.suffix.lower() not in VALID_SUFFIXES:
                    continue
                if any(part in SKIP_PARTS for part in file.parts):
                    continue
                try:
                    if file.stat().st_size > 2_000_000:
                        continue
                except Exception:
                    continue
                files.append(file)
    return sorted(set(files))


def _layer_for(rel: str, text: str) -> str:
    combined = f"{rel}\n{text}".lower()
    scores = {layer: sum(1 for term in terms if term in combined) for layer, terms in SPINE_LAYER_TERMS.items()}
    best = max(scores.items(), key=lambda item: (item[1], item[0]))
    return best[0] if best[1] else "closure_learning_layer"


def _is_relevant(rel: str, text: str) -> bool:
    combined = f"{rel}\n{text}".lower()
    if any(term in combined for term in ALL_TERMS):
        return True
    return rel in {"AGENTS.md", "CLAUDE.md", "DIRECTIVE_TRACKER.md", "OPERATIONS.md", "BOARD_PENDING.md", "CZL.md", ".czl_subgoals.json", "README.md", "pyproject.toml"}


def _status_for(path: Path, rel: str, text: str, repo: str, layer: str) -> str:
    lower = text.lower()
    name = path.name.lower()
    is_py = path.suffix == ".py"
    artifact_accessor = is_py and ("get_artifact(" in lower and re.search(r"return\s+get_artifact\(", lower) is not None)
    misleading = artifact_accessor and any(term in name for term in MISLEADING_NAME_TERMS)
    if misleading:
        return "misleading_runtime_name"
    if artifact_accessor:
        return "artifact_accessor"
    if is_py and ("def " in text or "class " in text):
        return "active_runtime"
    if repo != "ystar-bridge-labs" and layer in {"governance_kernel_layer", "execution_boundary_layer", "evidence_audit_layer"} and is_py:
        return "active_runtime"
    if "read_model" in rel or "ceo_brain" in rel or "ceo_kg" in rel or "working_memory" in rel or "wisdom" in rel:
        return "active_read_model"
    if "expert" in rel and ("e40" in rel or "expert_review" in rel):
        return "parked"
    if path.suffix in {".json", ".jsonl", ".md", ".toml", ".yaml", ".yml", ".txt"}:
        return "static_artifact"
    return "orphaned"


def _callables(text: str) -> list[str]:
    return re.findall(r"^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", text, flags=re.MULTILINE)[:12]


def _test_index(root: Path) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    tests = root / "tests"
    if not tests.exists():
        return index
    for file in tests.rglob("test_*.py"):
        body = _read(file, 80000)
        key = file.stem.replace("test_", "")
        index.setdefault(key, []).append(str(file.relative_to(root)))
        for match in re.findall(r"e\d+[a-z]?_[A-Za-z0-9_]+", body + "\n" + file.name):
            index.setdefault(match, []).append(str(file.relative_to(root)))
    return index


def _tests_for(rel: str, test_index: dict[str, list[str]]) -> list[str]:
    stem = Path(rel).stem
    found: list[str] = []
    for key, tests in test_index.items():
        if key in stem or stem in key:
            found.extend(tests)
    return sorted(set(found))[:8]


def _resource(repo: str, root: Path, path: Path, test_index: dict[str, list[str]]) -> dict[str, Any] | None:
    rel = str(path.relative_to(root))
    text = _read(path)
    if not _is_relevant(rel, text):
        return None
    layer = _layer_for(rel, text)
    status = _status_for(path, rel, text, repo, layer)
    tests = _tests_for(rel, test_index)
    written = ("operations/" in rel or "reports/integration" in rel) and path.suffix in {".json", ".jsonl", ".md"}
    read_by_future = any(token in rel for token in ["e42_", "e44a_", "e45_", "e46b_", "M_TRIANGLE", "WORK_METHODOLOGY", "DIRECTIVE_TRACKER", "OPERATIONS", "CZL", "article_11", "working_memory_snapshot", "wisdom_search"])
    return {
        "resource_id": f"{repo}:{rel}",
        "repo": repo,
        "path": rel,
        "spine_layer": layer,
        "current_status": status,
        "callable_entrypoints": _callables(text) if path.suffix == ".py" else [],
        "tests": tests,
        "upstream_dependencies": [term for term in ALL_TERMS if term in f"{rel}\n{text}".lower()][:12],
        "downstream_consumers": tests[:],
        "writes_outputs": written,
        "read_by_future_runtime": read_by_future,
        "operational_gap": "written_but_not_read" if written and not read_by_future else ("callable_without_direct_test" if path.suffix == ".py" and not tests else ""),
        "recommended_action": _recommended_action(repo, layer, status, read_by_future),
    }


def _recommended_action(repo: str, layer: str, status: str, read_by_future: bool) -> str:
    if repo != "ystar-bridge-labs":
        return "cross_repo_proposal" if status not in {"active_runtime", "active_read_model"} else "keep"
    if status in {"misleading_runtime_name", "artifact_accessor"}:
        return "bridge"
    if status == "parked":
        return "park"
    if not read_by_future and layer in {"ceo_brain_layer", "field_functional_projection_layer", "commercial_value_layer", "closure_learning_layer"}:
        return "bridge"
    return "keep"


def build_full_system_runtime_spine_archaeology(max_resources: int | None = None) -> dict[str, Any]:
    resources: list[dict[str, Any]] = []
    repo_heads: dict[str, str | None] = {}
    for repo, root in REPO_ROOTS.items():
        if not root.exists():
            repo_heads[repo] = None
            continue
        head = _run(["git", "rev-parse", "HEAD"], cwd=root)
        repo_heads[repo] = head["stdout"] if head["returncode"] == 0 else None
        index = _test_index(root)
        for path in _iter_scan_files(repo, root):
            item = _resource(repo, root, path, index)
            if item:
                resources.append(item)
    if max_resources:
        resources = resources[:max_resources]
    layer_counts = Counter(item["spine_layer"] for item in resources)
    status_counts = Counter(item["current_status"] for item in resources)
    action_counts = Counter(item["recommended_action"] for item in resources)
    required_evidence = {
        "article_11_found": any("article_11_tracker.py" in item["path"] for item in resources),
        "working_memory_snapshot_found": any("working_memory_snapshot.py" in item["path"] for item in resources),
        "wisdom_search_found": any("wisdom_search.py" in item["path"] for item in resources),
        "field_projection_resources_found": any(item["spine_layer"] == "field_functional_projection_layer" for item in resources),
        "ceo_brain_kg_read_model_found": any(item["spine_layer"] == "ceo_brain_layer" for item in resources),
        "e34_e35_e36_cognition_found": any(re.search(r"e3[456]_", item["path"]) for item in resources),
        "e42_e44a_e45_runtime_found": any(re.search(r"e42_|e44a_|e45_", item["path"]) for item in resources),
        "commercial_plugin_revenue_found": any(item["spine_layer"] == "commercial_value_layer" for item in resources),
    }
    return {
        "artifact_id": "e46b_full_system_runtime_spine_archaeology",
        "repo_heads": repo_heads,
        "resource_count": len(resources),
        "spine_layers": list(SPINE_LAYER_TERMS),
        "layer_counts": dict(layer_counts),
        "status_counts": dict(status_counts),
        "recommended_action_counts": dict(action_counts),
        "written_but_not_read_count": sum(1 for item in resources if item["operational_gap"] == "written_but_not_read"),
        "callable_without_direct_test_count": sum(1 for item in resources if item["operational_gap"] == "callable_without_direct_test"),
        "misleading_runtime_name_count": status_counts.get("misleading_runtime_name", 0),
        "required_evidence": required_evidence,
        "resources": resources,
        "unknown_resources_without_reason": [],
        "no_external_action": True,
    }
