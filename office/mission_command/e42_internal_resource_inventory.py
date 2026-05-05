from __future__ import annotations

import hashlib
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
KNOWN_REPOS = {
    "ystar-bridge-labs": REPO_ROOT,
    "Y-star-gov": Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov"),
    "gov-mcp": Path("/Users/haotianliu/.openclaw/workspace/gov-mcp"),
    "ystar-company": Path("/Users/haotianliu/.openclaw/workspace/ystar-company"),
    "K9Audit": Path("/Users/haotianliu/.openclaw/workspace/K9Audit"),
    "k9log-core": Path("/Users/haotianliu/.openclaw/workspace/k9log-core"),
}
OWNING_LAYER = {
    "ystar-bridge-labs": "bridge_labs_strategy",
    "Y-star-gov": "ystar_gov_governance_kernel",
    "gov-mcp": "gov_mcp_execution_boundary",
    "ystar-company": "ystar_company_commercial",
    "K9Audit": "k9audit_audit_layer",
    "k9log-core": "k9audit_audit_layer",
}
PRUNE_DIRS = {
    ".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "node_modules", ".next", "dist", "build", ".venv", "venv",
}
TEXT_EXTENSIONS = {".py", ".md", ".json", ".jsonl", ".yaml", ".yml", ".txt", ".toml"}
TARGET_DIRS = {
    "ystar-bridge-labs": [
        ".", "agents", "governance", "knowledge", "memory", "reports/daily",
        "reports/insights", "reports/integration", "scripts", "office/mission_command",
        "operations/external_validation", "operations/knowledge_graph", "tests/office",
    ],
    "Y-star-gov": [".", "ystar", "src", "tests", "docs"],
    "gov-mcp": [".", "gov_mcp", "src", "tests", "docs", "scripts"],
    "ystar-company": [".", "governance", "reports", "runtime_packets"],
    "K9Audit": [".", "src", "tests", "docs"],
    "k9log-core": [".", "src", "tests", "docs"],
}

TAG_RULES = [
    ("delivery", ["delivery", "repository_delivery", "bridge_status", "check_repository_delivery"]),
    ("evidence", ["evidence", "receipt", "claim", "source", "public_readonly"]),
    ("claim_graph", ["claim_graph", "claim graph", "deep_research", "contradiction"]),
    ("frontier_capability_import", ["frontier", "capability_import", "import_loop", "e41"]),
    ("governance", ["governance", "intentcontract", "check", "enforce", "obligation", "delegation"]),
    ("mcp_execution_boundary", ["gov_mcp", "mcp", "tool execution", "gov_check", "gov_enforce"]),
    ("ceo_memory", ["ceo", "brain", "kg", "memory", "directive", "daily"]),
    ("czl", ["czl", "closure", "subgoal"]),
    ("cieu", ["cieu", "event chain", "tamper"]),
    ("route_selection", ["route", "shortlist", "decision", "owner_decision"]),
    ("public_research", ["public", "readonly", "research", "source_collection"]),
    ("expert_route", ["expert", "review", "preflight", "no_send"]),
    ("commercial", ["commercial", "buyer", "pricing", "revenue", "market"]),
    ("audit", ["audit", "k9", "logging", "doctor"]),
    ("task_preflight", ["preflight", "task", "reuse", "router", "capability"]),
]


def _sha(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]


def _tokens(value: str) -> set[str]:
    return {token for token in re.split(r"[^a-z0-9]+", value.lower()) if len(token) >= 2}


def _read_sample(path: Path) -> str:
    try:
        if path.stat().st_size > 2_000_000:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")[:4000]
    except Exception:
        return ""


def iter_candidate_files(repo: str, root: Path, max_files: int = 2500) -> list[Path]:
    if not root.exists():
        return []
    seen: dict[str, Path] = {}
    for target in TARGET_DIRS.get(repo, ["."]):
        base = root / target
        if not base.exists():
            continue
        if target == "." and base.is_dir():
            candidates = [item for item in sorted(base.iterdir()) if item.is_file() and item.suffix.lower() in TEXT_EXTENSIONS]
        elif base.is_file():
            candidates = [base]
        else:
            candidates = []
            for current, dirnames, filenames in os.walk(base):
                dirnames[:] = [name for name in dirnames if name not in PRUNE_DIRS and not name.startswith(".git")]
                for filename in filenames:
                    path = Path(current) / filename
                    if path.suffix.lower() in TEXT_EXTENSIONS:
                        candidates.append(path)
        for path in candidates:
            try:
                rel = str(path.relative_to(root))
            except ValueError:
                continue
            if rel not in seen:
                seen[rel] = path
            if len(seen) >= max_files:
                break
        if len(seen) >= max_files:
            break
    return [seen[key] for key in sorted(seen)]


def classify_resource_type(repo: str, rel_path: str) -> str:
    path = rel_path.lower()
    name = Path(path).name
    if repo == "Y-star-gov":
        return "governance_contract" if path.endswith((".md", ".json", ".py")) else "unknown"
    if repo == "gov-mcp":
        return "MCP_boundary"
    if "repository_delivery" in path or "delivery_bridge" in path:
        return "delivery_bridge"
    if path.startswith("tests/") or name.startswith("test_"):
        return "test"
    if path.startswith("scripts/") and path.endswith(".py"):
        return "script"
    if path.startswith("office/mission_command/") and path.endswith(".py"):
        return "runtime_module"
    if path.startswith("operations/knowledge_graph/") and path.endswith(".jsonl"):
        return "KG_delta"
    if path.startswith("operations/knowledge_graph/") and ("brain" in path or "kg" in path):
        return "CEO_brain_update"
    if path.startswith("operations/external_validation/") and "czl_closure" in path:
        return "CZL_closure"
    if path.startswith("operations/external_validation/") and ("owner" in path or "decision_packet" in path):
        return "owner_decision_packet"
    if path.startswith("operations/external_validation/") and any(term in path for term in ["evidence", "claim", "receipt", "cieu"]):
        return "CIEU_or_evidence_artifact"
    if path.startswith("operations/external_validation/"):
        return "artifact"
    if path.startswith("reports/"):
        return "report"
    if path.startswith("governance/"):
        return "governance_contract"
    return "unknown"


def capability_tags_for(repo: str, rel_path: str, sample: str) -> list[str]:
    haystack = f"{repo} {rel_path} {sample[:1200]}".lower()
    tags = [tag for tag, needles in TAG_RULES if any(needle in haystack for needle in needles)]
    if repo == "Y-star-gov" and "governance" not in tags:
        tags.append("governance")
    if repo == "gov-mcp" and "mcp_execution_boundary" not in tags:
        tags.append("mcp_execution_boundary")
    if repo in {"K9Audit", "k9log-core"} and "audit" not in tags:
        tags.append("audit")
    return sorted(set(tags)) or ["general"]


def input_output_artifacts(rel_path: str, sample: str) -> tuple[list[str], list[str]]:
    references = sorted(set(re.findall(r"(operations/[A-Za-z0-9_./-]+|reports/[A-Za-z0-9_./-]+|tests/[A-Za-z0-9_./-]+)", sample)))
    outputs = [ref for ref in references if any(token in rel_path.lower() for token in ["builder", "update", "closure", "generator"])]
    inputs = [ref for ref in references if ref not in outputs]
    return inputs[:12], outputs[:12]


def infer_reuse_mode(repo: str, resource_type: str, tags: list[str]) -> str:
    if repo != "ystar-bridge-labs":
        return "do_not_modify"
    if resource_type in {"runtime_module", "script"}:
        return "direct_call"
    if resource_type == "test":
        return "use_as_test_fixture"
    if resource_type in {"artifact", "CIEU_or_evidence_artifact", "CEO_brain_update", "KG_delta", "CZL_closure", "owner_decision_packet"}:
        return "read_as_input"
    if resource_type == "report":
        return "use_as_report_context"
    if resource_type == "delivery_bridge":
        return "direct_call"
    return "extend_thin_adapter"


def boundary_notes(repo: str, resource_type: str, tags: list[str]) -> str:
    if repo == "Y-star-gov":
        return "Y-star-gov owns governance semantics; bridge-labs may reference but must not rebuild or modify in this milestone."
    if repo == "gov-mcp":
        return "gov-mcp owns MCP/tool execution boundary; bridge-labs must not create a substitute execution layer."
    if repo in {"K9Audit", "k9log-core"}:
        return "Audit/log capability is read-only unless explicitly approved."
    if "cieu" in tags:
        return "Evidence artifacts do not replace CIEU tamper-evident event semantics."
    if "ceo_memory" in tags:
        return "Use existing CEO brain/KG/daily memory conventions; do not create a second brain."
    return "bridge-labs strategy/runtime resource; extend rather than rebuild when possible."


def build_internal_resource_inventory(repos: dict[str, Path] | None = None, max_files_per_repo: int = 2500) -> dict[str, Any]:
    repos = repos or KNOWN_REPOS
    resources: list[dict[str, Any]] = []
    test_paths_by_stem: dict[str, list[str]] = defaultdict(list)
    candidate_files_by_repo = {repo: iter_candidate_files(repo, root, max_files_per_repo) for repo, root in repos.items()}
    for repo, paths in candidate_files_by_repo.items():
        root = repos[repo]
        for path in paths:
            rel_path = str(path.relative_to(root))
            if "test" in Path(rel_path).name.lower() or rel_path.startswith("tests/"):
                test_paths_by_stem[Path(rel_path).stem.replace("test_", "")].append(rel_path)

    for repo, paths in candidate_files_by_repo.items():
        root = repos[repo]
        for path in paths:
            rel_path = str(path.relative_to(root))
            sample = _read_sample(path)
            resource_type = classify_resource_type(repo, rel_path)
            tags = capability_tags_for(repo, rel_path, sample)
            stem = Path(rel_path).stem.replace("test_", "")
            validations = sorted(test_paths_by_stem.get(stem, []))[:12]
            if not validations and repo == "ystar-bridge-labs" and resource_type != "test":
                validations = [test for test in test_paths_by_stem if stem in test or test in stem][:8]
            inputs, outputs = input_output_artifacts(rel_path, sample)
            keywords = sorted((_tokens(rel_path) | set(tags)) - {"json", "md", "py"})[:40]
            resource_id = f"e42_{repo.replace('-', '_')}_{_sha(repo + ':' + rel_path)}"
            resources.append(
                {
                    "resource_id": resource_id,
                    "repo": repo,
                    "path": rel_path,
                    "resource_type": resource_type,
                    "capability_tags": tags,
                    "task_keywords": keywords,
                    "input_artifacts": inputs,
                    "output_artifacts": outputs,
                    "callable_or_readonly": "callable" if resource_type in {"runtime_module", "script", "delivery_bridge", "MCP_boundary"} and repo == "ystar-bridge-labs" else "readonly",
                    "validation_tests": validations,
                    "owning_layer": OWNING_LAYER.get(repo, "unknown"),
                    "reuse_mode": infer_reuse_mode(repo, resource_type, tags),
                    "duplicate_risk_notes": "duplicate risk if rebuilt instead of reused" if tags else "",
                    "boundary_notes": boundary_notes(repo, resource_type, tags),
                }
            )

    resources = sorted(resources, key=lambda item: (item["repo"], item["resource_type"], item["path"]))
    tag_index: dict[str, list[str]] = defaultdict(list)
    resource_to_test: dict[str, list[str]] = {}
    ownership: dict[str, dict[str, Any]] = defaultdict(lambda: {"resource_count": 0, "resource_types": Counter(), "capability_tags": Counter()})
    for item in resources:
        for tag in item["capability_tags"]:
            tag_index[tag].append(item["resource_id"])
        resource_to_test[item["resource_id"]] = item["validation_tests"]
        owner = ownership[item["owning_layer"]]
        owner["resource_count"] += 1
        owner["resource_types"][item["resource_type"]] += 1
        for tag in item["capability_tags"]:
            owner["capability_tags"][tag] += 1
    ownership_json = {
        layer: {
            "resource_count": value["resource_count"],
            "resource_types": dict(value["resource_types"]),
            "capability_tags": dict(value["capability_tags"]),
        }
        for layer, value in ownership.items()
    }
    return {
        "artifact_id": "e42_internal_resource_inventory",
        "generated_at": "2026-05-05T00:00:01Z",
        "resource_count": len(resources),
        "resources": resources,
        "capability_tag_index": {tag: ids[:200] for tag, ids in sorted(tag_index.items())},
        "resource_to_test_index": resource_to_test,
        "cross_repo_capability_ownership_index": ownership_json,
        "derived_from_real_files": True,
        "recent_milestones_only": False,
    }


def resource_by_id(inventory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["resource_id"]: item for item in inventory.get("resources", [])}
