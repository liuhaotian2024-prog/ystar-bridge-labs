from __future__ import annotations

import ast
import json
import re
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List


SEED_TERMS = [
    "CZL",
    "residual",
    "Rt+1",
    "Y*",
    "Xt",
    "U",
    "Yt+1",
    "counterfactual",
    "disconfirming",
    "kill condition",
    "evidence",
    "source",
    "provenance",
    "CIEU",
    "prediction delta",
    "learning eligibility",
    "brain writeback",
    "method kernel",
    "Aiden brain",
    "dream",
    "field",
    "field functional",
    "phi",
    "activation",
    "Hebbian",
    "M Triangle",
    "permission tier",
    "risk tier",
    "preflight",
    "action classifier",
    "approval",
    "manifest",
    "owner decision",
    "target seed",
    "target candidate",
    "proposed",
    "approved",
    "feedback",
    "validation signal",
    "paid signal",
    "suppression",
    "opt-out",
    "AI disclosure",
    "action ledger",
    "feedback ledger",
    "opportunity",
    "market reality",
    "buyer signal",
    "revenue path",
    "shortest path",
    "router",
    "registry",
    "lifecycle",
    "gateway",
    "MCP",
    "delegation",
    "escalation",
    "obligation",
    "writeback",
    "mission command",
    "commercial loop",
    "scheduler",
    "field state",
    "governance field",
    "evidence field",
    "场",
    "场泛函",
    "认知场",
    "反事实",
    "残差",
    "证据",
    "大脑",
    "梦",
    "治理",
    "预检",
    "审批",
    "反馈",
    "付费信号",
    "路由",
    "写回",
]

TEXT_EXTENSIONS = {".py", ".md", ".json", ".yaml", ".yml", ".toml", ".txt", ".sql"}
SENSITIVE_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".db-wal", ".db-shm", ".wal", ".shm", ".pid"}
SKIP_PARTS = {".git", "__pycache__", ".pytest_cache", "node_modules", ".logs"}
PRIMARY_DIRS = [
    "office/mission_command",
    "office/aiden_meeting_room",
    "knowledge/ceo/wisdom",
    "governance",
    "operations",
    "reports/integration",
    "reports/ceo",
    "scripts",
    "tests/office",
    "tests/governance",
    "tests/kernel",
    "tests/hook",
]


@dataclass
class RepoInventory:
    repo_id: str
    root: str
    available: bool
    branch: str = ""
    head: str = ""
    blocker: str = ""


@dataclass
class SemanticFileInventory:
    repo: str
    file_path: str
    artifact_type: str
    imports: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    dataclasses: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    constants: List[str] = field(default_factory=list)
    fields: List[str] = field(default_factory=list)
    return_keys: List[str] = field(default_factory=list)
    statuses_or_decisions: List[str] = field(default_factory=list)
    lifecycle_strings: List[str] = field(default_factory=list)
    report_paths: List[str] = field(default_factory=list)
    operation_paths: List[str] = field(default_factory=list)
    headings: List[str] = field(default_factory=list)
    json_keys: List[str] = field(default_factory=list)
    test_names: List[str] = field(default_factory=list)
    asserted_strings: List[str] = field(default_factory=list)
    capability_terms: List[str] = field(default_factory=list)
    snippet: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _run_git(root: Path, args: List[str]) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(root), *args], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _safe_to_read(path: Path) -> bool:
    if any(part in SKIP_PARTS for part in path.parts):
        return False
    name = path.name.lower()
    if name.startswith(".env") or "active_agent" in name or "secret" in name:
        return False
    if any(name.endswith(suffix) for suffix in SENSITIVE_SUFFIXES):
        return False
    return path.suffix.lower() in TEXT_EXTENSIONS


def _iter_primary_files(root: Path) -> Iterable[Path]:
    for rel in PRIMARY_DIRS:
        base = root / rel
        if base.exists():
            yield from (path for path in base.rglob("*") if path.is_file() and _safe_to_read(path))


def _iter_external_files(root: Path) -> Iterable[Path]:
    allowed_roots = ["ystar", "gov_mcp", "docs", "examples", "tests"]
    if root.name == "ystar-company":
        allowed_roots = [
            "controlled_public_page_read_adapter",
            "controlled_search_backend_adapters",
            "controlled_backend_safety_preflight",
            "l10_delegated_live_meta_development_runtime",
            "l8_first_cash_path_operating_loop",
            "l9_meta_development_opportunity_runtime",
            "field_functional_archaeology",
            "canonical_learning_target_registry",
            "approval_authority_model",
            "approval_validity_revocation_policy",
            "runtime_artifact_quarantine",
            "release_preflight_cieu_residual",
            "pilot_approval_non_persistence_receipts",
            "pilot_evidence_capture_readiness",
            "world_value_field_model",
            "agentic_pilot_approval_packet_assembler",
        ]
    for rel in allowed_roots:
        base = root / rel
        if base.exists():
            yield from (path for path in base.rglob("*") if path.is_file() and _safe_to_read(path))


def _terms(text: str) -> List[str]:
    lower = text.lower()
    found = []
    for term in SEED_TERMS:
        if term.lower() in lower:
            found.append(term)
    return sorted(set(found), key=str.lower)


def _string_constants(tree: ast.AST) -> List[str]:
    values: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if any(token in node.value.lower() for token in ["status", "blocked", "complete", "approval", "risk", "tier", "signal", "feedback", "evidence"]):
                values.append(node.value[:120])
    return sorted(set(values))


def _return_keys(tree: ast.AST) -> List[str]:
    keys: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for key in node.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    keys.append(key.value)
    return sorted(set(keys))


def _extract_python(repo: str, path: Path, rel: str, text: str) -> SemanticFileInventory:
    item = SemanticFileInventory(repo=repo, file_path=rel, artifact_type="python")
    try:
        tree = ast.parse(text)
    except SyntaxError:
        item.snippet = text[:500]
        item.capability_terms = _terms(text)
        return item
    for node in tree.body:
        if isinstance(node, ast.Import):
            item.imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            item.imports.append(node.module or "")
        elif isinstance(node, ast.ClassDef):
            item.classes.append(node.name)
            if any(getattr(dec, "id", "") == "dataclass" or getattr(getattr(dec, "func", None), "id", "") == "dataclass" for dec in node.decorator_list):
                item.dataclasses.append(node.name)
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                    item.fields.append(stmt.target.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            item.functions.append(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    item.constants.append(target.id)
    item.return_keys = _return_keys(tree)
    item.statuses_or_decisions = _string_constants(tree)
    item.lifecycle_strings = [value for value in item.statuses_or_decisions if any(t in value.lower() for t in ["candidate", "proposed", "approved", "complete", "blocked", "feedback"])]
    item.report_paths = sorted(set(re.findall(r"reports/integration/[A-Za-z0-9_./-]+", text)))
    item.operation_paths = sorted(set(re.findall(r"operations/[A-Za-z0-9_./-]+", text)))
    item.test_names = [name for name in item.functions if name.startswith("test_")]
    item.asserted_strings = sorted(set(re.findall(r"assert [^\n]+", text)))[:40]
    item.capability_terms = _terms(text)
    item.snippet = text[:500]
    return item


def _extract_markdown(repo: str, rel: str, text: str) -> SemanticFileInventory:
    item = SemanticFileInventory(repo=repo, file_path=rel, artifact_type="markdown")
    item.headings = [line.strip("# ").strip() for line in text.splitlines() if line.startswith("#")]
    item.statuses_or_decisions = sorted(set(re.findall(r"\b(?:complete[_a-z]*|BLOCKED[_A-Z_]*|ALLOW_INTERNAL|NEEDS_OWNER_APPROVAL|REVIEW_GATED|approved|proposed|blocked|residual)\b", text)))
    item.report_paths = sorted(set(re.findall(r"reports/[A-Za-z0-9_./-]+", text)))
    item.operation_paths = sorted(set(re.findall(r"operations/[A-Za-z0-9_./-]+", text)))
    item.capability_terms = _terms(text)
    item.snippet = text[:500]
    return item


def _walk_json_keys(value: Any, prefix: str = "") -> List[str]:
    keys: List[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            full = f"{prefix}.{key}" if prefix else str(key)
            keys.append(full)
            keys.extend(_walk_json_keys(child, full))
    elif isinstance(value, list):
        for child in value[:5]:
            keys.extend(_walk_json_keys(child, prefix + "[]"))
    return keys


def _extract_json(repo: str, rel: str, text: str) -> SemanticFileInventory:
    item = SemanticFileInventory(repo=repo, file_path=rel, artifact_type="json")
    try:
        payload = json.loads(text)
        item.json_keys = sorted(set(_walk_json_keys(payload)))[:250]
    except Exception:
        item.json_keys = []
    item.statuses_or_decisions = sorted(set(re.findall(r"\b(?:complete[_a-z]*|BLOCKED[_A-Z_]*|approved|proposed|blocked|feedback|signal)\b", text)))
    item.capability_terms = _terms(text)
    item.snippet = text[:500]
    return item


def _extract_file(repo: str, root: Path, path: Path) -> SemanticFileInventory:
    rel = str(path.relative_to(root))
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix == ".py":
        return _extract_python(repo, path, rel, text)
    if path.suffix == ".json":
        return _extract_json(repo, rel, text)
    return _extract_markdown(repo, rel, text)


def build_global_semantic_inventory(repo_root: Path, external_roots: Dict[str, Path] | None = None) -> Dict[str, Any]:
    external_roots = external_roots or {
        "y_star_gov": Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov"),
        "gov_mcp": Path("/Users/haotianliu/.openclaw/workspace/gov-mcp"),
        "ystar_company": Path("/Users/haotianliu/.openclaw/workspace/ystar-company"),
    }
    repos: Dict[str, RepoInventory] = {
        "ystar_bridge_labs": RepoInventory("ystar_bridge_labs", str(repo_root), repo_root.exists(), _run_git(repo_root, ["branch", "--show-current"]), _run_git(repo_root, ["rev-parse", "HEAD"])),
    }
    files: List[SemanticFileInventory] = []
    for path in _iter_primary_files(repo_root):
        files.append(_extract_file("ystar_bridge_labs", repo_root, path))
    for repo_id, root in external_roots.items():
        available = root.exists() and (root / ".git").exists()
        repos[repo_id] = RepoInventory(repo_id, str(root), available, _run_git(root, ["branch", "--show-current"]) if available else "", _run_git(root, ["rev-parse", "HEAD"]) if available else "", "" if available else "missing_or_not_git")
        if available:
            for path in _iter_external_files(root):
                try:
                    files.append(_extract_file(repo_id, root, path))
                except Exception:
                    continue
    return {"repos": {key: asdict(value) for key, value in repos.items()}, "files": [item.to_dict() for item in files]}


def render_global_environment_inventory(inventory: Dict[str, Any]) -> str:
    lines = ["# E11 Global Environment Inventory", ""]
    for repo_id, repo in inventory["repos"].items():
        lines.extend(
            [
                f"## {repo_id}",
                f"- root: {repo['root']}",
                f"- available: {repo['available']}",
                f"- branch: {repo.get('branch') or 'unknown'}",
                f"- head: {repo.get('head') or 'unknown'}",
                f"- blocker: {repo.get('blocker') or 'none'}",
                "",
            ]
        )
    by_repo: Dict[str, int] = {}
    by_type: Dict[str, int] = {}
    for item in inventory["files"]:
        by_repo[item["repo"]] = by_repo.get(item["repo"], 0) + 1
        by_type[item["artifact_type"]] = by_type.get(item["artifact_type"], 0) + 1
    lines.extend(["## Coverage", ""])
    lines.extend(f"- {repo}: {count} files inventoried" for repo, count in sorted(by_repo.items()))
    lines.extend(["", "## Artifact Types"])
    lines.extend(f"- {artifact_type}: {count}" for artifact_type, count in sorted(by_type.items()))
    lines.extend(
        [
            "",
            "## Sensitive Boundary",
            "- DB/WAL/SHM files, private logs, env files, and active-agent markers were not read.",
            "- ystar-company was inventoried as incubation source/docs/templates/code; dirty runtime private artifacts were not read.",
            "- `reports/integration/post_push_quality_audit.md` remains intentionally untracked in the original primary workspace.",
        ]
    )
    return "\n".join(lines)


def write_global_semantic_inventory(repo_root: Path) -> Dict[str, Path]:
    inventory = build_global_semantic_inventory(repo_root)
    reports = repo_root / "reports" / "integration"
    reports.mkdir(parents=True, exist_ok=True)
    json_path = reports / "e11_semantic_capability_inventory.json"
    md_path = reports / "e11_global_environment_inventory.md"
    json_path.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_global_environment_inventory(inventory) + "\n", encoding="utf-8")
    return {"json": json_path, "markdown": md_path}

