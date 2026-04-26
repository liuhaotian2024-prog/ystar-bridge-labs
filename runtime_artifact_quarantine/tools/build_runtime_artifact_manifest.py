#!/usr/bin/env python3
"""Build a path-only runtime artifact manifest from git status output."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "runtime_artifact_quarantine" / "generated"

UNSAFE_CLASSES = {
    "DB_CORE",
    "DB_SIDECARE",
    "LOG_RUNTIME",
    "ACTIVE_AGENT_MARKER",
    "DAEMON_STATE",
    "CACHE_SENTINEL",
    "PYCACHE",
    "DREAM_REPORT",
    "ESCALATION_REPORT",
    "DAILY_REPORT",
    "DRIFT_REPORT",
    "WHITELIST_REPORT",
    "BACKUP_DB",
    "UNKNOWN_RUNTIME_ARTIFACT"
}


def run_git_status() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def parse_status_line(line: str) -> tuple[str, str]:
    code = line[:2]
    path = line[3:]
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return code.strip() or "modified", path


def classify(path: str) -> tuple[str, str, str]:
    lower = path.lower()
    name = Path(path).name.lower()

    if lower.startswith("runtime_artifact_quarantine/"):
        return "FRAMEWORK_FILE", "none", "Exclude from mining; framework-owned file."
    if lower.startswith("backups/") and lower.endswith(".db"):
        return "BACKUP_DB", "backup_db_inventory_adapter", "Backup DB metadata only."
    if lower.endswith((".db-wal", ".db-shm", ".sqlite-wal", ".sqlite-shm")):
        return "DB_SIDECARE", "none_or_metadata_only", "DB sidecar; do not touch contents."
    if lower.endswith((".db", ".sqlite", ".sqlite3")):
        return "DB_CORE", "readonly_db_adapter_future", "DB content forbidden; metadata only."
    if lower.startswith("scripts/.logs/") or lower.endswith(".log"):
        return "LOG_RUNTIME", "bounded_log_summarizer_future", "Log content forbidden now."
    if ".ystar_active_agent" in lower:
        return "ACTIVE_AGENT_MARKER", "active_agent_marker_summarizer_future", "Marker content avoided."
    if lower.endswith(".pid") or "daemon" in lower or "subscriber_state" in lower or "alarm_consumer_state" in lower:
        return "DAEMON_STATE", "daemon_state_metadata_adapter_future", "Daemon state content forbidden."
    if "__pycache__" in lower or lower.endswith(".pyc"):
        return "PYCACHE", "ignore_or_cleanup_policy_future", "No semantic mining value expected."
    if "cache" in lower or "sentinel" in lower or "session_call_count" in lower or "last_board_msg" in lower:
        return "CACHE_SENTINEL", "cache_sentinel_classifier_future", "Ephemeral coordination state."
    if lower.startswith("reports/ceo/brain_dream_diffs/"):
        return "DREAM_REPORT", "dream_report_bounded_parser_future", "Dream report content not read."
    if lower.startswith("reports/escalation/"):
        return "ESCALATION_REPORT", "escalation_report_parser_future", "Escalation report content not read."
    if lower.startswith("reports/daily/"):
        return "DAILY_REPORT", "daily_report_parser_future", "Daily report content not read."
    if lower.startswith("reports/drift_hourly/"):
        return "DRIFT_REPORT", "drift_report_parser_future", "Drift report content not read."
    if lower.startswith("reports/whitelist_daily/"):
        return "WHITELIST_REPORT", "whitelist_report_parser_future", "Whitelist report content not read."
    if name.startswith(".") or lower.startswith("scripts/"):
        return "UNKNOWN_RUNTIME_ARTIFACT", "manual_triage_future", "Runtime-like path needs classification."
    return "UNKNOWN_OR_NON_RUNTIME", "none", "Likely normal repo change or unclassified non-runtime path."


def stat_size(path: str) -> int | None:
    try:
        return os.stat(ROOT / path).st_size
    except OSError:
        return None


def build_manifest() -> tuple[dict, str]:
    artifacts = []
    class_counts: Counter[str] = Counter()
    unsafe_count = 0

    for line in run_git_status():
        git_status_code, path = parse_status_line(line)
        artifact_class, adapter, notes = classify(path)
        class_counts[artifact_class] += 1
        direct_read_allowed = artifact_class not in UNSAFE_CLASSES
        if not direct_read_allowed:
            unsafe_count += 1
        artifacts.append(
            {
                "path": path,
                "git_status_code": git_status_code,
                "artifact_class": artifact_class,
                "extension": Path(path).suffix,
                "size_bytes": stat_size(path),
                "direct_read_allowed": direct_read_allowed,
                "future_adapter_candidate": adapter,
                "notes": notes
            }
        )

    manifest = {
        "schema_name": "ystar.runtime_artifact_quarantine.generated.manifest",
        "schema_version": "v0",
        "inventory_level": 0,
        "content_opened": False,
        "source": "git status --short plus os.stat metadata",
        "artifacts_classified": len(artifacts),
        "unsafe_artifacts_count": unsafe_count,
        "classes_seen": dict(sorted(class_counts.items())),
        "artifacts": artifacts
    }

    lines = [
        "# Runtime Artifact Summary",
        "",
        "Path-only inventory. No artifact contents were opened.",
        "",
        f"- Artifacts classified: {len(artifacts)}",
        f"- Unsafe artifacts: {unsafe_count}",
        "",
        "## Classes Seen",
        ""
    ]
    for klass, count in sorted(class_counts.items()):
        lines.append(f"- {klass}: {count}")
    lines.append("")
    return manifest, "\n".join(lines)


def main() -> int:
    try:
        manifest, summary = build_manifest()
        GENERATED.mkdir(parents=True, exist_ok=True)
        manifest_path = GENERATED / "runtime_artifact_manifest.json"
        summary_path = GENERATED / "runtime_artifact_summary.md"
        with manifest_path.open("w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
            f.write("\n")
        with summary_path.open("w", encoding="utf-8") as f:
            f.write(summary)
    except Exception as exc:
        print("Runtime Artifact Manifest Builder: FAIL")
        print(f"Error: {exc}")
        return 1

    print("Runtime Artifact Manifest Builder: PASS")
    print(f"Artifacts classified: {manifest['artifacts_classified']}")
    print(f"Classes seen: {', '.join(manifest['classes_seen'].keys())}")
    print(f"Unsafe artifacts count: {manifest['unsafe_artifacts_count']}")
    print("Generated files:")
    print("- runtime_artifact_quarantine/generated/runtime_artifact_manifest.json")
    print("- runtime_artifact_quarantine/generated/runtime_artifact_summary.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
