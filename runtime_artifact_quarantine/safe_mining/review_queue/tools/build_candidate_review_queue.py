#!/usr/bin/env python3
"""Build pending review queue entries from safe-mined candidates only.

The builder reads the generated safe-mining candidate index and does not reopen
source artifacts. It creates review-state records, not approvals or ingestion.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
CANDIDATE_INDEX_REF = "runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.json"
OUT_DIR = ROOT / "runtime_artifact_quarantine" / "safe_mining" / "review_queue" / "generated"

ALLOWED_REVIEW_ACTIONS = [
    "approve_for_capsule_hint",
    "approve_for_governance_gap_hint",
    "approve_for_packet_hint",
    "approve_for_cieu_delta_hint",
    "reject",
    "needs_more_context",
]
FORBIDDEN_ACTIONS = [
    "direct_brain_writeback",
    "direct_memory_ingestion",
    "direct_cieu_write",
    "runtime_recovery",
]
INTENDED_USE_BY_CLASS = {
    "DREAM_REPORT": ["memory_continuity_hint", "role_brain_capsule_hint"],
    "DAILY_REPORT": ["memory_continuity_hint", "role_brain_capsule_hint"],
    "DRIFT_REPORT": ["governance_gap_hint", "cieu_prediction_delta_hint"],
    "ESCALATION_REPORT": ["governance_gap_hint", "cieu_prediction_delta_hint"],
    "WHITELIST_REPORT": ["governance_gap_hint", "pre_u_packet_hint"],
}
SNIPPET_PREVIEW_CHARS = 800


def load_candidate_index() -> dict[str, Any]:
    path = ROOT / CANDIDATE_INDEX_REF
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def make_review_entry(index: int, candidate: dict[str, Any]) -> dict[str, Any]:
    artifact_class = candidate.get("artifact_class", "UNKNOWN")
    snippet = str(candidate.get("snippet", ""))
    return {
        "review_id": f"review-{index:03d}",
        "candidate_id": candidate.get("candidate_id"),
        "source_path": candidate.get("source_path"),
        "artifact_class": artifact_class,
        "candidate_safety_level": candidate.get("safety_level"),
        "review_status": "pending_review",
        "ingestion_status": "not_ingested",
        "default_intended_use": INTENDED_USE_BY_CLASS.get(artifact_class, ["needs_more_context"]),
        "allowed_review_actions": ALLOWED_REVIEW_ACTIONS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "snippet_preview": snippet[:SNIPPET_PREVIEW_CHARS],
        "generated_from_candidate_index_ref": CANDIDATE_INDEX_REF,
    }


def build_queue(candidate_index: dict[str, Any]) -> dict[str, Any]:
    candidates = candidate_index.get("candidates", [])
    entries = [make_review_entry(index, candidate) for index, candidate in enumerate(candidates, start=1)]
    status_counts = Counter(entry["review_status"] for entry in entries)
    ingestion_counts = Counter(entry["ingestion_status"] for entry in entries)
    intended_use_counts: Counter[str] = Counter()
    class_counts = Counter(entry["artifact_class"] for entry in entries)
    for entry in entries:
        intended_use_counts.update(entry.get("default_intended_use", []))

    return {
        "schema_name": "ystar.runtime_artifact_quarantine.safe_mining.review_queue",
        "schema_version": "v0",
        "builder": "runtime_artifact_quarantine/safe_mining/review_queue/tools/build_candidate_review_queue.py",
        "generated_from_candidate_index_ref": CANDIDATE_INDEX_REF,
        "review_count": len(entries),
        "statuses": dict(status_counts),
        "ingestion_statuses": dict(ingestion_counts),
        "artifact_classes": dict(class_counts),
        "intended_use_summary": dict(intended_use_counts),
        "allowed_review_actions": ALLOWED_REVIEW_ACTIONS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "default_review_status": "pending_review",
        "default_ingestion_status": "not_ingested",
        "entries": entries,
        "warning": (
            "Review queue entries are not brain memory, CIEU records, or writeback approval. "
            "They require explicit future review."
        ),
    }


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


def render_markdown(queue: dict[str, Any]) -> str:
    lines = [
        "# Candidate Review Queue",
        "",
        "This queue is generated from safe-mined candidates only. All entries are pending review and not ingested.",
        "",
        f"- Review count: {queue['review_count']}",
        "- Statuses:",
    ]
    for status, count in sorted(queue.get("statuses", {}).items()):
        lines.append(f"  - {status}: {count}")
    lines.append("- Intended use summary:")
    for use, count in sorted(queue.get("intended_use_summary", {}).items()):
        lines.append(f"  - {use}: {count}")
    lines.extend(["", "## Entries", ""])
    for entry in queue.get("entries", []):
        lines.extend(
            [
                f"### {entry['review_id']}",
                "",
                f"- Candidate: `{entry['candidate_id']}`",
                f"- Source: `{entry['source_path']}`",
                f"- Class: `{entry['artifact_class']}`",
                f"- Review status: `{entry['review_status']}`",
                f"- Ingestion status: `{entry['ingestion_status']}`",
                f"- Intended use: {', '.join(entry.get('default_intended_use', []))}",
                f"- Forbidden actions: {', '.join(entry.get('forbidden_actions', []))}",
                "",
            ]
        )
    return "\n".join(lines)


def build() -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    generated: list[str] = []
    candidate_index = load_candidate_index()
    queue = build_queue(candidate_index)
    manifest = {
        "schema_name": "ystar.runtime_artifact_quarantine.safe_mining.review_queue.manifest",
        "schema_version": "v0",
        "source_files": [CANDIDATE_INDEX_REF],
        "generated_files": [
            "runtime_artifact_quarantine/safe_mining/review_queue/generated/candidate_review_queue.json",
            "runtime_artifact_quarantine/safe_mining/review_queue/generated/candidate_review_queue.md",
            "runtime_artifact_quarantine/safe_mining/review_queue/generated/review_queue_manifest.json",
        ],
        "review_count": queue["review_count"],
        "statuses": queue["statuses"],
        "ingestion_statuses": queue["ingestion_statuses"],
        "safety_note": (
            "Review queue generation reads only the safe-mining candidate index. "
            "It does not reopen raw artifacts and does not approve ingestion."
        ),
    }
    write_json(
        "runtime_artifact_quarantine/safe_mining/review_queue/generated/candidate_review_queue.json",
        queue,
        generated,
    )
    write_text(
        "runtime_artifact_quarantine/safe_mining/review_queue/generated/candidate_review_queue.md",
        render_markdown(queue),
        generated,
    )
    write_json(
        "runtime_artifact_quarantine/safe_mining/review_queue/generated/review_queue_manifest.json",
        manifest,
        generated,
    )
    return queue, manifest, generated


def main() -> int:
    try:
        queue, _manifest, generated = build()
    except Exception as exc:
        print("Candidate Review Queue Builder: FAIL")
        print(f"Error: {exc}")
        return 1

    print("Candidate Review Queue Builder: PASS")
    print(f"Review entries generated: {queue['review_count']}")
    print("Statuses:")
    for status, count in sorted(queue.get("statuses", {}).items()):
        print(f"- {status}: {count}")
    print("Intended use summary:")
    for use, count in sorted(queue.get("intended_use_summary", {}).items()):
        print(f"- {use}: {count}")
    print("Generated files:")
    for path in generated:
        print(f"- {path}")
    print("Safety note: pending review only; no memory, brain, or CIEU ingestion.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
