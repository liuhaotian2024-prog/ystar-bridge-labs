#!/usr/bin/env python3
"""Build structural evidence scores, decision stubs, and hint routes.

The builder reads only generated candidate, review queue, and disposition
indexes. It does not reopen raw artifacts and does not approve or ingest
candidates.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CANDIDATE_INDEX_REF = "runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.json"
REVIEW_QUEUE_REF = "runtime_artifact_quarantine/safe_mining/review_queue/generated/candidate_review_queue.json"
DISPOSITION_INDEX_REF = "runtime_artifact_quarantine/backlog_disposition/generated/artifact_disposition_index.json"

REPORT_CLASSES = {
    "DREAM_REPORT",
    "DAILY_REPORT",
    "DRIFT_REPORT",
    "ESCALATION_REPORT",
    "WHITELIST_REPORT",
}
HINT_ROUTE_BY_USE = {
    "memory_continuity_hint": "memory_continuity_hint_queue",
    "governance_gap_hint": "governance_gap_hint_queue",
    "role_brain_capsule_hint": "role_brain_capsule_hint_queue",
    "pre_u_packet_hint": "pre_u_packet_hint_queue",
    "cieu_prediction_delta_hint": "cieu_prediction_delta_hint_queue",
}
FORBIDDEN_NEXT_STEPS = [
    "direct_brain_writeback",
    "direct_memory_ingestion",
    "direct_cieu_write",
    "candidate_auto_approval",
    "semantic_truth_claim",
]


def load_json(relative_path: str) -> Any:
    path = ROOT / relative_path
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def structural_score(
    candidate: dict[str, Any] | None,
    review: dict[str, Any],
    disposition: dict[str, Any] | None,
) -> tuple[int, list[str], list[str]]:
    score = 0
    basis: list[str] = []
    missing: list[str] = [
        "semantic_truth_validation",
        "contradiction_check",
        "human_review_decision",
    ]

    if disposition and disposition.get("disposition") == "safe_mined_to_review_queue":
        score += 2
        basis.append("candidate_is_safe_mined_to_review_queue")
    else:
        missing.append("safe_mined_to_review_queue_disposition")

    if candidate and candidate.get("snippet"):
        score += 1
        basis.append("bounded_snippet_present")
    else:
        missing.append("bounded_snippet")

    if candidate and candidate.get("headings"):
        score += 1
        basis.append("headings_present")
    else:
        missing.append("headings")

    if review.get("default_intended_use"):
        score += 1
        basis.append("intended_use_suggestions_present")
    else:
        missing.append("intended_use_suggestions")

    if review.get("artifact_class") in REPORT_CLASSES:
        score += 1
        basis.append("approved_report_like_class")
    else:
        missing.append("approved_report_like_class")

    return score, basis, missing


def readiness_for(score: int, disposition: dict[str, Any] | None) -> str:
    disposition_name = (disposition or {}).get("disposition")
    if disposition_name and disposition_name.startswith("deferred_requires"):
        return "defer_adapter_required"
    if disposition_name in {"ignored_generated_cache", "ignored_or_non_runtime"}:
        return "reject_low_value"
    if score >= 4 and disposition_name == "safe_mined_to_review_queue":
        return "hint_only"
    if score >= 2:
        return "needs_more_context"
    return "reject_low_value"


def confidence_for(readiness: str) -> str:
    if readiness == "hint_only":
        return "structural_only"
    if readiness == "needs_more_context":
        return "medium"
    return "low"


def source_quality_for(candidate: dict[str, Any] | None, disposition: dict[str, Any] | None) -> str:
    if candidate and disposition and disposition.get("disposition") == "safe_mined_to_review_queue":
        return "bounded_markdown_report_candidate"
    if disposition and str(disposition.get("disposition", "")).startswith("deferred"):
        return "adapter_required"
    return "low_or_unclassified"


def build_evidence_record(
    index: int,
    review: dict[str, Any],
    candidate: dict[str, Any] | None,
    disposition: dict[str, Any] | None,
) -> dict[str, Any]:
    score, basis, missing = structural_score(candidate, review, disposition)
    readiness = readiness_for(score, disposition)
    return {
        "evidence_id": f"evidence-{index:03d}",
        "candidate_id": review.get("candidate_id"),
        "review_id": review.get("review_id"),
        "source_path": review.get("source_path"),
        "artifact_class": review.get("artifact_class"),
        "disposition": (disposition or {}).get("disposition"),
        "review_status": review.get("review_status"),
        "ingestion_status": review.get("ingestion_status", "not_ingested"),
        "structural_score": score,
        "source_quality_level": source_quality_for(candidate, disposition),
        "reuse_readiness": readiness,
        "confidence_level": confidence_for(readiness),
        "contradiction_status": "not_checked",
        "semantic_truth_status": "not_evaluated",
        "evidence_basis": basis,
        "missing_evidence": missing,
        "allowed_next_step": "evidence_review_or_manual_decision",
        "forbidden_next_steps": FORBIDDEN_NEXT_STEPS,
        "brain_writeback_allowed": False,
        "memory_ingestion_allowed": False,
        "cieu_write_allowed": False,
    }


def build_decision_stub(index: int, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "decision_id": f"decision-{index:03d}",
        "review_id": evidence.get("review_id"),
        "candidate_id": evidence.get("candidate_id"),
        "decision_status": "undecided",
        "reviewer": "unset",
        "decision": "none",
        "approved_use_scope": [],
        "rejected_reason": None,
        "required_additional_evidence": [],
        "brain_writeback_allowed": False,
        "memory_ingestion_allowed": False,
        "cieu_write_allowed": False,
        "decision_notes": "pending human or validator review",
    }


def route_for_intended_use(intended_use: str, readiness: str) -> str:
    if readiness == "defer_adapter_required":
        return "deferred_adapter_required"
    if readiness == "needs_more_context":
        return "deferred_needs_more_context"
    if readiness == "reject_low_value":
        return "rejected_or_low_value"
    return HINT_ROUTE_BY_USE.get(intended_use, "deferred_needs_more_context")


def build_routes(evidence_records: list[dict[str, Any]], review_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    for evidence in evidence_records:
        review = review_by_id.get(evidence.get("review_id"), {})
        intended_uses = review.get("default_intended_use") or ["needs_more_context"]
        for intended_use in intended_uses:
            route = route_for_intended_use(intended_use, evidence["reuse_readiness"])
            routes.append(
                {
                    "route": route,
                    "candidate_id": evidence.get("candidate_id"),
                    "review_id": evidence.get("review_id"),
                    "evidence_id": evidence.get("evidence_id"),
                    "readiness": evidence.get("reuse_readiness"),
                    "status": "not_approved",
                    "ingestion_status": "not_ingested",
                    "allowed_next_step": "evidence_review_or_manual_decision",
                    "forbidden_next_step": "direct_brain_writeback",
                }
            )
    return routes


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


def build_pack() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    candidate_index = load_json(CANDIDATE_INDEX_REF)
    review_queue = load_json(REVIEW_QUEUE_REF)
    disposition_index = load_json(DISPOSITION_INDEX_REF)

    candidate_by_id = {candidate.get("candidate_id"): candidate for candidate in candidate_index.get("candidates", [])}
    disposition_by_path = {record.get("artifact_path"): record for record in disposition_index.get("records", [])}
    review_by_id = {entry.get("review_id"): entry for entry in review_queue.get("entries", [])}

    evidence_records = []
    for index, review in enumerate(review_queue.get("entries", []), start=1):
        candidate = candidate_by_id.get(review.get("candidate_id"))
        disposition = disposition_by_path.get(review.get("source_path"))
        evidence_records.append(build_evidence_record(index, review, candidate, disposition))

    decisions = [build_decision_stub(index, evidence) for index, evidence in enumerate(evidence_records, start=1)]
    routes = build_routes(evidence_records, review_by_id)

    readiness_counts = Counter(record["reuse_readiness"] for record in evidence_records)
    confidence_counts = Counter(record["confidence_level"] for record in evidence_records)
    route_counts = Counter(route["route"] for route in routes)
    semantic_counts = Counter(record["semantic_truth_status"] for record in evidence_records)

    summary = {
        "candidates_scored": len(evidence_records),
        "decision_stubs_created": len(decisions),
        "routes_created": len(routes),
        "reuse_readiness": dict(readiness_counts),
        "confidence": dict(confidence_counts),
        "route_counts": dict(route_counts),
        "semantic_truth_status": dict(semantic_counts),
        "automatic_approvals": 0,
        "brain_writeback_allowed": 0,
        "memory_ingestion_allowed": 0,
        "cieu_write_allowed": 0,
        "warning": "Evidence scoring is structural only. It is not truth validation and not memory ingestion.",
    }

    evidence_payload = {
        "schema_name": "ystar.runtime_artifact_quarantine.evidence_review.evidence_scores",
        "schema_version": "v0",
        "source_files": [CANDIDATE_INDEX_REF, REVIEW_QUEUE_REF, DISPOSITION_INDEX_REF],
        "summary": summary,
        "records": evidence_records,
    }
    decision_payload = {
        "schema_name": "ystar.runtime_artifact_quarantine.evidence_review.review_decision_stub",
        "schema_version": "v0",
        "source_files": [REVIEW_QUEUE_REF, "runtime_artifact_quarantine/evidence_review/generated/evidence_scores.json"],
        "decision_stubs_created": len(decisions),
        "automatic_approvals": 0,
        "decisions": decisions,
    }
    routing_payload = {
        "schema_name": "ystar.runtime_artifact_quarantine.evidence_review.hint_routing_index",
        "schema_version": "v0",
        "source_files": [REVIEW_QUEUE_REF, "runtime_artifact_quarantine/evidence_review/generated/evidence_scores.json"],
        "route_counts": dict(route_counts),
        "routes_created": len(routes),
        "routes": routes,
        "warning": "Hint routes are not approved and remain not_ingested.",
    }
    manifest = {
        "schema_name": "ystar.runtime_artifact_quarantine.evidence_review.manifest",
        "schema_version": "v0",
        "source_files": [CANDIDATE_INDEX_REF, REVIEW_QUEUE_REF, DISPOSITION_INDEX_REF],
        "generated_files": [
            "runtime_artifact_quarantine/evidence_review/generated/evidence_scores.json",
            "runtime_artifact_quarantine/evidence_review/generated/review_decision_stub.json",
            "runtime_artifact_quarantine/evidence_review/generated/hint_routing_index.json",
            "runtime_artifact_quarantine/evidence_review/generated/evidence_review_summary.md",
            "runtime_artifact_quarantine/evidence_review/generated/evidence_review_manifest.json",
        ],
        "summary": summary,
    }
    return evidence_payload, decision_payload, routing_payload, manifest


def render_summary(evidence_payload: dict[str, Any], routing_payload: dict[str, Any]) -> str:
    summary = evidence_payload["summary"]
    lines = [
        "# Evidence Review Summary",
        "",
        "Evidence review is structural only. It is not truth validation, approval, or ingestion.",
        "",
        f"- Candidates scored: {summary['candidates_scored']}",
        f"- Decision stubs created: {summary['decision_stubs_created']}",
        f"- Routes created: {summary['routes_created']}",
        f"- Automatic approvals: {summary['automatic_approvals']}",
        "",
        "## Reuse Readiness",
        "",
    ]
    for key, count in sorted(summary.get("reuse_readiness", {}).items()):
        lines.append(f"- {key}: {count}")
    lines.extend(["", "## Hint Routes", ""])
    for key, count in sorted(routing_payload.get("route_counts", {}).items()):
        lines.append(f"- {key}: {count}")
    lines.extend(["", f"Warning: {summary['warning']}", ""])
    return "\n".join(lines)


def main() -> int:
    try:
        evidence_payload, decision_payload, routing_payload, manifest = build_pack()
        write_json("runtime_artifact_quarantine/evidence_review/generated/evidence_scores.json", evidence_payload)
        write_json("runtime_artifact_quarantine/evidence_review/generated/review_decision_stub.json", decision_payload)
        write_json("runtime_artifact_quarantine/evidence_review/generated/hint_routing_index.json", routing_payload)
        write_text(
            "runtime_artifact_quarantine/evidence_review/generated/evidence_review_summary.md",
            render_summary(evidence_payload, routing_payload),
        )
        write_json("runtime_artifact_quarantine/evidence_review/generated/evidence_review_manifest.json", manifest)
    except Exception as exc:
        print("Evidence Review Pack Builder: FAIL")
        print(f"Error: {exc}")
        return 1

    summary = evidence_payload["summary"]
    print("Evidence Review Pack Builder: PASS")
    print(f"Candidates scored: {summary['candidates_scored']}")
    print(f"Decision stubs created: {summary['decision_stubs_created']}")
    print(f"Routes created: {summary['routes_created']}")
    print("Reuse readiness:")
    for key, count in sorted(summary.get("reuse_readiness", {}).items()):
        print(f"- {key}: {count}")
    print(summary["warning"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
