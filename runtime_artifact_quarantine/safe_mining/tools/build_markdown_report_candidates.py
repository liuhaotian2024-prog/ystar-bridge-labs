#!/usr/bin/env python3
"""Build bounded candidate records from low-risk Markdown runtime reports.

This adapter reads the path-level quarantine manifest and then opens only
approved Markdown report files with strict line/character limits. It does not
read DBs, logs, active-agent markers, daemon state, or unknown artifacts.
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
SOURCE_MANIFEST = "runtime_artifact_quarantine/generated/runtime_artifact_manifest.json"
OUT_DIR = ROOT / "runtime_artifact_quarantine" / "safe_mining" / "generated"

ALLOWED_CLASSES = {
    "DREAM_REPORT",
    "DAILY_REPORT",
    "DRIFT_REPORT",
    "ESCALATION_REPORT",
    "WHITELIST_REPORT",
}
REFUSED_CLASSES = {
    "DB_CORE",
    "DB_SIDECARE",
    "LOG_RUNTIME",
    "ACTIVE_AGENT_MARKER",
    "DAEMON_STATE",
    "CACHE_SENTINEL",
    "PYCACHE",
    "BACKUP_DB",
    "UNKNOWN_RUNTIME_ARTIFACT",
}
MARKDOWN_EXTENSIONS = {".md", ".markdown"}
MAX_FILES_PER_CLASS = 5
MAX_LINES_PER_FILE = 40
MAX_CHARS_PER_FILE = 4000
MAX_HEADINGS_PER_FILE = 12
UNSAFE_PATH_MARKERS = [
    ".db",
    ".db-wal",
    ".db-shm",
    ".wal",
    ".shm",
    ".sqlite",
    ".sqlite-wal",
    ".sqlite-shm",
    "scripts/.logs",
    "active-agent",
    ".ystar_active_agent",
    "__pycache__",
    ".pyc",
    ".pid",
    "daemon",
    "backups/",
]


class MiningError(Exception):
    """Raised when safe mining cannot proceed."""


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_manifest() -> dict[str, Any]:
    path = ROOT / SOURCE_MANIFEST
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def has_unsafe_marker(path: str) -> str | None:
    lowered = path.lower()
    for marker in UNSAFE_PATH_MARKERS:
        m = marker.lower()
        if m in {
            ".db",
            ".db-wal",
            ".db-shm",
            ".wal",
            ".shm",
            ".sqlite",
            ".sqlite-wal",
            ".sqlite-shm",
            ".pyc",
            ".pid",
        }:
            if lowered.endswith(m):
                return marker
        elif m in lowered:
            return marker
    return None


def sanitize_text(text: str) -> str:
    sanitized = text
    for marker in UNSAFE_PATH_MARKERS:
        sanitized = re.sub(re.escape(marker), "[redacted_unsafe_reference]", sanitized, flags=re.IGNORECASE)
    return sanitized


def is_allowed_markdown_artifact(artifact: dict[str, Any]) -> bool:
    artifact_class = artifact.get("artifact_class")
    path = str(artifact.get("path", ""))
    suffix = Path(path).suffix.lower()
    if artifact_class not in ALLOWED_CLASSES:
        return False
    if suffix not in MARKDOWN_EXTENSIONS:
        return False
    if has_unsafe_marker(path):
        return False
    return True


def bounded_read_markdown(path: Path) -> tuple[str, list[str]]:
    lines: list[str] = []
    chars = 0
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if len(lines) >= MAX_LINES_PER_FILE or chars >= MAX_CHARS_PER_FILE:
                break
            remaining = MAX_CHARS_PER_FILE - chars
            chunk = line[:remaining]
            lines.append(chunk.rstrip("\n"))
            chars += len(chunk)
    snippet = sanitize_text("\n".join(lines))
    headings = [
        sanitize_text(line.strip())
        for line in lines
        if line.lstrip().startswith("#")
    ][:MAX_HEADINGS_PER_FILE]
    return snippet, headings


def build_candidates(manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, int], int]:
    selected_by_class: dict[str, int] = defaultdict(int)
    candidates: list[dict[str, Any]] = []
    files_considered = 0

    artifacts = manifest.get("artifacts", [])
    for artifact in artifacts:
        artifact_class = artifact.get("artifact_class")
        path_text = str(artifact.get("path", ""))
        if artifact_class in REFUSED_CLASSES:
            continue
        if not is_allowed_markdown_artifact(artifact):
            continue
        if selected_by_class[artifact_class] >= MAX_FILES_PER_CLASS:
            continue

        files_considered += 1
        source_path = ROOT / path_text
        try:
            source_path.relative_to(ROOT)
        except ValueError as exc:
            raise MiningError(f"Refusing path outside repository: {path_text}") from exc
        if not source_path.exists() or not source_path.is_file():
            continue

        snippet, headings = bounded_read_markdown(source_path)
        selected_by_class[artifact_class] += 1
        candidate_id = f"mdcand-{len(candidates) + 1:03d}"
        candidates.append(
            {
                "candidate_id": candidate_id,
                "source_path": path_text,
                "artifact_class": artifact_class,
                "source_size_bytes": artifact.get("size_bytes"),
                "selected_reason": "allowed_bounded_markdown_report_class",
                "headings": headings,
                "snippet": snippet,
                "safety_level": "bounded_markdown_candidate",
                "ingestion_status": "candidate_only",
                "allowed_next_step": "human_review_or_curated_queue",
                "forbidden_next_step": "direct_brain_writeback",
                "generated_from_manifest_ref": SOURCE_MANIFEST,
            }
        )

    return candidates, dict(selected_by_class), files_considered


def write_json(relative_path: str, payload: Any, generated: list[str]) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
    generated.append(relative_path)


def write_text(relative_path: str, text: str, generated: list[str]) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)
    generated.append(relative_path)


def render_markdown(index: dict[str, Any]) -> str:
    lines = [
        "# Runtime Artifact Markdown Report Candidates",
        "",
        "These candidates were produced from allowed Markdown report classes with strict bounds.",
        "",
        f"- Candidate count: {index['candidate_count']}",
        f"- Ingestion status: {index['ingestion_status']}",
        f"- Safety level: {index['safety_level']}",
        "- Classes seen:",
    ]
    for class_name, count in sorted(index.get("classes_seen", {}).items()):
        lines.append(f"  - {class_name}: {count}")
    lines.extend(["", "## Candidates", ""])
    for candidate in index.get("candidates", []):
        lines.extend(
            [
                f"### {candidate['candidate_id']}",
                "",
                f"- Source: `{candidate['source_path']}`",
                f"- Class: `{candidate['artifact_class']}`",
                f"- Status: `{candidate['ingestion_status']}`",
                f"- Forbidden next step: `{candidate['forbidden_next_step']}`",
                "",
                "Headings:",
            ]
        )
        headings = candidate.get("headings") or ["none captured"]
        lines.extend(f"- {heading}" for heading in headings)
        lines.extend(["", "Snippet:", "", "```text", candidate.get("snippet", ""), "```", ""])
    return "\n".join(lines)


def build() -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    generated: list[str] = []
    manifest = load_manifest()
    candidates, classes_seen, files_considered = build_candidates(manifest)

    candidate_index = {
        "schema_name": "ystar.runtime_artifact_quarantine.safe_mining.markdown_report_candidates",
        "schema_version": "v0",
        "adapter": "runtime_artifact_quarantine/safe_mining/tools/build_markdown_report_candidates.py",
        "source_manifest_ref": SOURCE_MANIFEST,
        "mining_level": "bounded_markdown_report_sampling_v0",
        "allowed_artifact_classes": sorted(ALLOWED_CLASSES),
        "candidate_count": len(candidates),
        "classes_seen": classes_seen,
        "bounds": {
            "max_files_per_class": MAX_FILES_PER_CLASS,
            "max_lines_per_file": MAX_LINES_PER_FILE,
            "max_chars_per_file": MAX_CHARS_PER_FILE,
        },
        "safety_level": "bounded_markdown_candidate",
        "ingestion_status": "candidate_only",
        "allowed_next_step": "human_review_or_curated_queue",
        "forbidden_next_step": "direct_brain_writeback",
        "candidates": candidates,
    }

    mining_manifest = {
        "schema_name": "ystar.runtime_artifact_quarantine.safe_mining.mining_manifest",
        "schema_version": "v0",
        "source_manifest_ref": SOURCE_MANIFEST,
        "generated_files": [
            "runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.json",
            "runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.md",
            "runtime_artifact_quarantine/safe_mining/generated/mining_manifest.json",
        ],
        "allowed_artifact_classes": sorted(ALLOWED_CLASSES),
        "refused_artifact_classes": sorted(REFUSED_CLASSES),
        "files_considered": files_considered,
        "files_selected": len(candidates),
        "classes_seen": classes_seen,
        "bounds": candidate_index["bounds"],
        "safety_note": (
            "Safe mining v0 reads only bounded Markdown report snippets and produces "
            "candidate-only review assets. It does not write brain, memory, or CIEU records."
        ),
    }

    write_json(
        "runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.json",
        candidate_index,
        generated,
    )
    write_text(
        "runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.md",
        render_markdown(candidate_index),
        generated,
    )
    write_json(
        "runtime_artifact_quarantine/safe_mining/generated/mining_manifest.json",
        mining_manifest,
        generated,
    )
    return candidate_index, mining_manifest, generated


def main() -> int:
    try:
        candidate_index, _mining_manifest, generated = build()
    except Exception as exc:
        print("Markdown Report Candidate Builder: FAIL")
        print(f"Error: {exc}")
        return 1

    print("Markdown Report Candidate Builder: PASS")
    print(f"Candidates generated: {candidate_index['candidate_count']}")
    print("Classes seen:")
    for class_name, count in sorted(candidate_index.get("classes_seen", {}).items()):
        print(f"- {class_name}: {count}")
    print("Generated files:")
    for path in generated:
        print(f"- {path}")
    print(
        "Safety note: bounded Markdown candidates only; no DB/log/runtime state, "
        "brain writeback, or CIEU writes."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
