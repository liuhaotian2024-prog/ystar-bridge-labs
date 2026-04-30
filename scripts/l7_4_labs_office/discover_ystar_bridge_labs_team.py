#!/usr/bin/env python3
"""Safely discover legacy Y* Bridge Labs team evidence.

The scanner reads only safe tracked text files from the sibling
``ystar-bridge-labs`` repository. It deliberately skips DB/WAL/SHM, logs,
active-agent markers, local secret/env files, and common binary/runtime paths.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CURRENT_REPO = Path(__file__).resolve().parents[2]
DEFAULT_LEGACY_REPO = CURRENT_REPO.parent / "ystar-bridge-labs"
OUT = CURRENT_REPO / "l7_labs_office_legacy_integration" / "legacy_repo_inspection"
GENERATED_AT = "2026-04-30T00:00:00Z"

SEARCH_TERMS = [
    "team",
    "Aiden",
    "Ethan",
    "Sofia",
    "Marco",
    "Zara",
    "Samantha",
    "Leo",
    "Maya",
    "Ryan",
    "Jordan",
    "Jinjin",
    "K9 Scout",
    "Board",
    "Founder",
    "CEO",
    "CTO",
    "CMO",
    "CFO",
    "CSO",
    "Secretary",
    "Engineer",
    "Research",
    "brain",
    "memory",
    "DNA",
    "profile",
    "role",
    "agent",
    "governance",
    "directive",
    "responsibility",
    "inbox",
    "handoff",
    "report",
    "morning",
    "daily",
    "cases",
    "amendment",
]

CANONICAL_AGENTS: list[dict[str, str]] = [
    {"legacy_agent_id": "haotian_board_founder", "display_name": "Haotian Liu", "role": "Board / Founder"},
    {"legacy_agent_id": "aiden_ceo", "display_name": "Aiden Liu", "role": "CEO"},
    {"legacy_agent_id": "ethan_cto", "display_name": "Ethan Wright", "role": "CTO"},
    {"legacy_agent_id": "sofia_cmo", "display_name": "Sofia Blake", "role": "CMO"},
    {"legacy_agent_id": "marco_cfo", "display_name": "Marco Rivera", "role": "CFO"},
    {"legacy_agent_id": "zara_cso", "display_name": "Zara Johnson", "role": "CSO"},
    {"legacy_agent_id": "samantha_secretary", "display_name": "Samantha Lin", "role": "Secretary"},
    {"legacy_agent_id": "leo_engineer", "display_name": "Leo Chen", "role": "Kernel Engineer"},
    {"legacy_agent_id": "maya_engineer", "display_name": "Maya Patel", "role": "Governance Engineer"},
    {"legacy_agent_id": "ryan_engineer", "display_name": "Ryan Park", "role": "Platform Engineer"},
    {"legacy_agent_id": "jordan_engineer", "display_name": "Jordan Lee", "role": "Domains Engineer"},
    {"legacy_agent_id": "jinjin_k9_scout", "display_name": "Jinjin / K9 Scout", "role": "Research / Cross-model Scout"},
]


SKIP_SUFFIXES = {
    ".db",
    ".db-wal",
    ".db-shm",
    ".sqlite",
    ".sqlite3",
    ".pyc",
    ".pyo",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".mp4",
    ".mov",
    ".jsonl",
    ".log",
}

SAFE_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".py",
    ".sh",
    ".html",
    ".css",
    ".js",
}

SKIP_PARTS = {
    ".git",
    "__pycache__",
    "scripts/.logs",
    ".logs",
    "data/cieu_archive",
    "data/k9_export",
    "logs",
}

SKIP_NAME_PATTERNS = (
    "active_agent",
    ".env",
    "secret",
    "token",
    "credential",
)


@dataclass
class SafeFile:
    path: str
    text: str


def run_git(args: list[str], repo: Path) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True, stderr=subprocess.DEVNULL)


def is_safe_tracked_text(path: str) -> bool:
    normalized = path.replace("\\", "/")
    lowered = normalized.lower()
    if any(part in lowered for part in SKIP_PARTS):
        return False
    if any(pattern in lowered for pattern in SKIP_NAME_PATTERNS):
        return False
    if any(lowered.endswith(suffix) for suffix in SKIP_SUFFIXES):
        return False
    suffix = Path(normalized).suffix.lower()
    return suffix in SAFE_SUFFIXES or "/" not in normalized and suffix == ""


def safe_tracked_files(repo: Path) -> list[SafeFile]:
    files = []
    for line in run_git(["ls-files"], repo).splitlines():
        if not is_safe_tracked_text(line):
            continue
        path = repo / line
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        if b"\x00" in raw:
            continue
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            continue
        files.append(SafeFile(line, text))
    return files


def short_excerpt(line: str, limit: int = 220) -> str:
    compact = re.sub(r"\s+", " ", line).strip()
    return compact[:limit]


def find_matches(files: list[SafeFile]) -> dict[str, list[dict[str, Any]]]:
    pattern = re.compile("|".join(re.escape(term) for term in SEARCH_TERMS), re.IGNORECASE)
    results: dict[str, list[dict[str, Any]]] = {}
    for safe_file in files:
        matches = []
        for number, line in enumerate(safe_file.text.splitlines(), 1):
            match = pattern.search(line)
            if not match:
                continue
            matches.append(
                {
                    "file_path": safe_file.path,
                    "line_number": number,
                    "matched_pattern": match.group(0),
                    "matched_excerpt_short": short_excerpt(line),
                }
            )
            if len(matches) >= 10:
                break
        if matches:
            results[safe_file.path] = matches
    return results


def agent_evidence(files: list[SafeFile]) -> list[dict[str, Any]]:
    discovered = []
    for agent in CANONICAL_AGENTS:
        names = {agent["display_name"], agent["display_name"].split()[0], agent["legacy_agent_id"].split("_")[0]}
        if agent["legacy_agent_id"] == "jinjin_k9_scout":
            names |= {"Jinjin", "K9 Scout", "金金"}
        evidence = []
        brain_refs: set[str] = set()
        dna_refs: set[str] = set()
        governance_refs: set[str] = set()
        report_refs: set[str] = set()
        for safe_file in files:
            text_lower = safe_file.text.lower()
            if not any(name.lower() in text_lower for name in names):
                continue
            for number, line in enumerate(safe_file.text.splitlines(), 1):
                if any(name.lower() in line.lower() for name in names):
                    evidence.append(
                        {
                            "file_path": safe_file.path,
                            "line_number": number,
                            "excerpt": short_excerpt(line),
                        }
                    )
                    break
            lower_path = safe_file.path.lower()
            if "brain" in lower_path or "role_definition" in lower_path or "profile" in lower_path:
                brain_refs.add(safe_file.path)
            if "dna" in lower_path or "wisdom" in lower_path or "memory" in lower_path:
                dna_refs.add(safe_file.path)
            if "governance" in lower_path or "agents.md" in lower_path or "amendment" in lower_path:
                governance_refs.add(safe_file.path)
            if "reports/" in lower_path or "daily" in lower_path or "morning" in lower_path:
                report_refs.add(safe_file.path)
        discovered.append(
            {
                **agent,
                "source_files": sorted({item["file_path"] for item in evidence})[:20],
                "evidence_excerpt_short": evidence[0]["excerpt"] if evidence else "not found",
                "evidence_items": evidence[:10],
                "brain_profile_refs": sorted(brain_refs)[:20],
                "dna_memory_refs": sorted(dna_refs)[:20],
                "governance_refs": sorted(governance_refs)[:20],
                "report_refs": sorted(report_refs)[:20],
                "confidence": "high" if evidence else "needs_review",
                "safe_to_integrate": bool(evidence),
                "notes": "verified from safe tracked text files" if evidence else "needs source review",
            }
        )
    return discovered


def additional_agent_defs(files: list[SafeFile]) -> list[dict[str, Any]]:
    rows = []
    for safe_file in files:
        if not safe_file.path.startswith(".claude/agents/") or not safe_file.path.endswith(".md"):
            continue
        name_match = re.search(r"^name:\s*(.+)$", safe_file.text, re.MULTILINE)
        description_match = re.search(r"description:\s*>\s*\n([\s\S]*?)(?:\nmodel:|\neffort:|\n---)", safe_file.text)
        rows.append(
            {
                "agent_definition_file": safe_file.path,
                "declared_name": short_excerpt(name_match.group(1)) if name_match else Path(safe_file.path).stem,
                "description_excerpt": short_excerpt(description_match.group(1)) if description_match else "",
                "classification": "legacy_identity_or_capability_agent",
            }
        )
    return rows


def write(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def discover(repo: Path = DEFAULT_LEGACY_REPO) -> dict[str, Any]:
    files = safe_tracked_files(repo)
    matches = find_matches(files)
    agents = agent_evidence(files)
    extra_defs = additional_agent_defs(files)
    head = run_git(["rev-parse", "--short", "HEAD"], repo).strip()
    status = run_git(["status", "--short"], repo).splitlines()
    receipt = {
        "schema_version": "v0",
        "generated_at_utc": GENERATED_AT,
        "legacy_repo_path": str(repo),
        "legacy_repo_available": repo.exists(),
        "legacy_repo_head": head,
        "legacy_repo_status_short": status,
        "safe_tracked_text_files_scanned": len(files),
        "unsafe_runtime_patterns_skipped": sorted(SKIP_PARTS | set(SKIP_NAME_PATTERNS)),
        "db_wal_shm_log_active_agent_content_read": False,
        "legacy_repo_modified_by_scanner": False,
    }
    inventories = {
        "legacy_agent_file_inventory": extra_defs,
        "legacy_brain_profile_inventory": sorted(
            {f.path for f in files if any(part in f.path.lower() for part in ["brain", "profile", "role_definition"])}
        ),
        "legacy_governance_artifact_inventory": sorted(
            {f.path for f in files if any(part in f.path.lower() for part in ["governance", "agents.md", "amendment", "directive"])}
        ),
        "legacy_dna_memory_inventory": sorted(
            {f.path for f in files if any(part in f.path.lower() for part in ["dna", "memory", "wisdom"])}
        ),
        "legacy_reports_inventory": sorted(
            {f.path for f in files if any(part in f.path.lower() for part in ["reports/", "morning", "daily"])}
        ),
    }
    return {
        "receipt": receipt,
        "agents": agents,
        "additional_agent_definitions": extra_defs,
        "matches_by_file": matches,
        "inventories": inventories,
    }


def main() -> None:
    data = discover()
    OUT.mkdir(parents=True, exist_ok=True)
    write(OUT / "ystar_bridge_labs_clone_receipt.json", data["receipt"])
    write(
        OUT / "legacy_team_discovery_report.json",
        {
            "schema_version": "v0",
            "generated_at_utc": GENERATED_AT,
            "legacy_agents": data["agents"],
            "additional_agent_definitions": data["additional_agent_definitions"],
            "search_terms": SEARCH_TERMS,
        },
    )
    write(OUT / "legacy_agent_file_inventory.json", data["inventories"]["legacy_agent_file_inventory"])
    write(OUT / "legacy_brain_profile_inventory.json", data["inventories"]["legacy_brain_profile_inventory"])
    write(OUT / "legacy_governance_artifact_inventory.json", data["inventories"]["legacy_governance_artifact_inventory"])
    write(OUT / "legacy_dna_memory_inventory.json", data["inventories"]["legacy_dna_memory_inventory"])
    write(OUT / "legacy_reports_inventory.json", data["inventories"]["legacy_reports_inventory"])
    write(
        OUT / "legacy_unmapped_artifacts.json",
        {
            "schema_version": "v0",
            "generated_at_utc": GENERATED_AT,
            "note": "Additional agent definitions and broad matches that need human review before identity integration.",
            "additional_agent_definitions": data["additional_agent_definitions"],
            "matched_files_count": len(data["matches_by_file"]),
        },
    )
    write(
        OUT / "legacy_discovery_no_action_receipt.json",
        {
            "schema_version": "v0",
            "generated_at_utc": GENERATED_AT,
            "external_side_effects_occurred": False,
            "core_writeback_occurred": False,
            "legacy_repo_modified": False,
            "db_wal_shm_log_active_agent_content_read": False,
            "secret_files_read": False,
            "ask_user_url_occurred": False,
        },
    )
    lines = [
        "# Legacy Team Discovery Report",
        "",
        f"Legacy repo: `{data['receipt']['legacy_repo_path']}`",
        f"Safe tracked text files scanned: {data['receipt']['safe_tracked_text_files_scanned']}",
        "",
        "## Verified Legacy Team",
    ]
    for agent in data["agents"]:
        lines.append(
            f"- **{agent['display_name']}** — {agent['role']} (`{agent['legacy_agent_id']}`), confidence: {agent['confidence']}; evidence: {agent['evidence_excerpt_short']}"
        )
    lines.extend(
        [
            "",
            "## Important Correction",
            "",
            "New L7 role assumptions must not override original Y*Bridge Labs team identities. COO/Operator/Revenue Scout are capability slots unless source evidence proves otherwise.",
        ]
    )
    write_md(OUT / "legacy_team_discovery_report.md", "\n".join(lines))
    print(f"legacy_agents_discovered: {len(data['agents'])}")
    print(f"safe_tracked_text_files_scanned: {data['receipt']['safe_tracked_text_files_scanned']}")


if __name__ == "__main__":
    main()
