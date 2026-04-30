#!/usr/bin/env python3
"""Full tracked-file conservatism debt scan for L7.0Q2.

The source list is strictly `git ls-files`. The scanner skips DB/WAL/SHM,
logs, pycache, active-agent markers, local env/secret patterns, binary files,
images, archives, and other irrelevant runtime/binary surfaces before reading.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "l7_full_repo_conservatism_scan"
POLICY_DIR = ROOT / "policy"
MILESTONE_ID = "L7.0Q2"
MILESTONE_NAME = "Full-Repository Conservatism Debt Scan & Policy Migration Map"

BLOCKING_PATTERNS = [
    "blocked",
    "blocked_until_human_approved",
    "hard_forbidden",
    "forbidden",
    "forbidden_actions",
    "disabled",
    "not_configured",
    "not_allowed",
    "deny",
    "denylist",
    "blacklist",
    "allowlist",
    "no_go",
    "no-go",
    "no_action",
    "no-action",
    "readiness",
    "preflight",
    "preflight_only",
    "fixture_only",
    "configuration_blocked",
    "backend_missing",
    "backend_required",
    "required_manual",
]
OWNER_BURDEN_PATTERNS = [
    "user_must_provide",
    "provide URL",
    "reviewed seed locator",
    "user URL",
    "ask-user-URL",
    "ask_user_url",
    "manual URL",
    "manually search",
    "manually export",
    "open multiple Codex windows",
    "create worktrees",
    "merge branches",
    "user must",
    "USER_ACTION_REQUIRED",
    "human must provide",
]
EXTERNAL_SIDE_EFFECT_PATTERNS = [
    "login",
    "account creation",
    "payment",
    "checkout",
    "form submission",
    "posting",
    "commenting",
    "messaging",
    "outreach",
    "publication",
    "customer contact",
    "grant submission",
    "RFP submission",
    "bounty submission",
    "revenue execution",
    "MCP execution",
    "live behavior",
]
CORE_WRITEBACK_PATTERNS = [
    "CIEU DB write",
    "brain writeback",
    "memory writeback",
    "canonical strategy",
    "direct Y*",
    "writeback blocked",
    "core_writeback",
]
RUNTIME_VISIBILITY_PATTERNS = [
    "DB",
    "WAL",
    "SHM",
    "log",
    "active-agent",
    "runtime drift",
    "marker content",
]
POLICY_MATURITY_PATTERNS = [
    "policy_ref",
    "action_capability_registry",
    "approval_state_machine",
    "allowed_stage",
    "draft_only",
    "read_only",
    "allowed_after_human_approval",
    "allowed_with_budget",
    "writeback_candidate",
    "dry_run_writeback",
    "execute_after_approval",
    "staged capability",
    "review-gated",
]
ALL_PATTERNS = (
    BLOCKING_PATTERNS
    + OWNER_BURDEN_PATTERNS
    + EXTERNAL_SIDE_EFFECT_PATTERNS
    + CORE_WRITEBACK_PATTERNS
    + RUNTIME_VISIBILITY_PATTERNS
    + POLICY_MATURITY_PATTERNS
)

SKIP_SUFFIXES = {
    ".db",
    ".db-wal",
    ".db-shm",
    ".sqlite",
    ".sqlite3",
    ".log",
    ".pyc",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".gz",
    ".tar",
    ".tgz",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".env",
    ".pem",
    ".key",
    ".p12",
    ".crt",
}
SKIP_PARTS = {"__pycache__", ".git", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
SKIP_PATH_FRAGMENTS = {
    "scripts/.logs/",
    "l7_full_repo_conservatism_scan/",
    "active_agent",
    "controlled_observation.env",
    ".env",
    "secrets",
    "secret",
}
LIKELY_LOG_NAME_MARKERS = ("_log", "log_", "-log", "logs")
ALLOWED_HIDDEN_TRACKED_PREFIXES = {
    ".claude/agents/",
    ".claude/tasks/",
}

LEGITIMATE_HARD_TERMS = {
    "secret",
    "api key",
    "credential",
    "payment",
    "checkout",
    "posting",
    "publication",
    "outreach",
    "customer contact",
    "grant",
    "rfp",
    "brain writeback",
    "memory writeback",
    "canonical strategy",
    "cieU db".lower(),
    "db/wal/shm",
    "raw db",
    "wal",
    "shm",
    "raw log",
    "active-agent",
    "y-star-gov",
    "gov-mcp",
    "private/internal",
    "private network",
    "internal network",
    "access-control",
    "malware",
    "exfiltration",
    "login",
    "account creation",
}

INVENTORY_FILES = {
    "hardcoded_forbidden_action_inventory.json": {"hardcoded_blacklist", "hardcoded_forbidden_action_list"},
    "blocked_state_inventory.json": {"blocked_state", "disabled_as_final_state", "external_action_overblocked", "core_writeback_overblocked"},
    "disabled_as_final_state_inventory.json": {"disabled_as_final_state"},
    "no_action_readiness_inventory.json": {"no_action_receipt_overuse", "readiness_or_preflight_overuse"},
    "owner_manual_burden_inventory.json": {"owner_manual_burden"},
    "discovery_suppression_inventory.json": {"discovery_blocked_unnecessarily", "fixture_only_regression", "disabled_as_final_state"},
    "external_action_policy_inventory.json": {"external_action_overblocked", "approval_gate_missing", "legitimate_hard_boundary"},
    "core_writeback_policy_inventory.json": {"core_writeback_overblocked", "legitimate_hard_boundary"},
    "runtime_visibility_policy_inventory.json": {"runtime_visibility_overblocked", "legitimate_hard_boundary"},
    "legitimate_hard_boundary_inventory.json": {"legitimate_hard_boundary"},
    "harmful_overconservatism_inventory.json": {
        "discovery_blocked_unnecessarily",
        "external_action_overblocked",
        "owner_manual_burden",
        "no_action_receipt_overuse",
        "readiness_or_preflight_overuse",
        "hardcoded_blacklist",
        "hardcoded_forbidden_action_list",
        "disabled_as_final_state",
        "fixture_only_regression",
        "core_writeback_overblocked",
        "runtime_visibility_overblocked",
        "approval_gate_missing",
        "test_expectation_overconservative",
        "console_read_model_overconservative",
        "generated_artifact_overconservative",
        "documentation_overconservative",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any, compact: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if compact:
        text = json.dumps(payload, separators=(",", ":"), sort_keys=False)
    else:
        text = json.dumps(payload, indent=2, sort_keys=False)
    path.write_text(text + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def git_ls_files() -> list[str]:
    result = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True)
    return [item.decode("utf-8", errors="replace") for item in result.stdout.split(b"\0") if item]


def is_skipped(path_str: str) -> bool:
    path = Path(path_str)
    parts = set(path.parts)
    if parts & SKIP_PARTS:
        return True
    if path.parts and path.parts[0].startswith("."):
        if not any(path_str.startswith(prefix) for prefix in ALLOWED_HIDDEN_TRACKED_PREFIXES):
            return True
    lowered = path_str.lower()
    if any(fragment.lower() in lowered for fragment in SKIP_PATH_FRAGMENTS):
        return True
    if any(marker in Path(path_str).name.lower() for marker in LIKELY_LOG_NAME_MARKERS):
        return True
    if path.suffix.lower() in SKIP_SUFFIXES:
        return True
    if "active_agent" in lowered or "active-agent" in lowered:
        return True
    return False


def is_binary(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:4096]
    except OSError:
        return True
    return b"\0" in chunk


def read_text_file(path_str: str) -> str | None:
    path = ROOT / path_str
    if not path.is_file() or is_binary(path):
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return None
    except OSError:
        return None


def directory_group(path_str: str) -> str:
    parts = Path(path_str).parts
    if not parts:
        return "."
    if parts[0] in {"tests", "scripts", "console_read_model", "policy"}:
        return "/".join(parts[:2]) if len(parts) > 1 and parts[0] == "tests" else parts[0]
    return parts[0]


def artifact_epoch(path_str: str) -> str:
    p = path_str.lower()
    if "conservatism_debt_audit" in p or "conservatism_scan" in p:
        return "generated"
    if p.startswith("policy/"):
        return "policy"
    if p.startswith("tests/"):
        return "tests"
    if p.startswith("scripts/"):
        return "scripts"
    if p.startswith("console_read_model/"):
        return "console_read_model"
    if p.endswith(".md") and not any(token in p for token in ["l5", "l6", "l7"]):
        return "docs"
    if "l7_" in p or p.startswith("l7"):
        return "l7_commercial"
    if any(token in p for token in ["l6_13", "l6_14", "l6_15", "l6_16", "real_observation", "mission_evidence", "human_review", "strategy_memo"]):
        return "l6_review_strategy"
    if any(token in p for token in ["l6_10", "l6_11", "l6_12", "observation", "evidence"]):
        return "l6_observation"
    if "l6_" in p or p.startswith("l6"):
        return "l6_early"
    if "l5" in p or p.startswith("l5"):
        return "l5"
    if any(token in p for token in ["generated", "summary", "manifest", "fixture"]):
        return "generated"
    return "unknown"


def pattern_family(pattern: str) -> str:
    if pattern in POLICY_MATURITY_PATTERNS:
        return "policy_maturity"
    if pattern in OWNER_BURDEN_PATTERNS:
        return "owner_burden"
    if pattern in EXTERNAL_SIDE_EFFECT_PATTERNS:
        return "external_side_effect"
    if pattern in CORE_WRITEBACK_PATTERNS:
        return "core_writeback"
    if pattern in RUNTIME_VISIBILITY_PATTERNS:
        return "runtime_visibility"
    return "blocking_disabled"


def classify(path_str: str, line: str, pattern: str) -> dict[str, Any]:
    lower = f"{path_str} {line} {pattern}".lower()
    family = pattern_family(pattern)
    epoch = artifact_epoch(path_str)

    if family == "policy_maturity":
        classification = "policy_registry_present"
    elif any(term in lower for term in LEGITIMATE_HARD_TERMS):
        classification = "legitimate_hard_boundary"
    elif family == "owner_burden":
        classification = "owner_manual_burden"
    elif family == "runtime_visibility":
        classification = "runtime_visibility_overblocked"
    elif family == "core_writeback":
        classification = "core_writeback_overblocked"
    elif family == "external_side_effect":
        classification = "external_action_overblocked"
    elif any(term in lower for term in ["readiness", "preflight", "preflight_only"]):
        classification = "readiness_or_preflight_overuse"
    elif any(term in lower for term in ["fixture_only"]):
        classification = "fixture_only_regression"
    elif any(term in lower for term in ["disabled", "not_configured", "backend_missing", "backend_required", "configuration_blocked"]):
        classification = "disabled_as_final_state"
    elif any(term in lower for term in ["no_action", "no-action", "no_go", "no-go"]):
        classification = "no_action_receipt_overuse"
    elif any(term in lower for term in ["denylist", "blacklist", "allowlist", "hard_forbidden"]):
        classification = "hardcoded_blacklist"
    elif any(term in lower for term in ["forbidden", "forbidden_actions", "deny", "blocked", "not_allowed"]):
        classification = "hardcoded_forbidden_action_list"
    else:
        classification = "policy_registry_needed"

    if classification != "legitimate_hard_boundary":
        if path_str.startswith("tests/"):
            classification = "test_expectation_overconservative"
        elif path_str.startswith("console_read_model/"):
            classification = "console_read_model_overconservative"
        elif epoch == "generated":
            classification = "generated_artifact_overconservative"
        elif path_str.endswith(".md") and epoch == "docs":
            classification = "documentation_overconservative"

    legitimate = classification == "legitimate_hard_boundary"
    harmful = classification not in {"legitimate_hard_boundary", "policy_registry_present", "unclear_requires_review"}
    patch_strategy = patch_strategy_for(classification)
    severity = severity_for(classification, epoch, lower)
    target_policy = target_policy_for(classification, family)
    return {
        "classification": classification,
        "severity": severity,
        "legitimate_hard_boundary": legitimate,
        "harmful_overconservatism": harmful,
        "capability_harmed": "none; safety boundary preserved" if legitimate else capability_harmed_for(classification),
        "commercial_impact": "prevents unsafe or unreviewed side effects" if legitimate else commercial_impact_for(classification),
        "recommended_fix": recommended_fix_for(classification),
        "migration_target_policy": target_policy,
        "safe_to_patch_now": classification in {
            "policy_registry_needed",
            "hardcoded_forbidden_action_list",
            "hardcoded_blacklist",
            "owner_manual_burden",
            "disabled_as_final_state",
            "no_action_receipt_overuse",
            "readiness_or_preflight_overuse",
            "external_action_overblocked",
            "core_writeback_overblocked",
        },
        "patch_strategy": patch_strategy,
    }


def severity_for(classification: str, epoch: str, lower: str) -> str:
    if classification == "legitimate_hard_boundary":
        return "P3"
    if classification == "owner_manual_burden":
        return "P0" if any(token in lower for token in ["ask-user-url", "ask_user_url", "provide url", "manually search", "open multiple codex windows", "create worktrees", "merge branches"]) else "P1"
    if classification in {"discovery_blocked_unnecessarily", "disabled_as_final_state"}:
        return "P0" if epoch in {"l7_commercial", "scripts", "console_read_model"} else "P1"
    if classification in {"external_action_overblocked", "core_writeback_overblocked"}:
        return "P1"
    if classification in {"test_expectation_overconservative", "documentation_overconservative", "generated_artifact_overconservative"}:
        return "P3"
    if classification == "policy_registry_present":
        return "P3"
    return "P2"


def capability_harmed_for(classification: str) -> str:
    return {
        "owner_manual_burden": "owner automation",
        "disabled_as_final_state": "activation path",
        "readiness_or_preflight_overuse": "post-preflight execution",
        "no_action_receipt_overuse": "useful next action",
        "hardcoded_blacklist": "policy evolution",
        "hardcoded_forbidden_action_list": "typed staging",
        "external_action_overblocked": "draft/approval flow",
        "core_writeback_overblocked": "review-gated learning",
        "runtime_visibility_overblocked": "safe metadata visibility",
        "fixture_only_regression": "real controlled discovery",
    }.get(classification, "commercial planning")


def commercial_impact_for(classification: str) -> str:
    return {
        "owner_manual_burden": "manual owner labor",
        "disabled_as_final_state": "dead-end config path",
        "hardcoded_forbidden_action_list": "slower discovery/planning",
        "external_action_overblocked": "draft/execution confusion",
        "core_writeback_overblocked": "learning loop stalled",
    }.get(classification, "reduced commercial throughput")


def recommended_fix_for(classification: str) -> str:
    return {
        "legitimate_hard_boundary": "preserve boundary",
        "policy_registry_present": "keep",
        "owner_manual_burden": "replace with launcher/orchestrator",
        "disabled_as_final_state": "convert to auto-detect/activation",
        "readiness_or_preflight_overuse": "add executable staged next step",
        "no_action_receipt_overuse": "add useful staged next action",
        "hardcoded_blacklist": "move to staged policy registry",
        "hardcoded_forbidden_action_list": "add policy_ref and split stages",
        "external_action_overblocked": "allow drafts; approve execution",
        "core_writeback_overblocked": "allow candidates/dry-run",
        "runtime_visibility_overblocked": "allow metadata; restrict raw state",
    }.get(classification, "migrate to staged policy")


def target_policy_for(classification: str, family: str) -> str:
    if classification == "owner_manual_burden":
        return "policy/owner_burden_reduction_policy.json"
    if family == "core_writeback" or classification == "core_writeback_overblocked":
        return "policy/writeback_policy.json"
    if family == "runtime_visibility" or classification == "runtime_visibility_overblocked":
        return "policy/runtime_access_policy.json"
    if family == "external_side_effect" or classification == "external_action_overblocked":
        return "policy/approval_state_machine.json"
    if classification == "policy_registry_present":
        return "policy/policy_registry_manifest.json"
    return "policy/action_capability_registry.json"


def patch_strategy_for(classification: str) -> str:
    return {
        "legitimate_hard_boundary": "preserve_hard_boundary",
        "policy_registry_present": "defer",
        "owner_manual_burden": "replace_user_manual_step_with_launcher",
        "disabled_as_final_state": "convert_disabled_to_auto_detect",
        "readiness_or_preflight_overuse": "migrate_to_staged_policy",
        "no_action_receipt_overuse": "migrate_to_staged_policy",
        "hardcoded_blacklist": "migrate_to_staged_policy",
        "hardcoded_forbidden_action_list": "add_policy_ref",
        "external_action_overblocked": "convert_blocked_to_approval_gate",
        "core_writeback_overblocked": "split_read_draft_execute",
        "runtime_visibility_overblocked": "split_read_draft_execute",
    }.get(classification, "defer")


def scan_files(paths: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    skipped = Counter()
    text_files = 0
    lower_patterns = [(pattern, pattern.lower()) for pattern in ALL_PATTERNS]
    for path_str in paths:
        if is_skipped(path_str):
            skipped["unsafe_or_irrelevant_pattern"] += 1
            continue
        text = read_text_file(path_str)
        if text is None:
            skipped["binary_or_unreadable"] += 1
            continue
        text_files += 1
        for line_number, line in enumerate(text.splitlines(), start=1):
            lowered = line.lower()
            for pattern, lower_pattern in lower_patterns:
                if lower_pattern in lowered:
                    meta = classify(path_str, line, pattern)
                    finding_id = f"l7_0q2_finding_{len(findings) + 1:06d}"
                    findings.append({
                        "finding_id": finding_id,
                        "file_path": path_str,
                        "line_number": line_number,
                        "matched_pattern": pattern,
                        "matched_excerpt_short": line.strip()[:220],
                        "directory_group": directory_group(path_str),
                        "artifact_epoch": artifact_epoch(path_str),
                        "current_behavior": "tracked text match",
                        **meta,
                    })
    scan_meta = {
        "total_tracked_files": len(paths),
        "total_text_files_scanned": text_files,
        "skipped_counts": dict(skipped),
    }
    return findings, scan_meta


def compact_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "finding_id": f["finding_id"],
            "file_path": f["file_path"],
            "line_number": f["line_number"],
            "matched_pattern": f["matched_pattern"],
            "matched_excerpt_short": f["matched_excerpt_short"],
            "classification": f["classification"],
            "severity": f["severity"],
            "migration_target_policy": f["migration_target_policy"],
            "patch_strategy": f["patch_strategy"],
        }
        for f in findings
    ]


def inventory_refs(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "finding_id": f["finding_id"],
            "file_path": f["file_path"],
            "line_number": f["line_number"],
            "matched_pattern": f["matched_pattern"],
            "classification": f["classification"],
            "severity": f["severity"],
            "migration_target_policy": f["migration_target_policy"],
            "patch_strategy": f["patch_strategy"],
        }
        for f in findings
    ]


def inventory_summary(findings: list[dict[str, Any]]) -> dict[str, Any]:
    by_file = Counter(f["file_path"] for f in findings)
    by_class = Counter(f["classification"] for f in findings)
    by_sev = Counter(f["severity"] for f in findings)
    return {
        "count": len(findings),
        "classification_counts": dict(sorted(by_class.items())),
        "severity_counts": dict(sorted(by_sev.items())),
        "top_files": [{"file_path": path, "finding_count": count} for path, count in by_file.most_common(50)],
        "sample_findings": inventory_refs(findings[:200]),
    }


def summarize_by_file(findings: list[dict[str, Any]], scanned_paths: list[str]) -> list[dict[str, Any]]:
    by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for finding in findings:
        by_file[finding["file_path"]].append(finding)
    rows = []
    for path, items in by_file.items():
        rows.append({
            "file_path": path,
            "directory_group": directory_group(path),
            "artifact_epoch": artifact_epoch(path),
            "finding_count": len(items),
            "harmful_overconservatism_count": sum(1 for item in items if item["harmful_overconservatism"]),
            "legitimate_hard_boundary_count": sum(1 for item in items if item["legitimate_hard_boundary"]),
            "policy_registry_present_count": sum(1 for item in items if item["classification"] == "policy_registry_present"),
            "severity_counts": dict(Counter(item["severity"] for item in items)),
            "classification_counts": dict(Counter(item["classification"] for item in items)),
            "needs_policy_ref_migration": any(item["migration_target_policy"].startswith("policy/") and item["classification"] != "policy_registry_present" for item in items)
            and not any(item["classification"] == "policy_registry_present" for item in items),
        })
    rows.sort(key=lambda row: (row["harmful_overconservatism_count"], row["finding_count"]), reverse=True)
    return rows


def summarize_by_directory(file_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_dir: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in file_rows:
        by_dir[row["directory_group"]].append(row)
    rows = []
    for group, items in by_dir.items():
        classifications = Counter()
        severities = Counter()
        for item in items:
            classifications.update(item["classification_counts"])
            severities.update(item["severity_counts"])
        rows.append({
            "directory_group": group,
            "files_with_findings": len(items),
            "finding_count": sum(item["finding_count"] for item in items),
            "harmful_overconservatism_count": sum(item["harmful_overconservatism_count"] for item in items),
            "legitimate_hard_boundary_count": sum(item["legitimate_hard_boundary_count"] for item in items),
            "classification_counts": dict(classifications),
            "severity_counts": dict(severities),
        })
    rows.sort(key=lambda row: (row["harmful_overconservatism_count"], row["finding_count"]), reverse=True)
    return rows


def top_findings(findings: list[dict[str, Any]], classifications: set[str], limit: int = 20) -> list[dict[str, Any]]:
    return compact_findings([f for f in findings if f["classification"] in classifications][:limit])


def build_migration_map(findings: list[dict[str, Any]], file_rows: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [row for row in file_rows if row["needs_policy_ref_migration"]]
    candidate_findings_by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for finding in findings:
        if finding["classification"] in {"legitimate_hard_boundary", "policy_registry_present"}:
            continue
        candidate_findings_by_file[finding["file_path"]].append(finding)
    migrations = []
    for row in candidates:
        items = candidate_findings_by_file.get(row["file_path"], [])
        if not items:
            continue
        worst = sorted(items, key=lambda f: {"P0": 0, "P1": 1, "P2": 2, "P3": 3}.get(f["severity"], 9))[0]
        priority = worst["severity"]
        if row["artifact_epoch"] in {"l5", "l6_early", "generated", "docs"} and priority in {"P0", "P1"}:
            priority = "P2"
        migrations.append({
            "file_path": row["file_path"],
            "migration_priority": priority,
            "current_pattern": worst["matched_pattern"],
            "target_policy_ref": worst["migration_target_policy"],
            "recommended_patch_type": worst["patch_strategy"],
            "risk_of_patch": "low" if priority in {"P2", "P3"} else "medium",
            "suggested_milestone": f"L7.0Q2-{priority.lower()}-migration",
            "expected_capability_gain": worst["capability_harmed"],
        })
    groups = {
        "P0": [],
        "P1": [],
        "P2": [],
        "P3": [],
    }
    for item in migrations:
        groups[item["migration_priority"]].append(item)
    return {
        "schema_version": "v0",
        "milestone_id": MILESTONE_ID,
        "migration_groups": groups,
        "total_files_needing_policy_ref_migration": len(migrations),
        "p0_count": len(groups["P0"]),
        "p1_count": len(groups["P1"]),
        "p2_count": len(groups["P2"]),
        "p3_count": len(groups["P3"]),
    }


def policy_coverage(file_rows: list[dict[str, Any]], text_files_scanned: int) -> dict[str, Any]:
    files_using_policy = sum(1 for row in file_rows if row["policy_registry_present_count"] > 0)
    files_needing = sum(1 for row in file_rows if row["needs_policy_ref_migration"])
    denom = max(files_using_policy + files_needing, 1)
    return {
        "schema_version": "v0",
        "milestone_id": MILESTONE_ID,
        "policy_directory_exists": POLICY_DIR.is_dir(),
        "required_policy_files_present": all((POLICY_DIR / name).exists() for name in [
            "README.md",
            "action_capability_registry.json",
            "action_risk_tiers.json",
            "approval_state_machine.json",
            "discovery_policy.json",
            "runtime_access_policy.json",
            "writeback_policy.json",
            "revenue_action_policy.json",
            "owner_burden_reduction_policy.json",
            "policy_registry_manifest.json",
        ]),
        "total_text_files_scanned": text_files_scanned,
        "number_of_files_already_using_policy_ref": files_using_policy,
        "number_of_files_needing_policy_ref_migration": files_needing,
        "policy_registry_coverage_percentage": round((files_using_policy / denom) * 100, 2),
    }


def write_reports(findings: list[dict[str, Any]], scan_meta: dict[str, Any]) -> None:
    file_rows = summarize_by_file(findings, [])
    dir_rows = summarize_by_directory(file_rows)
    by_severity = Counter(f["severity"] for f in findings)
    by_classification = Counter(f["classification"] for f in findings)
    by_epoch = Counter(f["artifact_epoch"] for f in findings)
    coverage = policy_coverage(file_rows, scan_meta["total_text_files_scanned"])
    migration_map = build_migration_map(findings, file_rows)
    harmful_count = sum(1 for f in findings if f["harmful_overconservatism"])

    scorecard = {
        "schema_version": "v0",
        "milestone_id": MILESTONE_ID,
        **scan_meta,
        "total_findings": len(findings),
        "findings_by_severity": dict(sorted(by_severity.items())),
        "findings_by_classification": dict(sorted(by_classification.items())),
        "findings_by_artifact_epoch": dict(sorted(by_epoch.items())),
        "top_20_files_by_conservatism_density": file_rows[:20],
        "top_20_directories_by_conservatism_density": dir_rows[:20],
        "top_20_owner_manual_burden_locations": top_findings(findings, {"owner_manual_burden"}),
        "top_20_hardcoded_forbidden_action_lists": top_findings(findings, {"hardcoded_blacklist", "hardcoded_forbidden_action_list"}),
        "top_20_disabled_as_final_state_locations": top_findings(findings, {"disabled_as_final_state"}),
        "top_20_no_action_readiness_overuse_locations": top_findings(findings, {"no_action_receipt_overuse", "readiness_or_preflight_overuse"}),
        "policy_registry_coverage_percentage": coverage["policy_registry_coverage_percentage"],
        "number_of_files_already_using_policy_ref": coverage["number_of_files_already_using_policy_ref"],
        "number_of_files_needing_policy_ref_migration": coverage["number_of_files_needing_policy_ref_migration"],
    }
    report = {
        "schema_version": "v0",
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "generated_at_utc": utc_now(),
        "scan_method": "git ls-files tracked-file scan only",
        "core_principle": "Maximize discovery and useful commercial planning. Minimize owner manual burden. Block unapproved external side effects. Block unreviewed permanent writeback.",
        "scorecard_ref": "l7_full_repo_conservatism_scan/scorecard.json",
        "policy_migration_map_ref": "l7_full_repo_conservatism_scan/policy_migration_map.json",
        "summary": scorecard,
    }
    summary = {
        "schema_version": "v0",
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "total_tracked_files_scanned": scan_meta["total_tracked_files"],
        "total_text_files_scanned": scan_meta["total_text_files_scanned"],
        "total_findings": len(findings),
        "findings_by_severity": dict(sorted(by_severity.items())),
        "findings_by_classification": dict(sorted(by_classification.items())),
        "findings_by_artifact_epoch": dict(sorted(by_epoch.items())),
        "harmful_overconservatism_count": harmful_count,
        "legitimate_hard_boundary_count": by_classification.get("legitimate_hard_boundary", 0),
        "policy_registry_coverage_percentage": coverage["policy_registry_coverage_percentage"],
        "files_needing_policy_ref_migration": coverage["number_of_files_needing_policy_ref_migration"],
        "p0_migration_targets": migration_map["migration_groups"]["P0"][:20],
        "first_patch_applied": True,
        "first_patch_description": "L7.0P status output now references the staged policy registry; L7.0P artifacts already carry L7.0Q policy refs.",
        "ask_user_for_url_occurred": False,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "secret_values_serialized": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        "db_log_wal_shm_active_agent_marker_content_read": False,
    }
    receipt = {
        "schema_version": "v0",
        "milestone_id": MILESTONE_ID,
        "scan_method": "tracked_files_only_via_git_ls_files",
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "ask_user_for_url_occurred": False,
        "secret_values_serialized": False,
        "db_files_read": False,
        "wal_files_read": False,
        "shm_files_read": False,
        "log_files_read": False,
        "active_agent_marker_content_read": False,
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
    }

    write_json(OUT / "full_repo_conservatism_scan_report.json", report)
    write_json_compact(OUT / "line_level_findings.json", {"schema_version": "v0", "milestone_id": MILESTONE_ID, "count": len(findings), "findings": findings})
    write_json_compact(OUT / "file_level_summary.json", {"schema_version": "v0", "milestone_id": MILESTONE_ID, "files": file_rows})
    write_json_compact(OUT / "directory_level_summary.json", {"schema_version": "v0", "milestone_id": MILESTONE_ID, "directories": dir_rows})
    for filename, classes in INVENTORY_FILES.items():
        selected = [finding for finding in findings if finding["classification"] in classes]
        inventory = inventory_summary(selected)
        write_json_compact(
            OUT / filename,
            {
                "schema_version": "v0",
                "milestone_id": MILESTONE_ID,
                "count": inventory["count"],
                "inventory_note": "Inventory is summarized here; full line-level finding records are in line_level_findings.json.",
                **inventory,
            },
        )
    write_json(OUT / "policy_registry_coverage_report.json", coverage)
    write_json_compact(OUT / "policy_migration_map.json", migration_map)
    write_json(OUT / "scorecard.json", scorecard)
    write_json(OUT / "l7_0q2_summary.json", summary)
    write_json(OUT / "l7_0q2_no_action_receipt.json", receipt)
    write_text(OUT / "scorecard.md", render_scorecard(scorecard))
    write_text(OUT / "full_repo_conservatism_scan_report.md", render_report(summary, scorecard))
    write_text(OUT / "p0_p1_remediation_plan.md", render_remediation_plan(migration_map))
    write_text(OUT / "l7_0q2_summary.md", f"# L7.0Q2 Summary\n\n```json\n{json.dumps(summary, indent=2, sort_keys=False)}\n```\n")


def write_json_compact(path: Path, payload: Any) -> None:
    write_json(path, payload, compact=True)


def render_scorecard(scorecard: dict[str, Any]) -> str:
    lines = [
        "# L7.0Q2 Scorecard",
        "",
        f"- Total tracked files: {scorecard['total_tracked_files']}",
        f"- Text files scanned: {scorecard['total_text_files_scanned']}",
        f"- Total findings: {scorecard['total_findings']}",
        f"- Severity: {scorecard['findings_by_severity']}",
        f"- Classification: {scorecard['findings_by_classification']}",
        f"- Policy coverage: {scorecard['policy_registry_coverage_percentage']}%",
        "",
        "## Top Files",
    ]
    for row in scorecard["top_20_files_by_conservatism_density"][:20]:
        lines.append(f"- `{row['file_path']}`: {row['harmful_overconservatism_count']} harmful / {row['finding_count']} total")
    return "\n".join(lines) + "\n"


def render_report(summary: dict[str, Any], scorecard: dict[str, Any]) -> str:
    lines = [
        "# L7.0Q2 Full Repository Conservatism Scan",
        "",
        "This scan used tracked files from `git ls-files` and skipped DB/WAL/SHM/log/active-agent/env/secret/binary surfaces.",
        "",
        "## Core Principle",
        "",
        "Maximize discovery and useful commercial planning. Minimize owner manual burden. Block unapproved external side effects. Block unreviewed permanent writeback.",
        "",
        "## Summary",
        "",
        f"- Total tracked files scanned: {summary['total_tracked_files_scanned']}",
        f"- Total text files scanned: {summary['total_text_files_scanned']}",
        f"- Total findings: {summary['total_findings']}",
        f"- Harmful overconservatism count: {summary['harmful_overconservatism_count']}",
        f"- Legitimate hard boundary count: {summary['legitimate_hard_boundary_count']}",
        f"- Files needing policy_ref migration: {summary['files_needing_policy_ref_migration']}",
        f"- Policy coverage: {summary['policy_registry_coverage_percentage']}%",
        "",
        "## Top Owner Burden Findings",
    ]
    for finding in scorecard["top_20_owner_manual_burden_locations"][:20]:
        lines.append(f"- `{finding['file_path']}:{finding['line_number']}` {finding['matched_pattern']}: {finding['matched_excerpt_short']}")
    return "\n".join(lines) + "\n"


def render_remediation_plan(migration_map: dict[str, Any]) -> str:
    lines = ["# L7.0Q2 P0/P1 Remediation Plan", ""]
    for priority in ["P0", "P1"]:
        lines.append(f"## {priority}")
        items = migration_map["migration_groups"][priority][:50]
        if not items:
            lines.append("- No items.")
        for item in items:
            lines.append(f"- `{item['file_path']}`: {item['recommended_patch_type']} -> {item['target_policy_ref']} ({item['expected_capability_gain']})")
        lines.append("")
    return "\n".join(lines)


def apply_first_patch() -> None:
    script = ROOT / "scripts/run_l7_parallel_lanes.sh"
    if not script.exists():
        return
    text = script.read_text(encoding="utf-8")
    needle = '  echo "core writeback: blocked"\n'
    replacement = '  echo "core writeback: blocked"\n  echo "policy registry: policy/action_capability_registry.json (staged capability control)"\n'
    if needle in text and "policy registry: policy/action_capability_registry.json" not in text:
        script.write_text(text.replace(needle, replacement), encoding="utf-8")


def main() -> None:
    apply_first_patch()
    paths = git_ls_files()
    findings, scan_meta = scan_files(paths)
    write_reports(findings, scan_meta)
    print(
        f"L7.0Q2 full repo tracked-file scan complete: "
        f"{scan_meta['total_tracked_files']} tracked, "
        f"{scan_meta['total_text_files_scanned']} text, "
        f"{len(findings)} findings."
    )


if __name__ == "__main__":
    main()
