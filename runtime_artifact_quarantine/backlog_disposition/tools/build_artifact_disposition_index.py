#!/usr/bin/env python3
"""Build disposition records for the full quarantined artifact backlog.

This builder reads only curated generated indexes. It does not open raw artifact
contents, DBs, logs, active-agent markers, daemon state, or runtime reports.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
QUARANTINE_MANIFEST_REF = "runtime_artifact_quarantine/generated/runtime_artifact_manifest.json"
CANDIDATE_INDEX_REF = "runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.json"
REVIEW_QUEUE_REF = "runtime_artifact_quarantine/safe_mining/review_queue/generated/candidate_review_queue.json"

SAFE_REPORT_CLASSES = {
    "DREAM_REPORT",
    "DAILY_REPORT",
    "DRIFT_REPORT",
    "ESCALATION_REPORT",
    "WHITELIST_REPORT",
}
FORBIDDEN_DIRECT_READ_CLASSES = {
    "DB_CORE",
    "BACKUP_DB",
    "DB_SIDECARE",
    "LOG_RUNTIME",
    "ACTIVE_AGENT_MARKER",
    "DAEMON_STATE",
    "CACHE_SENTINEL",
    "PYCACHE",
    "UNKNOWN_RUNTIME_ARTIFACT",
}
MARKER_METADATA_CLASSES = {"ACTIVE_AGENT_MARKER", "DAEMON_STATE", "CACHE_SENTINEL"}


def load_json(relative_path: str) -> Any:
    path = ROOT / relative_path
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def disposition_for_class(artifact_class: str, path: str, candidate: dict[str, Any] | None, review: dict[str, Any] | None) -> tuple[str, str, bool]:
    if candidate and review:
        return (
            "safe_mined_to_review_queue",
            "Safe-mined candidate is present in the generated review queue.",
            False,
        )
    if candidate:
        return (
            "safe_mined_candidate_only",
            "Safe-mined candidate exists but no review queue entry was found.",
            False,
        )
    if artifact_class in {"DB_CORE", "BACKUP_DB"}:
        return (
            "deferred_requires_readonly_db_adapter",
            "Database artifacts require a future readonly metadata/DB adapter.",
            False,
        )
    if artifact_class == "DB_SIDECARE" or path.lower().endswith((".db-wal", ".db-shm", ".sqlite-wal", ".sqlite-shm", ".wal", ".shm")):
        return (
            "deferred_sidecar_or_transaction_file",
            "Database sidecar or transaction files must not be directly read.",
            False,
        )
    if artifact_class == "LOG_RUNTIME":
        return (
            "deferred_requires_bounded_log_adapter",
            "Runtime logs require a future bounded log adapter.",
            False,
        )
    if artifact_class in MARKER_METADATA_CLASSES:
        return (
            "deferred_requires_marker_metadata_adapter",
            "Marker, daemon, and cache/sentinel files require future metadata-only adapters.",
            False,
        )
    if artifact_class == "PYCACHE":
        return (
            "ignored_generated_cache",
            "Python cache files have no direct semantic value for memory.",
            False,
        )
    if artifact_class == "UNKNOWN_RUNTIME_ARTIFACT":
        return (
            "deferred_requires_classification",
            "Unknown runtime artifacts require future classification before handling.",
            False,
        )
    if artifact_class in {"UNKNOWN_OR_NON_RUNTIME", "FRAMEWORK_FILE"}:
        return (
            "ignored_or_non_runtime",
            "Non-runtime or framework files are not artifact-mining targets.",
            False,
        )
    if artifact_class in SAFE_REPORT_CLASSES:
        return (
            "deferred_markdown_report_not_selected",
            "Markdown report class is eligible for safe mining but was not selected within current bounds.",
            False,
        )
    return (
        "deferred_requires_classification",
        "Artifact class has no disposition-specific adapter yet.",
        False,
    )


def allowed_next_step(disposition: str) -> str:
    mapping = {
        "safe_mined_to_review_queue": "future_evidence_scoring_after_review",
        "safe_mined_candidate_only": "generate_or_repair_review_queue_entry",
        "deferred_requires_readonly_db_adapter": "future_readonly_db_metadata_adapter",
        "deferred_sidecar_or_transaction_file": "do_not_read_until_db_adapter_policy",
        "deferred_requires_bounded_log_adapter": "future_bounded_log_adapter",
        "deferred_requires_marker_metadata_adapter": "future_metadata_only_marker_adapter",
        "ignored_generated_cache": "ignore_or_future_cleanup_policy",
        "deferred_requires_classification": "future_artifact_classification",
        "ignored_or_non_runtime": "ignore_for_runtime_artifact_mining",
        "deferred_markdown_report_not_selected": "future_safe_mining_bounds_or_review",
    }
    return mapping.get(disposition, "future_classification")


def forbidden_next_steps() -> list[str]:
    return [
        "direct_brain_writeback",
        "direct_memory_ingestion",
        "direct_cieu_write",
        "runtime_recovery",
        "semantic_truth_scoring_without_review",
        "candidate_auto_approval",
    ]


def build_index() -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    quarantine = load_json(QUARANTINE_MANIFEST_REF)
    candidates = load_json(CANDIDATE_INDEX_REF)
    review_queue = load_json(REVIEW_QUEUE_REF)

    candidate_by_path = {candidate.get("source_path"): candidate for candidate in candidates.get("candidates", [])}
    review_by_candidate = {entry.get("candidate_id"): entry for entry in review_queue.get("entries", [])}
    records: list[dict[str, Any]] = []

    for index, artifact in enumerate(quarantine.get("artifacts", []), start=1):
        artifact_path = artifact.get("path")
        artifact_class = artifact.get("artifact_class", "UNKNOWN_RUNTIME_ARTIFACT")
        candidate = candidate_by_path.get(artifact_path)
        review = review_by_candidate.get(candidate.get("candidate_id")) if candidate else None
        disposition, rationale, direct_read_allowed = disposition_for_class(
            artifact_class,
            str(artifact_path),
            candidate,
            review,
        )
        if artifact_class in FORBIDDEN_DIRECT_READ_CLASSES:
            direct_read_allowed = False
        record = {
            "disposition_id": f"disp-{index:04d}",
            "artifact_path": artifact_path,
            "artifact_class": artifact_class,
            "disposition": disposition,
            "source_in_quarantine_manifest": True,
            "safe_mining_candidate_id": candidate.get("candidate_id") if candidate else None,
            "review_id": review.get("review_id") if review else None,
            "review_status": review.get("review_status") if review else None,
            "ingestion_status": "not_ingested",
            "evidence_scoring_status": "not_started",
            "allowed_next_step": allowed_next_step(disposition),
            "forbidden_next_steps": forbidden_next_steps(),
            "direct_read_allowed": direct_read_allowed,
            "forbidden_direct_read": artifact_class in FORBIDDEN_DIRECT_READ_CLASSES,
            "brain_writeback_allowed": False,
            "memory_ingestion_allowed": False,
            "cieu_write_allowed": False,
            "rationale": rationale,
            "generated_from_refs": [
                QUARANTINE_MANIFEST_REF,
                CANDIDATE_INDEX_REF,
                REVIEW_QUEUE_REF,
            ],
        }
        records.append(record)

    disposition_counts = Counter(record["disposition"] for record in records)
    class_counts = Counter(record["artifact_class"] for record in records)
    evidence_counts = Counter(record["evidence_scoring_status"] for record in records)
    forbidden_count = sum(1 for record in records if record["forbidden_direct_read"])
    deferred_adapter_counts = {
        key: count
        for key, count in disposition_counts.items()
        if key.startswith("deferred_")
    }

    summary = {
        "total_artifacts": len(quarantine.get("artifacts", [])),
        "artifacts_with_disposition": len(records),
        "dispositions": dict(disposition_counts),
        "artifact_classes": dict(class_counts),
        "safe_mined_to_review_queue": disposition_counts.get("safe_mined_to_review_queue", 0),
        "deferred_adapter_counts": deferred_adapter_counts,
        "ignored_generated_cache": disposition_counts.get("ignored_generated_cache", 0),
        "forbidden_direct_read_count": forbidden_count,
        "evidence_scoring_status": dict(evidence_counts),
        "warning": "Disposition is not ingestion. No brain/memory/CIEU writes are allowed.",
    }

    index_payload = {
        "schema_name": "ystar.runtime_artifact_quarantine.backlog_disposition.index",
        "schema_version": "v0",
        "builder": "runtime_artifact_quarantine/backlog_disposition/tools/build_artifact_disposition_index.py",
        "source_files": [
            QUARANTINE_MANIFEST_REF,
            CANDIDATE_INDEX_REF,
            REVIEW_QUEUE_REF,
        ],
        "summary": summary,
        "records": records,
    }
    manifest = {
        "schema_name": "ystar.runtime_artifact_quarantine.backlog_disposition.manifest",
        "schema_version": "v0",
        "source_files": index_payload["source_files"],
        "generated_files": [
            "runtime_artifact_quarantine/backlog_disposition/generated/artifact_disposition_index.json",
            "runtime_artifact_quarantine/backlog_disposition/generated/artifact_disposition_summary.md",
            "runtime_artifact_quarantine/backlog_disposition/generated/disposition_manifest.json",
        ],
        "total_artifacts": summary["total_artifacts"],
        "artifacts_with_disposition": summary["artifacts_with_disposition"],
        "safety_note": summary["warning"],
    }
    return index_payload, manifest, manifest["generated_files"]


def write_json(relative_path: str, payload: Any) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")


def write_text(relative_path: str, text: str) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)


def render_summary(index_payload: dict[str, Any]) -> str:
    summary = index_payload["summary"]
    lines = [
        "# Runtime Artifact Backlog Disposition Summary",
        "",
        "Disposition is classification and routing metadata only. It is not ingestion.",
        "",
        f"- Total artifacts: {summary['total_artifacts']}",
        f"- Artifacts with disposition: {summary['artifacts_with_disposition']}",
        f"- Safe-mined to review queue: {summary['safe_mined_to_review_queue']}",
        f"- Forbidden direct read count: {summary['forbidden_direct_read_count']}",
        "",
        "## Dispositions",
        "",
    ]
    for disposition, count in sorted(summary.get("dispositions", {}).items()):
        lines.append(f"- {disposition}: {count}")
    lines.extend(["", "## Deferred Adapter Counts", ""])
    for disposition, count in sorted(summary.get("deferred_adapter_counts", {}).items()):
        lines.append(f"- {disposition}: {count}")
    lines.extend(["", f"Warning: {summary['warning']}", ""])
    return "\n".join(lines)


def main() -> int:
    try:
        index_payload, manifest, generated_files = build_index()
        write_json(
            "runtime_artifact_quarantine/backlog_disposition/generated/artifact_disposition_index.json",
            index_payload,
        )
        write_text(
            "runtime_artifact_quarantine/backlog_disposition/generated/artifact_disposition_summary.md",
            render_summary(index_payload),
        )
        write_json(
            "runtime_artifact_quarantine/backlog_disposition/generated/disposition_manifest.json",
            manifest,
        )
    except Exception as exc:
        print("Artifact Disposition Index Builder: FAIL")
        print(f"Error: {exc}")
        return 1

    summary = index_payload["summary"]
    print("Artifact Disposition Index Builder: PASS")
    print(f"Total artifacts: {summary['total_artifacts']}")
    print(f"Artifacts with disposition: {summary['artifacts_with_disposition']}")
    print("Dispositions:")
    for disposition, count in sorted(summary.get("dispositions", {}).items()):
        print(f"- {disposition}: {count}")
    print("Generated files:")
    for path in generated_files:
        print(f"- {path}")
    print(summary["warning"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
