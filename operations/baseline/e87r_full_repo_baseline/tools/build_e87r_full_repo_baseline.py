#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import os
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


OUTPUT_ROOT = Path(__file__).resolve().parents[1]

REPOS = {
    "bridge_labs": {
        "display_name": "bridge-labs",
        "path": Path("/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs"),
        "expected_head": "4be40ebd78b13fc02fc8adf71d8f0d0ac3e74862",
    },
    "Y_star_gov": {
        "display_name": "Y-star-gov",
        "path": Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov"),
        "expected_head": "738e8118fcf7ab87e08a942f265c17eb3386910d",
    },
    "gov_mcp": {
        "display_name": "gov-mcp",
        "path": Path("/Users/haotianliu/.openclaw/workspace/gov-mcp"),
        "expected_head": "d0181bc8f19d8ae7714bd0f8a220fe12e6ceee90",
    },
}

K9AUDIT_PATH = Path("/Users/haotianliu/.openclaw/workspace/K9Audit")


SOURCE_EXTENSIONS = {
    ".py": "source_python",
    ".js": "source_js_ts",
    ".jsx": "source_js_ts",
    ".ts": "source_js_ts",
    ".tsx": "source_js_ts",
    ".sh": "shell_script",
    ".bash": "shell_script",
    ".zsh": "shell_script",
    ".ps1": "shell_script",
}

CONFIG_EXTENSIONS = {
    ".toml",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".json",
    ".lock",
    ".env",
}

DOC_EXTENSIONS = {".md", ".rst", ".txt"}
DATA_EXTENSIONS = {".csv", ".tsv", ".jsonl", ".db", ".sqlite", ".sqlite3", ".parquet"}
ARCHIVE_EXTENSIONS = {".zip", ".tgz", ".tar", ".gz", ".bak"}

DOMAIN_QUERIES = {
    "bridge_labs_CEO_company_runtime": [
        "CEO",
        "Aiden",
        "mission_command",
        "owner decision",
        "external_validation",
        "action planner",
        "readback",
        "behavior center",
        "CIEU",
        "delivery_bridge",
    ],
    "Y_star_gov_governance_runtime": [
        "validate_ceo_runtime_envelope",
        "validate_ceo_pre_action_packet",
        "CIEUStore",
        "PreToolUse",
        "IntentContract",
        "OmissionEngine",
        "validate_pre_u_packet",
        "validate_prediction_delta",
        "run_governance_contract_dry_run",
        "write_ceo_cognitive_os_cieu_log_record",
    ],
    "gov_mcp_execution_boundary": [
        "gov_check",
        "gov_enforce",
        "dry_run",
        "provider_guard_stack",
        "outbound",
        "receipt",
        "provider_action_executed",
        "external_side_effect",
    ],
    "cross_repo_integration": [
        "Y-star-gov",
        "gov-mcp",
        "K9Audit",
        "CIEUStore",
        "delivery bridge",
        "repository_delivery_bridge",
        "validate_ceo_runtime_envelope",
        "dry_run_outbound_action",
    ],
}


@dataclass
class PythonSymbolIndex:
    repo: str
    path: str
    module: str
    imports: list[str]
    classes: list[dict[str, Any]]
    functions: list[dict[str, Any]]
    constants: list[str]
    all_exports: list[str]
    docstring: str | None
    parse_error: str | None
    category: str
    lifecycle: str


def run(cmd: list[str], cwd: Path) -> str:
    return subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True).stdout


def git_head(repo: Path) -> str:
    return run(["git", "rev-parse", "HEAD"], repo).strip()


def git_branch(repo: Path) -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip()


def tracked_files(repo: Path) -> list[str]:
    return [line for line in run(["git", "ls-files"], repo).splitlines() if line]


def all_files(repo: Path) -> list[str]:
    out: list[str] = []
    for root, dirs, files in os.walk(repo):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in files:
            path = root_path / name
            out.append(str(path.relative_to(repo)))
    return sorted(out)


def classify_file(path: str) -> tuple[str, str]:
    p = Path(path)
    lower = path.lower()
    suffix = p.suffix.lower()
    parts = set(p.parts)
    archive_like = "deprecated" in lower or "archive" in parts or "archives" in parts or "bak" in lower
    runtime_like = any(
        token in lower
        for token in (
            "runtime_state",
            "receipt",
            "readback",
            "state",
            "residual",
            "decision_packet",
            "owner_decision",
        )
    )

    if archive_like:
        lifecycle = "deprecated_or_archive"
    elif any(part in parts for part in {"reports", "generated", "operations", "external_validation"}):
        lifecycle = "generated_or_report"
    elif any(part in parts for part in {"tests", "test", "fixtures", "fixture"}):
        lifecycle = "active_test_or_fixture"
    elif runtime_like:
        lifecycle = "runtime_or_readback_artifact"
    else:
        lifecycle = "active_or_source"

    if archive_like:
        return "archive_deprecated", lifecycle
    if "tests" in parts or p.name.startswith("test_") or "_test" in p.name:
        return "test", lifecycle
    if runtime_like and suffix in {".json", ".jsonl", ".md", ".txt", ".db", ".sqlite", ".sqlite3"}:
        return "runtime_state", lifecycle
    if any(part in parts for part in {"reports", "operations", "external_validation"}) and suffix in {".json", ".md", ".txt"}:
        return "generated_report", lifecycle
    if suffix in SOURCE_EXTENSIONS:
        return SOURCE_EXTENSIONS[suffix], lifecycle
    if suffix in DOC_EXTENSIONS or p.name in {"README", "AGENTS", "CLAUDE"}:
        return "docs", lifecycle
    if suffix in CONFIG_EXTENSIONS or p.name in {"Makefile", "Dockerfile"}:
        return "config", lifecycle
    if suffix in DATA_EXTENSIONS:
        return "data", lifecycle
    if suffix in ARCHIVE_EXTENSIONS:
        return "archive_deprecated", lifecycle
    if "fixture" in lower:
        return "fixture", lifecycle
    return "unknown", lifecycle


def file_entry(repo: Path, path: str, tracked: bool) -> dict[str, Any]:
    full = repo / path
    category, lifecycle = classify_file(path)
    return {
        "path": path,
        "extension": Path(path).suffix.lower(),
        "file_type": category,
        "size_bytes": full.stat().st_size if full.exists() else None,
        "likely_category": category,
        "lifecycle": lifecycle,
        "tracked": tracked,
    }


def build_file_manifest(repo_key: str, repo_info: dict[str, Any]) -> dict[str, Any]:
    repo = repo_info["path"]
    tracked = tracked_files(repo)
    tracked_set = set(tracked)
    allf = all_files(repo)
    entries = [file_entry(repo, path, True) for path in tracked]
    untracked = [path for path in allf if path not in tracked_set and "/.git/" not in path]
    by_category = Counter(entry["likely_category"] for entry in entries)
    by_extension = Counter(entry["extension"] or "[none]" for entry in entries)
    by_top_dir = Counter(Path(entry["path"]).parts[0] if Path(entry["path"]).parts else "" for entry in entries)
    by_lifecycle = Counter(entry["lifecycle"] for entry in entries)
    return {
        "repo": repo_key,
        "display_name": repo_info["display_name"],
        "path": str(repo),
        "expected_head": repo_info["expected_head"],
        "actual_head": git_head(repo),
        "branch": git_branch(repo),
        "tracked_file_count": len(tracked),
        "all_file_count": len(allf),
        "untracked_file_count": len(untracked),
        "untracked_files_sample": untracked[:200],
        "counts_by_category": dict(sorted(by_category.items())),
        "counts_by_extension": dict(sorted(by_extension.items())),
        "counts_by_top_directory": dict(by_top_dir.most_common()),
        "counts_by_lifecycle": dict(sorted(by_lifecycle.items())),
        "tracked_files": entries,
    }


def module_name(path: str) -> str:
    no_suffix = str(Path(path).with_suffix(""))
    return no_suffix.replace("/", ".")


def import_name(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if isinstance(node, ast.ImportFrom):
        mod = "." * node.level + (node.module or "")
        return [f"{mod}.{alias.name}".strip(".") for alias in node.names]
    return []


def public_constants(tree: ast.Module) -> list[str]:
    names: list[str] = []
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and target.id.isupper() and not target.id.startswith("_"):
                    names.append(target.id)
    return sorted(set(names))


def exports(tree: ast.Module) -> list[str]:
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    try:
                        value = ast.literal_eval(node.value)
                    except Exception:
                        return []
                    if isinstance(value, (list, tuple)):
                        return [str(item) for item in value]
    return []


def decorators(node: ast.AST) -> list[str]:
    decos: list[str] = []
    for deco in getattr(node, "decorator_list", []):
        if isinstance(deco, ast.Name):
            decos.append(deco.id)
        elif isinstance(deco, ast.Attribute):
            decos.append(deco.attr)
        elif isinstance(deco, ast.Call):
            func = deco.func
            decos.append(getattr(func, "id", getattr(func, "attr", "call")))
    return decos


def parse_python_file(repo_key: str, repo: Path, path: str) -> PythonSymbolIndex:
    category, lifecycle = classify_file(path)
    full = repo / path
    module = module_name(path)
    try:
        source = full.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        source = full.read_text(encoding="latin-1")
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return PythonSymbolIndex(repo_key, path, module, [], [], [], [], [], None, str(exc), category, lifecycle)

    imports: list[str] = []
    classes: list[dict[str, Any]] = []
    functions: list[dict[str, Any]] = []
    for node in tree.body:
        imports.extend(import_name(node))
        if isinstance(node, ast.ClassDef):
            classes.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "bases": [ast.unparse(base) for base in node.bases],
                    "decorators": decorators(node),
                    "methods": [
                        {
                            "name": child.name,
                            "line": child.lineno,
                            "async": isinstance(child, ast.AsyncFunctionDef),
                            "decorators": decorators(child),
                        }
                        for child in node.body
                        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                    ],
                }
            )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "async": isinstance(node, ast.AsyncFunctionDef),
                    "decorators": decorators(node),
                }
            )
    return PythonSymbolIndex(
        repo=repo_key,
        path=path,
        module=module,
        imports=sorted(set(imports)),
        classes=classes,
        functions=functions,
        constants=public_constants(tree),
        all_exports=exports(tree),
        docstring=ast.get_docstring(tree),
        parse_error=None,
        category=category,
        lifecycle=lifecycle,
    )


def build_code_index(manifests: dict[str, Any]) -> dict[str, Any]:
    python_files: list[PythonSymbolIndex] = []
    entrypoints: list[dict[str, Any]] = []
    for repo_key, repo_info in REPOS.items():
        repo = repo_info["path"]
        for entry in manifests[repo_key]["tracked_files"]:
            path = entry["path"]
            if path.endswith(".py"):
                python_files.append(parse_python_file(repo_key, repo, path))
            if is_entrypoint(path):
                entrypoints.append({"repo": repo_key, "path": path, "reason": entrypoint_reason(path)})

    test_paths = [
        entry["path"]
        for manifest in manifests.values()
        for entry in manifest["tracked_files"]
        if entry["likely_category"] == "test"
    ]
    by_repo = defaultdict(lambda: {"python_files": 0, "functions": 0, "classes": 0, "methods": 0, "parse_errors": 0})
    for item in python_files:
        by_repo[item.repo]["python_files"] += 1
        by_repo[item.repo]["functions"] += len(item.functions)
        by_repo[item.repo]["classes"] += len(item.classes)
        by_repo[item.repo]["methods"] += sum(len(cls["methods"]) for cls in item.classes)
        if item.parse_error:
            by_repo[item.repo]["parse_errors"] += 1

    total_counts = {
        "total_tracked_files": sum(m["tracked_file_count"] for m in manifests.values()),
        "total_python_files": len(python_files),
        "total_functions": sum(len(item.functions) for item in python_files),
        "total_classes": sum(len(item.classes) for item in python_files),
        "total_methods": sum(sum(len(cls["methods"]) for cls in item.classes) for item in python_files),
        "total_tests": sum(m["counts_by_category"].get("test", 0) for m in manifests.values()),
        "total_docs": sum(m["counts_by_category"].get("docs", 0) for m in manifests.values()),
        "total_generated_reports": sum(m["counts_by_category"].get("generated_report", 0) for m in manifests.values()),
        "total_runtime_artifacts": sum(m["counts_by_category"].get("runtime_state", 0) for m in manifests.values()),
        "total_archived_deprecated_files": sum(m["counts_by_category"].get("archive_deprecated", 0) for m in manifests.values()),
    }
    return {
        "artifact_id": "e87r_code_index",
        "counts": total_counts,
        "counts_by_repo": {repo: dict(counts) for repo, counts in by_repo.items()},
        "entrypoints": entrypoints,
        "python_symbol_index": [asdict(item) for item in python_files],
        "test_file_paths": test_paths,
    }


def is_entrypoint(path: str) -> bool:
    p = Path(path)
    lower = path.lower()
    return (
        p.name in {"pyproject.toml", "setup.py", "package.json", "plugin.json", "manifest.json"}
        or "server.py" in lower
        or "cli" in lower
        or "hook" in lower
        or "run_" in p.name
        or path.startswith("scripts/")
        or path.startswith(".github/")
    )


def entrypoint_reason(path: str) -> str:
    lower = path.lower()
    if "server" in lower:
        return "server_or_mcp_registration"
    if "hook" in lower:
        return "hook_or_runtime_adapter"
    if "cli" in lower:
        return "cli_entrypoint"
    if path.startswith("scripts/"):
        return "script_entrypoint"
    if path.startswith(".github/"):
        return "workflow_entrypoint"
    return "package_or_config_entrypoint"


def rg(repo: Path, pattern: str) -> list[dict[str, Any]]:
    result = subprocess.run(
        ["rg", "-n", "--glob", "!*.db", "--glob", "!*.sqlite", "--glob", "!*.pyc", pattern, "."],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    hits: list[dict[str, Any]] = []
    for line in result.stdout.splitlines()[:500]:
        parts = line.split(":", 2)
        if len(parts) == 3:
            hits.append({"path": parts[0].lstrip("./"), "line": int(parts[1]) if parts[1].isdigit() else None, "text": parts[2][:240]})
    return hits


def architecture_domain(
    domain_id: str,
    owner_repo: str,
    status: str,
    purpose: str,
    files: list[str],
    functions: list[str],
    tests: list[str],
    gaps: list[str],
    evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "domain_id": domain_id,
        "canonical_owner_repo": owner_repo,
        "status": status,
        "purpose": purpose,
        "exact_files": files,
        "exact_functions_or_classes": functions,
        "tests": tests,
        "evidence": evidence,
        "gaps": gaps,
    }


def build_architecture_evidence_map(code_index: dict[str, Any]) -> dict[str, Any]:
    symbol_by_path = {
        (item["repo"], item["path"]): item
        for item in code_index["python_symbol_index"]
    }

    def symbols(repo: str, path: str) -> list[str]:
        item = symbol_by_path.get((repo, path))
        if not item:
            return []
        names = [fn["name"] for fn in item["functions"]]
        names.extend(cls["name"] for cls in item["classes"])
        return names

    evidence_searches: dict[str, list[dict[str, Any]]] = {}
    for repo_key, info in REPOS.items():
        for domain, queries in DOMAIN_QUERIES.items():
            hits: list[dict[str, Any]] = []
            for query in queries[:5]:
                hits.extend({**hit, "repo": repo_key, "query": query} for hit in rg(info["path"], query)[:30])
            evidence_searches[f"{repo_key}:{domain}"] = hits[:80]

    domains = [
        architecture_domain(
            "bridge_labs_ceo_company_runtime",
            "bridge-labs",
            "active_runtime_and_generated_artifact_mixture",
            "Owns company/CEO behavior center, mission command, business context, owner decision artifacts, external validation plans, and delivery reports.",
            [
                "office/mission_command/e85_ceo_cognitive_os_runtime_bridge.py",
                "office/mission_command/e46b_ceo_brain_adapter.py",
                "office/aiden_meeting_room/aiden_response_engine.py",
                "office/aiden_meeting_room/company_context_loader.py",
                "operations/external_validation/",
                "scripts/repository_delivery_bridge_submit.py",
            ],
            symbols("bridge_labs", "office/mission_command/e85_ceo_cognitive_os_runtime_bridge.py")
            + symbols("bridge_labs", "office/aiden_meeting_room/aiden_response_engine.py")
            + symbols("bridge_labs", "scripts/repository_delivery_bridge_submit.py"),
            [
                "tests/office/test_e85_ceo_cognitive_os_runtime_bridge.py",
                "tests/office/test_e86_cieu_log_insertion_point_report.py",
            ],
            [
                "CEO intelligence remains split across generated artifacts, meeting-room code, mission_command, and reports.",
                "A single end-to-end CEO runtime session that invokes Y-star-gov and gov-mcp from normal CEO work still needs a major closure milestone.",
            ],
            evidence_searches["bridge_labs:bridge_labs_CEO_company_runtime"],
        ),
        architecture_domain(
            "Y_star_gov_governance_runtime",
            "Y-star-gov",
            "active_runtime",
            "Owns deterministic governance reflexes: CEO Cognitive OS contract, runtime hook, check/enforce patterns, CIEUStore persistence, pre-U validation, omission/delegation/governance loop.",
            [
                "ystar/governance/ceo_cognitive_os_contract.py",
                "ystar/governance/ceo_cognitive_os_runtime_hook.py",
                "ystar/governance/ceo_cognitive_os_cieu_log.py",
                "ystar/governance/cieu_store.py",
                "ystar/governance/pre_u_packet_validator.py",
                "ystar/governance/cieu_prediction_delta.py",
                "ystar/governance/contract_dry_run.py",
                "ystar/adapters/cieu_writer.py",
            ],
            symbols("Y_star_gov", "ystar/governance/ceo_cognitive_os_contract.py")
            + symbols("Y_star_gov", "ystar/governance/ceo_cognitive_os_runtime_hook.py")
            + symbols("Y_star_gov", "ystar/governance/ceo_cognitive_os_cieu_log.py")
            + symbols("Y_star_gov", "ystar/governance/cieu_store.py"),
            [
                "tests/governance/test_ceo_cognitive_os_contract.py",
                "tests/governance/test_ceo_cognitive_os_runtime_hook.py",
                "tests/governance/test_ceo_cognitive_os_cieu_log.py",
                "tests/test_cieu_store.py",
            ],
            [
                "Formal CIEUStore writes are explicit opt-in; no hidden runtime write by default.",
                "Hook/check/enforce integration beyond CEO runtime wrapper still needs normal runtime-session wiring.",
            ],
            evidence_searches["Y_star_gov:Y_star_gov_governance_runtime"],
        ),
        architecture_domain(
            "gov_mcp_execution_boundary",
            "gov-mcp",
            "active_dry_run",
            "Owns MCP/provider/tool execution boundary, gov_check/gov_enforce tools, dry-run outbound adapter, guard stack, and no-send receipts.",
            [
                "gov_mcp/server.py",
                "gov_mcp/company_runtime_tools.py",
                "gov_mcp/outbound/policy.py",
                "gov_mcp/outbound/dry_run_adapter.py",
                "gov_mcp/outbound/provider_guard_stack.py",
                "gov_mcp/models.py",
            ],
            symbols("gov_mcp", "gov_mcp/server.py")
            + symbols("gov_mcp", "gov_mcp/company_runtime_tools.py")
            + symbols("gov_mcp", "gov_mcp/outbound/dry_run_adapter.py")
            + symbols("gov_mcp", "gov_mcp/outbound/provider_guard_stack.py"),
            [
                "tests/test_company_runtime_tools.py",
                "tests/test_outbound_dry_run_adapter.py",
                "tests/test_provider_guard_stack.py",
            ],
            [
                "No live provider execution should be claimed from current evidence.",
                "Owner-activated live-ready preflight and provider promotion remain future work.",
            ],
            evidence_searches["gov_mcp:gov_mcp_execution_boundary"],
        ),
        architecture_domain(
            "cross_repo_runtime_chain",
            "shared_with_clear_owners",
            "partial_runtime_chain",
            "Bridge-labs produces CEO packets; Y-star-gov validates and writes CIEUStore records; gov-mcp provides dry-run provider envelope after allow; K9Audit remains separate stronger evidence-chain boundary unless owner-approved integration is added.",
            [
                "bridge-labs:office/mission_command/e85_ceo_cognitive_os_runtime_bridge.py",
                "Y-star-gov:ystar/governance/ceo_cognitive_os_runtime_hook.py",
                "Y-star-gov:ystar/governance/ceo_cognitive_os_cieu_log.py",
                "gov-mcp:gov_mcp/outbound/dry_run_adapter.py",
                "bridge-labs:scripts/repository_delivery_bridge_submit.py",
            ],
            [
                "bridge-labs.build_ceo_runtime_envelope",
                "Y-star-gov.validate_ceo_runtime_envelope",
                "Y-star-gov.write_ceo_cognitive_os_cieu_log_record",
                "gov-mcp.dry_run_outbound_action",
            ],
            [
                "bridge-labs:tests/office/test_e85_ceo_cognitive_os_runtime_bridge.py",
                "Y-star-gov:tests/governance/test_ceo_cognitive_os_cieu_log.py",
            ],
            [
                "End-to-end normal CEO session binding across all three repos is not yet one canonical runtime command.",
                "K9Audit ledger/hash-chain is read-only reference, not integrated write path.",
            ],
            evidence_searches["bridge_labs:cross_repo_integration"]
            + evidence_searches["Y_star_gov:cross_repo_integration"]
            + evidence_searches["gov_mcp:cross_repo_integration"],
        ),
    ]

    return {
        "artifact_id": "e87r_architecture_evidence_map",
        "domains": domains,
        "domain_queries_used": DOMAIN_QUERIES,
    }


def build_vocabulary_map() -> dict[str, Any]:
    terms = [
        {
            "term": "CEO behavior center",
            "canonical_owner": "bridge-labs",
            "definition": "Business/company-facing CEO behavior, mission command, readback, owner decisions, strategy artifacts, and external validation planning.",
            "evidence_files": ["office/aiden_meeting_room/", "office/mission_command/", "operations/external_validation/"],
            "not_owner": ["gov-mcp is not the sole behavior center; it is an execution boundary."],
        },
        {
            "term": "CEO brain",
            "canonical_owner": "bridge-labs",
            "definition": "Readback/adapters/history/context used by CEO-facing company runtime; currently partly artifact/readback driven.",
            "evidence_files": ["office/mission_command/e46b_ceo_brain_adapter.py", "office/aiden_meeting_room/"],
        },
        {
            "term": "CEO intelligence loop",
            "canonical_owner": "bridge-labs with Y-star-gov gates",
            "definition": "Repo/history recall, candidate route generation, counterfactuals, commercial sharpness, adversarial critique, what-not-to-do, pre-action prediction, and learning update before major action.",
            "evidence_files": ["operations/external_validation/e80_*", "office/mission_command/e85_ceo_cognitive_os_runtime_bridge.py"],
        },
        {
            "term": "CEO runtime nervous system",
            "canonical_owner": "cross-repo",
            "definition": "bridge-labs CEO packet -> Y-star-gov runtime hook -> formal CIEUStore write if invoked -> gov-mcp dry-run boundary where provider/tool action is involved -> post-action residual.",
            "evidence_files": ["office/mission_command/e85_ceo_cognitive_os_runtime_bridge.py", "ystar/governance/ceo_cognitive_os_runtime_hook.py", "gov_mcp/outbound/dry_run_adapter.py"],
        },
        {
            "term": "governance reflex center",
            "canonical_owner": "Y-star-gov",
            "definition": "Deterministic validation, check/enforce/hook contracts, omission/delegation/intervention, CEO Cognitive OS runtime hook, and CIEUStore.",
            "evidence_files": ["ystar/governance/", "ystar/kernel/", "ystar/adapters/"],
        },
        {
            "term": "execution boundary",
            "canonical_owner": "gov-mcp",
            "definition": "MCP/provider/tool envelope and guard layer. Current evidence supports dry-run/no-send receipts, not live provider execution.",
            "evidence_files": ["gov_mcp/server.py", "gov_mcp/company_runtime_tools.py", "gov_mcp/outbound/"],
        },
        {
            "term": "provider/tool motor interface",
            "canonical_owner": "gov-mcp",
            "definition": "Outbound dry-run adapter, provider guard stack, receipts, and future provider promotion boundary.",
            "evidence_files": ["gov_mcp/outbound/dry_run_adapter.py", "gov_mcp/outbound/provider_guard_stack.py"],
        },
        {
            "term": "CIEU memory / audit store",
            "canonical_owner": "Y-star-gov",
            "definition": "SQLite CIEUStore records, query, stats, seal, verify. E86 added explicit CEO Cognitive OS writer.",
            "evidence_files": ["ystar/governance/cieu_store.py", "ystar/governance/ceo_cognitive_os_cieu_log.py"],
        },
        {
            "term": "K9Audit evidence chain",
            "canonical_owner": "K9Audit",
            "definition": "Separate stronger hash-chain CIEU ledger/verifier. E87R did not find/claim a write integration from CEO Cognitive OS into K9Audit.",
            "evidence_files": ["K9Audit:README.md", "K9Audit:k9log/core.py", "K9Audit:k9log/verifier.py"],
        },
        {
            "term": "owner decision path",
            "canonical_owner": "bridge-labs produces, Y-star-gov escalates",
            "definition": "Y-star-gov returns ESCALATE for complete but authority-bound actions; bridge-labs records owner decision packets and does not execute.",
            "evidence_files": ["ystar/governance/ceo_cognitive_os_contract.py", "office/mission_command/e85_ceo_cognitive_os_runtime_bridge.py"],
        },
        {
            "term": "L4 external feedback",
            "canonical_owner": "bridge-labs under Y-star-gov/governed boundary",
            "definition": "A future owner-approved external feedback pilot; current repo evidence shows planning and packets, not executed feedback.",
            "evidence_files": ["operations/external_validation/", "office/mission_command/"],
        },
        {
            "term": "L5 revenue loop",
            "canonical_owner": "bridge-labs business runtime, gated by Y-star-gov and gov-mcp",
            "definition": "Future customer/revenue/payment/pricing learning loop. Current evidence is not complete and must not be claimed.",
            "evidence_files": ["operations/external_validation/", "gov_mcp/outbound/"],
        },
    ]
    return {
        "artifact_id": "e87r_stable_vocabulary_and_owner_map",
        "terms": terms,
        "guardrails": [
            "gov-mcp is not the sole behavior center; code evidence places it at provider/tool execution boundary.",
            "Do not call Y-star-gov a business strategy brain; it is the governance reflex center.",
            "Do not call Y-star-gov CIEUStore writes K9Audit ledger writes.",
            "Do not claim complete L5 revenue/customer/payment loop from runtime-foundation evidence.",
        ],
    }


def build_l5_truth_table() -> dict[str, Any]:
    levels = [
        {
            "level": "L5-A Runtime Foundation",
            "status": "partial_to_complete_foundation",
            "evidence_files": [
                "bridge-labs:office/mission_command/e85_ceo_cognitive_os_runtime_bridge.py",
                "Y-star-gov:ystar/governance/ceo_cognitive_os_runtime_hook.py",
                "Y-star-gov:ystar/governance/ceo_cognitive_os_cieu_log.py",
                "Y-star-gov:tests/governance/test_ceo_cognitive_os_cieu_log.py",
            ],
            "tests": ["Y-star-gov CEO runtime hook and CIEU writer tests", "bridge-labs E85 runtime bridge tests"],
            "complete_parts": [
                "major-action classification",
                "CEO Cognitive OS pre-action contract",
                "Y-star-gov runtime hook",
                "ALLOW / REQUIRE_REVISION / DENY / ESCALATE routing",
                "formal CIEUStore write path when invoked",
                "post-action residual requirement",
            ],
            "gaps": ["normal CEO session still needs one canonical end-to-end runner binding all parts"],
            "next_milestone_needed": "E87 end-to-end CEO runtime session binding",
        },
        {
            "level": "L5-B CEO Intelligence Loop",
            "status": "partial",
            "evidence_files": ["bridge-labs:operations/external_validation/e80*", "bridge-labs:office/aiden_meeting_room/", "bridge-labs:office/mission_command/"],
            "tests": ["report consistency and selected runtime bridge tests"],
            "complete_parts": ["schemas/artifacts for recall, counterfactual, critique, what-not-to-do"],
            "gaps": ["not yet consistently invoked as live CEO intelligence before every major action"],
            "next_milestone_needed": "E88 upgrade CEO intelligence loop and bind it before runtime packet creation",
        },
        {
            "level": "L5-C Controlled External Action",
            "status": "partial_dry_run_only",
            "evidence_files": ["gov-mcp:gov_mcp/outbound/dry_run_adapter.py", "gov-mcp:gov_mcp/outbound/provider_guard_stack.py", "bridge-labs:office/mission_command/e85_ceo_cognitive_os_runtime_bridge.py"],
            "tests": ["gov-mcp dry-run and bridge-labs provider route tests"],
            "complete_parts": ["dry-run outbound guard behavior", "no-send invariant", "receipts/candidate records"],
            "gaps": ["owner-activated live-ready preflight not complete; no live provider execution authorized"],
            "next_milestone_needed": "E89 owner-activated live-ready gov-mcp preflight without default live execution",
        },
        {
            "level": "L5-D Revenue/Customer/Payment Loop",
            "status": "absent_or_not_executed",
            "evidence_files": ["bridge-labs:operations/external_validation/", "bridge-labs:reports/"],
            "tests": [],
            "complete_parts": [],
            "gaps": [
                "no real feedback execution",
                "no buyer/customer validation evidence",
                "no paid signal",
                "no pricing validation",
                "no payment/revenue evidence",
                "no business learning loop from actual customer feedback",
            ],
            "next_milestone_needed": "E90/E91 owner-approved minimal L4 feedback then revenue-path learning loop",
        },
    ]
    return {"artifact_id": "e87r_l5_truth_table", "levels": levels}


def build_gap_analysis() -> dict[str, Any]:
    capabilities = [
        ("discover opportunities", "implemented_but_not_wired", ["bridge-labs:office/aiden_meeting_room/", "bridge-labs:operations/external_validation/"]),
        ("recall internal and historical capabilities", "implemented_but_not_wired", ["bridge-labs:operations/baseline/e87r_full_repo_baseline/code_index.json", "bridge-labs:operations/external_validation/e80*"]),
        ("compare routes non-trivially", "artifact_report_only", ["bridge-labs:operations/external_validation/e80*", "bridge-labs:operations/external_validation/e81*"]),
        ("select shortest credible cash path", "partial", ["bridge-labs:operations/external_validation/", "bridge-labs:office/aiden_meeting_room/"]),
        ("generate governed action packets", "implemented", ["bridge-labs:office/mission_command/e85_ceo_cognitive_os_runtime_bridge.py"]),
        ("pass deterministic runtime governance", "implemented", ["Y-star-gov:ystar/governance/ceo_cognitive_os_runtime_hook.py"]),
        ("use CIEU records as memory/evidence", "partial", ["Y-star-gov:ystar/governance/cieu_store.py", "Y-star-gov:ystar/governance/ceo_cognitive_os_cieu_log.py"]),
        ("use gov-mcp to safely reach tool/provider boundaries", "simulated_dry_run_only", ["gov-mcp:gov_mcp/outbound/dry_run_adapter.py"]),
        ("collect real external feedback", "missing", ["bridge-labs:operations/external_validation/"]),
        ("convert feedback into residual learning", "artifact_report_only", ["bridge-labs:operations/external_validation/"]),
        ("update strategy", "partial", ["bridge-labs:office/aiden_meeting_room/", "bridge-labs:operations/external_validation/"]),
        ("move toward revenue/customer/payment loop under owner-approved boundaries", "unsafe_to_execute_yet", ["gov-mcp:gov_mcp/outbound/", "bridge-labs:operations/external_validation/"]),
    ]
    return {
        "artifact_id": "e87r_final_goal_gap_analysis",
        "final_goal": "high-intelligence CEO agent company runtime",
        "capabilities": [
            {
                "capability": capability,
                "status": status,
                "evidence_files": evidence,
                "gap": gap_for_status(status),
            }
            for capability, status, evidence in capabilities
        ],
    }


def gap_for_status(status: str) -> str:
    return {
        "implemented": "needs end-to-end regression only",
        "partial": "exists in pieces but not a full closed loop",
        "implemented_but_not_wired": "code/artifacts exist but normal CEO runtime does not always invoke it",
        "artifact_report_only": "documented/generated but not active runtime behavior",
        "simulated_dry_run_only": "safe dry-run exists; live execution remains unauthorized",
        "missing": "no executed evidence found",
        "unsafe_to_execute_yet": "requires owner approval and stronger gates before live action",
    }.get(status, "inspect_more")


def build_roadmap() -> dict[str, Any]:
    milestones = [
        {
            "milestone": "E87_End_to_End_CEO_Runtime_Session_Binding_R1",
            "goal": "Bind existing bridge-labs CEO behavior center to Y-star-gov runtime hook, E86 CIEUStore writer, gov-mcp dry-run, and post-action residual in one canonical internal CEO runtime session.",
            "repo_scope": ["bridge-labs", "Y-star-gov read/import", "gov-mcp dry-run import"],
            "existing_files_to_reuse": [
                "office/mission_command/e85_ceo_cognitive_os_runtime_bridge.py",
                "Y-star-gov:ystar/governance/ceo_cognitive_os_runtime_hook.py",
                "Y-star-gov:ystar/governance/ceo_cognitive_os_cieu_log.py",
                "gov-mcp:gov_mcp/outbound/dry_run_adapter.py",
            ],
            "likely_files_to_modify": ["bridge-labs:office/mission_command/e87_ceo_runtime_session.py", "bridge-labs:tests/office/test_e87_ceo_runtime_session.py"],
            "no_new_wheel_constraints": ["do not rewrite Y-star-gov validator", "do not duplicate gov-mcp dry-run", "do not invent another CIEU store"],
            "runtime_chain_to_prove": "CEO action -> packet -> Y-star-gov decision -> formal CIEUStore write -> gov-mcp dry-run if provider category -> post-action residual",
            "tests_required": ["ALLOW/REQUIRE_REVISION/DENY/ESCALATE route tests", "formal CIEUStore write test", "no external side effect test"],
            "completion_criteria": ["one canonical internal runtime session fixture passes", "no L4/L5 live claim"],
            "what_must_not_be_claimed": ["L4 external feedback executed", "L5 revenue loop complete", "K9Audit ledger integration"],
            "next_routing": "E88 CEO intelligence loop if runtime session passes",
        },
        {
            "milestone": "E88_CEO_Intelligence_Loop_Runtime_Upgrade_R1",
            "goal": "Make repo/history recall, route generation, counterfactual comparison, commercial sharpness, adversarial critique, and action selection mandatory before packet creation.",
            "repo_scope": ["bridge-labs primary", "Y-star-gov contract unchanged"],
            "existing_files_to_reuse": ["operations/baseline/e87r_full_repo_baseline/", "office/aiden_meeting_room/", "office/mission_command/"],
            "likely_files_to_modify": ["bridge-labs:office/mission_command/e88_ceo_intelligence_loop.py"],
            "no_new_wheel_constraints": ["reuse E87R code index and existing readbacks", "do not create another CEO brain"],
            "runtime_chain_to_prove": "full repo evidence -> candidates -> counterfactuals -> selected action -> packet",
            "tests_required": ["non-prompt evidence use", "counterfactual quality gate", "commercial sharpness gate"],
            "completion_criteria": ["every major action packet includes evidence-backed intelligence loop output"],
            "what_must_not_be_claimed": ["customer validation", "paid signal"],
            "next_routing": "E89 controlled external action readiness",
        },
        {
            "milestone": "E89_GovMCP_Owner_Activated_Live_Ready_Preflight_R1",
            "goal": "Upgrade gov-mcp from dry-run-only receipt to owner-activated live-ready preflight while keeping real provider execution disabled by default.",
            "repo_scope": ["gov-mcp", "bridge-labs integration fixtures", "Y-star-gov decision import"],
            "existing_files_to_reuse": ["gov_mcp/outbound/dry_run_adapter.py", "gov_mcp/outbound/provider_guard_stack.py", "gov_mcp/company_runtime_tools.py"],
            "likely_files_to_modify": ["gov-mcp outbound policy/tests", "bridge-labs integration fixture"],
            "no_new_wheel_constraints": ["do not bypass provider guard stack", "do not enable live send by default"],
            "runtime_chain_to_prove": "Y-star-gov ALLOW + owner activation + guard pass -> live-ready receipt, no live send",
            "tests_required": ["no-send invariant", "owner activation missing blocks", "idempotency/rate limit/suppression"],
            "completion_criteria": ["live-ready preflight exists but no provider action executes"],
            "what_must_not_be_claimed": ["live provider execution", "customer feedback"],
            "next_routing": "E90 owner-approved minimal L4 feedback pilot",
        },
        {
            "milestone": "E90_Owner_Approved_Minimal_L4_Feedback_Pilot_Through_Runtime_R1",
            "goal": "Run the first owner-approved minimal L4 feedback pilot or owner-mediated external feedback draft through the full runtime chain.",
            "repo_scope": ["bridge-labs primary", "Y-star-gov governance", "gov-mcp preflight if provider/tool used"],
            "existing_files_to_reuse": ["office/mission_command/e87_ceo_runtime_session.py", "office/mission_command/e88_ceo_intelligence_loop.py"],
            "likely_files_to_modify": ["bridge-labs external validation pilot artifacts/tests"],
            "no_new_wheel_constraints": ["owner approval required", "no mass outreach", "no publication/payment/login"],
            "runtime_chain_to_prove": "owner-approved L4 packet -> Y-star-gov -> CIEUStore -> gov-mcp preflight/dry-run -> residual",
            "tests_required": ["approval-boundary tests", "no overclaim tests", "residual learning candidate test"],
            "completion_criteria": ["first real or owner-mediated external feedback packet recorded honestly"],
            "what_must_not_be_claimed": ["customer validation unless real feedback exists", "paid signal"],
            "next_routing": "E91 feedback-to-revenue learning loop",
        },
        {
            "milestone": "E91_Feedback_To_Revenue_Path_Learning_Loop_R1",
            "goal": "Convert L4 feedback into residual learning, offer/pricing/route update, and next governed action.",
            "repo_scope": ["bridge-labs primary", "Y-star-gov gates", "gov-mcp only if controlled action needed"],
            "existing_files_to_reuse": ["operations/external_validation/", "office/mission_command/", "Y-star-gov CIEUStore records"],
            "likely_files_to_modify": ["bridge-labs feedback learning loop module/tests"],
            "no_new_wheel_constraints": ["do not invent paid signal", "do not claim pricing validation without evidence"],
            "runtime_chain_to_prove": "feedback -> residual -> route/pricing hypothesis update -> next governed packet",
            "tests_required": ["feedback evidence classification", "residual update", "no paid/pricing overclaim"],
            "completion_criteria": ["feedback changes next action intelligently and auditably"],
            "what_must_not_be_claimed": ["L5 revenue loop complete until real revenue/payment evidence exists"],
            "next_routing": "owner-approved next feedback/revenue experiment only after evidence",
        },
    ]
    return {"artifact_id": "e87r_next_engineering_roadmap", "milestones": milestones}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def write_md(path: Path, title: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# " + title + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def manifest_md(manifest: dict[str, Any]) -> list[str]:
    return [
        f"- Repo: `{manifest['display_name']}`",
        f"- Path: `{manifest['path']}`",
        f"- Branch: `{manifest['branch']}`",
        f"- Expected HEAD: `{manifest['expected_head']}`",
        f"- Actual HEAD: `{manifest['actual_head']}`",
        f"- Tracked files: `{manifest['tracked_file_count']}`",
        f"- All local files: `{manifest['all_file_count']}`",
        f"- Untracked files: `{manifest['untracked_file_count']}`",
        "",
        "## Category Counts",
        *[f"- `{key}`: {value}" for key, value in manifest["counts_by_category"].items()],
        "",
        "## Top Directories",
        *[f"- `{key}`: {value}" for key, value in list(manifest["counts_by_top_directory"].items())[:40]],
        "",
        "Full tracked file manifest is in the paired JSON file.",
    ]


def code_index_md(index: dict[str, Any]) -> list[str]:
    counts = index["counts"]
    lines = ["## Counts"]
    lines.extend(f"- `{key}`: {value}" for key, value in counts.items())
    lines.append("")
    lines.append("## Counts By Repo")
    for repo, repo_counts in index["counts_by_repo"].items():
        lines.append(f"- `{repo}`: " + ", ".join(f"{k}={v}" for k, v in repo_counts.items()))
    lines.append("")
    lines.append("## Entrypoints Sample")
    for entry in index["entrypoints"][:120]:
        lines.append(f"- `{entry['repo']}:{entry['path']}` - {entry['reason']}")
    lines.append("")
    lines.append("Full Python symbol index is in the paired JSON file.")
    return lines


def architecture_md(data: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for domain in data["domains"]:
        lines.extend([
            f"## {domain['domain_id']}",
            f"- Owner: `{domain['canonical_owner_repo']}`",
            f"- Status: `{domain['status']}`",
            f"- Purpose: {domain['purpose']}",
            "- Files: " + ", ".join(f"`{path}`" for path in domain["exact_files"][:12]),
            "- Tests: " + (", ".join(f"`{path}`" for path in domain["tests"]) or "none found"),
            "- Gaps: " + "; ".join(domain["gaps"]),
            "",
        ])
    return lines


def vocabulary_md(data: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for item in data["terms"]:
        lines.extend([
            f"## {item['term']}",
            f"- Canonical owner: `{item['canonical_owner']}`",
            f"- Definition: {item['definition']}",
            "- Evidence: " + ", ".join(f"`{path}`" for path in item.get("evidence_files", [])),
            "",
        ])
    lines.extend(["## Guardrails", *[f"- {item}" for item in data["guardrails"]]])
    return lines


def l5_md(data: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for level in data["levels"]:
        lines.extend([
            f"## {level['level']}",
            f"- Status: `{level['status']}`",
            "- Evidence: " + ", ".join(f"`{path}`" for path in level["evidence_files"]),
            "- Complete parts: " + ("; ".join(level["complete_parts"]) or "none"),
            "- Gaps: " + "; ".join(level["gaps"]),
            f"- Exact next milestone needed: `{level['next_milestone_needed']}`",
            "",
        ])
    return lines


def gap_md(data: dict[str, Any]) -> list[str]:
    return [
        f"- Final goal: {data['final_goal']}",
        "",
        *[
            f"- `{item['capability']}`: `{item['status']}` - {item['gap']} Evidence: "
            + ", ".join(f"`{path}`" for path in item["evidence_files"])
            for item in data["capabilities"]
        ],
    ]


def roadmap_md(data: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for milestone in data["milestones"]:
        lines.extend([
            f"## {milestone['milestone']}",
            f"- Goal: {milestone['goal']}",
            "- Repo scope: " + ", ".join(f"`{repo}`" for repo in milestone["repo_scope"]),
            "- Existing files to reuse: " + ", ".join(f"`{path}`" for path in milestone["existing_files_to_reuse"]),
            "- Likely files to modify: " + ", ".join(f"`{path}`" for path in milestone["likely_files_to_modify"]),
            "- Runtime chain to prove: " + milestone["runtime_chain_to_prove"],
            "- Tests required: " + "; ".join(milestone["tests_required"]),
            "- Completion criteria: " + "; ".join(milestone["completion_criteria"]),
            "- Must not claim: " + "; ".join(milestone["what_must_not_be_claimed"]),
            f"- Next routing: `{milestone['next_routing']}`",
            "",
        ])
    return lines


def main() -> int:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    manifests = {repo: build_file_manifest(repo, info) for repo, info in REPOS.items()}
    for repo, manifest in manifests.items():
        write_json(OUTPUT_ROOT / f"{repo}_file_manifest.json", manifest)
        write_md(OUTPUT_ROOT / f"{repo}_file_manifest.md", f"E87R {manifest['display_name']} File Manifest", manifest_md(manifest))

    code_index = build_code_index(manifests)
    write_json(OUTPUT_ROOT / "code_index.json", code_index)
    write_md(OUTPUT_ROOT / "code_index.md", "E87R Full Code Index", code_index_md(code_index))

    architecture = build_architecture_evidence_map(code_index)
    write_json(OUTPUT_ROOT / "architecture_evidence_map.json", architecture)
    write_md(OUTPUT_ROOT / "architecture_evidence_map.md", "E87R Architecture Evidence Map", architecture_md(architecture))

    vocabulary = build_vocabulary_map()
    write_json(OUTPUT_ROOT / "stable_vocabulary_and_owner_map.json", vocabulary)
    write_md(OUTPUT_ROOT / "stable_vocabulary_and_owner_map.md", "E87R Stable Vocabulary And Owner Map", vocabulary_md(vocabulary))

    l5 = build_l5_truth_table()
    write_json(OUTPUT_ROOT / "l5_truth_table.json", l5)
    write_md(OUTPUT_ROOT / "l5_truth_table.md", "E87R L5 Truth Table", l5_md(l5))

    gaps = build_gap_analysis()
    write_json(OUTPUT_ROOT / "final_goal_gap_analysis.json", gaps)
    write_md(OUTPUT_ROOT / "final_goal_gap_analysis.md", "E87R Final Goal Gap Analysis", gap_md(gaps))

    roadmap = build_roadmap()
    write_json(OUTPUT_ROOT / "next_engineering_roadmap.json", roadmap)
    write_md(OUTPUT_ROOT / "next_engineering_roadmap.md", "E87R Next Engineering Roadmap", roadmap_md(roadmap))

    summary = {
        "artifact_id": "e87r_full_repo_baseline_summary",
        "job_id": "E87R_FULL_REPO_BASELINE_COGNITION_AND_NEXT_ENGINEERING_MAP_R1",
        "repos": {
            repo: {
                "path": manifest["path"],
                "expected_head": manifest["expected_head"],
                "actual_head": manifest["actual_head"],
                "branch": manifest["branch"],
                "tracked_file_count": manifest["tracked_file_count"],
            }
            for repo, manifest in manifests.items()
        },
        "code_counts": code_index["counts"],
        "real_architecture_baseline": {
            "bridge_labs_role": "CEO/company behavior center, mission command, business artifacts, owner decisions, external validation planning, delivery reports.",
            "Y_star_gov_role": "governance reflex center, deterministic contracts/hooks/checks, CIEUStore formal governance records.",
            "gov_mcp_role": "provider/tool execution boundary, dry-run/no-send envelope and receipts.",
            "K9Audit_boundary": "separate stronger hash-chain evidence ledger; inspected read-only only; no integration write claimed.",
        },
        "L5_truth_table_summary": {level["level"]: level["status"] for level in l5["levels"]},
        "biggest_previous_misconception_corrected": "gov-mcp is not the CEO behavior center; bridge-labs owns CEO/company behavior, Y-star-gov owns governance reflexes, and gov-mcp owns provider/tool execution boundary.",
        "reports": [
            "bridge_labs_file_manifest.json",
            "Y_star_gov_file_manifest.json",
            "gov_mcp_file_manifest.json",
            "code_index.json",
            "architecture_evidence_map.json",
            "stable_vocabulary_and_owner_map.json",
            "l5_truth_table.json",
            "final_goal_gap_analysis.json",
            "next_engineering_roadmap.json",
        ],
    }
    write_json(OUTPUT_ROOT / "baseline_summary.json", summary)
    write_md(
        OUTPUT_ROOT / "baseline_summary.md",
        "E87R Full Repo Baseline Summary",
        [
            f"- Job: `{summary['job_id']}`",
            f"- Total tracked files: `{code_index['counts']['total_tracked_files']}`",
            f"- Total Python files parsed: `{code_index['counts']['total_python_files']}`",
            f"- Total functions: `{code_index['counts']['total_functions']}`",
            f"- Total classes: `{code_index['counts']['total_classes']}`",
            "",
            "## Real Architecture Baseline",
            *[f"- `{key}`: {value}" for key, value in summary["real_architecture_baseline"].items()],
            "",
            "## L5 Truth Table",
            *[f"- `{key}`: `{value}`" for key, value in summary["L5_truth_table_summary"].items()],
            "",
            f"Biggest corrected misconception: {summary['biggest_previous_misconception_corrected']}",
        ],
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
