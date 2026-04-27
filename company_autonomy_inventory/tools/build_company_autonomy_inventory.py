#!/usr/bin/env python3
"""Build the company autonomy capability inventory from bounded source archaeology."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT.parent
GENERATED = ROOT / "company_autonomy_inventory" / "generated"

ALLOWED_EXTENSIONS = {".py", ".md", ".json", ".toml", ".yaml", ".yml", ".txt"}
SNIPPET_CHAR_LIMIT = 240
READ_CHAR_LIMIT = 1200
EVIDENCE_TERM_LIMIT = 8
MAX_INDEXED_ASSETS = 900
MAX_SINGLE_GENERATED_JSON_BYTES = 2_000_000
MAX_TOTAL_GENERATED_INVENTORY_BYTES = 8_000_000
SKIP_DIRS = {
    ".git",
    ".logs",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".venv",
    "venv",
    "backups",
}
SKIP_PATH_PARTS = {
    "reports/ceo/brain_dream_diffs",
    "reports/escalation",
    "reports/daily",
    "reports/drift_hourly",
}
SKIP_SUFFIXES = {
    "." + "db",
    "." + "db-shm",
    "." + "db-wal",
    "." + "sqlite",
    "." + "sqlite3",
    "." + "log",
}
ACTIVE_MARKER_TERMS = {"active_agent", "active-agent"}
GENERATED_SNIPPET_DENY_TERMS = {
    "." + "db",
    "." + "db-wal",
    "." + "db-shm",
    "." + "sqlite",
    "." + "sqlite3",
    "scripts/.logs",
    "reports/ceo/brain_dream_diffs",
    "reports/escalation",
    "reports/daily",
    "reports/drift_hourly",
    "active_agent",
    ".ystar_active_agent",
}

CAPABILITY_CLASSES = [
    "brain_and_memory",
    "agent_identity",
    "console_and_read_model",
    "governance_bridge",
    "pre_u_counterfactual",
    "cieu_event_boundary",
    "cieu_helpers_or_audit",
    "hook_or_gate",
    "cli_or_terminal_tool",
    "mcp_or_external_interface",
    "resource_sensing",
    "market_or_web_observation",
    "repo_or_code_observation",
    "scheduler_or_daemon",
    "skill_library_or_tooling",
    "action_execution",
    "auto_commit_or_git_action",
    "testing_or_validation",
    "reporting_or_status",
    "safety_or_quarantine",
]

CLASS_TERMS = {
    "brain_and_memory": ["brain", "memory", "capsule", "writeback"],
    "agent_identity": ["agent", "identity", "role", "profile", "team_capsule"],
    "console_and_read_model": ["console_read_model", "read_model", "team_console", "snapshot"],
    "governance_bridge": ["governance_bridge", "Y-star-gov", "ystar_gov", "governance"],
    "pre_u_counterfactual": ["pre_u", "Pre-U", "counterfactual", "packet"],
    "cieu_event_boundary": ["cieu_runtime", "CIEU runtime", "prediction_delta", "cieu_boundary"],
    "cieu_helpers_or_audit": ["cieu", "audit", "trace"],
    "hook_or_gate": ["hook", "gate", "boundary", "approval"],
    "cli_or_terminal_tool": ["cli", "command", "terminal", "argparse", "subprocess"],
    "mcp_or_external_interface": ["mcp", "interface", "external", "github", "api"],
    "resource_sensing": ["resource", "inventory", "sensing", "manifest", "discover"],
    "market_or_web_observation": ["market", "web", "browser", "search", "customer"],
    "repo_or_code_observation": ["repo", "code", "git", "source", "scan"],
    "scheduler_or_daemon": ["schedule", "daemon", "cron", "heartbeat", "worker"],
    "skill_library_or_tooling": ["skill", "tool", "library", "wrapper"],
    "action_execution": ["execute", "action", "run_", "perform", "dispatch"],
    "auto_commit_or_git_action": ["commit", "push", "pull_request", "git"],
    "testing_or_validation": ["test", "pytest", "validation", "validate", "check"],
    "reporting_or_status": ["report", "status", "summary", "readiness"],
    "safety_or_quarantine": ["safety", "quarantine", "forbidden", "blocked", "policy"],
}

AGENT_TERMS = {
    "Aiden-CEO": ["aiden", "ceo", "orchestration", "company", "goal"],
    "Ethan-CTO": ["ethan", "cto", "implementation", "technical", "code"],
    "Maya-Governance": ["maya", "governance", "risk", "policy", "boundary"],
    "Ryan-Platform": ["ryan", "platform", "mcp", "cli", "automation"],
    "Samantha-Secretary": ["samantha", "secretary", "handoff", "report", "summary"],
    "Leo-Kernel": ["leo", "kernel", "runtime", "contract", "invariant"],
}

REPO_SPECS = [
    ("ystar-company", ROOT),
    ("Y-star-gov", WORKSPACE / "Y-star-gov"),
    ("gov-mcp", WORKSPACE / "gov-mcp"),
    ("riverbed", WORKSPACE / "riverbed"),
    ("k9log-core", WORKSPACE / "k9log-core"),
    ("K9Audit", WORKSPACE / "K9Audit"),
]


def safe_relative_path(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def path_is_forbidden(relative_path: str) -> bool:
    lowered = relative_path.lower()
    parts = set(Path(relative_path).parts)
    if parts & SKIP_DIRS:
        return True
    if any(part in lowered for part in SKIP_PATH_PARTS):
        return True
    if any(term in lowered for term in ACTIVE_MARKER_TERMS):
        return True
    return any(lowered.endswith(suffix) for suffix in SKIP_SUFFIXES)


def iter_safe_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        rel = safe_relative_path(repo_root, path)
        if path_is_forbidden(rel):
            continue
        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue
        files.append(path)
    return sorted(files)


def read_bounded_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:READ_CHAR_LIMIT]
    except OSError:
        return ""


def compact_snippet(snippet: str) -> str | None:
    compact = " ".join(snippet.split())[:SNIPPET_CHAR_LIMIT].strip()
    if not compact:
        return None
    lowered = compact.lower()
    if any(term in lowered for term in GENERATED_SNIPPET_DENY_TERMS):
        return None
    return compact


def classify_asset(relative_path: str, snippet: str) -> tuple[list[str], list[str]]:
    haystack = f"{relative_path}\n{snippet}".lower()
    classes: list[str] = []
    evidence_terms: list[str] = []
    for class_name, terms in CLASS_TERMS.items():
        matched = sorted({term for term in terms if term.lower() in haystack})
        if matched:
            classes.append(class_name)
            evidence_terms.extend(f"{class_name}:{term}" for term in matched[:3])
    if not classes:
        classes.append("repo_or_code_observation")
        evidence_terms.append("repo_or_code_observation:path")
    return sorted(set(classes)), sorted(set(evidence_terms))


def owner_candidates(relative_path: str, snippet: str, classes: list[str]) -> list[str]:
    haystack = f"{relative_path}\n{snippet}".lower()
    owners = [
        agent_id
        for agent_id, terms in AGENT_TERMS.items()
        if any(term.lower() in haystack for term in terms)
    ]
    if not owners:
        if "governance_bridge" in classes or "safety_or_quarantine" in classes:
            owners.append("Maya-Governance")
        if "cli_or_terminal_tool" in classes or "mcp_or_external_interface" in classes:
            owners.append("Ryan-Platform")
        if "testing_or_validation" in classes or "repo_or_code_observation" in classes:
            owners.append("Ethan-CTO")
        if "reporting_or_status" in classes:
            owners.append("Samantha-Secretary")
    return sorted(set(owners or ["Aiden-CEO"]))


def actionability(relative_path: str, classes: list[str]) -> str:
    if "/generated/" in relative_path or relative_path.startswith("console_read_model/generated/"):
        return "generated_summary"
    if relative_path.startswith("tests/") or "test" in Path(relative_path).name:
        return "test_available"
    if Path(relative_path).suffix == ".py":
        return "source_available"
    if any(cls in classes for cls in ["action_execution", "hook_or_gate", "auto_commit_or_git_action"]):
        return "runtime_candidate_disabled"
    return "documentation_only"


def risk_tier(classes: list[str], relative_path: str) -> str:
    high = {"action_execution", "auto_commit_or_git_action", "scheduler_or_daemon", "hook_or_gate"}
    medium = {"mcp_or_external_interface", "market_or_web_observation", "cieu_helpers_or_audit"}
    if any(cls in classes for cls in high):
        return "high"
    if any(cls in classes for cls in medium):
        return "medium"
    if "brain_and_memory" in classes and "schema" not in relative_path:
        return "medium"
    return "low"


def asset_score(asset: dict[str, Any]) -> int:
    actionability_score = {
        "source_available": 35,
        "test_available": 30,
        "generated_summary": 28,
        "runtime_candidate_disabled": 24,
        "documentation_only": 12,
    }
    repo_score = {
        "ystar-company": 40,
        "Y-star-gov": 32,
        "gov-mcp": 24,
        "K9Audit": 12,
        "k9log-core": 10,
        "riverbed": 10,
    }
    risk_score = {"high": 16, "medium": 12, "low": 8, "blocked": 4}
    path = asset["relative_path"]
    bonus = 0
    for term in [
        "company_autonomy",
        "company_autonomous",
        "labs_cieu",
        "labs_live",
        "labs_runtime",
        "cross_repo",
        "console_read_model",
        "governance",
        "pre_u",
        "schema",
        "README",
        "test_",
    ]:
        if term.lower() in path.lower():
            bonus += 4
    return (
        repo_score.get(asset["repo_name"], 0)
        + actionability_score.get(asset["actionability_level"], 0)
        + risk_score.get(asset["risk_tier"], 0)
        + len(asset["capability_classes"]) * 3
        + min(len(asset["evidence_terms"]), EVIDENCE_TERM_LIMIT)
        + bonus
    )


def compact_assets(assets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = sorted(
        assets,
        key=lambda asset: (-asset_score(asset), asset["repo_name"], asset["relative_path"]),
    )
    selected: dict[str, dict[str, Any]] = {}

    for class_name in CAPABILITY_CLASSES:
        class_assets = [asset for asset in ranked if class_name in asset["capability_classes"]]
        for asset in class_assets[:25]:
            selected[asset["asset_id"]] = asset

    for asset in ranked:
        if len(selected) >= MAX_INDEXED_ASSETS:
            break
        selected[asset["asset_id"]] = asset

    return sorted(selected.values(), key=lambda asset: asset["asset_id"])


def discover_assets() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    roots: list[dict[str, Any]] = []
    asset_index = 1
    for repo_name, repo_root in REPO_SPECS:
        exists = repo_root.exists()
        roots.append(
            {
                "repo_name": repo_name,
                "repo_root": str(repo_root),
                "exists": exists,
                "write_performed": False,
            }
        )
        if not exists:
            continue
        for path in iter_safe_files(repo_root):
            relative_path = safe_relative_path(repo_root, path)
            snippet = read_bounded_text(path)
            classes, evidence_terms = classify_asset(relative_path, snippet)
            owners = owner_candidates(relative_path, snippet, classes)
            level = actionability(relative_path, classes)
            risk = risk_tier(classes, relative_path)
            governance_required = risk in {"medium", "high", "blocked"} or any(
                cls in classes
                for cls in [
                    "action_execution",
                    "auto_commit_or_git_action",
                    "hook_or_gate",
                    "cieu_event_boundary",
                    "mcp_or_external_interface",
                ]
            )
            can_candidate = (
                level in {"source_available", "test_available", "generated_summary", "runtime_candidate_disabled"}
                and risk != "blocked"
            )
            stat = path.stat()
            bounded_snippet = compact_snippet(snippet)
            compact_asset: dict[str, Any] = {
                "asset_id": f"asset-{asset_index:04d}",
                "repo_name": repo_name,
                "relative_path": relative_path,
                "file_type": path.suffix.lower().lstrip(".") or "text",
                "capability_classes": classes,
                "likely_owner_agent_candidates": owners,
                "actionability_level": level,
                "risk_tier": risk,
                "governance_required": governance_required,
                "can_be_tool_registry_candidate": can_candidate,
                "size_bytes": stat.st_size,
                "line_count_estimate": snippet.count("\n") + 1 if snippet else 0,
                "compact_reason": "metadata and bounded lexical evidence only; full source/doc content excluded",
                "evidence_terms": evidence_terms[:EVIDENCE_TERM_LIMIT],
            }
            if bounded_snippet:
                compact_asset["bounded_snippet"] = bounded_snippet
            assets.append(compact_asset)
            asset_index += 1
    manifest = {
        "schema_name": "ystar.company_autonomy_inventory.generated.repo_discovery_manifest",
        "schema_version": "v0",
        "repo_archaeology_completed": True,
        "classification_method": "deterministic_lexical_path_name_and_bounded_snippet",
        "allowed_file_extensions": sorted(ALLOWED_EXTENSIONS),
        "read_char_limit": READ_CHAR_LIMIT,
        "snippet_char_limit": SNIPPET_CHAR_LIMIT,
        "max_indexed_assets": MAX_INDEXED_ASSETS,
        "scanned_roots": roots,
        "assets_discovered": len(assets),
        "forbidden_runtime_content_read": False,
        "external_roots_read_only": True,
        "compaction_applied": True,
        "full_source_embedding_allowed": False,
        "full_doc_embedding_allowed": False,
    }
    return assets, manifest


def assets_by_class(assets: list[dict[str, Any]], class_name: str) -> list[str]:
    return [asset["asset_id"] for asset in assets if class_name in asset["capability_classes"]][:20]


def build_existing_asset_inventory(all_assets: list[dict[str, Any]], indexed_assets: list[dict[str, Any]]) -> dict[str, Any]:
    classes: dict[str, int] = {class_name: 0 for class_name in CAPABILITY_CLASSES}
    repos: dict[str, int] = {}
    for asset in all_assets:
        repos[asset["repo_name"]] = repos.get(asset["repo_name"], 0) + 1
        for class_name in asset["capability_classes"]:
            classes[class_name] = classes.get(class_name, 0) + 1
    return {
        "schema_name": "ystar.company_autonomy_inventory.generated.existing_asset_inventory",
        "schema_version": "v0",
        "asset_count": len(all_assets),
        "indexed_asset_count": len(indexed_assets),
        "max_indexed_assets": MAX_INDEXED_ASSETS,
        "compaction_applied": True,
        "full_source_embedding_allowed": False,
        "full_doc_embedding_allowed": False,
        "repo_counts": repos,
        "capability_class_counts": classes,
        "assets": indexed_assets,
    }


def build_observation_map(assets: list[dict[str, Any]]) -> dict[str, Any]:
    specs = [
        ("codebase_observation", "codebase", ["repo_or_code_observation"], False, False),
        ("git_status_observation", "git_status", ["auto_commit_or_git_action"], False, False),
        ("test_result_observation", "test_result", ["testing_or_validation"], False, False),
        ("generated_report_observation", "generated_report", ["reporting_or_status"], False, False),
        ("console_read_model_observation", "console_read_model", ["console_and_read_model"], False, True),
        ("cieu_event_observation", "cieu_event", ["cieu_event_boundary"], False, True),
        ("governance_decision_observation", "governance_decision", ["governance_bridge"], False, True),
        ("runtime_readiness_observation", "runtime_readiness", ["safety_or_quarantine"], False, True),
        ("resource_tool_inventory_observation", "resource_tool_inventory", ["resource_sensing"], False, True),
        ("market_web_observation", "market_web", ["market_or_web_observation"], True, False),
        ("github_issue_pr_observation", "github_issue_pr", ["mcp_or_external_interface"], True, False),
        ("mcp_interface_observation", "mcp_interface", ["mcp_or_external_interface"], False, False),
    ]
    channels = []
    for channel_id, channel_type, classes, requires_network, safe_now_if_assets in specs:
        source_assets = sorted(set(sum((assets_by_class(assets, cls) for cls in classes), [])))
        status = "existing" if source_assets and safe_now_if_assets else "candidate" if source_assets else "missing"
        if channel_id in {"market_web_observation", "github_issue_pr_observation"}:
            status = "candidate" if source_assets else "missing"
        channels.append(
            {
                "channel_id": channel_id,
                "channel_type": channel_type,
                "source_assets": source_assets,
                "current_status": status,
                "requires_network": requires_network,
                "requires_credentials": channel_id in {"github_issue_pr_observation"},
                "reads_raw_runtime_artifacts": False,
                "safe_for_autonomy_now": bool(source_assets and not requires_network and safe_now_if_assets),
                "governance_notes": "read-only generated/source observation; live external observation remains disabled",
            }
        )
    return {
        "schema_name": "ystar.company_autonomy_inventory.generated.observation_capability_map",
        "schema_version": "v0",
        "channels": channels,
    }


def build_resource_sensing_map(assets: list[dict[str, Any]]) -> dict[str, Any]:
    specs = [
        ("repositories", "repository", "repo_discovery_manifest", "bounded_source_archaeology", True, False),
        ("cli_tools", "cli_tool", "cli_or_terminal_tool assets", "source_inventory", True, False),
        ("generated_reports", "generated_report", "console and generated summaries", "generated_json_summary", True, False),
        ("test_harnesses", "test_harness", "testing_or_validation assets", "source_inventory", True, False),
        ("governance_endpoints", "governance_endpoint", "governance_bridge assets", "source_inventory", True, False),
        ("console_summaries", "console_summary", "console_read_model/generated", "generated_json_summary", True, False),
        ("agent_brains_capsules", "agent_capsule", "agent_brains", "curated_capsule_files", True, False),
        ("action_scripts", "action_script", "action_execution assets", "source_inventory_disabled", False, False),
        ("mcp_interfaces", "mcp_interface", "mcp_or_external_interface assets", "source_inventory", True, False),
        ("external_tools", "external_tool", "external interface docs", "candidate_inventory", False, False),
        ("dirty_runtime_artifacts", "untrusted_evidence_ore", "quarantine summaries", "path_level_generated_summary", False, True),
    ]
    resources = []
    for resource_id, resource_type, source, method, safe, raw in specs:
        resources.append(
            {
                "resource_id": resource_id,
                "resource_type": resource_type,
                "source": source,
                "sensing_method": method,
                "safe_to_read_now": safe,
                "raw_runtime_artifact": raw,
                "requires_review": raw or not safe,
                "governance_boundary": "generated summaries only" if raw else "source/docs/schema inventory only",
                "notes": "resource is mapped for autonomy planning, not executed",
            }
        )
    return {
        "schema_name": "ystar.company_autonomy_inventory.generated.resource_sensing_map",
        "schema_version": "v0",
        "resources": resources,
    }


def source_assets_for_action(assets: list[dict[str, Any]], action_id: str) -> list[str]:
    mapping = {
        "local_file_generation": ["cli_or_terminal_tool", "repo_or_code_observation"],
        "docs_update": ["reporting_or_status"],
        "schema_generation": ["testing_or_validation", "repo_or_code_observation"],
        "test_execution": ["testing_or_validation"],
        "safe_repo_scan": ["repo_or_code_observation", "resource_sensing"],
        "git_commit": ["auto_commit_or_git_action"],
        "git_push": ["auto_commit_or_git_action"],
        "github_issue": ["mcp_or_external_interface"],
        "github_pr": ["mcp_or_external_interface", "auto_commit_or_git_action"],
        "shell_command": ["cli_or_terminal_tool"],
        "mcp_call": ["mcp_or_external_interface"],
        "codex_execution": ["cli_or_terminal_tool", "action_execution"],
        "claude_code_execution": ["cli_or_terminal_tool", "action_execution"],
        "brain_writeback": ["brain_and_memory"],
        "memory_ingestion": ["brain_and_memory"],
        "cieu_write": ["cieu_event_boundary", "cieu_helpers_or_audit"],
        "daemon_start_stop": ["scheduler_or_daemon"],
        "external_web_action": ["market_or_web_observation"],
        "market_research": ["market_or_web_observation"],
        "email_or_communication": ["mcp_or_external_interface", "reporting_or_status"],
    }
    return sorted(set(sum((assets_by_class(assets, cls) for cls in mapping[action_id]), [])))[:20]


def build_action_map(assets: list[dict[str, Any]]) -> dict[str, Any]:
    high_risk = {
        "git_push",
        "brain_writeback",
        "memory_ingestion",
        "cieu_write",
        "daemon_start_stop",
        "external_web_action",
        "email_or_communication",
    }
    categories = [
        "local_file_generation",
        "docs_update",
        "schema_generation",
        "test_execution",
        "safe_repo_scan",
        "git_commit",
        "git_push",
        "github_issue",
        "github_pr",
        "shell_command",
        "mcp_call",
        "codex_execution",
        "claude_code_execution",
        "brain_writeback",
        "memory_ingestion",
        "cieu_write",
        "daemon_start_stop",
        "external_web_action",
        "market_research",
        "email_or_communication",
    ]
    actions = []
    for action_id in categories:
        source_assets = source_assets_for_action(assets, action_id)
        blocked = action_id in high_risk
        actions.append(
            {
                "action_id": action_id,
                "current_status": "blocked" if blocked else "candidate_disabled" if source_assets else "missing",
                "source_assets": source_assets,
                "risk_tier": "blocked" if blocked else "high" if action_id in {"git_commit", "shell_command", "mcp_call"} else "medium",
                "requires_operator_approval": True,
                "requires_y_star_gov": action_id not in {"safe_repo_scan", "docs_update"},
                "requires_cieu_event": action_id not in {"safe_repo_scan", "docs_update", "schema_generation"},
                "requires_rollback_policy": action_id not in {"safe_repo_scan", "docs_update"},
                "live_enabled": False,
                "notes": "inventoried only; live action remains disabled",
            }
        )
    return {
        "schema_name": "ystar.company_autonomy_inventory.generated.action_capability_map",
        "schema_version": "v0",
        "actions": actions,
    }


def build_tool_registry(assets: list[dict[str, Any]]) -> dict[str, Any]:
    candidate_specs = [
        ("console-read-model-tools", "Console read model tools", "console_read_model", "Ryan-Platform", ["console_and_read_model"], "candidate"),
        ("governance-dry-run-tools", "Governance dry-run tools", "governance_dry_run", "Maya-Governance", ["governance_bridge"], "needs_wrapper"),
        ("live-boundary-tools", "Live readiness and boundary tools", "live_boundary", "Maya-Governance", ["hook_or_gate", "safety_or_quarantine"], "needs_tests"),
        ("cieu-boundary-tools", "CIEU boundary tools", "cieu_boundary", "Leo-Kernel", ["cieu_event_boundary"], "needs_schema"),
        ("repo-scan-tools", "Safe repository scan tools", "repo_scan", "Ethan-CTO", ["repo_or_code_observation", "resource_sensing"], "candidate"),
        ("local-validation-tools", "Local validation and test tools", "validation", "Ethan-CTO", ["testing_or_validation"], "candidate"),
        ("docs-report-tools", "Docs and report generation tools", "docs_report", "Samantha-Secretary", ["reporting_or_status"], "candidate"),
        ("github-pr-issue-tools", "GitHub PR and issue tools", "github", "Ryan-Platform", ["mcp_or_external_interface"], "blocked"),
        ("mcp-interface-tools", "MCP interface tools", "mcp", "Ryan-Platform", ["mcp_or_external_interface"], "needs_wrapper"),
    ]
    candidates = []
    for index, (tool_id, name, category, owner, classes, readiness) in enumerate(candidate_specs, start=1):
        source_assets = sorted(set(sum((assets_by_class(assets, cls) for cls in classes), [])))[:15]
        blocked = readiness == "blocked"
        candidates.append(
            {
                "tool_id": tool_id,
                "tool_name": name,
                "source_asset_ids": source_assets,
                "owner_agent_candidate": owner,
                "tool_category": category,
                "input_contract_required": True,
                "output_contract_required": True,
                "risk_tier": "blocked" if blocked else "medium",
                "allowed_paths": ["curated source/docs/schema paths", "generated read-model paths"],
                "denied_paths": ["runtime stores", "logs", "active markers", "backups", "raw reports"],
                "requires_network": tool_id == "github-pr-issue-tools",
                "requires_credentials": tool_id == "github-pr-issue-tools",
                "requires_operator_approval": True,
                "requires_y_star_gov": True,
                "requires_cieu_event": tool_id not in {"console-read-model-tools", "repo-scan-tools"},
                "requires_rollback_policy": tool_id not in {"console-read-model-tools", "repo-scan-tools"},
                "live_enabled": False,
                "readiness": readiness,
                "notes": "registry candidate only; not an enabled tool",
            }
        )
    return {
        "schema_name": "ystar.company_autonomy_inventory.generated.governed_tool_registry_candidates",
        "schema_version": "v0",
        "candidates": candidates,
    }


def build_agent_matrix(observation: dict[str, Any], resources: dict[str, Any], actions: dict[str, Any], tools: dict[str, Any]) -> dict[str, Any]:
    all_observation = [channel["channel_id"] for channel in observation["channels"] if channel["current_status"] != "missing"]
    all_resources = [resource["resource_id"] for resource in resources["resources"]]
    action_ids = [action["action_id"] for action in actions["actions"] if action["current_status"] != "missing"]
    tool_ids = [tool["tool_id"] for tool in tools["candidates"]]
    role_specs = {
        "Aiden-CEO": {
            "role_focus": "company orchestration, goal tracking, priority setting, task delegation, business loop review",
            "self_drive_scope": "set priorities and delegate governed work without direct high-risk execution",
            "forbidden_actions": ["git_push", "daemon_start_stop", "brain_writeback", "memory_ingestion", "cieu_write"],
        },
        "Ethan-CTO": {
            "role_focus": "codebase understanding, tool building, technical implementation, test validation",
            "self_drive_scope": "build and validate tools inside governance boundaries",
            "forbidden_actions": ["bypass_governance", "git_push", "daemon_start_stop"],
        },
        "Maya-Governance": {
            "role_focus": "risk review, policy boundaries, Y-star-gov alignment, live gate readiness",
            "self_drive_scope": "evaluate boundaries and readiness without executing business actions",
            "forbidden_actions": ["business_action_execution", "candidate_auto_approval"],
        },
        "Ryan-Platform": {
            "role_focus": "CLI/MCP/platform integration, execution substrate mapping, automation plumbing",
            "self_drive_scope": "map and wrap platform capabilities without enabling live action",
            "forbidden_actions": ["enable_live_actions_without_governance", "external_action_execution"],
        },
        "Samantha-Secretary": {
            "role_focus": "memory/doc/report coordination, communication drafts, schedule/status/read-model support",
            "self_drive_scope": "prepare summaries and handoffs without sending external communications",
            "forbidden_actions": ["send_external_communication_without_approval", "memory_ingestion"],
        },
        "Leo-Kernel": {
            "role_focus": "kernel/runtime integrity, contract and boundary logic",
            "self_drive_scope": "reason about runtime contracts without direct writeback",
            "forbidden_actions": ["direct_brain_writeback", "direct_memory_ingestion", "bypass_cieu_policy"],
        },
    }
    agents = []
    for agent_id, spec in role_specs.items():
        agents.append(
            {
                "agent_id": agent_id,
                "role_focus": spec["role_focus"],
                "observation_channels": all_observation,
                "resource_sensing_channels": all_resources,
                "action_categories": action_ids,
                "governed_tool_candidates": tool_ids,
                "forbidden_actions": spec["forbidden_actions"],
                "requires_governance_for": ["medium_risk_actions", "high_risk_actions", "external_interfaces", "persistence"],
                "self_drive_scope": spec["self_drive_scope"],
                "gaps": ["live actions disabled", "tool registry candidates not approved"],
            }
        )
    return {
        "schema_name": "ystar.company_autonomy_inventory.generated.agent_role_capability_matrix",
        "schema_version": "v0",
        "agents": agents,
    }


def build_readiness_summary() -> dict[str, Any]:
    return {
        "schema_name": "ystar.company_autonomy_inventory.generated.company_autonomy_readiness_summary",
        "schema_version": "v0",
        "company_autonomy_inventory_defined": True,
        "repo_archaeology_completed": True,
        "observation_capability_map_defined": True,
        "resource_sensing_map_defined": True,
        "action_capability_map_defined": True,
        "governed_tool_registry_candidates_defined": True,
        "agent_role_capability_matrix_defined": True,
        "commercial_agent_company_goal_aligned": True,
        "governance_only_runtime": False,
        "live_actions_enabled": False,
        "external_actions_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "cieu_persistence_enabled": False,
        "git_push_enabled": False,
        "daemon_control_enabled": False,
        "email_or_external_communication_enabled": False,
        "requires_manual_enablement": True,
        "next_required_milestone": "L4.2 Company Autonomous Work Cycle Simulator v0",
    }


def render_reports(asset_inventory: dict[str, Any], action_map: dict[str, Any], tools: dict[str, Any], readiness: dict[str, Any]) -> tuple[str, str, str]:
    top_classes = sorted(
        asset_inventory["capability_class_counts"].items(),
        key=lambda item: (-item[1], item[0]),
    )[:8]
    dormant = [
        "# Dormant Asset Report",
        "",
        "## Strongest existing assets",
        "",
        *[f"- {name}: {count} mapped assets" for name, count in top_classes],
        "",
        "## Action-capable assets that remain disabled",
        "",
        "- shell, git, hook, daemon, CIEU, brain/memory, and external interface surfaces require governed wrappers",
        "",
        "## Should be wrapped into governed tools",
        "",
        *[f"- {tool['tool_name']} ({tool['readiness']})" for tool in tools["candidates"]],
        "",
        "## Should not be reused yet",
        "",
        "- direct push, external communication, CIEU persistence, daemon control, brain writeback, memory ingestion",
        "",
    ]
    gaps = [
        "# Autonomy Gap Report",
        "",
        "- Observation: local generated/source observation is strong; market/web and GitHub live observation remain candidates.",
        "- Resource understanding: repository and read-model sensing exists; dirty runtime artifacts remain untrusted evidence ore.",
        "- Tool selection: registry candidates exist, but no approved live registry exists.",
        "- Real action: all live actions remain disabled.",
        "- Governance wrapping: action surfaces need input/output contracts, Y-star-gov checks, rollback policy, and CIEU events.",
        "- CIEU learning loop: event boundary exists, but persistence and learning eligibility remain disabled.",
        "- Self-drive lifecycle: next milestone should simulate an autonomous work cycle without enabling live execution.",
        "",
    ]
    report = [
        "# Company Autonomy Inventory Report",
        "",
        f"repo_archaeology_completed: {readiness['repo_archaeology_completed']}",
        f"commercial_agent_company_goal_aligned: {readiness['commercial_agent_company_goal_aligned']}",
        f"governance_only_runtime: {readiness['governance_only_runtime']}",
        f"live_actions_enabled: {readiness['live_actions_enabled']}",
        "",
        "## Already observable",
        "",
        "- codebase/source/docs/schema files",
        "- generated read-model and governance summaries",
        "- local validation and acceptance outputs",
        "",
        "## Safe now",
        "",
        "- source archaeology",
        "- generated report reading",
        "- local validation/test execution under explicit command",
        "",
        "## Candidate only",
        "",
        "- governed tool registry candidates",
        "- GitHub/MCP/external observation wrappers",
        "- CIEU runtime writer boundary",
        "",
        "## Blocked",
        "",
        "- live actions, push, external communication, daemon control, CIEU persistence, brain/memory writeback",
        "",
        f"Next milestone: {readiness['next_required_milestone']}",
        "",
    ]
    return "\n".join(dormant), "\n".join(gaps), "\n".join(report)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def generated_inventory_files() -> list[Path]:
    names = [
        "repo_discovery_manifest.json",
        "existing_asset_inventory.json",
        "observation_capability_map.json",
        "resource_sensing_map.json",
        "action_capability_map.json",
        "governed_tool_registry_candidates.json",
        "agent_role_capability_matrix.json",
        "company_autonomy_readiness_summary.json",
        "dormant_asset_report.md",
        "autonomy_gap_report.md",
        "company_autonomy_report.md",
        "inventory_size_guard.json",
    ]
    return [GENERATED / name for name in names if (GENERATED / name).exists()]


def write_inventory_size_guard() -> dict[str, Any]:
    def build_payload() -> dict[str, Any]:
        files = generated_inventory_files()
        sizes = {path.name: path.stat().st_size for path in files}
        oversized = [
            {"file": name, "size_bytes": size}
            for name, size in sorted(sizes.items())
            if name.endswith(".json") and size > MAX_SINGLE_GENERATED_JSON_BYTES
        ]
        return {
            "schema_name": "ystar.company_autonomy_inventory.generated.inventory_size_guard",
            "schema_version": "v0",
            "inventory_size_guard_defined": True,
            "max_single_generated_json_bytes": MAX_SINGLE_GENERATED_JSON_BYTES,
            "max_total_generated_inventory_bytes": MAX_TOTAL_GENERATED_INVENTORY_BYTES,
            "oversized_files": oversized,
            "total_generated_inventory_bytes": sum(sizes.values()),
            "generated_file_sizes": sizes,
            "compaction_applied": True,
            "max_indexed_assets": MAX_INDEXED_ASSETS,
            "full_source_embedding_allowed": False,
            "full_doc_embedding_allowed": False,
            "generated_inventory_safe_for_read_model": not oversized
            and sum(sizes.values()) <= MAX_TOTAL_GENERATED_INVENTORY_BYTES,
        }

    guard_path = GENERATED / "inventory_size_guard.json"
    write_json(guard_path, build_payload())
    payload = build_payload()
    write_json(guard_path, payload)
    return payload


def main() -> int:
    assets, discovery_manifest = discover_assets()
    indexed_assets = compact_assets(assets)
    discovery_manifest["assets_indexed"] = len(indexed_assets)
    asset_inventory = build_existing_asset_inventory(assets, indexed_assets)
    observation = build_observation_map(indexed_assets)
    resources = build_resource_sensing_map(indexed_assets)
    actions = build_action_map(indexed_assets)
    tools = build_tool_registry(indexed_assets)
    agent_matrix = build_agent_matrix(observation, resources, actions, tools)
    readiness = build_readiness_summary()
    dormant_report, gap_report, autonomy_report = render_reports(asset_inventory, actions, tools, readiness)

    GENERATED.mkdir(parents=True, exist_ok=True)
    write_json(GENERATED / "repo_discovery_manifest.json", discovery_manifest)
    write_json(GENERATED / "existing_asset_inventory.json", asset_inventory)
    write_json(GENERATED / "observation_capability_map.json", observation)
    write_json(GENERATED / "resource_sensing_map.json", resources)
    write_json(GENERATED / "action_capability_map.json", actions)
    write_json(GENERATED / "governed_tool_registry_candidates.json", tools)
    write_json(GENERATED / "agent_role_capability_matrix.json", agent_matrix)
    write_json(GENERATED / "company_autonomy_readiness_summary.json", readiness)
    (GENERATED / "dormant_asset_report.md").write_text(dormant_report, encoding="utf-8")
    (GENERATED / "autonomy_gap_report.md").write_text(gap_report, encoding="utf-8")
    (GENERATED / "company_autonomy_report.md").write_text(autonomy_report, encoding="utf-8")
    size_guard = write_inventory_size_guard()

    print("Company Autonomy Inventory Builder: PASS")
    print(f"assets_discovered: {discovery_manifest['assets_discovered']}")
    print(f"assets_indexed: {discovery_manifest['assets_indexed']}")
    print(f"total_generated_inventory_bytes: {size_guard['total_generated_inventory_bytes']}")
    print(f"repo_archaeology_completed: {readiness['repo_archaeology_completed']}")
    print(f"governance_only_runtime: {readiness['governance_only_runtime']}")
    print(f"live_actions_enabled: {readiness['live_actions_enabled']}")
    print(f"next_required_milestone: {readiness['next_required_milestone']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
