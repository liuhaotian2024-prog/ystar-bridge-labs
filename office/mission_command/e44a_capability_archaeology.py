from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
EXTERNAL_ROOTS = {
    "Y-star-gov": Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov"),
    "gov-mcp": Path("/Users/haotianliu/.openclaw/workspace/gov-mcp"),
    "K9Audit": Path("/Users/haotianliu/.openclaw/workspace/K9Audit"),
    "ystar-company": Path("/Users/haotianliu/.openclaw/workspace/ystar-company"),
}
CAPABILITY_TERMS = ['imagination', 'innovation', 'cognition', 'strategy', 'strategic', 'opportunity', 'field', 'market', 'commercial', 'customer', 'demand', 'budget', 'evidence', 'claim', 'contradiction', 'decision', 'route', 'frontier', 'memory', 'brain', 'kg', 'reviewer', 'adversarial', 'skeptical', 'contrarian', 'empathy', 'abstraction', 'recombination', 'protocol', 'engine', 'runtime', 'planner', 'selector', 'router', 'no-rebuild', 'delivery', 'first-user', 'execution', 'governance', 'mcp', 'audit', 'cieu', 'czl']
SCAN_DIRS = ['office/mission_command', 'operations/external_validation', 'operations/knowledge_graph', 'reports/integration', 'reports/insights', 'reports/daily', 'governance', 'knowledge', 'memory', 'scripts', 'tests']

def _read(path: Path, limit: int = 50000) -> str:
    try:
        if not path.exists() or path.is_dir() or path.stat().st_size > 2_000_000:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""

def _callable_names(text: str) -> list[str]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    return [node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]

def _imports(text: str) -> list[str]:
    return [line.strip()[:180] for line in text.splitlines() if line.strip().startswith(("import ", "from "))][:20]

def _domains(rel: str, text: str) -> list[str]:
    basis = f"{rel}\n{text[:12000]}".lower()
    domains = []
    for term in CAPABILITY_TERMS:
        if term in basis or term.replace("-", " ") in basis:
            domains.append(term.replace("-", "_"))
    if "buyer" in basis:
        domains.append("customer")
    if "six dimensional" in basis or "six_dimensional" in basis:
        domains.append("six_dimensional_cognition")
    return sorted(dict.fromkeys(domains))

def _resource_id(repo: str, rel: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", f"{repo}_{rel}").strip("_").lower()[:180]

def _milestone(rel: str) -> str:
    found = re.search(r"(e\d+[a-z]?)", rel.lower())
    return found.group(1).upper() if found else ""

def _classify(repo: str, rel: str, text: str) -> str:
    lower = rel.lower()
    if lower.startswith("tests/") or "/tests/" in f"/{lower}":
        return "test_only"
    if lower.endswith(".md") and lower.startswith("reports/"):
        return "report_only"
    if lower.endswith((".json", ".jsonl")):
        return "static_artifact"
    if "registry" in lower:
        return "registry"
    if "router" in lower:
        return "router"
    if repo == "Y-star-gov" or "governance" in lower:
        return "governance_boundary"
    if repo == "gov-mcp" or "mcp" in lower:
        return "execution_boundary"
    if lower.endswith(".py"):
        names = _callable_names(text)
        if "get_artifact(" in text and len(names) <= 2 and len(text.splitlines()) <= 35:
            return "artifact_accessor"
        if names:
            return "runtime_callable" if any(term in lower or term in text.lower()[:5000] for term in ["runtime", "engine", "runner", "build_", "run_", "evaluate", "match", "route", "select", "screen", "review"]) else "script"
        return "script"
    return "unknown"

def _scan(repo: str, root: Path, dirs: list[str]) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    resources = []
    seen: set[str] = set()
    for directory in dirs:
        base = root / directory
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or ".git" in path.parts:
                continue
            if path.suffix.lower() not in {".py", ".json", ".jsonl", ".md", ".toml", ".txt", ".yaml", ".yml"}:
                continue
            rel = str(path.relative_to(root))
            if rel in seen:
                continue
            seen.add(rel)
            lower_rel = rel.lower()
            if lower_rel.startswith("reports/") and not re.search(r"e(3[1-9]|4[0-4][a-z]?)", lower_rel):
                continue
            text = _read(path)
            domains = _domains(rel, text)
            if not domains and not re.search(r"e(3[1-9]|4[0-3])", rel.lower()):
                continue
            rtype = _classify(repo, rel, text)
            tests = []
            if repo == "ystar-bridge-labs":
                candidate = REPO_ROOT / "tests" / "office" / f"test_{Path(rel).stem}.py"
                if candidate.exists():
                    tests.append(str(candidate.relative_to(REPO_ROOT)))
            connected_e42 = "e42" in rel.lower() or "match_task_to_capabilities" in text
            connected_e43 = "e43" in rel.lower() or "first_value" in text
            connected_cognition = any(tag in domains for tag in ["imagination", "innovation", "cognition", "opportunity", "strategic", "customer", "commercial", "demand", "budget"])
            resources.append({
                "resource_id": _resource_id(repo, rel),
                "repo": repo,
                "path": rel,
                "milestone": _milestone(rel),
                "resource_type": rtype,
                "capability_domains": domains,
                "callable_function_names": _callable_names(text)[:20],
                "imports_used": _imports(text),
                "artifact_dependencies": sorted(set(re.findall(r"operations/[A-Za-z0-9_./-]+\.(?:json|jsonl)", text)))[:20],
                "output_artifacts": sorted(set(re.findall(r"e\d+[a-z]?_[A-Za-z0-9_./-]+\.(?:json|jsonl|md)", text)))[:20],
                "tests_covering_it": tests,
                "task_time_callable_today": rtype in {"runtime_callable", "router", "script"} and repo == "ystar-bridge-labs",
                "connected_to_E42_router": connected_e42,
                "connected_to_CEO_cognition_flow": connected_cognition and connected_e42,
                "connected_to_E43_task_flow": connected_e43,
                "orphaned": rtype in {"artifact_accessor", "static_artifact", "report_only"} and not connected_e42 and not connected_e43,
                "duplicated_or_overlapping": any(term in domains for term in ["router", "memory", "brain", "kg", "evidence", "governance", "mcp"]),
                "superseded_or_covered_by_later_workflow": _milestone(rel) in {"E35", "E36", "E37", "E38", "E39", "E40"} and not connected_e42,
                "activation_needed": "upgrade_artifact_accessor_to_lens" if rtype == "artifact_accessor" else ("use_as_static_input" if rtype == "static_artifact" else ("park_with_reason" if rtype in {"report_only", "test_only"} else "direct_activate")),
            })
    return resources

def build_full_ceo_capability_archaeology() -> dict[str, Any]:
    resources = _scan("ystar-bridge-labs", REPO_ROOT, SCAN_DIRS)
    resources += _scan("Y-star-gov", EXTERNAL_ROOTS["Y-star-gov"], ["ystar", "tests", "docs"])
    resources += _scan("gov-mcp", EXTERNAL_ROOTS["gov-mcp"], ["gov_mcp", "tests", "docs"])
    resources += _scan("K9Audit", EXTERNAL_ROOTS["K9Audit"], ["k9log", "tests", "docs"])
    resources += _scan("ystar-company", EXTERNAL_ROOTS["ystar-company"], ["docs", "sales", "operations", "reports"])
    counts: dict[str, int] = {}
    for resource in resources:
        counts[resource["resource_type"]] = counts.get(resource["resource_type"], 0) + 1
    return {
        "artifact_id": "e44a_full_ceo_capability_archaeology",
        "resources_inspected": len(resources),
        "resource_type_counts": counts,
        "required_milestone_discovery": {milestone: any(r["milestone"] == milestone for r in resources) for milestone in ["E35", "E36", "E39", "E41", "E42", "E43"]},
        "artifact_accessor_examples": [r for r in resources if r["resource_type"] == "artifact_accessor"][:20],
        "orphaned_or_disconnected_count": sum(1 for r in resources if r["orphaned"]),
        "covered_over_count": sum(1 for r in resources if r["superseded_or_covered_by_later_workflow"]),
        "resources": resources,
        "external_action_occurred": False,
    }
