from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
K9_ROOT = Path(os.environ.get("K9AUDIT_ROOT", "/Users/haotianliu/.openclaw/workspace/K9Audit"))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
YSTAR_COMPANY_ROOT = Path(os.environ.get("YSTAR_COMPANY_ROOT", "/Users/haotianliu/.openclaw/workspace/ystar-company"))

JOB_ID = "e80_r2_discovery_first_ecosystem_capability_audit_and_ceo_cognitive_runtime_activation_20260507T000001Z"
EXPECTED_BRANCH = "backflow/aiden-ceo-meeting-room"
EXPECTED_BASE = "c7adf8c453a37fa410851ea7203093f27a282f9a"

READONLY_REPOS = {
    "K9Audit": K9_ROOT,
    "Y-star-gov": Y_GOV_ROOT,
    "gov-mcp": GOV_MCP_ROOT,
    "ystar-company": YSTAR_COMPANY_ROOT,
}

PROMPT_HINT_CONCEPTS = {
    "CIEU": ["cieu"],
    "6D_or_field_brain": ["6d", "six_dimensional", "field", "projection"],
    "KG_or_long_memory": ["knowledge_graph", "kg", "memory", "read_model"],
    "self_bootstrap": ["self_bootstrap", "capability_growth"],
    "market_model": ["market_model", "market_dynamics"],
    "counterfactual": ["counterfactual"],
    "live_MCP_execution": ["live mcp execution enabled", "provider live enabled"],
    "production_CIEU_ledger": ["production_hash_chain_enabled", "production cieu ledger"],
    "customer_validation": ["customer_validation_claimed true", "customer validation achieved"],
    "paid_signal": ["paid_signal_claimed true", "paid signal achieved"],
    "pricing_validation": ["pricing_validation_claimed true", "pricing validation achieved"],
    "L5_revenue_readiness": ["l5_ready true", "revenue readiness achieved"],
}

DOMAIN_MARKERS = {
    "governance": ["governance", "govern", "enforce", "check", "policy", "contract", "obligation", "boundary"],
    "audit": ["audit", "trace", "receipt", "ledger", "verify", "verifier", "hash", "chain"],
    "CIEU": ["cieu", "residual", "Y_star", "Y_t_plus_1", "R_t_plus_1", "prediction_delta"],
    "brain": ["brain", "cognition", "ceo", "readback", "adapter", "wisdom"],
    "6D_field": ["6d", "six_dimensional", "dimension", "field", "projection", "cascade"],
    "KG_memory": ["knowledge_graph", "kg", "memory", "read_model", "recall", "history"],
    "market": ["market", "buyer", "problem", "segment", "route", "wedge", "thesis"],
    "commercial": ["commercial", "revenue", "sales", "customer", "paid", "first_cash", "offer"],
    "pricing": ["pricing", "price", "package", "discount", "forecast", "ledger"],
    "validation": ["validation", "evidence", "signal", "readiness", "EV", "pilot", "research"],
    "external_observation": ["external", "public_read", "source", "receipt", "allowlist", "denylist"],
    "provider": ["provider", "mcp", "tool", "dry_run", "idempotency", "promotion"],
    "self_bootstrap": ["self_bootstrap", "capability_gap", "capability_growth", "codex_job"],
    "route_planning": ["planner", "decision", "counterfactual", "candidate", "score", "router"],
    "product": ["product", "blueprint", "module", "packet", "control_room", "diagnostic"],
    "launch": ["launch", "marketing", "show_hn", "listing", "publication", "social"],
    "runtime": ["runtime", "daemon", "orchestrator", "heartbeat", "loop", "driver"],
}

RAW_OUTPUTS = [
    "operations/external_validation/e80_raw_file_inventory.json",
    "operations/external_validation/e80_python_symbol_index.json",
    "operations/external_validation/e80_generated_artifact_index.json",
    "operations/external_validation/e80_test_index.json",
    "operations/external_validation/e80_import_dependency_map.json",
    "operations/external_validation/e80_artifact_provenance_map.json",
]


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def write_json(root: Path, rel: str, data: Any) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(root: Path, rel: str, title: str, lines: list[str]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# " + title + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def load_json(rel: str, root: Path | None = None) -> Any:
    try:
        return json.loads(((root or BRIDGE_ROOT) / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def _run_git(root: Path, args: list[str]) -> list[str]:
    try:
        out = subprocess.check_output(["git", *args], cwd=root, text=True, stderr=subprocess.DEVNULL)
        return [line for line in out.splitlines() if line]
    except Exception:
        return []


def git_state(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    branch = _run_git(base, ["branch", "--show-current"])
    head = _run_git(base, ["rev-parse", "HEAD"])
    return {
        "branch": branch[0] if branch else "",
        "head": head[0] if head else "",
        "expected_branch": EXPECTED_BRANCH,
        "expected_head": EXPECTED_BASE,
    }


def base_verified(root: Path | None = None) -> bool:
    state = git_state(root)
    return state["branch"] == EXPECTED_BRANCH and state["head"] == EXPECTED_BASE


def _read_text(path: Path, limit: int = 200_000) -> str:
    try:
        if not path.exists() or path.is_dir() or path.stat().st_size > 3_000_000:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""


def _safe_json(path: Path) -> Any:
    try:
        if path.stat().st_size > 3_000_000:
            return None
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None


def _repo_files(root: Path) -> list[str]:
    if not root.exists():
        return []
    files = _run_git(root, ["ls-files"])
    if files:
        return files
    return [str(path.relative_to(root)) for path in root.rglob("*") if path.is_file()]


def _repo_untracked(root: Path) -> list[str]:
    if not root.exists():
        return []
    return _run_git(root, ["ls-files", "--others", "--exclude-standard"])


def _extension(rel: str) -> str:
    suffix = Path(rel).suffix.lower()
    return suffix or "<none>"


def artifact_type(rel: str) -> str:
    path = Path(rel)
    lower = rel.lower()
    suffix = path.suffix.lower()
    if rel.startswith("tests/") or "/test_" in lower or path.name.startswith("test_"):
        return "test"
    if suffix == ".py":
        return "code"
    if suffix in {".json", ".jsonl"}:
        if "knowledge_graph" in lower or "/kg" in lower:
            return "KG_artifact"
        if "czl" in lower:
            return "CZL_artifact"
        if "cieu" in lower or "residual" in lower:
            return "CIEU_artifact"
        if "readback" in lower:
            return "readback_artifact"
        if "decision" in lower or "proposal" in lower or "packet" in lower:
            return "decision_artifact"
        return "generated_artifact"
    if suffix in {".md", ".rst", ".txt"}:
        if rel.startswith("reports/") or "report" in lower:
            return "report"
        if rel.startswith("products/"):
            return "product"
        return "doc"
    if suffix in {".yaml", ".yml", ".toml", ".ini", ".cfg"}:
        return "config"
    if rel.startswith("products/"):
        return "product"
    if rel.startswith("reports/"):
        return "report"
    return "other"


def _directory_key(rel: str) -> str:
    parts = Path(rel).parts
    if not parts:
        return "."
    return "/".join(parts[:2]) if len(parts) > 1 else parts[0]


def _milestone(rel: str, text: str = "") -> str:
    haystack = f"{rel}\n{text[:2000]}"
    match = re.search(r"\b(e\d+[a-z]?(?:_e\d+[a-z]?)?)\b", haystack, flags=re.IGNORECASE)
    return match.group(1).lower() if match else ""


def detect_domain(*chunks: str) -> str:
    haystack = " ".join(chunk for chunk in chunks if chunk).lower()
    scores: Counter[str] = Counter()
    for domain, markers in DOMAIN_MARKERS.items():
        for marker in markers:
            if marker.lower() in haystack:
                scores[domain] += 1
    if not scores:
        return "other"
    return scores.most_common(1)[0][0]


def _canonical_owner(repo: str, domain: str, rel: str) -> str:
    lower = rel.lower()
    if repo == "K9Audit":
        return "K9Audit"
    if repo == "Y-star-gov":
        return "Y-star-gov"
    if repo == "gov-mcp":
        return "gov-mcp"
    if repo == "ystar-company":
        return "ystar-company"
    if domain in {"audit", "CIEU"} and any(token in lower for token in ["ledger", "verifier", "hash_chain", "verify"]):
        return "K9Audit"
    if domain == "governance" and any(token in lower for token in ["enforce", "boundary", "contract", "obligation"]):
        return "Y-star-gov"
    if domain == "provider" and any(token in lower for token in ["provider", "mcp", "dry_run", "promotion"]):
        return "gov-mcp"
    return "bridge-labs"


def build_raw_file_inventory(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    repos = {"bridge-labs": base, **READONLY_REPOS}
    repo_records: dict[str, Any] = {}
    total_tracked = 0
    for repo, repo_root in repos.items():
        tracked = sorted(_repo_files(repo_root))
        untracked = sorted(_repo_untracked(repo_root)) if repo == "bridge-labs" else []
        records = [
            {
                "path": rel,
                "directory": _directory_key(rel),
                "extension": _extension(rel),
                "artifact_type": artifact_type(rel),
            }
            for rel in tracked
        ]
        repo_records[repo] = {
            "repo": repo,
            "root": str(repo_root),
            "available": repo_root.exists(),
            "tracked_file_count": len(tracked),
            "untracked_file_count": len(untracked),
            "tracked_files": tracked,
            "untracked_files": untracked,
            "counts_by_directory": dict(Counter(item["directory"] for item in records).most_common()),
            "counts_by_extension": dict(Counter(item["extension"] for item in records).most_common()),
            "counts_by_artifact_type": dict(Counter(item["artifact_type"] for item in records).most_common()),
            "file_records": records,
        }
        total_tracked += len(tracked)
    bridge = repo_records["bridge-labs"]
    return {
        "artifact_id": "e80_raw_file_inventory",
        "bridge_job_id": JOB_ID,
        "created_at": utc_now(),
        "method": "git_ls_files_first_raw_inventory_before_capability_interpretation",
        "base_verification": git_state(base),
        "base_verified": base_verified(base),
        "raw_discovery_phase": True,
        "interpretation_started": False,
        "bridge_labs_tracked_file_count": bridge["tracked_file_count"],
        "bridge_labs_untracked_file_count": bridge["untracked_file_count"],
        "total_tracked_files_across_available_repos": total_tracked,
        "repos": repo_records,
    }


def _module_name(rel: str) -> str:
    path = Path(rel)
    if path.suffix == ".py":
        path = path.with_suffix("")
    return ".".join(path.parts)


def _parse_python_file(root: Path, repo: str, rel: str) -> dict[str, Any]:
    path = root / rel
    text = _read_text(path, 1_000_000)
    record: dict[str, Any] = {
        "repo": repo,
        "path": rel,
        "module_path": _module_name(rel),
        "classes": [],
        "functions": [],
        "constants": [],
        "imports": [],
        "file_docstring": "",
        "parse_error": "",
    }
    try:
        tree = ast.parse(text)
        record["file_docstring"] = (ast.get_docstring(tree) or "")[:1000]
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                record["classes"].append(node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                record["functions"].append(node.name)
            elif isinstance(node, ast.Import):
                record["imports"].extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                prefix = "." * node.level + (node.module or "")
                record["imports"].extend(prefix + ("." + alias.name if node.module else alias.name) for alias in node.names)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        record["constants"].append(target.id)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id.isupper():
                record["constants"].append(node.target.id)
    except Exception as exc:
        record["parse_error"] = str(exc)[:500]
    return record


def build_python_symbol_index(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    repos = {"bridge-labs": base, **READONLY_REPOS}
    records: list[dict[str, Any]] = []
    for repo, repo_root in repos.items():
        for rel in sorted(_repo_files(repo_root)):
            if rel.endswith(".py"):
                records.append(_parse_python_file(repo_root, repo, rel))
    return {
        "artifact_id": "e80_python_symbol_index",
        "bridge_job_id": JOB_ID,
        "created_at": utc_now(),
        "raw_discovery_phase": True,
        "python_file_count": len(records),
        "total_classes": sum(len(item["classes"]) for item in records),
        "total_functions": sum(len(item["functions"]) for item in records),
        "total_constants": sum(len(item["constants"]) for item in records),
        "total_imports": sum(len(item["imports"]) for item in records),
        "parse_error_count": sum(1 for item in records if item["parse_error"]),
        "records": records,
    }


def _extract_json_metadata(path: Path) -> dict[str, Any]:
    data = _safe_json(path)
    meta: dict[str, Any] = {"parseable_json": data is not None}
    if isinstance(data, dict):
        meta["top_level_keys"] = sorted(str(key) for key in data.keys())[:80]
        for key in ["artifact_id", "job_id", "bridge_job_id", "source_artifact", "source_artifacts", "capability_id", "route_id", "decision_status", "owner_approval_status", "readiness_decision", "next_recommended_milestone"]:
            if key in data:
                value = data.get(key)
                meta[key] = value if isinstance(value, (str, int, float, bool)) else str(value)[:500]
        for key in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
            if key in data:
                meta.setdefault("cieu_fields_present", []).append(key)
    elif isinstance(data, list):
        meta["list_length"] = len(data)
        if data and isinstance(data[0], dict):
            meta["first_item_keys"] = sorted(str(key) for key in data[0].keys())[:50]
    return meta


def build_generated_artifact_index(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    records: list[dict[str, Any]] = []
    artifact_roots = ("operations/", "reports/", "products/", "finance/", "marketing/", "sales/")
    for rel in sorted(_repo_files(base)):
        suffix = Path(rel).suffix.lower()
        kind = artifact_type(rel)
        if not (rel.startswith(artifact_roots) or suffix in {".json", ".jsonl", ".md", ".yaml", ".yml", ".toml"}):
            continue
        path = base / rel
        text = _read_text(path, 120_000)
        meta = _extract_json_metadata(path) if suffix == ".json" else {}
        headings = [line.strip("# ").strip() for line in text.splitlines() if line.startswith("#")][:10] if suffix == ".md" else []
        records.append(
            {
                "path": rel,
                "artifact_type": kind,
                "extension": suffix or "<none>",
                "directory": _directory_key(rel),
                "milestone": _milestone(rel, text),
                "size_bytes": path.stat().st_size if path.exists() else 0,
                "json_metadata": meta,
                "markdown_headings": headings,
                "content_flags": {
                    "has_cieu_tuple": all(token in text for token in ["X_t", "U_t", "Y_star"]),
                    "has_owner_gate": "owner" in text.lower() and ("approval" in text.lower() or "decision" in text.lower()),
                    "has_no_overclaim_boundary": "overclaim" in text.lower() or "customer validation" in text.lower(),
                    "has_readback": "readback" in text.lower(),
                    "has_decision": "decision" in text.lower(),
                },
            }
        )
    return {
        "artifact_id": "e80_generated_artifact_index",
        "bridge_job_id": JOB_ID,
        "created_at": utc_now(),
        "raw_discovery_phase": True,
        "artifact_count": len(records),
        "counts_by_artifact_type": dict(Counter(item["artifact_type"] for item in records).most_common()),
        "counts_by_directory": dict(Counter(item["directory"] for item in records).most_common()),
        "records": records,
    }


def build_test_index(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    records: list[dict[str, Any]] = []
    for rel in sorted(_repo_files(base)):
        if not (rel.startswith("tests/") and rel.endswith(".py")):
            continue
        path = base / rel
        text = _read_text(path, 300_000)
        imports: list[str] = []
        test_functions: list[str] = []
        assert_snippets: list[str] = []
        try:
            tree = ast.parse(text)
            lines = text.splitlines()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module or "")
                elif isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    test_functions.append(node.name)
                elif isinstance(node, ast.Assert):
                    lineno = max(node.lineno - 1, 0)
                    assert_snippets.append(lines[lineno].strip()[:240] if lineno < len(lines) else "assert")
        except Exception:
            pass
        modules_tested = sorted({item for item in imports if item.startswith("office.") or item.startswith("operations.")})[:40]
        capability_domain = detect_domain(rel, " ".join(test_functions), " ".join(assert_snippets), " ".join(imports))
        records.append(
            {
                "path": rel,
                "test_functions": test_functions,
                "imports": sorted(set(imports))[:80],
                "modules_tested": modules_tested,
                "assert_count": len(assert_snippets),
                "behavior_asserted": assert_snippets[:30],
                "capability_implied_by_tests": capability_domain,
            }
        )
    return {
        "artifact_id": "e80_test_index",
        "bridge_job_id": JOB_ID,
        "created_at": utc_now(),
        "raw_discovery_phase": True,
        "test_file_count": len(records),
        "test_function_count": sum(len(item["test_functions"]) for item in records),
        "assert_count": sum(item["assert_count"] for item in records),
        "domains_implied": dict(Counter(item["capability_implied_by_tests"] for item in records).most_common()),
        "records": records,
    }


def build_import_dependency_map(root: Path | None = None, symbol_index: dict[str, Any] | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    symbols = symbol_index or build_python_symbol_index(base)
    module_imports: dict[str, Any] = {}
    artifact_reads: dict[str, list[str]] = defaultdict(list)
    readback_modules: list[str] = []
    adapter_imports: list[str] = []
    path_regex = re.compile(r"[\"']((?:operations|products|reports|finance|marketing|sales)/[^\"']+?\.(?:json|jsonl|md|yaml|yml))[\"']")
    for record in symbols.get("records", []):
        if record["repo"] != "bridge-labs":
            continue
        module = record["module_path"]
        imports = sorted(set(record.get("imports", [])))
        module_imports[module] = imports
        if "readback" in record["path"].lower():
            readback_modules.append(module)
        if record["path"] == "office/mission_command/e46b_ceo_brain_adapter.py":
            adapter_imports = imports
        text = _read_text(base / record["path"], 250_000)
        for match in path_regex.findall(text):
            artifact_reads[module].append(match)
    loaded_by_adapter = []
    adapter_text = _read_text(base / "office/mission_command/e46b_ceo_brain_adapter.py", 300_000)
    for match in re.findall(r"from\s+office\.mission_command\.(\w+)\s+import\s+([\w, ]+)", adapter_text):
        loaded_by_adapter.append({"module": f"office.mission_command.{match[0]}", "imported_names": [name.strip() for name in match[1].split(",")]})
    return {
        "artifact_id": "e80_import_dependency_map",
        "bridge_job_id": JOB_ID,
        "created_at": utc_now(),
        "raw_discovery_phase": True,
        "module_count": len(module_imports),
        "module_imports": module_imports,
        "artifact_reads": {key: sorted(set(value)) for key, value in artifact_reads.items()},
        "readback_modules": sorted(set(readback_modules)),
        "ceo_brain_adapter": {
            "path": "office/mission_command/e46b_ceo_brain_adapter.py",
            "imports": sorted(set(adapter_imports)),
            "mission_command_modules_loaded": loaded_by_adapter,
        },
    }


def build_artifact_provenance_map(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    records: list[dict[str, Any]] = []
    for rel in sorted(_repo_files(base)):
        path = base / rel
        suffix = Path(rel).suffix.lower()
        text = _read_text(path, 120_000) if suffix in {".json", ".jsonl", ".md", ".py", ".yaml", ".yml", ".toml"} else ""
        meta = _extract_json_metadata(path) if suffix == ".json" else {}
        records.append(
            {
                "path": rel,
                "milestone": _milestone(rel, text),
                "artifact_type": artifact_type(rel),
                "declared_artifact_id": meta.get("artifact_id") or "",
                "declared_job_id": meta.get("job_id") or meta.get("bridge_job_id") or "",
                "declared_source_artifact": meta.get("source_artifact") or meta.get("source_artifacts") or "",
                "provenance_basis": "declared_metadata" if any(meta.get(key) for key in ["artifact_id", "job_id", "bridge_job_id", "source_artifact", "source_artifacts"]) else ("milestone_filename" if _milestone(rel, text) else "directory_and_content"),
            }
        )
    return {
        "artifact_id": "e80_artifact_provenance_map",
        "bridge_job_id": JOB_ID,
        "created_at": utc_now(),
        "raw_discovery_phase": True,
        "record_count": len(records),
        "counts_by_milestone": dict(Counter(item["milestone"] or "none" for item in records).most_common()),
        "counts_by_provenance_basis": dict(Counter(item["provenance_basis"] for item in records).most_common()),
        "records": records,
    }


def _clean_id(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return value[:90] or "unknown"


def _new_candidate(repo: str, domain: str, key: str) -> dict[str, Any]:
    return {
        "capability_id": "cap_" + _clean_id(f"{repo}_{domain}_{key}"),
        "repo": repo,
        "domain": domain,
        "discovered_from": [],
        "primary_discovery_signal": "",
        "evidence_paths": [],
        "evidence_symbols": [],
        "evidence_artifacts": [],
        "evidence_tests": [],
        "dependency_relationships": [],
        "inferred_capability": "",
        "confidence": 0.0,
        "prompt_hint_used": False,
        "repository_discovered": False,
    }


def _candidate_text(candidate: dict[str, Any]) -> str:
    return " ".join(
        [
            candidate.get("capability_id", ""),
            candidate.get("repo", ""),
            candidate.get("domain", ""),
            candidate.get("inferred_capability", ""),
            " ".join(candidate.get("evidence_paths", [])),
            " ".join(candidate.get("evidence_symbols", [])),
            " ".join(candidate.get("evidence_artifacts", [])),
            " ".join(candidate.get("evidence_tests", [])),
        ]
    ).lower()


def _uses_prompt_hint(candidate: dict[str, Any]) -> bool:
    text = _candidate_text(candidate)
    return any(term.lower() in text for terms in PROMPT_HINT_CONCEPTS.values() for term in terms)


def build_discovered_capability_candidates(
    root: Path | None = None,
    raw_inventory: dict[str, Any] | None = None,
    symbol_index: dict[str, Any] | None = None,
    artifact_index: dict[str, Any] | None = None,
    test_index: dict[str, Any] | None = None,
    dependency_map: dict[str, Any] | None = None,
) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    raw = raw_inventory or build_raw_file_inventory(base)
    symbols = symbol_index or build_python_symbol_index(base)
    artifacts = artifact_index or build_generated_artifact_index(base)
    tests = test_index or build_test_index(base)
    deps = dependency_map or build_import_dependency_map(base, symbols)
    candidates: dict[str, dict[str, Any]] = {}

    def add(repo: str, domain: str, key: str, signal: str, path: str = "", symbol: str = "", artifact: str = "", test: str = "", dependency: str = "") -> None:
        cid_key = f"{repo}:{domain}:{key}"
        item = candidates.setdefault(cid_key, _new_candidate(repo, domain, key))
        if signal not in item["discovered_from"]:
            item["discovered_from"].append(signal)
        if not item["primary_discovery_signal"]:
            item["primary_discovery_signal"] = signal
        if path and path not in item["evidence_paths"]:
            item["evidence_paths"].append(path)
        if symbol and symbol not in item["evidence_symbols"]:
            item["evidence_symbols"].append(symbol)
        if artifact and artifact not in item["evidence_artifacts"]:
            item["evidence_artifacts"].append(artifact)
        if test and test not in item["evidence_tests"]:
            item["evidence_tests"].append(test)
        if dependency and dependency not in item["dependency_relationships"]:
            item["dependency_relationships"].append(dependency)
        item["inferred_capability"] = f"{domain} capability inferred from {key.replace('_', ' ')}"

    for repo, repo_data in raw.get("repos", {}).items():
        for record in repo_data.get("file_records", []):
            rel = record["path"]
            domain = detect_domain(rel, record.get("artifact_type", ""))
            milestone = _milestone(rel)
            key = milestone or record.get("directory") or Path(rel).stem
            add(repo, domain, key, "path_signal", path=rel)

    for record in symbols.get("records", []):
        domain = detect_domain(record["path"], " ".join(record.get("functions", [])), " ".join(record.get("classes", [])), " ".join(record.get("constants", [])))
        key = _milestone(record["path"]) or Path(record["path"]).stem
        for symbol in (record.get("classes", []) + record.get("functions", []) + record.get("constants", []))[:80]:
            add(record["repo"], domain, key, "symbol_signal", path=record["path"], symbol=symbol)

    for record in artifacts.get("records", []):
        meta = record.get("json_metadata", {})
        domain = detect_domain(record["path"], " ".join(meta.get("top_level_keys", [])), " ".join(record.get("markdown_headings", [])))
        key = record.get("milestone") or _directory_key(record["path"])
        declared = meta.get("artifact_id") or meta.get("bridge_job_id") or meta.get("job_id") or record["path"]
        add("bridge-labs", domain, key, "content_signal", path=record["path"], artifact=str(declared))

    for record in tests.get("records", []):
        domain = record.get("capability_implied_by_tests") or detect_domain(record["path"], " ".join(record.get("test_functions", [])))
        key = _milestone(record["path"]) or Path(record["path"]).stem
        add("bridge-labs", domain, key, "test_signal", path=record["path"], test=record["path"])

    for module, imports in deps.get("module_imports", {}).items():
        domain = detect_domain(module, " ".join(imports))
        key = _milestone(module) or module.split(".")[-1]
        for imported in imports[:40]:
            add("bridge-labs", domain, key, "dependency_signal", dependency=f"{module} imports {imported}")
    for module, paths in deps.get("artifact_reads", {}).items():
        domain = detect_domain(module, " ".join(paths))
        key = _milestone(module) or module.split(".")[-1]
        for path in paths[:80]:
            add("bridge-labs", domain, key, "dependency_signal", artifact=path, dependency=f"{module} reads {path}")

    for repo in READONLY_REPOS:
        repo_data = raw.get("repos", {}).get(repo, {})
        for domain, count in Counter(detect_domain(record["path"]) for record in repo_data.get("file_records", [])).items():
            if count:
                add(repo, domain, "cross_repo_owner_surface", "cross_repo_owner_signal", dependency=f"{repo} exposes {count} tracked files in {domain}")

    final = []
    for item in candidates.values():
        item["discovered_from"] = sorted(item["discovered_from"])
        for key in ["evidence_paths", "evidence_symbols", "evidence_artifacts", "evidence_tests", "dependency_relationships"]:
            item[key] = sorted(item[key])[:120]
        evidence_count = sum(len(item[key]) for key in ["evidence_paths", "evidence_symbols", "evidence_artifacts", "evidence_tests", "dependency_relationships"])
        item["prompt_hint_used"] = _uses_prompt_hint(item)
        item["repository_discovered"] = not item["prompt_hint_used"]
        item["confidence"] = min(0.98, round(0.35 + 0.10 * len(item["discovered_from"]) + min(evidence_count, 20) * 0.015 + (0.10 if item["evidence_tests"] else 0), 3))
        final.append(item)
    final = sorted(final, key=lambda item: (-item["confidence"], item["repo"], item["domain"], item["capability_id"]))
    return {
        "artifact_id": "e80_discovered_capability_candidates",
        "bridge_job_id": JOB_ID,
        "created_at": utc_now(),
        "method": "capabilities_extracted_after_raw_inventory_from_path_symbol_content_test_dependency_and_cross_repo_owner_signals",
        "candidate_count": len(final),
        "repository_discovered_count": sum(1 for item in final if item["repository_discovered"]),
        "prompt_hint_used_count": sum(1 for item in final if item["prompt_hint_used"]),
        "signals_used": ["path_signal", "symbol_signal", "content_signal", "test_signal", "dependency_signal", "cross_repo_owner_signal"],
        "candidates": final,
    }


def build_anti_memory_contamination_report(candidates: dict[str, Any], raw: dict[str, Any], symbols: dict[str, Any], artifacts: dict[str, Any], tests: dict[str, Any]) -> dict[str, Any]:
    all_text = json.dumps({"candidates": candidates.get("candidates", [])[:2000]}, ensure_ascii=False).lower()
    prompt_unverified = []
    for concept, terms in PROMPT_HINT_CONCEPTS.items():
        found = any(term.lower() in all_text for term in terms)
        if not found or concept in {"live_MCP_execution", "production_CIEU_ledger", "customer_validation", "paid_signal", "pricing_validation", "L5_revenue_readiness"}:
            prompt_unverified.append(
                {
                    "concept": concept,
                    "status": "prompt_hint_unverified" if not found else "prompt_hint_found_only_as_forbidden_or_non_active_claim",
                    "searched_terms": terms,
                    "active_runtime_capability_claimed": False,
                }
            )
    repository_discovered = [item for item in candidates.get("candidates", []) if item.get("repository_discovered")]
    return {
        "artifact_id": "e80_anti_memory_contamination_report",
        "bridge_job_id": JOB_ID,
        "created_at": utc_now(),
        "method": "raw_inventory_and_symbol_artifact_test_indexes_before_prompt_hint_interpretation",
        "findings_from_raw_file_inventory": {
            "bridge_labs_tracked_files": raw.get("bridge_labs_tracked_file_count"),
            "total_tracked_files_across_available_repos": raw.get("total_tracked_files_across_available_repos"),
            "directory_counts_basis": "git ls-files file graph",
        },
        "findings_from_symbol_index": {
            "python_file_count": symbols.get("python_file_count"),
            "total_functions": symbols.get("total_functions"),
            "total_classes": symbols.get("total_classes"),
        },
        "findings_from_generated_artifact_metadata": {
            "artifact_count": artifacts.get("artifact_count"),
            "artifact_type_counts": artifacts.get("counts_by_artifact_type", {}),
        },
        "findings_from_tests": {
            "test_file_count": tests.get("test_file_count"),
            "test_function_count": tests.get("test_function_count"),
            "domains_implied": tests.get("domains_implied", {}),
        },
        "findings_only_from_prompt_hints": prompt_unverified,
        "prompt_hinted_capabilities_not_verified_by_repository_evidence_count": len(prompt_unverified),
        "actual_capabilities_discovered_not_named_in_prompt_count": len(repository_discovered),
        "actual_capabilities_discovered_not_named_in_prompt_examples": repository_discovered[:30],
        "prompt_hinted_capabilities_not_found_or_not_active": prompt_unverified,
        "prior_assumptions_corrected": [
            "E80-R2 does not begin from E65-E79 named memory; it begins from tracked file inventory.",
            "A capability cannot be runtime-active merely because this prompt mentioned it.",
            "Production ledger/verifier, compliance proof, paid signal, and L5 revenue readiness are not treated as active capabilities.",
            "Repository-discovered older runtime, test, amendment, hook, memory, and commercial surfaces remain visible even when not named by the prompt.",
        ],
        "rules_enforced": [
            "active classification requires file, symbol, artifact, test, or dependency evidence",
            "prompt-hinted but unsupported concepts are marked prompt_hint_unverified",
            "repository-discovered capabilities are marked separately from prompt-hinted capabilities",
        ],
    }


def _source_type(candidate: dict[str, Any]) -> str:
    paths = candidate.get("evidence_paths", [])
    if any(path.endswith(".py") for path in paths):
        return "code"
    if any(path.startswith("tests/") for path in paths):
        return "test"
    if any(path.startswith("products/") for path in paths):
        return "product"
    if any(path.startswith("reports/") for path in paths):
        return "report"
    if any(path.startswith(("finance/", "marketing/", "sales/")) for path in paths):
        return "legacy_asset"
    if any(path.endswith((".json", ".jsonl")) for path in paths):
        return "generated_artifact"
    if any(path.endswith((".md", ".txt", ".rst")) for path in paths):
        return "doc"
    return "config" if any(path.endswith((".yaml", ".yml", ".toml")) for path in paths) else "generated_artifact"


def _maturity(candidate: dict[str, Any], source_type: str) -> str:
    text = _candidate_text(candidate)
    if source_type == "code" and candidate.get("evidence_symbols"):
        return "implemented"
    if source_type in {"generated_artifact", "report"}:
        return "generated_only"
    if source_type in {"doc", "product"}:
        return "design_only" if any(token in text for token in ["plan", "draft", "blueprint", "spec", "proposal"]) else "partial"
    if re.search(r"\be([1-9]|1\d|2[0-4])\b", text) and "e71" not in text:
        return "stale"
    return "partial"


def _activation_state(candidate: dict[str, Any], source_type: str, maturity: str, dependency_map: dict[str, Any]) -> str:
    text = _candidate_text(candidate)
    adapter_modules = {item["module"].split(".")[-1] for item in dependency_map.get("ceo_brain_adapter", {}).get("mission_command_modules_loaded", [])}
    if candidate.get("prompt_hint_used") and not candidate.get("evidence_paths"):
        return "prompt_hint_unverified"
    if candidate["repo"] == "ystar-company" or "quarantine" in text:
        return "quarantined"
    if any(module in text for module in adapter_modules) or "e46b_ceo_brain_adapter" in text:
        return "active_in_current_CEO_loop"
    if "readback" in text:
        return "readback_only"
    if "e71_legacy" in text or "promoted_legacy" in text:
        return "legacy_promoted"
    if candidate["repo"] in {"K9Audit", "Y-star-gov", "gov-mcp"}:
        return "active_but_shallow"
    if source_type == "code" and any(token in text for token in ["ledger", "verifier", "governance_engine", "provider_executor"]) and candidate["repo"] == "bridge-labs":
        return "duplicate_risk"
    if maturity == "stale":
        return "obsolete"
    if maturity == "design_only":
        return "dormant"
    return "dormant"


def _evidence_quality(candidate: dict[str, Any]) -> str:
    count = sum(len(candidate.get(key, [])) for key in ["evidence_paths", "evidence_symbols", "evidence_artifacts", "evidence_tests", "dependency_relationships"])
    if candidate.get("evidence_tests") and count >= 5:
        return "high"
    if count >= 4:
        return "medium"
    return "low"


def _relevance(candidate: dict[str, Any], kind: str) -> int:
    text = _candidate_text(candidate)
    domain = candidate.get("domain")
    base = 30
    if kind == "owner" and domain in {"brain", "route_planning", "validation", "self_bootstrap", "product", "commercial"}:
        base += 35
    if kind == "commercial" and domain in {"commercial", "market", "pricing", "product", "launch"}:
        base += 40
    if kind == "ceo" and domain in {"brain", "6D_field", "KG_memory", "route_planning", "counterfactual", "self_bootstrap"}:
        base += 45
    if any(token in text for token in ["e79", "e78", "e73", "e70", "e65", "e24", "e44a", "e35"]):
        base += 15
    if candidate["repo"] in {"K9Audit", "Y-star-gov", "gov-mcp"}:
        base += 10
    return min(base, 100)


def build_whole_ecosystem_capability_inventory(candidates: dict[str, Any], dependency_map: dict[str, Any]) -> dict[str, Any]:
    capabilities: list[dict[str, Any]] = []
    for candidate in candidates.get("candidates", []):
        source_type = _source_type(candidate)
        maturity = _maturity(candidate, source_type)
        activation_state = _activation_state(candidate, source_type, maturity, dependency_map)
        owner_relevance = _relevance(candidate, "owner")
        commercial_relevance = _relevance(candidate, "commercial")
        ceo_relevance = _relevance(candidate, "ceo")
        disposition = "inspect_more"
        if activation_state in {"active_in_current_CEO_loop", "legacy_promoted"}:
            disposition = "activate_now"
        elif activation_state == "active_but_shallow":
            disposition = "wrap_existing"
        elif activation_state == "readback_only":
            disposition = "bind_as_context"
        elif activation_state in {"duplicate_risk", "quarantined", "obsolete"}:
            disposition = "quarantine"
        elif max(owner_relevance, commercial_relevance, ceo_relevance) >= 75:
            disposition = "activate_now"
        capability = {
            "capability_id": candidate["capability_id"],
            "name": candidate["inferred_capability"],
            "repo": candidate["repo"],
            "file_paths": candidate.get("evidence_paths", []),
            "source_type": source_type,
            "discovered_from": candidate.get("discovered_from", []),
            "evidence_count": sum(len(candidate.get(key, [])) for key in ["evidence_paths", "evidence_symbols", "evidence_artifacts", "evidence_tests", "dependency_relationships"]),
            "capability_domain": candidate.get("domain"),
            "maturity": maturity,
            "activation_state": activation_state,
            "canonical_owner": _canonical_owner(candidate["repo"], candidate.get("domain", "other"), " ".join(candidate.get("evidence_paths", []))),
            "current_use_path": "CEO brain adapter or readback import evidence" if activation_state == "active_in_current_CEO_loop" else ("read-only owner context" if candidate["repo"] != "bridge-labs" else ""),
            "missing_activation_path": "" if activation_state == "active_in_current_CEO_loop" else "bind through E80 online cognition loop as evidence-backed context, decision gate, or reuse target",
            "conflict_risk": "high" if activation_state == "duplicate_risk" else ("medium" if candidate["repo"] in {"K9Audit", "Y-star-gov", "gov-mcp"} else "low"),
            "evidence_quality": _evidence_quality(candidate),
            "tests_present": bool(candidate.get("evidence_tests")),
            "owner_relevance": owner_relevance,
            "commercial_relevance": commercial_relevance,
            "CEO_intelligence_relevance": ceo_relevance,
            "recommended_disposition": disposition,
            "prompt_hint_used": candidate.get("prompt_hint_used", False),
            "repository_discovered": candidate.get("repository_discovered", False),
            "evidence_symbols": candidate.get("evidence_symbols", []),
            "evidence_artifacts": candidate.get("evidence_artifacts", []),
            "evidence_tests": candidate.get("evidence_tests", []),
            "dependency_relationships": candidate.get("dependency_relationships", []),
        }
        capabilities.append(capability)
    # Include explicit negative capabilities so prompt hints cannot become silent assumptions.
    negative_caps = [
        ("production_CIEU_ledger_in_bridge_labs", "production CIEU ledger is not verified or active in bridge-labs"),
        ("live_MCP_provider_execution_in_bridge_labs", "live MCP/provider execution is not verified or active in bridge-labs"),
        ("customer_validation_claim", "customer validation is not verified"),
        ("paid_signal_claim", "paid signal is not verified"),
        ("pricing_validation_claim", "pricing validation is not verified"),
        ("L5_revenue_readiness_claim", "L5 revenue readiness is not verified"),
    ]
    for cap_id, name in negative_caps:
        capabilities.append(
            {
                "capability_id": "cap_prompt_hint_unverified_" + _clean_id(cap_id),
                "name": name,
                "repo": "bridge-labs",
                "file_paths": [],
                "source_type": "generated_artifact",
                "discovered_from": ["anti_memory_contamination_check"],
                "evidence_count": 0,
                "capability_domain": "other",
                "maturity": "unknown",
                "activation_state": "prompt_hint_unverified",
                "canonical_owner": "ambiguous",
                "current_use_path": "",
                "missing_activation_path": "not active; must remain forbidden or owner-gated until evidence exists",
                "conflict_risk": "high",
                "evidence_quality": "low",
                "tests_present": False,
                "owner_relevance": 100,
                "commercial_relevance": 100,
                "CEO_intelligence_relevance": 100,
                "recommended_disposition": "quarantine",
                "prompt_hint_used": True,
                "repository_discovered": False,
                "evidence_symbols": [],
                "evidence_artifacts": [],
                "evidence_tests": [],
                "dependency_relationships": [],
            }
        )
    counts = Counter(item["activation_state"] for item in capabilities)
    domains = Counter(item["capability_domain"] for item in capabilities)
    return {
        "artifact_id": "e80_whole_ecosystem_capability_inventory",
        "bridge_job_id": JOB_ID,
        "created_at": utc_now(),
        "method": "classification_after_discovered_capability_candidates_not_prompt_memory",
        "capability_count": len(capabilities),
        "repository_discovered_not_prompt_hinted_count": sum(1 for item in capabilities if item.get("repository_discovered")),
        "prompt_hinted_unverified_count": counts.get("prompt_hint_unverified", 0),
        "activation_state_counts": dict(counts.most_common()),
        "capability_domain_counts": dict(domains.most_common()),
        "capabilities": sorted(capabilities, key=lambda item: (-item["CEO_intelligence_relevance"], -item["commercial_relevance"], item["capability_id"])),
    }


def build_capability_activation_gap_map(inventory: dict[str, Any]) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = {
        "active_and_useful": [],
        "active_but_shallow": [],
        "readback_only": [],
        "dormant_high_value": [],
        "dormant_low_value": [],
        "design_only": [],
        "duplicate_conflicting": [],
        "stale_quarantined": [],
        "prompt_hinted_but_unverified": [],
        "repository_discovered_but_previously_ignored": [],
    }
    high_value_entries: list[dict[str, Any]] = []
    for cap in inventory.get("capabilities", []):
        state = cap["activation_state"]
        if state == "active_in_current_CEO_loop":
            buckets["active_and_useful"].append(cap)
        elif state == "active_but_shallow":
            buckets["active_but_shallow"].append(cap)
        elif state == "readback_only":
            buckets["readback_only"].append(cap)
        elif state == "prompt_hint_unverified":
            buckets["prompt_hinted_but_unverified"].append(cap)
        elif state in {"duplicate_risk"}:
            buckets["duplicate_conflicting"].append(cap)
        elif state in {"quarantined", "obsolete"}:
            buckets["stale_quarantined"].append(cap)
        elif cap["maturity"] == "design_only":
            buckets["design_only"].append(cap)
        elif state == "dormant" and max(cap["owner_relevance"], cap["commercial_relevance"], cap["CEO_intelligence_relevance"]) >= 75:
            buckets["dormant_high_value"].append(cap)
        else:
            buckets["dormant_low_value"].append(cap)
        if cap.get("repository_discovered") and state != "active_in_current_CEO_loop":
            buckets["repository_discovered_but_previously_ignored"].append(cap)
        if state in {"active_but_shallow", "dormant", "readback_only"} and max(cap["owner_relevance"], cap["commercial_relevance"], cap["CEO_intelligence_relevance"]) >= 75:
            high_value_entries.append(
                {
                    "capability_id": cap["capability_id"],
                    "name": cap["name"],
                    "previous_activation_state": state,
                    "current_CEO_failure_addressed": "recent-memory, artifact-factory, or generic-strategy behavior",
                    "where_enters_CEO_cognition_loop": _loop_stage_for_domain(cap["capability_domain"]),
                    "activation_mode": _activation_mode_for_owner(cap["canonical_owner"]),
                    "no_duplication_risk": "wrap/read/context-bind only; canonical owner preserved",
                    "test_required": "tests/office/test_e80_high_value_capability_activation.py",
                }
            )
    return {
        "artifact_id": "e80_capability_activation_gap_map",
        "bridge_job_id": JOB_ID,
        "created_at": utc_now(),
        "bucket_counts": {key: len(value) for key, value in buckets.items()},
        "buckets": {key: value[:120] for key, value in buckets.items()},
        "high_value_dormant_or_shallow_activation_targets": high_value_entries[:40],
        "capabilities_discovered_from_repository_evidence_not_named_in_prompt": buckets["repository_discovered_but_previously_ignored"][:50],
    }


def _loop_stage_for_domain(domain: str) -> str:
    mapping = {
        "brain": "long_memory_KG_brain_recall",
        "6D_field": "field_dimensional_reasoning",
        "KG_memory": "long_memory_KG_brain_recall",
        "CIEU": "pre_action_CIEU_residual_prediction",
        "audit": "pre_action_CIEU_residual_prediction",
        "route_planning": "counterfactual_action_comparison",
        "market": "thesis_generation_and_commercial_sharpness_gate",
        "commercial": "thesis_generation_and_commercial_sharpness_gate",
        "pricing": "commercial_sharpness_gate",
        "validation": "decision_and_real_feedback_path",
        "provider": "canonical_owner_selection_no_new_wheel_gate",
        "governance": "canonical_owner_selection_no_new_wheel_gate",
        "self_bootstrap": "existing_module_reuse_extend_wrap_decision",
    }
    return mapping.get(domain, "full_capability_inventory_recall")


def _activation_mode_for_owner(owner: str) -> str:
    if owner == "bridge-labs":
        return "call_or_context_bind_existing_bridge_labs_module"
    if owner in {"K9Audit", "Y-star-gov", "gov-mcp"}:
        return "wrap_existing_owner_context_read_only_no_reimplementation"
    return "context_bind_or_quarantine"


def _md_table(rows: list[list[Any]], headers: list[str]) -> list[str]:
    result = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        result.append("| " + " | ".join(str(value).replace("\n", " ")[:180] for value in row) + " |")
    return result


def write_raw_markdowns(root: Path, raw: dict[str, Any], symbols: dict[str, Any], artifacts: dict[str, Any], tests: dict[str, Any], deps: dict[str, Any], provenance: dict[str, Any]) -> None:
    bridge = raw["repos"]["bridge-labs"]
    write_md(
        root,
        "operations/external_validation/e80_raw_file_inventory.md",
        "E80 Raw File Inventory",
        [
            "Discovery-first layer written before capability interpretation.",
            f"- Bridge-labs tracked files: {bridge['tracked_file_count']}",
            f"- Bridge-labs untracked files: {bridge['untracked_file_count']}",
            f"- Total tracked files across available repos: {raw['total_tracked_files_across_available_repos']}",
            "",
            "Top bridge-labs directories:",
            *_md_table([[key, value] for key, value in list(bridge["counts_by_directory"].items())[:20]], ["directory", "count"]),
            "",
            "Top bridge-labs artifact types:",
            *_md_table([[key, value] for key, value in bridge["counts_by_artifact_type"].items()], ["artifact_type", "count"]),
        ],
    )
    write_md(
        root,
        "operations/external_validation/e80_python_symbol_index.md",
        "E80 Python Symbol Index",
        [
            f"- Python files indexed: {symbols['python_file_count']}",
            f"- Functions: {symbols['total_functions']}",
            f"- Classes: {symbols['total_classes']}",
            f"- Constants: {symbols['total_constants']}",
            f"- Parse errors: {symbols['parse_error_count']}",
        ],
    )
    write_md(
        root,
        "operations/external_validation/e80_generated_artifact_index.md",
        "E80 Generated Artifact Index",
        [
            f"- Artifacts indexed: {artifacts['artifact_count']}",
            "",
            *_md_table([[key, value] for key, value in artifacts["counts_by_artifact_type"].items()], ["artifact_type", "count"]),
        ],
    )
    write_md(
        root,
        "operations/external_validation/e80_test_index.md",
        "E80 Test Index",
        [
            f"- Test files indexed: {tests['test_file_count']}",
            f"- Test functions indexed: {tests['test_function_count']}",
            f"- Assertions indexed: {tests['assert_count']}",
            "",
            *_md_table([[key, value] for key, value in tests["domains_implied"].items()], ["domain", "test_file_count"]),
        ],
    )
    write_md(
        root,
        "operations/external_validation/e80_import_dependency_map.md",
        "E80 Import Dependency Map",
        [
            f"- Bridge Python modules mapped: {deps['module_count']}",
            f"- Readback modules found: {len(deps['readback_modules'])}",
            f"- CEO adapter mission command modules loaded: {len(deps['ceo_brain_adapter']['mission_command_modules_loaded'])}",
        ],
    )
    write_md(
        root,
        "operations/external_validation/e80_artifact_provenance_map.md",
        "E80 Artifact Provenance Map",
        [
            f"- Files with provenance records: {provenance['record_count']}",
            "",
            *_md_table([[key, value] for key, value in list(provenance["counts_by_provenance_basis"].items())], ["basis", "count"]),
        ],
    )


def write_interpretation_markdowns(root: Path, candidates: dict[str, Any], anti: dict[str, Any], inventory: dict[str, Any], gap_map: dict[str, Any]) -> None:
    write_md(
        root,
        "operations/external_validation/e80_discovered_capability_candidates.md",
        "E80 Discovered Capability Candidates",
        [
            "Capabilities were extracted after raw discovery from path, symbol, content, test, dependency, and cross-repo owner signals.",
            f"- Candidates: {candidates['candidate_count']}",
            f"- Repository-discovered not prompt-hinted: {candidates['repository_discovered_count']}",
            f"- Prompt-hinted with evidence: {candidates['prompt_hint_used_count']}",
            "",
            *_md_table(
                [[item["capability_id"], item["repo"], item["domain"], ",".join(item["discovered_from"]), item["confidence"]] for item in candidates["candidates"][:30]],
                ["capability_id", "repo", "domain", "signals", "confidence"],
            ),
        ],
    )
    write_md(
        root,
        "operations/external_validation/e80_anti_memory_contamination_report.md",
        "E80 Anti-Memory-Contamination Report",
        [
            "This report separates repository evidence from prompt hints.",
            f"- Raw bridge-labs tracked files: {anti['findings_from_raw_file_inventory']['bridge_labs_tracked_files']}",
            f"- Python files indexed: {anti['findings_from_symbol_index']['python_file_count']}",
            f"- Artifacts indexed: {anti['findings_from_generated_artifact_metadata']['artifact_count']}",
            f"- Tests indexed: {anti['findings_from_tests']['test_file_count']}",
            f"- Repository-discovered capabilities not named in prompt: {anti['actual_capabilities_discovered_not_named_in_prompt_count']}",
            f"- Prompt-hinted concepts not verified as active capabilities: {anti['prompt_hinted_capabilities_not_verified_by_repository_evidence_count']}",
            "",
            "Corrections:",
            *[f"- {item}" for item in anti["prior_assumptions_corrected"]],
        ],
    )
    write_md(
        root,
        "operations/external_validation/e80_whole_ecosystem_capability_inventory.md",
        "E80 Whole-Ecosystem Capability Inventory",
        [
            f"- Capabilities classified: {inventory['capability_count']}",
            f"- Repository-discovered not prompt-hinted: {inventory['repository_discovered_not_prompt_hinted_count']}",
            f"- Prompt-hinted unverified: {inventory['prompt_hinted_unverified_count']}",
            "",
            "Activation states:",
            *_md_table([[key, value] for key, value in inventory["activation_state_counts"].items()], ["state", "count"]),
            "",
            "Domains:",
            *_md_table([[key, value] for key, value in inventory["capability_domain_counts"].items()], ["domain", "count"]),
        ],
    )
    write_md(
        root,
        "operations/external_validation/e80_capability_activation_gap_map.md",
        "E80 Capability Activation Gap Map",
        [
            "Capabilities were bucketed only after repository-discovered candidate extraction.",
            "",
            *_md_table([[key, value] for key, value in gap_map["bucket_counts"].items()], ["bucket", "count"]),
            "",
            "Repository-discovered capabilities not named in prompt remain visible instead of being forgotten.",
        ],
    )


def write_discovery_outputs(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    raw = build_raw_file_inventory(base)
    symbols = build_python_symbol_index(base)
    artifacts = build_generated_artifact_index(base)
    tests = build_test_index(base)
    deps = build_import_dependency_map(base, symbols)
    provenance = build_artifact_provenance_map(base)

    # Raw discovery outputs are intentionally written before candidate interpretation.
    write_json(base, "operations/external_validation/e80_raw_file_inventory.json", raw)
    write_json(base, "operations/external_validation/e80_python_symbol_index.json", symbols)
    write_json(base, "operations/external_validation/e80_generated_artifact_index.json", artifacts)
    write_json(base, "operations/external_validation/e80_test_index.json", tests)
    write_json(base, "operations/external_validation/e80_import_dependency_map.json", deps)
    write_json(base, "operations/external_validation/e80_artifact_provenance_map.json", provenance)
    write_raw_markdowns(base, raw, symbols, artifacts, tests, deps, provenance)

    candidates = build_discovered_capability_candidates(base, raw, symbols, artifacts, tests, deps)
    anti = build_anti_memory_contamination_report(candidates, raw, symbols, artifacts, tests)
    inventory = build_whole_ecosystem_capability_inventory(candidates, deps)
    gap_map = build_capability_activation_gap_map(inventory)

    write_json(base, "operations/external_validation/e80_discovered_capability_candidates.json", candidates)
    write_json(base, "operations/external_validation/e80_anti_memory_contamination_report.json", anti)
    write_json(base, "operations/external_validation/e80_whole_ecosystem_capability_inventory.json", inventory)
    write_json(base, "operations/external_validation/e80_capability_activation_gap_map.json", gap_map)
    write_interpretation_markdowns(base, candidates, anti, inventory, gap_map)
    return {
        "raw": raw,
        "symbols": symbols,
        "artifacts": artifacts,
        "tests": tests,
        "dependency_map": deps,
        "provenance": provenance,
        "candidates": candidates,
        "anti_memory": anti,
        "inventory": inventory,
        "gap_map": gap_map,
    }


if __name__ == "__main__":
    result = write_discovery_outputs()
    print(json.dumps({"artifact_id": "e80_repository_discovery_run", "capabilities": result["inventory"]["capability_count"]}, indent=2))
